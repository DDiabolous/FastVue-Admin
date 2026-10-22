from typing import Literal

from pydantic import BaseModel, Field

from .common import Identifier, Input, RecordOutput, Short


class RoleCreate(Input):
    roleKey: Identifier
    roleName: Short
    description: str = Field(default='', max_length=500)
    permissions: list[str] = Field(default_factory=list, max_length=100)
    status: Literal[0, 1] = 1


class RoleUpdate(Input):
    roleKey: Identifier | None = None
    roleName: Short | None = None
    description: str | None = Field(default=None, max_length=500)
    permissions: list[str] | None = Field(default=None, max_length=100)
    status: Literal[0, 1] | None = None


class RoleRead(RecordOutput):
    roleKey: str
    roleName: str
    description: str
    permissions: list[str]
    status: Literal[0, 1]


class RoleOption(BaseModel):
    roleKey: str
    roleName: str
