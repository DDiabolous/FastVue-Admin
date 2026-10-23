"""真实 PostgreSQL + Redis 的 App 认证测试；短信发送器只在测试中注入。"""

import asyncio
from datetime import timedelta
import json
import os
import unittest
import uuid
from unittest.mock import patch
import jwt
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from redis.asyncio import Redis
from app.main import create_app
from app.core.config import Settings
from app.db.base import utcnow
from app.cli import initialize
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from alembic import command
from alembic.config import Config
from pathlib import Path
from app.core.redis import get_redis
from app.models.user.accounts import UserAccount
from app.services.user.auth_store import UserAuthStore
from app.services.sms import get_sms_sender

ROOT = '/api/v1/user'
TEST_SECRET = 'app-test-only-secret-' + 'x' * 48
PASSWORD = 'App test password 123!'


class CapturingSender:
    def __init__(self):
        self.codes = {}
        self.fail = False

    async def send(self, phone, scene, code):
        if self.fail:
            raise HTTPException(503, '短信发送失败，请稍后重试')
        self.codes[phone, scene] = code


class UserAuthTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        url = os.getenv('TEST_DATABASE_URL')
        if not url:
            self.skipTest('Set TEST_DATABASE_URL to PostgreSQL for integration tests')
        self.prefix = 'test:app-auth:' + uuid.uuid4().hex
        self.config = Settings(
            database_url=url,
            user_sms_mock_enabled=False,
            user_jwt_secret=SecretStr(TEST_SECRET),
            user_auth_redis_prefix=self.prefix,
        )
        self.app = create_app(self.config)
        self.schema = 'test_user_auth_' + uuid.uuid4().hex
        self.admin_engine = create_async_engine(url)
        async with self.admin_engine.begin() as db:
            await db.execute(text(f'CREATE SCHEMA "{self.schema}"'))
        self.engine = create_async_engine(
            url, connect_args={'server_settings': {'search_path': self.schema}}
        )
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        await self.app.state.engine.dispose()
        self.app.state.engine, self.app.state.sessions = self.engine, self.sessions
        config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))

        def migrate(connection):
            config.attributes['connection'] = connection
            command.upgrade(config, 'head')

        async with self.engine.begin() as db:
            await db.run_sync(migrate)
        await initialize(self.sessions, 'AdminPass123!', demo=False)
        self.redis = Redis.from_url(
            os.getenv('USER_AUTH_TEST_REDIS_URL', 'redis://localhost:6379/15'),
            decode_responses=True,
        )
        await self.redis.ping()
        self.store = UserAuthStore(self.redis, TEST_SECRET, self.prefix, self.config)
        self.sender = CapturingSender()
        self.app.dependency_overrides[get_redis] = lambda: self.redis
        self.app.dependency_overrides[get_sms_sender] = lambda: self.sender
        self.client = AsyncClient(transport=ASGITransport(app=self.app), base_url='http://test')
        self.ids = set()
        self.phone = self.new_phone()

    def new_phone(self):
        return '139' + str(uuid.uuid4().int % 100000000).zfill(8)

    async def asyncTearDown(self):
        await self.client.aclose()
        keys = [k async for k in self.redis.scan_iter(match=self.prefix + ':*')]
        if keys:
            await self.redis.delete(*keys)
        await self.redis.aclose()
        await self.engine.dispose()
        async with self.admin_engine.begin() as db:
            await db.execute(text(f'DROP SCHEMA "{self.schema}" CASCADE'))
        await self.admin_engine.dispose()

    def auth(self, tokens):
        return {'Authorization': 'Bearer ' + tokens['access_token']}

    async def send_code(self, scene, phone=None, tokens=None, allow_resend=False):
        phone = phone or self.phone
        canonical = '+86' + phone if not phone.startswith('+') else phone
        if allow_resend:
            await self.redis.delete(self.store.code_keys(canonical, scene)[0])
        res = await self.client.post(
            ROOT + '/auth/send-code',
            json={'phone': phone, 'scene': scene},
            headers=self.auth(tokens) if tokens else {},
        )
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()['data'], {'expires_in': 300, 'retry_after': 60})
        self.assertNotIn('code', res.json()['data'])
        code = self.sender.codes[canonical, scene]
        self.assertRegex(code, r'^[0-9]{6}$')
        return code

    async def register(self, device='device-A'):
        code = await self.send_code('register')
        res = await self.client.post(
            ROOT + '/auth/register',
            json={'phone': self.phone, 'code': code, 'password': PASSWORD, 'device_id': device},
        )
        self.assertEqual(res.status_code, 200, res.text)
        tokens = res.json()['data']
        self.ids.add(tokens['user']['id'])
        self.assertNotIn('set-cookie', res.headers)
        self.assertEqual(res.headers['cache-control'], 'no-store')
        return tokens

    async def login(self, device='device-B', password=PASSWORD):
        res = await self.client.post(
            ROOT + '/auth/login',
            json={
                'phone': self.phone,
                'login_type': 'password',
                'credential': password,
                'device_id': device,
            },
        )
        self.assertEqual(res.status_code, 200, res.text)
        return res.json()['data']

    async def me(self, tokens):
        return await self.client.get(ROOT + '/me', headers=self.auth(tokens))

    async def test_registration_tokens_profile_and_rotation(self):
        tokens = await self.register()
        claims = jwt.decode(
            tokens['access_token'],
            TEST_SECRET,
            algorithms=['HS256'],
            audience='app',
            issuer=self.config.user_jwt_issuer,
        )
        self.assertEqual(claims['scope'], 'app')
        self.assertEqual(claims['exp'] - claims['iat'], 900)
        self.assertEqual(tokens['expires_in'], 900)
        self.assertEqual(tokens['refresh_expires_in'], 604800)
        info = (await self.me(tokens)).json()['data']
        self.assertEqual(info['phone'], '+86' + self.phone)
        self.assertNotIn('membership', info)
        async with self.sessions() as db:
            user = await db.get(UserAccount, info['id'])
            self.assertTrue(user.password_hash.startswith('$argon2id$'))
        raw = await self.redis.hget(self.store.sessions_key(info['id']), claims['sid'])
        self.assertNotIn(tokens['refresh_token'], raw)
        self.assertNotIn('device-A', raw)
        code_key = self.store.code_keys('+86' + self.phone, 'register')[1]
        self.assertFalse(await self.redis.exists(code_key))
        refreshed = await self.client.post(
            ROOT + '/auth/refresh', json={'refresh_token': tokens['refresh_token']}
        )
        self.assertEqual(refreshed.status_code, 200, refreshed.text)
        fresh = refreshed.json()['data']
        self.assertNotEqual(fresh['refresh_token'], tokens['refresh_token'])
        self.assertEqual((await self.me(tokens)).status_code, 401)
        self.assertEqual((await self.me(fresh)).status_code, 200)
        replay = await self.client.post(
            ROOT + '/auth/refresh', json={'refresh_token': tokens['refresh_token']}
        )
        self.assertEqual(replay.status_code, 401)

    async def test_concurrent_refresh_only_one_wins(self):
        tokens = await self.register()
        results = await asyncio.gather(
            *[
                self.client.post(
                    ROOT + '/auth/refresh', json={'refresh_token': tokens['refresh_token']}
                )
                for _ in range(2)
            ]
        )
        self.assertEqual(sorted(r.status_code for r in results), [200, 401])
        winner = next(r.json()['data'] for r in results if r.status_code == 200)
        self.assertEqual((await self.me(winner)).status_code, 200)

    async def test_logout_device_isolation_and_same_device_relogin(self):
        a = await self.register()
        b = await self.login('device-B')
        mismatch = await self.client.post(
            ROOT + '/auth/logout', json={'refresh_token': b['refresh_token']}, headers=self.auth(a)
        )
        self.assertEqual(mismatch.status_code, 403)
        result = await self.client.post(
            ROOT + '/auth/logout', json={'refresh_token': a['refresh_token']}, headers=self.auth(a)
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual((await self.me(a)).status_code, 401)
        self.assertEqual((await self.me(b)).status_code, 200)
        c = await self.login('device-B')
        self.assertEqual((await self.me(b)).status_code, 401)
        self.assertEqual((await self.me(c)).status_code, 200)

    async def test_sms_cooldown_ttl_scene_isolation_and_single_use(self):
        code = await self.send_code('register')
        canonical = '+86' + self.phone
        code_key = self.store.code_keys(canonical, 'register')[1]
        self.assertGreater(await self.redis.ttl(code_key), 290)
        self.assertNotIn(code, json.dumps(await self.redis.hgetall(code_key)))
        # 同一号码不同写法、不同场景也不能绕过短信冷却。
        cooldown = await self.client.post(
            ROOT + '/auth/send-code', json={'phone': canonical, 'scene': 'login'}
        )
        self.assertEqual(cooldown.status_code, 429)
        self.assertIn('retry-after', cooldown.headers)
        await self.redis.pexpire(self.store.code_keys(canonical, 'register')[0], 500)
        edge = await self.client.post(
            ROOT + '/auth/send-code', json={'phone': canonical, 'scene': 'login'}
        )
        self.assertEqual(edge.status_code, 429)
        wrong_scene = await self.client.post(
            ROOT + '/auth/login',
            json={'phone': self.phone, 'login_type': 'sms', 'credential': code, 'device_id': 'A'},
        )
        self.assertEqual(wrong_scene.status_code, 401)
        res = await self.client.post(
            ROOT + '/auth/register',
            json={'phone': canonical, 'code': code, 'password': PASSWORD, 'device_id': 'A'},
        )
        self.assertEqual(res.status_code, 200, res.text)
        self.ids.add(res.json()['data']['user']['id'])
        replay = await self.client.post(
            ROOT + '/auth/register',
            json={'phone': self.phone, 'code': code, 'password': PASSWORD, 'device_id': 'A'},
        )
        self.assertEqual(replay.status_code, 400)
        sms = await self.send_code('login', allow_resend=True)
        logged = await self.client.post(
            ROOT + '/auth/login',
            json={'phone': self.phone, 'login_type': 'sms', 'credential': sms, 'device_id': 'B'},
        )
        self.assertEqual(logged.status_code, 200, logged.text)

    async def test_code_expires_and_five_wrong_attempts_destroy_it(self):
        code = await self.send_code('register')
        wrong = '000000' if code != '000000' else '111111'
        for _ in range(5):
            res = await self.client.post(
                ROOT + '/auth/register',
                json={'phone': self.phone, 'code': wrong, 'password': PASSWORD, 'device_id': 'A'},
            )
            self.assertEqual(res.status_code, 400)
        self.assertFalse(
            await self.redis.exists(self.store.code_keys('+86' + self.phone, 'register')[1])
        )
        code = await self.send_code('register', allow_resend=True)
        await self.redis.delete(self.store.code_keys('+86' + self.phone, 'register')[1])
        expired = await self.client.post(
            ROOT + '/auth/register',
            json={'phone': self.phone, 'code': code, 'password': PASSWORD, 'device_id': 'A'},
        )
        self.assertEqual(expired.status_code, 400)

    async def test_sixth_failure_locks_for_fifteen_minutes(self):
        await self.register()
        for _ in range(5):
            res = await self.client.post(
                ROOT + '/auth/login',
                json={
                    'phone': self.phone,
                    'login_type': 'password',
                    'credential': 'wrong',
                    'device_id': 'B',
                },
            )
            self.assertEqual(res.status_code, 401)
        key = self.store.phone_key('+86' + self.phone)
        self.assertGreater(await self.redis.ttl(self.store.key('failed', key)), 280)
        sixth = await self.client.post(
            ROOT + '/auth/login',
            json={
                'phone': self.phone,
                'login_type': 'password',
                'credential': 'wrong',
                'device_id': 'B',
            },
        )
        self.assertEqual(sixth.status_code, 429)
        self.assertGreater(await self.redis.ttl(self.store.key('locked', key)), 890)
        correct = await self.client.post(
            ROOT + '/auth/login',
            json={
                'phone': self.phone,
                'login_type': 'password',
                'credential': PASSWORD,
                'device_id': 'B',
            },
        )
        self.assertEqual(correct.status_code, 429)
        await self.redis.delete(self.store.key('locked', key))
        await self.login()

    async def test_password_reset_invalidates_every_device(self):
        a = await self.register()
        b = await self.login()
        code = await self.send_code('reset_pwd', allow_resend=True)
        reset = await self.client.post(
            ROOT + '/auth/reset-password',
            json={'phone': self.phone, 'code': code, 'new_password': 'New password 456!'},
        )
        self.assertEqual(reset.status_code, 200, reset.text)
        for tokens in [a, b]:
            self.assertEqual((await self.me(tokens)).status_code, 401)
            refreshed = await self.client.post(
                ROOT + '/auth/refresh', json={'refresh_token': tokens['refresh_token']}
            )
            self.assertEqual(refreshed.status_code, 401)
        wrong = await self.client.post(
            ROOT + '/auth/login',
            json={
                'phone': self.phone,
                'login_type': 'password',
                'credential': PASSWORD,
                'device_id': 'A',
            },
        )
        self.assertEqual(wrong.status_code, 401)
        await self.login(password='New password 456!')

    async def test_reset_refresh_race_cannot_resurrect_session(self):
        a = await self.register()
        code = await self.send_code('reset_pwd', allow_resend=True)
        reset, refresh = await asyncio.gather(
            self.client.post(
                ROOT + '/auth/reset-password',
                json={'phone': self.phone, 'code': code, 'new_password': 'New password 456!'},
            ),
            self.client.post(ROOT + '/auth/refresh', json={'refresh_token': a['refresh_token']}),
        )
        self.assertEqual(reset.status_code, 200, reset.text)
        self.assertIn(refresh.status_code, [200, 401])
        if refresh.status_code == 200:
            self.assertEqual((await self.me(refresh.json()['data'])).status_code, 401)
        self.assertFalse(await self.redis.exists(self.store.sessions_key(a['user']['id'])))

    async def test_delete_with_password_or_dedicated_code(self):
        a = await self.register()
        b = await self.login()
        bad = await self.client.post(
            ROOT + '/auth/delete-account', json={'password': 'wrong'}, headers=self.auth(a)
        )
        self.assertEqual(bad.status_code, 400)
        delete_code = await self.send_code('delete_account', tokens=a, allow_resend=True)
        result = await self.client.post(
            ROOT + '/auth/delete-account', json={'code': delete_code}, headers=self.auth(a)
        )
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual((await self.me(b)).status_code, 401)
        async with self.sessions() as db:
            user = await db.get(UserAccount, a['user']['id'])
            self.assertEqual(user.status, 'deleted')
            self.assertIsNone(user.phone)
            self.assertIsNone(user.password_hash)
        # 释放手机号后可以重新注册为全新的 App 用户。
        code = await self.send_code('register', allow_resend=True)
        res = await self.client.post(
            ROOT + '/auth/register',
            json={'phone': self.phone, 'code': code, 'password': PASSWORD, 'device_id': 'A'},
        )
        fresh = res.json()['data']
        self.ids.add(fresh['user']['id'])
        self.assertNotEqual(fresh['user']['id'], a['user']['id'])
        result = await self.client.post(
            ROOT + '/auth/delete-account', json={'password': PASSWORD}, headers=self.auth(fresh)
        )
        self.assertEqual(result.status_code, 200)

    async def test_delete_code_requires_own_authenticated_phone(self):
        a = await self.register()
        no_auth = await self.client.post(
            ROOT + '/auth/send-code', json={'phone': self.phone, 'scene': 'delete_account'}
        )
        self.assertEqual(no_auth.status_code, 401)
        other = await self.client.post(
            ROOT + '/auth/send-code',
            json={'phone': self.new_phone(), 'scene': 'delete_account'},
            headers=self.auth(a),
        )
        self.assertEqual(other.status_code, 403)
        login_code = await self.send_code('login', allow_resend=True)
        wrong_scene = await self.client.post(
            ROOT + '/auth/delete-account', json={'code': login_code}, headers=self.auth(a)
        )
        self.assertEqual(wrong_scene.status_code, 400)
        for body in [{}, {'password': PASSWORD, 'code': '123456'}]:
            self.assertEqual(
                (
                    await self.client.post(
                        ROOT + '/auth/delete-account', json=body, headers=self.auth(a)
                    )
                ).status_code,
                422,
            )

    async def test_scope_audience_expiry_and_backend_isolation(self):
        a = await self.register()
        for path in ['/api/v1/admin/accounts', '/api/v1/admin/me']:
            self.assertEqual((await self.client.get(path, headers=self.auth(a))).status_code, 401)
        claims = jwt.decode(a['access_token'], TEST_SECRET, algorithms=['HS256'], audience='app')
        for change in [
            {'scope': 'admin'},
            {'aud': 'backend'},
            {'type': 'refresh'},
            {'exp': utcnow() - timedelta(seconds=1)},
        ]:
            invalid = jwt.encode({**claims, **change}, TEST_SECRET, algorithm='HS256')
            self.assertEqual((await self.me({'access_token': invalid})).status_code, 401)
        no_jti = dict(claims)
        no_jti.pop('jti')
        for token in [
            jwt.encode(no_jti, TEST_SECRET, algorithm='HS256'),
            jwt.encode(claims, 'wrong-key-' * 8, algorithm='HS256'),
            'local-auth:super',
        ]:
            self.assertEqual((await self.me({'access_token': token})).status_code, 401)
        res = await self.client.post(
            '/api/v1/admin/auth/login', json={'username': 'admin', 'password': 'AdminPass123!'}
        )
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(
            (await self.me({'access_token': res.json()['data']['token']})).status_code, 401
        )
        self.assertEqual(
            (
                await self.client.get(
                    '/api/v1/admin/accounts',
                    headers={'Authorization': 'Bearer ' + res.json()['data']['token']},
                )
            ).status_code,
            200,
        )

    async def test_gateway_failure_removes_unusable_code(self):
        self.sender.fail = True
        res = await self.client.post(
            ROOT + '/auth/send-code', json={'phone': self.phone, 'scene': 'register'}
        )
        self.assertEqual(res.status_code, 503)
        self.assertFalse(
            await self.redis.exists(*self.store.code_keys('+86' + self.phone, 'register'))
        )
        self.sender.fail = False
        await self.send_code('register')

    async def test_sms_daily_budget_and_concurrent_cooldown(self):
        results = await asyncio.gather(
            *[
                self.client.post(
                    ROOT + '/auth/send-code', json={'phone': self.phone, 'scene': 'register'}
                )
                for _ in range(2)
            ]
        )
        self.assertEqual(sorted(r.status_code for r in results), [200, 429])
        for _ in range(9):
            await self.send_code('register', allow_resend=True)
        await self.redis.delete(self.store.code_keys('+86' + self.phone, 'register')[0])
        res = await self.client.post(
            ROOT + '/auth/send-code', json={'phone': self.phone, 'scene': 'register'}
        )
        self.assertEqual(res.status_code, 429)

    async def test_redis_failure_fails_closed_and_password_reset_rolls_back(self):
        from redis.exceptions import RedisError
        from unittest.mock import AsyncMock

        a = await self.register()
        code = await self.send_code('reset_pwd', allow_resend=True)
        with patch.object(
            UserAuthStore, 'revoke_all', AsyncMock(side_effect=RedisError('unavailable'))
        ):
            res = await self.client.post(
                ROOT + '/auth/reset-password',
                json={'phone': self.phone, 'code': code, 'new_password': 'New password 456!'},
            )
            self.assertEqual(res.status_code, 503)
        self.assertEqual((await self.me(a)).status_code, 200)
        await self.login(password=PASSWORD)
        with patch.object(
            UserAuthStore, 'valid_access', AsyncMock(side_effect=RedisError('unavailable'))
        ):
            self.assertEqual((await self.me(a)).status_code, 503)

    async def test_expired_and_disabled_sessions_are_rejected(self):
        a = await self.register()
        claims = jwt.decode(a['access_token'], TEST_SECRET, algorithms=['HS256'], audience='app')
        key = self.store.sessions_key(a['user']['id'])
        session = json.loads(await self.redis.hget(key, claims['sid']))
        session['expires_at'] = 0
        await self.redis.hset(key, claims['sid'], json.dumps(session))
        self.assertEqual((await self.me(a)).status_code, 401)
        self.assertEqual(
            (
                await self.client.post(
                    ROOT + '/auth/refresh', json={'refresh_token': a['refresh_token']}
                )
            ).status_code,
            401,
        )
        b = await self.login()
        async with self.sessions() as db:
            user = await db.get(UserAccount, a['user']['id'])
            user.status = 'disabled'
            await db.commit()
        self.assertEqual((await self.me(b)).status_code, 401)
        self.assertEqual(
            (
                await self.client.post(
                    ROOT + '/auth/refresh', json={'refresh_token': b['refresh_token']}
                )
            ).status_code,
            401,
        )

    async def test_gateway_cancel_does_not_remove_newer_code(self):
        phone = '+86' + self.phone
        await self.store.reserve_code(phone, 'register', '123456', 'old', 'test')
        await self.redis.delete(self.store.code_keys(phone, 'register')[0])
        await self.store.reserve_code(phone, 'register', '654321', 'new', 'test')
        await self.store.cancel_code(phone, 'register', 'old')
        self.assertTrue(await self.store.consume_code(phone, 'register', '654321'))

    async def test_mock_sms_allows_any_six_digits_without_sending(self):
        # 使用真正的 sender 工厂，确保模拟模式不会触发 HTTP 网关。
        self.app.dependency_overrides.pop(get_sms_sender)
        with (
            patch.object(self.config, 'user_sms_mock_enabled', True),
            patch(
                'app.services.sms.HttpSmsSender.send',
                side_effect=AssertionError('must not send real SMS'),
            ),
        ):
            res = await self.client.post(
                ROOT + '/auth/register',
                json={
                    'phone': self.phone,
                    'code': '000000',
                    'password': PASSWORD,
                    'device_id': 'mock-A',
                },
            )
            self.assertEqual(res.status_code, 200, res.text)
            a = res.json()['data']
            self.ids.add(a['user']['id'])
            sent = await self.client.post(
                ROOT + '/auth/send-code', json={'phone': self.phone, 'scene': 'login'}
            )
            self.assertEqual(sent.status_code, 200, sent.text)
            self.assertIn('模拟模式', sent.json()['message'])
            logged = await self.client.post(
                ROOT + '/auth/login',
                json={
                    'phone': self.phone,
                    'login_type': 'sms',
                    'credential': '999999',
                    'device_id': 'mock-B',
                },
            )
            self.assertEqual(logged.status_code, 200, logged.text)
            reset = await self.client.post(
                ROOT + '/auth/reset-password',
                json={'phone': self.phone, 'code': '123456', 'new_password': 'New mock password!'},
            )
            self.assertEqual(reset.status_code, 200)
            self.assertEqual((await self.me(a)).status_code, 401)
            tokens = await self.login(password='New mock password!')
            deleted = await self.client.post(
                ROOT + '/auth/delete-account', json={'code': '654321'}, headers=self.auth(tokens)
            )
            self.assertEqual(deleted.status_code, 200)
            for invalid in ['12345', '1234567', 'abcdef', '１２３４５６']:
                bad = await self.client.post(
                    ROOT + '/auth/register',
                    json={
                        'phone': self.phone,
                        'code': invalid,
                        'password': PASSWORD,
                        'device_id': 'mock-A',
                    },
                )
                self.assertEqual(bad.status_code, 422)

    async def test_legacy_routes_removed_and_new_prefix_documented(self):
        for method, path in [
            ('get', '/api/v1/app/me'),
            ('post', '/api/v1/app/auth/login'),
            ('get', '/v1/admin/users'),
            ('post', '/v1/auth/login'),
            ('get', '/api/v1/app/users/me'),
        ]:
            self.assertEqual((await getattr(self.client, method)(path)).status_code, 404, path)
        schema = self.app.openapi()
        user_paths = [p for p in schema['paths'] if p.startswith('/api/v1/user/')]
        self.assertEqual(len(user_paths), 8)
        self.assertIn('/api/v1/user/me', user_paths)
        self.assertIn('/api/v1/admin/auth/login', schema['paths'])

    async def test_profile_update_validation_isolation_and_deletion(self):
        tokens = await self.register()
        headers = self.auth(tokens)
        initial = (await self.me(tokens)).json()['data']
        self.assertEqual(initial['gender'], 'unspecified')
        for field in ('birthday', 'city', 'email', 'bio'):
            self.assertIsNone(initial[field])
        changes = {
            'gender': 'female',
            'birthday': '2000-02-29',
            'city': ' 杭州 ',
            'email': ' person@example.com ',
            'bio': ' 个人介绍 ',
        }
        updated = await self.client.patch(ROOT + '/me', json=changes, headers=headers)
        self.assertEqual(updated.status_code, 200, updated.text)
        info = updated.json()['data']
        self.assertEqual(info['city'], '杭州')
        self.assertEqual(info['email'], 'person@example.com')
        self.assertEqual(info['birthday'], '2000-02-29')
        self.assertEqual((await self.me(tokens)).json()['data'], info)
        self.assertEqual(updated.headers['Cache-Control'], 'no-store')
        partial = await self.client.patch(ROOT + '/me', json={'city': '上海'}, headers=headers)
        self.assertEqual(partial.json()['data']['birthday'], '2000-02-29')
        self.assertEqual(partial.json()['data']['email'], 'person@example.com')
        for invalid in [
            {'birthday': '2999-01-01'},
            {'birthday': '2001-02-29'},
            {'birthday': 946684800},
            {'birthday': '2000-01-01T00:00:00Z'},
            {'gender': 'invalid'},
            {'email': 'invalid'},
            {'city': 'x' * 101},
            {'bio': 'x' * 501},
            {'membership_level': 'premium'},
            {'id': 'other'},
        ]:
            res = await self.client.patch(ROOT + '/me', json=invalid, headers=headers)
            self.assertEqual(res.status_code, 422, res.text)
        res = await self.client.patch(ROOT + '/me', json={'city': '杭州'})
        self.assertEqual(res.status_code, 401)
        self.phone = self.new_phone()
        other = await self.register()
        self.assertIsNone((await self.me(other)).json()['data']['email'])
        res = await self.client.patch(
            ROOT + '/me', json={'email': 'person@example.com'}, headers=self.auth(other)
        )
        self.assertEqual(res.status_code, 200, res.text)  # Contact emails need not be unique.
        cleared = await self.client.patch(
            ROOT + '/me',
            json={
                'gender': None,
                'birthday': '',
                'city': ' ',
                'email': '',
                'bio': None,
            },
            headers=headers,
        )
        self.assertEqual(cleared.status_code, 200, cleared.text)
        self.assertEqual(cleared.json()['data']['gender'], 'unspecified')
        for field in ('birthday', 'city', 'email', 'bio'):
            self.assertIsNone(cleared.json()['data'][field])
        await self.client.patch(ROOT + '/me', json=changes, headers=headers)
        deleted = await self.client.post(
            ROOT + '/auth/delete-account', json={'password': PASSWORD}, headers=headers
        )
        self.assertEqual(deleted.status_code, 200, deleted.text)
        async with self.sessions() as db:
            user = await db.get(UserAccount, tokens['user']['id'])
            self.assertEqual(user.gender, 'unspecified')
            for field in ('birthday', 'city', 'email', 'bio'):
                self.assertIsNone(getattr(user, field))
        self.assertEqual((await self.me(tokens)).status_code, 401)
        self.assertEqual((await self.me(other)).status_code, 200)

    async def test_missing_configuration(self):
        with patch.object(self.config, 'user_jwt_secret', None):
            res = await self.client.post(ROOT + '/auth/refresh', json={'refresh_token': 'invalid'})
            self.assertEqual(res.status_code, 503)
