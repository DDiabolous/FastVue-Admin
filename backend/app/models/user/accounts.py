"""注册用户，独立于后台 admin_accounts。"""

import uuid
from sqlalchemy import CheckConstraint, Column, Date, DateTime, Integer, String
from app.db.base import Base
from app.db.base import utcnow


class UserAccount(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'disabled', 'deleted')", name='ck_user_account_status'
        ),
        CheckConstraint(
            "gender IN ('unspecified', 'male', 'female', 'other')", name='ck_users_gender'
        ),
    )

    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    phone = Column(String(16), nullable=True, unique=True)
    password_hash = Column(String(256), nullable=True)
    nickname = Column(String(64), nullable=False, default='')
    avatar_url = Column(String(2048), nullable=False, default='')
    gender = Column(String(16), nullable=False, default='unspecified', server_default='unspecified')
    birthday = Column(Date, nullable=True)
    city = Column(String(100), nullable=True)
    email = Column(String(254), nullable=True)
    bio = Column(String(500), nullable=True)
    status = Column(String(16), nullable=False, default='active')
    auth_version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
