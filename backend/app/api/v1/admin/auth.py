from fastapi import APIRouter, Depends, Request

from app.api.v1.admin.dependencies import audit_context, client_ip, get_current_admin, get_db
from app.core.responses import ok
from app.schemas.admin.auth import (
    AdminLogin,
    AdminLoginResult,
    AdminPasswordChange,
    AdminSessionInfo,
)
from app.schemas.common import Envelope
from app.schemas.admin.roles import AdminRoleOption
from app.services.admin.auth import AdminAuthService

router = APIRouter(prefix='/auth', tags=['Admin · 后台认证'])
service = AdminAuthService()


@router.post('/login', response_model=Envelope[AdminLoginResult])
async def login(body: AdminLogin, request: Request, db=Depends(get_db)):
    return ok(
        await service.login(
            db,
            request.app.state.config,
            client_ip(request),
            body.username,
            body.password,
            user_agent=request.headers.get('user-agent', ''),
        )
    )


@router.get('/roles', response_model=Envelope[list[AdminRoleOption]])
async def assignable_roles(principal=Depends(get_current_admin), db=Depends(get_db)):
    return ok(await service.assignable_roles(db, principal))


@router.post('/logout', response_model=Envelope[None])
async def logout(request: Request, principal=Depends(get_current_admin), db=Depends(get_db)):
    await service.logout(db, principal, audit_context(request, principal))
    return ok()


@router.post('/password', response_model=Envelope[None])
async def password(
    body: AdminPasswordChange,
    request: Request,
    principal=Depends(get_current_admin),
    db=Depends(get_db),
):
    await service.change_password(
        db, principal, audit_context(request, principal), body.oldPassword, body.newPassword
    )
    return ok()


@router.get('/sessions', response_model=Envelope[list[AdminSessionInfo]])
async def sessions(principal=Depends(get_current_admin), db=Depends(get_db)):
    return ok(await service.list_sessions(db, principal))


@router.delete('/sessions/{token_hash}', response_model=Envelope[None])
async def revoke_session(
    token_hash: str, request: Request, principal=Depends(get_current_admin), db=Depends(get_db)
):
    await service.revoke_session(db, principal, audit_context(request, principal), token_hash)
    return ok()
