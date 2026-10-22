import secrets
from asyncio import to_thread
from dataclasses import dataclass
from datetime import timedelta

from app.core.context import AuditContext
from app.core.errors import AppError
from app.core.security import can, covers, hash_password, token_digest, verify_password
from app.db.base import utcnow
from app.models.users import User
from app.repositories.auth import LoginRepository, SessionRepository
from app.repositories.roles import RoleRepository
from app.repositories.users import UserRepository

from .audit import audit
from .presenters import public_user


def parse_device_info(ua: str) -> str:
    if not ua:
        return 'Web 客户端'
    os_name = 'Unknown OS'
    if 'iPhone' in ua or 'iPad' in ua or 'iPod' in ua:
        os_name = 'iOS'
    elif 'Macintosh' in ua or 'Mac OS X' in ua:
        os_name = 'macOS'
    elif 'Windows' in ua:
        os_name = 'Windows'
    elif 'Android' in ua:
        os_name = 'Android'
    elif 'Linux' in ua:
        os_name = 'Linux'

    browser_name = 'Browser'
    if 'Chrome' in ua and 'Edg' not in ua:
        browser_name = 'Chrome'
    elif 'Safari' in ua and 'Chrome' not in ua:
        browser_name = 'Safari'
    elif 'Firefox' in ua:
        browser_name = 'Firefox'
    elif 'Edg' in ua:
        browser_name = 'Edge'

    return f'{browser_name} on {os_name}'


@dataclass(frozen=True)
class Principal:
    user: User
    permissions: list[str]
    token_hash: str


class AuthService:
    users = UserRepository()
    roles = RoleRepository()
    sessions = SessionRepository()

    async def authenticate(self, db, raw_token):
        if not raw_token:
            raise AppError(401, '请先登录')
        digest = token_digest(raw_token)
        session = await self.sessions.get(db, digest)
        if not session or session.expires_at <= utcnow():
            raise AppError(401, '登录已失效，请重新登录')
        user = await self.users.get(db, session.user_id)
        role = await self.roles.by_key(db, user.role) if user else None
        if not user or user.status != 1 or not role or role.status != 1:
            raise AppError(401, '账号或角色已停用，请重新登录')
        return Principal(user, role.permissions, digest)

    async def login(self, db, config, ip, username, password, user_agent=''):
        now = utcnow()
        context = AuditContext(username, ip)
        bucket = await LoginRepository().bucket(db, token_digest(ip), now)
        if bucket.started_at + timedelta(seconds=config.login_window_seconds) <= now:
            bucket.started_at, bucket.attempts = now, 0
        if bucket.attempts >= config.login_limit:
            audit(db, context, '登录限流', '登录', 'login', 'failed')
            await db.commit()
            raise AppError(
                429,
                '登录尝试过于频繁，请稍后重试',
                {'Retry-After': str(config.login_window_seconds)},
            )
        bucket.attempts += 1
        user = await self.users.by_username(db, username)
        valid = await to_thread(verify_password, password, user.password_hash if user else None)
        role = await self.roles.by_key(db, user.role) if user else None
        if not valid or not user or user.status != 1 or not role or role.status != 1:
            audit(db, context, '登录失败', '登录', 'login', 'failed')
            # Persist failed attempts and audit even though the operation is rejected.
            await db.commit()
            raise AppError(401, '账号或密码错误，或账号不可用')
        raw = secrets.token_urlsafe(48)
        self.sessions.add(
            db,
            token_digest(raw),
            user.id,
            now + timedelta(hours=config.session_hours),
            ip=ip,
            user_agent=user_agent,
        )
        audit(db, context, '登录成功', '登录', 'login')
        result = {'token': raw, 'user': await public_user(db, user)}
        await db.commit()
        return result

    async def me(self, db, principal):
        return await public_user(db, principal.user)

    async def assignable_roles(self, db, principal):
        if not any(
            can(principal.permissions, f'system:users:{action}') for action in ['create', 'update']
        ):
            raise AppError(403, '没有操作权限')
        return [
            {'roleKey': role.roleKey, 'roleName': role.roleName}
            for role in await self.roles.enabled(db)
            if covers(principal.permissions, role.permissions)
        ]

    async def logout(self, db, principal, context):
        await self.sessions.revoke(db, principal.token_hash)
        audit(db, context, '退出登录', '登录', 'login')
        await db.commit()

    async def profile(self, db, principal, context, data):
        await self.users.update(db, principal.user, data)
        audit(db, context, '更新个人资料', principal.user.id)
        result = await public_user(db, principal.user)
        await db.commit()
        return result

    async def change_password(self, db, principal, context, old_password, new_password):
        if not await to_thread(verify_password, old_password, principal.user.password_hash):
            raise AppError(400, '当前密码不正确')
        principal.user.password_hash = await to_thread(hash_password, new_password)
        await self.sessions.revoke_user(db, principal.user.id)
        audit(db, context, '修改密码', principal.user.id)
        await db.commit()

    async def list_sessions(self, db, principal):
        now = utcnow()
        sessions = await self.sessions.list_user_sessions(db, principal.user.id, now)
        return [
            {
                'tokenHash': s.token_hash,
                'device': parse_device_info(s.user_agent),
                'ip': s.ip or '127.0.0.1',
                'createdAt': (s.created_at or s.expires_at).isoformat(),
                'expiresAt': s.expires_at.isoformat(),
                'isCurrent': s.token_hash == principal.token_hash,
            }
            for s in sessions
        ]

    async def revoke_session(self, db, principal, context, token_hash):
        target = await self.sessions.get(db, token_hash)
        if target and target.user_id == principal.user.id:
            await self.sessions.revoke(db, token_hash)
            audit(db, context, '撤销登录会话', principal.user.id)
            await db.commit()
