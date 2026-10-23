from fastapi import APIRouter, Depends, Response
from app.api.v1.user.dependencies import get_current_user_account
from app.models.user.accounts import UserAccount
from app.schemas.user.auth import USER_ERROR_RESPONSES, UserResponse
from app.schemas.user.accounts import UserProfile
from app.services.user.auth import profile
from app.core.user_responses import no_store, result

router = APIRouter(prefix='', tags=['User · 产品账号'], responses=USER_ERROR_RESPONSES)


@router.get('/me', response_model=UserResponse[UserProfile], summary='获取当前注册用户及会员状态')
async def me(res: Response, user: UserAccount = Depends(get_current_user_account)):
    no_store(res)
    return result(profile(user))
