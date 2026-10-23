"""注册用户，独立于后台 admin_accounts。"""

import uuid
from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String
from app.db.base import Base
from app.db.base import utcnow


class UserAccount(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'disabled', 'deleted')", name='ck_user_account_status'
        ),
    )

    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    phone = Column(String(16), nullable=True, unique=True)
    password_hash = Column(String(256), nullable=True)
    nickname = Column(String(64), nullable=False, default='')
    avatar_url = Column(String(2048), nullable=False, default='')
    status = Column(String(16), nullable=False, default='active')
    auth_version = Column(Integer, nullable=False, default=0)
    membership_level = Column(String(32), nullable=False, default='free')
    membership_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
