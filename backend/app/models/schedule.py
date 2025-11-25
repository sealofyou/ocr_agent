from sqlalchemy import Column, String, Date, Time, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class ScheduleItem(Base):
    """日程项模型"""
    __tablename__ = "schedule_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    time = Column(Time, nullable=True)
    description = Column(Text, nullable=False)
    original_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
