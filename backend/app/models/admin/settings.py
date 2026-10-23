from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SystemSettings(Base):
    __tablename__ = 'settings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    siteName: Mapped[str] = mapped_column(String(100), default='FastVue-Admin')
    description: Mapped[str] = mapped_column(String(1000), default='')
    contactEmail: Mapped[str] = mapped_column(String(254), default='')
    registration: Mapped[str] = mapped_column(String(200), default='')
