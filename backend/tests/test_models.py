"""数据模型测试"""
import pytest
from datetime import date, time
from app.models.user import User
from app.models.schedule import ScheduleItem
from app.models.memo import Memo


@pytest.mark.unit
def test_user_model_creation(db_session, sample_user_data):
    """测试用户模型创建"""
    user = User(
        username=sample_user_data["username"],
        email=sample_user_data["email"],
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.username == sample_user_data["username"]
    assert user.email == sample_user_data["email"]
    assert user.created_at is not None


@pytest.mark.unit
def test_schedule_model_creation(db_session, sample_schedule_data):
    """测试日程模型创建"""
    # 先创建用户
    user = User(username="testuser", email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # 创建日程
    schedule = ScheduleItem(
        user_id=user.id,
        date=date.fromisoformat(sample_schedule_data["date"]),
        time=time.fromisoformat(sample_schedule_data["time"]),
        description=sample_schedule_data["description"],
        original_text=sample_schedule_data["original_text"]
    )
    db_session.add(schedule)
    db_session.commit()
    db_session.refresh(schedule)
    
    assert schedule.id is not None
    assert schedule.user_id == user.id
    assert schedule.description == sample_schedule_data["description"]


@pytest.mark.unit
def test_memo_model_creation(db_session, sample_memo_data):
    """测试备忘录模型创建"""
    # 先创建用户
    user = User(username="testuser", email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # 创建备忘录
    memo = Memo(
        user_id=user.id,
        content=sample_memo_data["content"],
        summary=sample_memo_data["summary"],
        tags=sample_memo_data["tags"]
    )
    db_session.add(memo)
    db_session.commit()
    db_session.refresh(memo)
    
    assert memo.id is not None
    assert memo.user_id == user.id
    assert memo.content == sample_memo_data["content"]
    assert memo.tags == sample_memo_data["tags"]
