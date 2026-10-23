"""用户认证的 Redis 原子操作；不保存原始验证码或刷新令牌。"""

import hashlib
import hmac
import json
import time
from fastapi import Depends, HTTPException, Request
from redis.asyncio import Redis
from app.core.config import Settings
from app.core.redis import get_redis

RESERVE_CODE = """
local cooldown = redis.call('PTTL', KEYS[1])
if cooldown >= 0 then return math.max(1,math.ceil(cooldown/1000)) end
if tonumber(redis.call('GET', KEYS[3]) or '0') >= 10 then return math.max(1,redis.call('TTL',KEYS[3])) end
if tonumber(redis.call('GET', KEYS[4]) or '0') >= 30 then return math.max(1,redis.call('TTL',KEYS[4])) end
if redis.call('INCR',KEYS[3]) == 1 then redis.call('EXPIRE',KEYS[3],86400) end
if redis.call('INCR',KEYS[4]) == 1 then redis.call('EXPIRE',KEYS[4],3600) end
redis.call('SET',KEYS[1],ARGV[2],'EX',60)
redis.call('HSET',KEYS[2],'digest',ARGV[1],'nonce',ARGV[2],'tries',0)
redis.call('EXPIRE',KEYS[2],300)
return 0
"""
CANCEL_CODE = """
if redis.call('HGET',KEYS[2],'nonce') == ARGV[1] then redis.call('DEL',KEYS[2]) end
if redis.call('GET',KEYS[1]) == ARGV[1] then redis.call('DEL',KEYS[1]) end
return 1
"""
CONSUME_CODE = """
local expected = redis.call('HGET',KEYS[1],'digest')
if not expected then return 0 end
if expected == ARGV[1] then redis.call('DEL',KEYS[1]); return 1 end
if redis.call('HINCRBY',KEYS[1],'tries',1) >= 5 then redis.call('DEL',KEYS[1]) end
return 0
"""
BUDGET = """
local n = redis.call('INCR',KEYS[1])
if n == 1 then redis.call('EXPIRE',KEYS[1],ARGV[2]) end
if n > tonumber(ARGV[1]) then return math.max(1,redis.call('TTL',KEYS[1])) end
return 0
"""
LOGIN_FAILURE = """
local locked=redis.call('TTL',KEYS[2])
if locked>=0 then return math.max(1,locked) end
local n=redis.call('INCR',KEYS[1])
if n==1 then redis.call('EXPIRE',KEYS[1],300) end
if n>5 then redis.call('SET',KEYS[2],'1','EX',900); redis.call('DEL',KEYS[1]); return 900 end
return 0
"""
ISSUE_SESSION = """
local entries=redis.call('HGETALL',KEYS[1])
local incoming=cjson.decode(ARGV[2])
local count=0
local oldest=nil
local oldest_exp=nil
for i=1,#entries,2 do
 local item=cjson.decode(entries[i+1])
 if item.expires_at<=tonumber(ARGV[3]) or item.device==incoming.device then
  redis.call('HDEL',KEYS[1],entries[i])
 else
  count=count+1
  if not oldest_exp or item.expires_at<oldest_exp then oldest=entries[i]; oldest_exp=item.expires_at end
 end
end
if count>=10 and oldest then redis.call('HDEL',KEYS[1],oldest) end
redis.call('HSET',KEYS[1],ARGV[1],ARGV[2])
local ttl=math.max(tonumber(ARGV[4]),redis.call('TTL',KEYS[1]))
redis.call('EXPIRE',KEYS[1],ttl)
return 1
"""
ROTATE_SESSION = """
local value=redis.call('HGET',KEYS[1],ARGV[1])
if not value then return 0 end
local item=cjson.decode(value)
if item.refresh~=ARGV[2] or item.expires_at<=tonumber(ARGV[4]) or item.version~=tonumber(ARGV[5]) then return 0 end
local incoming=cjson.decode(ARGV[3])
incoming.device=item.device
redis.call('HSET',KEYS[1],ARGV[1],cjson.encode(incoming))
redis.call('EXPIRE',KEYS[1],math.max(tonumber(ARGV[6]),redis.call('TTL',KEYS[1])))
return 1
"""
DELETE_SESSION = """
local value=redis.call('HGET',KEYS[1],ARGV[1])
if not value then return 0 end
local item=cjson.decode(value)
if item.refresh~=ARGV[2] then return 0 end
redis.call('HDEL',KEYS[1],ARGV[1])
return 1
"""


def rate_limited(seconds):
    return HTTPException(
        429, '请求过于频繁，请稍后重试', headers={'Retry-After': str(max(1, int(seconds)))}
    )


class AppAuthStore:
    def __init__(self, redis: Redis, secret: str, prefix: str, config: Settings):
        self.redis, self.secret, self.prefix = redis, secret, prefix
        self.config = config

    def digest(self, value):
        return hmac.new(self.secret.encode(), value.encode(), hashlib.sha256).hexdigest()

    def key(self, *parts):
        return self.prefix + ':' + ':'.join(parts)

    def phone_key(self, phone):
        return self.digest('phone:' + phone)

    def code_keys(self, phone, scene):
        key = self.phone_key(phone)
        return self.key('cooldown', key), self.key('code', scene, key)

    async def reserve_code(self, phone, scene, code, nonce, ip):
        cooldown, code_key = self.code_keys(phone, scene)
        ttl = await self.redis.eval(
            RESERVE_CODE,
            4,
            cooldown,
            code_key,
            self.key('sms-day', self.phone_key(phone)),
            self.key('sms-ip', self.digest(ip)),
            self.digest(f'{scene}:{phone}:{code}'),
            nonce,
        )
        if ttl:
            raise rate_limited(ttl)

    async def cancel_code(self, phone, scene, nonce):
        await self.redis.eval(CANCEL_CODE, 2, *self.code_keys(phone, scene), nonce)

    async def consume_code(self, phone, scene, code):
        if self.config.user_sms_mock_enabled:
            import re

            return bool(re.fullmatch(r'[0-9]{6}', code))
        return bool(
            await self.redis.eval(
                CONSUME_CODE,
                1,
                self.code_keys(phone, scene)[1],
                self.digest(f'{scene}:{phone}:{code}'),
            )
        )

    async def login_budget(self, ip):
        ttl = await self.redis.eval(BUDGET, 1, self.key('login-ip', self.digest(ip)), 60, 300)
        if ttl:
            raise rate_limited(ttl)

    async def check_login_lock(self, phone):
        ttl = await self.redis.ttl(self.key('locked', self.phone_key(phone)))
        if ttl >= 0:
            raise rate_limited(ttl)

    async def login_failure(self, phone):
        key = self.phone_key(phone)
        ttl = await self.redis.eval(
            LOGIN_FAILURE, 2, self.key('failed', key), self.key('locked', key)
        )
        if ttl:
            raise rate_limited(ttl)

    async def login_success(self, phone):
        await self.check_login_lock(phone)
        await self.redis.delete(self.key('failed', self.phone_key(phone)))

    def sessions_key(self, uid):
        return self.key('sessions', uid)

    def session_record(self, refresh, jti, version, device=''):
        return json.dumps(
            {
                'refresh': self.digest(refresh),
                'jti': jti,
                'version': version,
                'device': self.digest(device),
                'expires_at': int(time.time()) + self.config.user_refresh_token_days * 86400,
            }
        )

    async def issue(self, uid, sid, refresh, jti, version, device):
        await self.redis.eval(
            ISSUE_SESSION,
            1,
            self.sessions_key(uid),
            sid,
            self.session_record(refresh, jti, version, device),
            int(time.time()),
            self.config.user_refresh_token_days * 86400,
        )

    async def rotate(self, uid, sid, previous, refresh, jti, version):
        return bool(
            await self.redis.eval(
                ROTATE_SESSION,
                1,
                self.sessions_key(uid),
                sid,
                self.digest(previous),
                self.session_record(refresh, jti, version),
                int(time.time()),
                version,
                self.config.user_refresh_token_days * 86400,
            )
        )

    async def valid_access(self, uid, sid, jti, version):
        raw = await self.redis.hget(self.sessions_key(uid), sid)
        if not raw:
            return False
        session = json.loads(raw)
        return (
            session['expires_at'] > time.time()
            and session['jti'] == jti
            and session['version'] == version
        )

    async def logout(self, uid, sid, refresh):
        return bool(
            await self.redis.eval(
                DELETE_SESSION, 1, self.sessions_key(uid), sid, self.digest(refresh)
            )
        )

    async def revoke_all(self, uid):
        await self.redis.delete(self.sessions_key(uid))


def get_app_store(request: Request, redis: Redis = Depends(get_redis)):
    from app.core.app_security import app_secret

    config = request.app.state.config
    return AppAuthStore(redis, app_secret(config), config.user_auth_redis_prefix, config)
