from fastapi import APIRouter, Depends, Response
from app.api.v1.app.dependencies import get_current_app_account
from app.models.app.accounts import AppAccount
from app.schemas.app.auth import APP_ERROR_RESPONSES, AppResponse
from app.schemas.app.accounts import AppProfile
from app.services.app.auth import profile
from app.core.app_responses import no_store, result

router = APIRouter(prefix='', tags=['App · 产品账号'], responses=APP_ERROR_RESPONSES)


@router.get('/me', response_model=AppResponse[AppProfile], summary='获取当前注册用户及会员状态')
async def me(res: Response, user: AppAccount = Depends(get_current_app_account)):
    no_store(res)
    return result(profile(user))
