from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .common import EmailInput, Input, Password, Short
from .users import UserRead


class Login(Input):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class Profile(EmailInput):
    realName: Short | None = None
    gender: Literal['unspecified', 'male', 'female', 'other'] = 'unspecified'
    phone: str = Field(default='', max_length=32)
    location: str = Field(default='', max_length=100)
    bio: str = Field(default='', max_length=500)
    avatar: str | None = None
    coverImage: str | None = None

    @field_validator('realName')
    @classmethod
    def name_not_null(cls, value):
        if value is None:
            raise ValueError('姓名不能为空')
        return value


class SessionInfo(BaseModel):
    tokenHash: str
    device: str
    ip: str
    createdAt: str
    expiresAt: str
    isCurrent: bool


class PasswordChange(Input):
    oldPassword: str = Field(min_length=1, max_length=128)
    newPassword: Password


class LoginResult(BaseModel):
    token: str
    user: UserRead
