from sqlalchemy import JSON, Boolean, CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class Role(Record, Base):
    __tablename__ = 'roles'
    __table_args__ = (CheckConstraint('status IN (0, 1)', name='role_status'),)
    roleKey: Mapped[str] = mapped_column(String(64), unique=True)
    roleName: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500), default='')
    permissions: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[int] = mapped_column(Integer, default=1)
    builtin: Mapped[bool] = mapped_column(Boolean, default=False)
