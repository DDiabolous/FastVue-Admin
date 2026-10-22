from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from .common import Input, RecordOutput, Short


class DictionaryCreate(Input):
    type: Short
    label: Short
    value: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    sort: int = Field(default=0, ge=-2147483648, le=2147483647)
    status: Literal[0, 1] = 1


class DictionaryUpdate(Input):
    type: Short | None = None
    label: Short | None = None
    value: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
        | None
    ) = None
    sort: int | None = Field(default=None, ge=-2147483648, le=2147483647)
    status: Literal[0, 1] | None = None


class DictionaryRead(RecordOutput):
    type: str
    label: str
    value: str
    sort: int
    status: Literal[0, 1]
