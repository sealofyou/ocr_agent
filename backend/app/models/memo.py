from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class Memo(Base):
    """备忘录模型"""
    __tablename__ = "memos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(String(500), nullable=False)
    tags = Column(String(500), nullable=True)  # 存储为逗号分隔的字符串
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
