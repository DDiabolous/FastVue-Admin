from fastapi import APIRouter, Depends, Request

from app.api.v1.admin.dependencies import audit_context, get_current_admin, get_db
from app.core.responses import ok
from app.schemas.admin.accounts import AdminAccountRead
from app.schemas.admin.auth import AdminProfile
from app.schemas.common import Envelope
from app.services.admin.auth import AdminAuthService

router = APIRouter(tags=['Admin · 后台资料'])
service = AdminAuthService()


@router.get('/me', response_model=Envelope[AdminAccountRead])
async def me(principal=Depends(get_current_admin), db=Depends(get_db)):
    return ok(await service.me(db, principal))


@router.patch('/me', response_model=Envelope[AdminAccountRead])
async def profile(
    body: AdminProfile, request: Request, principal=Depends(get_current_admin), db=Depends(get_db)
):
    return ok(
        await service.profile(
            db, principal, audit_context(request, principal), body.model_dump(exclude_unset=True)
        )
    )
