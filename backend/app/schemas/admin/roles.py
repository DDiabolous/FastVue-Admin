from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import Identifier, Input, RecordOutput, Short


class AdminRoleCreate(Input):
    roleKey: Identifier
    roleName: Short
    description: str = Field(default='', max_length=500)
    permissions: list[str] = Field(default_factory=list, max_length=100)
    status: Literal[0, 1] = 1


class AdminRoleUpdate(Input):
    roleKey: Identifier | None = None
    roleName: Short | None = None
    description: str | None = Field(default=None, max_length=500)
    permissions: list[str] | None = Field(default=None, max_length=100)
    status: Literal[0, 1] | None = None


class AdminRoleRead(RecordOutput):
    roleKey: str
    roleName: str
    description: str
    permissions: list[str]
    status: Literal[0, 1]


class AdminRoleOption(BaseModel):
    roleKey: str
    roleName: str
