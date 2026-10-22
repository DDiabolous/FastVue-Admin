from typing import Literal

from pydantic import Field, field_validator

from .common import EmailInput, Identifier, Password, RecordOutput, Short


class UserCreate(EmailInput):
    username: Identifier
    realName: Short
    role: Identifier
    status: Literal[0, 1] = 1
    password: Password


class UserUpdate(EmailInput):
    username: Identifier | None = None
    realName: Short | None = None
    role: Identifier | None = None
    status: Literal[0, 1] | None = None
    password: str | None = Field(default=None, max_length=128)

    @field_validator('password')
    @classmethod
    def password_length(cls, value):
        if value and len(value) < 8:
            raise ValueError('密码至少 8 位')
        return value


class UserRead(RecordOutput):
    username: str
    realName: str
    email: str
    role: str
    roleName: str
    status: Literal[0, 1]
    permissions: list[str]
