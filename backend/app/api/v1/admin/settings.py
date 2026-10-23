from fastapi import APIRouter, Depends, Request

from app.api.v1.admin.dependencies import audit_context, get_db, require
from app.core.responses import ok
from app.schemas.common import Envelope
from app.schemas.admin.settings import PublicSettings, SettingsRead, SettingsUpdate
from app.services.admin.settings import SettingsService

router = APIRouter(prefix='/settings', tags=['v1 · 配置'])
service = SettingsService()


@router.get('/public', response_model=Envelope[PublicSettings])
async def public_settings(db=Depends(get_db)):
    return ok(await service.get(db, public=True))


@router.get('', response_model=Envelope[SettingsRead])
async def get_settings(principal=Depends(require('system:settings:read')), db=Depends(get_db)):
    return ok(await service.get(db))


@router.patch('', response_model=Envelope[SettingsRead])
async def update_settings(
    body: SettingsUpdate,
    request: Request,
    principal=Depends(require('system:settings:update')),
    db=Depends(get_db),
):
    return ok(
        await service.update(
            db, audit_context(request, principal), body.model_dump(exclude_unset=True)
        )
    )
