from sqlalchemy import CheckConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class Dictionary(Record, Base):
    __tablename__ = 'dictionary'
    __table_args__ = (
        UniqueConstraint('type', 'value', name='dictionary_type_value'),
        CheckConstraint('status IN (0, 1)', name='dictionary_status'),
    )
    type: Mapped[str] = mapped_column(String(100))
    label: Mapped[str] = mapped_column(String(100))
    value: Mapped[str] = mapped_column(String(200))
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)
