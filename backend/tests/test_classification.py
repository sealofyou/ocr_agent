"""分类服务单元测试"""
import pytest
from app.services.classification_service import ClassificationService, get_classification_service


@pytest.mark.unit
def test_classification_service_initialization():
    """测试分类服务初始化"""
    service = ClassificationService()
    assert service is not None
    assert service.CONFIDENCE_THRESHOLD == 0.6


@pytest.mark.unit
def test_get_classification_service_singleton():
    """测试分类服务单例模式"""
    service1 = get_classification_service()
    service2 = get_classification_service()
    assert service1 is service2


@pytest.mark.unit
def test_classify_schedule_with_time():
    """测试分类包含时间的日程文本"""
    service = ClassificationService()
    text = "明天下午2点开会"
    result = service.classify_text(text)
    
    assert result["type"] == "schedule"
    assert result["confidence"] > 0.5
    assert "extracted_data" in result


@pytest.mark.unit
def test_classify_schedule_with_date():
    """测试分类包含日期的日程文本"""
    service = ClassificationService()
    text = "2024年1月15日下午2点项目评审会议"
    result = service.classify_text(text)
    
    assert result["type"] == "schedule"
    assert result["confidence"] > 0.5


@pytest.mark.unit
def test_classify_memo_text():
    """测试分类备忘录文本"""
    service = ClassificationService()
    text = "今天学习了Python编程，感觉很有收获。需要继续深入学习面向对象编程的概念。记录一下心得体会。"
    result = service.classify_text(text)
    
    assert result["type"] == "memo"
    assert result["confidence"] >= 0.5
    assert "extracted_data" in result


@pytest.mark.unit
def test_classify_empty_text():
    """测试分类空文本"""
    service = ClassificationService()
    result = service.classify_text("")
    
    assert result["type"] == "memo"
    assert result["confidence"] == 0.5


@pytest.mark.unit
def test_extract_schedule_info_with_time():
    """测试提取包含时间的日程信息"""
    service = ClassificationService()
    text = "明天下午3点30分开会讨论项目进度"
    info = service.extract_schedule_info(text)
    
    assert info["time"] is not None
    assert info["date"] is not None
    assert info["has_time_info"] is True
    assert "description" in info


@pytest.mark.unit
def test_extract_schedule_info_without_time():
    """测试提取不包含时间的日程信息"""
    service = ClassificationService()
    text = "准备项目文档"
    info = service.extract_schedule_info(text)
    
    assert info["time"] is None
    assert info["has_time_info"] is False


@pytest.mark.unit
def test_extract_memo_info():
    """测试提取备忘录信息"""
    service = ClassificationService()
    text = "今天学习了Python，需要继续深入学习"
    info = service.extract_memo_info(text)
    
    assert "content" in info
    assert info["content"] == text
    assert "summary" in info
    assert "tags" in info
    assert isinstance(info["tags"], list)


@pytest.mark.unit
def test_extract_memo_summary_long_text():
    """测试提取长文本的摘要"""
    service = ClassificationService()
    long_text = "这是一段很长的文本" * 50
    info = service.extract_memo_info(long_text)
    
    assert len(info["summary"]) <= 103  # 100 + "..."


@pytest.mark.unit
def test_extract_memo_tags():
    """测试提取备忘录标签"""
    service = ClassificationService()
    text = "今天工作很忙，完成了项目的重要功能"
    info = service.extract_memo_info(text)
    
    assert "工作" in info["tags"]


@pytest.mark.unit
def test_needs_manual_selection_low_confidence():
    """测试低置信度需要手动选择"""
    service = ClassificationService()
    assert service.needs_manual_selection(0.5) is True
    assert service.needs_manual_selection(0.3) is True


@pytest.mark.unit
def test_needs_manual_selection_high_confidence():
    """测试高置信度不需要手动选择"""
    service = ClassificationService()
    assert service.needs_manual_selection(0.8) is False
    assert service.needs_manual_selection(0.9) is False


@pytest.mark.unit
def test_classify_api_without_auth(client):
    """测试未认证调用分类API"""
    response = client.post(
        "/api/v1/classify",
        json={"text": "明天开会"}
    )
    
    # 未认证应该返回401或403
    assert response.status_code in [401, 403]


@pytest.mark.unit
def test_classify_api_with_auth(client, db_session):
    """测试认证后调用分类API"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 调用分类API
    response = client.post(
        "/api/v1/classify",
        json={"text": "明天下午2点开会"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    assert data["type"] in ["schedule", "memo"]
    assert "confidence" in data
    assert "extracted_data" in data
    assert "needs_manual_selection" in data


@pytest.mark.unit
def test_manual_classify_api(client, db_session):
    """测试手动分类API"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 调用手动分类API
    response = client.post(
        "/api/v1/classify/manual",
        json={
            "text": "明天开会",
            "type": "schedule"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["type"] == "schedule"
    assert "extracted_data" in data


@pytest.mark.unit
def test_classify_schedule_with_multiple_keywords():
    """测试包含多个日程关键词的文本分类"""
    service = ClassificationService()
    text = "明天上午10点会议，需要提前准备材料"
    result = service.classify_text(text)
    
    assert result["type"] == "schedule"
    assert result["confidence"] > 0.6


@pytest.mark.unit
def test_classify_memo_with_keywords():
    """测试包含备忘录关键词的文本分类"""
    service = ClassificationService()
    text = "记录一下今天的想法和心得体会"
    result = service.classify_text(text)
    
    assert result["type"] == "memo"


@pytest.mark.unit
def test_extract_time_patterns():
    """测试提取各种时间格式"""
    service = ClassificationService()
    
    # 测试不同的时间格式
    texts = [
        "14:30开会",
        "下午2点会议",
        "3点30分到达",
        "2 pm meeting"
    ]
    
    for text in texts:
        time_str = service._extract_time(text)
        assert time_str is not None


@pytest.mark.unit
def test_extract_date_patterns():
    """测试提取各种日期格式"""
    service = ClassificationService()
    
    # 测试不同的日期格式
    texts = [
        "2024-01-15会议",
        "明天开会",
        "下周一讨论",
        "1月15日活动"
    ]
    
    for text in texts:
        date_str = service._extract_date(text)
        assert date_str is not None
