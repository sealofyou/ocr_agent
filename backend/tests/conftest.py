"""Pytest配置和fixtures"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.base import Base, get_db
from app.core.config import settings
from main import app

# 预先初始化bcrypt以避免测试时的初始化问题
from passlib.context import CryptContext
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
try:
    # 尝试哈希一个简单的密码来触发bcrypt初始化
    _pwd_context.hash("init")
except Exception:
    pass


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_text_archive.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }


@pytest.fixture
def sample_schedule_data():
    """示例日程数据"""
    return {
        "date": "2025-12-01",
        "time": "14:30:00",
        "description": "团队会议",
        "original_text": "12月1日下午2点30分团队会议"
    }


@pytest.fixture
def sample_memo_data():
    """示例备忘录数据"""
    return {
        "content": "今天学习了FastAPI和SQLAlchemy的使用方法，收获很大。",
        "summary": "学习FastAPI和SQLAlchemy",
        "tags": "学习,编程,Python"
    }
