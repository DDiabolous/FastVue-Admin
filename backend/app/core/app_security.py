"""用户专用 JWT 域：固定算法、issuer/audience/scope，并校验 Redis 会话。"""

from datetime import timedelta
import secrets
import uuid
import jwt
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select
from app.core.config import Settings
from app.db.base import utcnow
from app.models.app.accounts import AppAccount

app_bearer = HTTPBearer(auto_error=False, scheme_name='AppBearer')


def app_secret(config: Settings) -> str:
    key = config.user_jwt_secret.get_secret_value() if config.user_jwt_secret else ''
    if len(key.encode()) < 32:
        raise HTTPException(503, '用户认证签名密钥未配置，至少需要 32 字节独立随机密钥')
    return key


def app_unauthorized():
    return HTTPException(401, '用户登录已失效，请重新登录', headers={'WWW-Authenticate': 'Bearer'})


def make_tokens(user: AppAccount, sid: str, config: Settings):
    now = utcnow()
    jti = uuid.uuid4().hex
    access = jwt.encode(
        {
            'sub': user.id,
            'sid': sid,
            'ver': user.auth_version,
            'scope': 'app',
            'type': 'access',
            'jti': jti,
            'iss': config.user_jwt_issuer,
            'aud': 'app',
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(minutes=15),
        },
        app_secret(config),
        algorithm='HS256',
    )
    refresh = f'{user.id}.{sid}.{secrets.token_urlsafe(48)}'
    return {
        'access_token': access,
        'refresh_token': refresh,
        'token_type': 'bearer',
        'expires_in': 900,
        'refresh_expires_in': config.user_refresh_token_days * 86400,
    }, jti


def decode_access(token: str, config: Settings):
    try:
        payload = jwt.decode(
            token,
            app_secret(config),
            algorithms=['HS256'],
            audience='app',
            issuer=config.user_jwt_issuer,
            options={'require': ['sub', 'sid', 'ver', 'scope', 'type', 'jti', 'iat', 'nbf', 'exp']},
        )
        if (
            payload['scope'] != 'app'
            or payload['type'] != 'access'
            or not isinstance(payload['ver'], int)
            or isinstance(payload['ver'], bool)
            or not all(
                isinstance(payload[k], str) and len(payload[k]) == 32 for k in ('sub', 'sid', 'jti')
            )
        ):
            raise app_unauthorized()
        return payload
    except jwt.InvalidTokenError:
        raise app_unauthorized() from None


def parse_refresh(token: str):
    import re

    if not re.fullmatch(r'[0-9a-f]{32}\.[0-9a-f]{32}\.[A-Za-z0-9_-]{64}', token):
        raise app_unauthorized()
    return token.split('.', 2)[:2]


async def authenticate_app_token(token, db, store, lock=False):
    payload = decode_access(token, store.config)
    if lock:
        user = (
            await db.execute(
                select(AppAccount)
                .where(AppAccount.id == payload['sub'])
                .with_for_update()
                .execution_options(populate_existing=True)
            )
        ).scalar_one_or_none()
    else:
        user = await db.get(AppAccount, payload['sub'])
    if (
        user is None
        or user.status != 'active'
        or user.auth_version != payload['ver']
        or not await store.valid_access(user.id, payload['sid'], payload['jti'], payload['ver'])
    ):
        raise app_unauthorized()
    return user
