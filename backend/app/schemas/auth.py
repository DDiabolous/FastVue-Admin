from pydantic import BaseModel, Field

from .common import EmailInput, Input, Password, Short
from .users import UserRead


class Login(Input):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class Profile(EmailInput):
    realName: Short


class PasswordChange(Input):
    oldPassword: str = Field(min_length=1, max_length=128)
    newPassword: Password


class LoginResult(BaseModel):
    token: str
    user: UserRead
