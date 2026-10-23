import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.user.dependencies import get_user_db as get_db, get_current_user_account
from app.core.user_responses import no_store, result
from app.core.user_security import (
    user_bearer,
    user_unauthorized,
    authenticate_user_token,
    decode_access,
    parse_refresh,
)
from app.models.user.accounts import UserAccount
from app.schemas.user.auth import (
    USER_ERROR_RESPONSES,
    UserResponse,
    UserAuthResult,
    UserCodeSent,
    UserDeletedAccount,
    UserTokenPair,
    UserDeleteAccountRequest,
    UserLoginRequest,
    UserRefreshRequest,
    UserRegisterRequest,
    UserResetPasswordRequest,
    UserSendCodeRequest,
)
from app.services.user.auth_store import UserAuthStore, get_user_store
from app.services.sms import HttpSmsSender, get_sms_sender
from app.services.user import auth as service

router = APIRouter(prefix='/auth', tags=['User · 产品认证'], responses=USER_ERROR_RESPONSES)


def client_ip(request: Request):
    # 仅使用 ASGI 提供的地址；代理场景需配置 uvicorn 的可信代理范围。
    return request.client.host if request.client else 'unknown'


@router.post(
    '/send-code',
    response_model=UserResponse[UserCodeSent],
    summary='发送短信验证码',
    openapi_extra={'security': [{}, {'UserBearer': []}]},
)
async def send_code(
    payload: UserSendCodeRequest,
    request: Request,
    res: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(user_bearer),
    db: AsyncSession = Depends(get_db),
    store: UserAuthStore = Depends(get_user_store),
    sender: HttpSmsSender = Depends(get_sms_sender),
):
    no_store(res)
    if payload.scene == 'delete_account':
        if credentials is None:
            raise user_unauthorized()
        user = await authenticate_user_token(credentials.credentials, db, store)
        if user.phone != payload.phone:
            raise HTTPException(403, '只能为本人手机号发送注销验证码')
    code, nonce = f'{secrets.randbelow(1000000):06d}', secrets.token_hex(16)
    await store.reserve_code(payload.phone, payload.scene, code, nonce, client_ip(request))
    try:
        await sender.send(payload.phone, payload.scene, code)
    except Exception:
        await store.cancel_code(payload.phone, payload.scene, nonce)
        raise
    return result(
        {'expires_in': 300, 'retry_after': 60},
        '短信模拟模式，请输入任意6位数字' if store.config.user_sms_mock_enabled else '验证码已发送',
    )


@router.post('/register', response_model=UserResponse[UserAuthResult], summary='手机号注册并登录')
async def register(
    payload: UserRegisterRequest,
    res: Response,
    db: AsyncSession = Depends(get_db),
    store: UserAuthStore = Depends(get_user_store),
):
    no_store(res)
    return result(await service.register(db, store, payload), '注册成功')


@router.post('/login', response_model=UserResponse[UserAuthResult], summary='密码或短信验证码登录')
async def login(
    payload: UserLoginRequest,
    request: Request,
    res: Response,
    db: AsyncSession = Depends(get_db),
    store: UserAuthStore = Depends(get_user_store),
):
    no_store(res)
    return result(await service.login(db, store, payload, client_ip(request)))


@router.post('/refresh', response_model=UserResponse[UserTokenPair], summary='轮换双令牌')
async def refresh(
    payload: UserRefreshRequest,
    res: Response,
    db: AsyncSession = Depends(get_db),
    store: UserAuthStore = Depends(get_user_store),
):
    no_store(res)
    return result(await service.refresh(db, store, payload.refresh_token))


@router.post(
    '/reset-password', response_model=UserResponse[None], summary='验证码重置密码并退出全部设备'
)
async def reset_password(
    payload: UserResetPasswordRequest,
    res: Response,
    db: AsyncSession = Depends(get_db),
    store: UserAuthStore = Depends(get_user_store),
):
    no_store(res)
    await service.reset_password(db, store, payload)
    return result(message='密码已重置，请重新登录')


@router.post('/logout', response_model=UserResponse[None], summary='退出当前设备')
async def logout(
    payload: UserRefreshRequest,
    res: Response,
    user: UserAccount = Depends(get_current_user_account),
    credentials: HTTPAuthorizationCredentials = Depends(user_bearer),
    db: AsyncSession = Depends(get_db),
    store: UserAuthStore = Depends(get_user_store),
):
    no_store(res)
    uid, sid = parse_refresh(payload.refresh_token)
    claims = decode_access(credentials.credentials, store.config)
    if uid != user.id or sid != claims['sid']:
        raise HTTPException(403, '令牌不属于当前登录设备')
    # 与刷新、重置的用户行锁顺序一致，避免注销/退出后旧会话重新写入。
    await authenticate_user_token(credentials.credentials, db, store, lock=True)
    if not await store.logout(uid, sid, payload.refresh_token):
        raise user_unauthorized()
    return result(message='已退出登录')


@router.post(
    '/delete-account', response_model=UserResponse[UserDeletedAccount], summary='二次核验后注销账号'
)
async def delete_account(
    payload: UserDeleteAccountRequest,
    res: Response,
    credentials: HTTPAuthorizationCredentials = Depends(user_bearer),
    user: UserAccount = Depends(get_current_user_account),
    db: AsyncSession = Depends(get_db),
    store: UserAuthStore = Depends(get_user_store),
):
    no_store(res)
    await store.login_budget('delete:' + user.id)
    user = await authenticate_user_token(credentials.credentials, db, store, lock=True)
    await service.delete_account(db, store, user, payload)
    return result({'status': 'deleted'}, '账号已注销')
