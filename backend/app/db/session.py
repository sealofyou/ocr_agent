from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 按需初始化数据库
if settings.DB_URL:
    engine = create_engine(settings.DB_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
else:
    SessionLocal = None
    Base = None


def get_db():
    """依赖注入的数据库会话"""
    if not SessionLocal:
        raise RuntimeError("Database not configured")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()