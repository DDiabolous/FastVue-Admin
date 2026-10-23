from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.common import PageQuery


class LogQuery(PageQuery):
    category: Literal['login', 'operation'] | None = None


class LogRead(BaseModel):
    id: str
    time: datetime
    operator: str
    action: str
    target: str
    category: Literal['login', 'operation']
    status: str
    ip: str
