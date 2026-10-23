import re
from typing import Annotated, Generic, Literal, TypeVar
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .accounts import AppProfile

Scene = Literal['register', 'login', 'reset_pwd', 'delete_account']
Code = Annotated[str, Field(pattern=r'^[0-9]{6}$')]
Password = Annotated[str, Field(min_length=8, max_length=128)]


class AppRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')


class AppPhoneRequest(AppRequest):
    phone: str = Field(min_length=8, max_length=16)

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, value):
        if re.fullmatch(r'1[3-9]\d{9}', value, flags=re.ASCII):
            return '+86' + value
        if not re.fullmatch(r'\+[1-9][0-9]{7,14}', value):
            raise ValueError('手机号须为中国大陆 11 位号码或 E.164 格式')
        return value


class AppSendCodeRequest(AppPhoneRequest):
    scene: Scene


class AppRegisterRequest(AppPhoneRequest):
    code: Code
    password: Password
    device_id: str = Field(min_length=1, max_length=128, pattern=r'^\S+$')


class AppLoginRequest(AppPhoneRequest):
    login_type: Literal['password', 'sms']
    credential: str = Field(min_length=1, max_length=128)
    device_id: str = Field(min_length=1, max_length=128, pattern=r'^\S+$')

    @model_validator(mode='after')
    def validate_sms(self):
        if self.login_type == 'sms' and not re.fullmatch(r'[0-9]{6}', self.credential):
            raise ValueError('短信验证码为 6 位数字')
        return self


class AppRefreshRequest(AppRequest):
    refresh_token: str = Field(min_length=1, max_length=256)


class AppResetPasswordRequest(AppPhoneRequest):
    code: Code
    new_password: Password


class AppDeleteAccountRequest(AppRequest):
    code: Code | None = None
    password: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode='after')
    def one_proof(self):
        if (self.code is None) == (self.password is None):
            raise ValueError('请提供验证码或密码，且只能提供一种')
        return self


class AppTokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal['bearer']
    expires_in: int
    refresh_expires_in: int


class AppAuthResult(AppTokenPair):
    user: AppProfile


class AppCodeSent(BaseModel):
    expires_in: int
    retry_after: int


class AppDeletedAccount(BaseModel):
    status: Literal['deleted']


T = TypeVar('T')


class AppResponse(BaseModel, Generic[T]):
    code: Literal[200] = 200
    message: str
    data: T


class AppErrorResponse(BaseModel):
    code: int
    message: str
    data: None = None


APP_ERROR_RESPONSES = {
    status: {'model': AppErrorResponse, 'description': description}
    for status, description in {
        400: '验证码或二次身份核验失败',
        401: '登录凭证或令牌无效',
        403: '不允许访问该账号或设备',
        409: '手机号已注册',
        422: '请求字段不符合规范',
        429: '请求限流或账号锁定，参见 Retry-After',
        503: 'Redis、短信网关或认证配置暂不可用',
    }.items()
}
