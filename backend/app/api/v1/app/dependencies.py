"""注册用户独立数据库会话，不使用后台权限变更的全局事务锁。"""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.app_security import app_bearer, app_unauthorized, authenticate_app_token
from app.services.app.auth_store import AppAuthStore, get_app_store


async def get_app_db(request: Request):
    async with request.app.state.sessions() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise


async def get_current_app_account(
    credentials: HTTPAuthorizationCredentials | None = Depends(app_bearer),
    db: AsyncSession = Depends(get_app_db),
    store: AppAuthStore = Depends(get_app_store),
):
    if credentials is None:
        raise app_unauthorized()
    return await authenticate_app_token(credentials.credentials, db, store)
