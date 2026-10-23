"""注册用户独立数据库会话，不使用后台权限变更的全局事务锁。"""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.user_security import user_bearer, user_unauthorized, authenticate_user_token
from app.services.user.auth_store import UserAuthStore, get_user_store


async def get_user_db(request: Request):
    async with request.app.state.sessions() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise


async def get_current_user_account(
    credentials: HTTPAuthorizationCredentials | None = Depends(user_bearer),
    db: AsyncSession = Depends(get_user_db),
    store: UserAuthStore = Depends(get_user_store),
):
    if credentials is None:
        raise user_unauthorized()
    return await authenticate_user_token(credentials.credentials, db, store)
