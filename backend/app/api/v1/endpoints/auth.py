from fastapi import APIRouter, Depends, Request

from app.api.dependencies import audit_context, client_ip, current_user, get_db
from app.core.responses import ok
from app.schemas.auth import Login, LoginResult, PasswordChange, Profile, SessionInfo
from app.schemas.common import Envelope
from app.schemas.roles import RoleOption
from app.schemas.users import UserRead
from app.services.auth import AuthService

router = APIRouter(prefix='/auth', tags=['v1 · 认证'])
service = AuthService()


@router.post('/login', response_model=Envelope[LoginResult])
async def login(body: Login, request: Request, db=Depends(get_db)):
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


@router.get('/me', response_model=Envelope[UserRead])
async def me(principal=Depends(current_user), db=Depends(get_db)):
    return ok(await service.me(db, principal))


@router.get('/roles', response_model=Envelope[list[RoleOption]])
async def assignable_roles(principal=Depends(current_user), db=Depends(get_db)):
    return ok(await service.assignable_roles(db, principal))


@router.post('/logout', response_model=Envelope[None])
async def logout(request: Request, principal=Depends(current_user), db=Depends(get_db)):
    await service.logout(db, principal, audit_context(request, principal))
    return ok()


@router.patch('/profile', response_model=Envelope[UserRead])
async def profile(
    body: Profile, request: Request, principal=Depends(current_user), db=Depends(get_db)
):
    return ok(
        await service.profile(
            db, principal, audit_context(request, principal), body.model_dump(exclude_unset=True)
        )
    )


@router.post('/password', response_model=Envelope[None])
async def password(
    body: PasswordChange, request: Request, principal=Depends(current_user), db=Depends(get_db)
):
    await service.change_password(
        db, principal, audit_context(request, principal), body.oldPassword, body.newPassword
    )
    return ok()


@router.get('/sessions', response_model=Envelope[list[SessionInfo]])
async def sessions(principal=Depends(current_user), db=Depends(get_db)):
    return ok(await service.list_sessions(db, principal))


@router.delete('/sessions/{token_hash}', response_model=Envelope[None])
async def revoke_session(
    token_hash: str, request: Request, principal=Depends(current_user), db=Depends(get_db)
):
    await service.revoke_session(db, principal, audit_context(request, principal), token_hash)
    return ok()
