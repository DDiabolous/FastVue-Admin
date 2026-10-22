from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class User(Record, Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint('status IN (0, 1)', name='user_status'),
        CheckConstraint("gender IN ('unspecified', 'male', 'female', 'other')", name='user_gender'),
    )
    username: Mapped[str] = mapped_column(String(64), unique=True)
    realName: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), default='')
    gender: Mapped[str] = mapped_column(String(16), default='unspecified')
    phone: Mapped[str] = mapped_column(String(32), default='')
    location: Mapped[str] = mapped_column(String(100), default='')
    bio: Mapped[str] = mapped_column(String(500), default='')
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    coverImage: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    role: Mapped[str] = mapped_column(
        ForeignKey('roles.roleKey', ondelete='RESTRICT', onupdate='RESTRICT'), index=True
    )
    status: Mapped[int] = mapped_column(Integer, default=1)
    password_hash: Mapped[str] = mapped_column(Text)
    builtin: Mapped[bool] = mapped_column(Boolean, default=False)
