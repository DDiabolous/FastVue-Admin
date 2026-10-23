from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.context import AuditContext
from app.core.errors import AppError
from app.core.admin_permissions import can
from app.db.session import request_session
from app.services.admin.auth import AdminAuthService

bearer = HTTPBearer(auto_error=False, scheme_name='AdminBearer')


async def get_db(request: Request):
    async with request_session(
        request.app.state.sessions, read_only=request.method in ('GET', 'HEAD')
    ) as db:
        yield db


def client_ip(request):
    return request.client.host if request.client else 'unknown'


def audit_context(request, principal):
    return AuditContext(principal.user.username, client_ip(request))


async def get_current_admin(
    db=Depends(get_db), credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
):
    return await AdminAuthService().authenticate(
        db, credentials.credentials if credentials else None
    )


def require(permission):
    async def dependency(principal=Depends(get_current_admin)):
        if not can(principal.permissions, permission):
            raise AppError(403, '没有操作权限')
        return principal

    return dependency
