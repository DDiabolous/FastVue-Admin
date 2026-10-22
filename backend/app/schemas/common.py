from datetime import datetime
from typing import Annotated, Generic, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    TypeAdapter,
    field_validator,
)

Short = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Identifier = Annotated[
    str, StringConstraints(strip_whitespace=True, pattern=r'^[A-Za-z0-9_.-]{1,64}$')
]
Password = Annotated[str, Field(min_length=8, max_length=128)]


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @field_validator('status', check_fields=False, mode='before')
    @classmethod
    def strict_status(cls, value):
        if type(value) is not int:
            raise ValueError('状态必须为 0 或 1')
        return value


class EmailInput(Input):
    email: str = Field(default='', max_length=254)

    @field_validator('email', check_fields=False)
    @classmethod
    def valid_email(cls, value):
        return str(TypeAdapter(EmailStr).validate_python(value)) if value else ''


class PageQuery(BaseModel):
    page: int = Field(default=1, ge=1, le=1000000)
    pageSize: int = Field(default=10, ge=1, le=200)
    keyword: str = Field(default='', max_length=200)


T = TypeVar('T')


class Envelope(BaseModel, Generic[T]):
    code: int = 200
    message: str = '操作成功'
    data: T


class Page(BaseModel, Generic[T]):
    list: list[T]
    total: int


class RecordOutput(BaseModel):
    id: str
    createdAt: datetime
