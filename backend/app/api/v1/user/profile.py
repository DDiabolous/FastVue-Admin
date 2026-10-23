from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPAuthorizationCredentials
from app.api.v1.user.dependencies import get_current_user_account, get_user_db
from app.core.user_security import user_bearer, authenticate_user_token
from app.models.user.accounts import UserAccount
from app.schemas.user.auth import USER_ERROR_RESPONSES, UserResponse
from app.schemas.user.accounts import UserProfile, UserProfileUpdate
from app.services.user.auth import profile
from app.services.user.profile import update_profile
from app.services.user.auth_store import UserAuthStore, get_user_store
from app.core.user_responses import no_store, result

router = APIRouter(prefix='', tags=['User · 产品账号'], responses=USER_ERROR_RESPONSES)


@router.get('/me', response_model=UserResponse[UserProfile], summary='获取当前注册用户资料')
async def me(res: Response, user: UserAccount = Depends(get_current_user_account)):
    no_store(res)
    return result(profile(user))


@router.patch('/me', response_model=UserResponse[UserProfile], summary='修改本人基础资料')
async def update_me(
    body: UserProfileUpdate,
    res: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(user_bearer),
    user: UserAccount = Depends(get_current_user_account),
    db=Depends(get_user_db),
    store: UserAuthStore = Depends(get_user_store),
):
    no_store(res)
    # Revalidate under the same account row lock used by deletion and password reset.
    user = await authenticate_user_token(credentials.credentials, db, store, lock=True)
    return result(await update_profile(db, user, body.model_dump(exclude_unset=True)))
