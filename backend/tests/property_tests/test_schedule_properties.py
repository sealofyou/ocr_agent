"""日程管理属性测试"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, date, time
from app.services.classification_service import ClassificationService


# 自定义策略：生成包含时间信息的文本
@st.composite
def text_with_time_info(draw):
    """生成包含时间信息的文本"""
    time_patterns = [
        "14:30",
        "14点30分",
        "下午2点30分",
        "上午10点",
        "2 pm",
        "10 am"
    ]
    date_patterns = [
        "2025-12-01",
        "2025年12月1日",
        "明天",
        "今天",
        "后天"
    ]
    
    time_str = draw(st.sampled_from(time_patterns))
    date_str = draw(st.sampled_from(date_patterns))
    description = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))))
    
    # 随机组合
    choice = draw(st.integers(min_value=0, max_value=2))
    if choice == 0:
        return f"{date_str} {time_str} {description}"
    elif choice == 1:
        return f"{date_str} {description}"
    else:
        return f"{time_str} {description}"


@pytest.mark.property
@settings(max_examples=100)
@given(text_with_time_info())
def test_schedule_info_extraction_property(text):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    对于任意被分类为日程的文本，后端服务应该从中提取时间、日期和事件描述信息
    
    属性：提取的日程信息应该包含所有必需字段
    """
    service = ClassificationService()
    
    # 提取日程信息
    info = service.extract_schedule_info(text)
    
    # 属性1：必须包含所有必需字段
    required_fields = ["date", "time", "description", "has_time_info"]
    for field in required_fields:
        assert field in info, f"日程信息必须包含 {field} 字段"
    
    # 属性2：description不应该为空
    assert info["description"] is not None, "事件描述不应该为None"
    assert isinstance(info["description"], str), "事件描述应该是字符串类型"
    
    # 属性3：如果有日期或时间，has_time_info应该为True
    has_date_or_time = info["date"] is not None or info["time"] is not None
    assert info["has_time_info"] == has_date_or_time, "has_time_info应该反映是否有日期或时间信息"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_schedule_extraction_always_returns_structure_property(text):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：对于任意文本，日程信息提取应该总是返回完整的数据结构
    """
    service = ClassificationService()
    
    # 提取日程信息
    info = service.extract_schedule_info(text)
    
    # 属性：必须返回字典
    assert isinstance(info, dict), "提取结果应该是字典类型"
    
    # 属性：必须包含所有必需字段
    required_fields = ["date", "time", "description", "has_time_info"]
    for field in required_fields:
        assert field in info, f"日程信息必须包含 {field} 字段"
    
    # 属性：has_time_info应该是布尔值
    assert isinstance(info["has_time_info"], bool), "has_time_info应该是布尔类型"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.sampled_from(["14:30", "14点30分", "下午2点30分", "上午10点", "2 pm", "10 am"])
)
def test_time_extraction_property(description, time_str):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：包含时间信息的文本应该能够提取出时间
    """
    service = ClassificationService()
    
    # 构造包含时间的文本
    text = f"{time_str} {description}"
    
    # 提取日程信息
    info = service.extract_schedule_info(text)
    
    # 属性：应该提取到时间信息
    assert info["has_time_info"] is True, "包含时间的文本应该标记has_time_info为True"
    assert info["time"] is not None, "应该提取到时间信息"
    
    # 属性：提取的时间应该是标准格式 HH:MM
    if info["time"]:
        assert isinstance(info["time"], str), "时间应该是字符串类型"
        # 验证格式（应该是HH:MM）
        parts = info["time"].split(":")
        assert len(parts) == 2, "时间格式应该是HH:MM"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.sampled_from(["2025-12-01", "2025年12月1日", "明天", "今天", "后天"])
)
def test_date_extraction_property(description, date_str):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：包含日期信息的文本应该能够提取出日期
    """
    service = ClassificationService()
    
    # 构造包含日期的文本
    text = f"{date_str} {description}"
    
    # 提取日程信息
    info = service.extract_schedule_info(text)
    
    # 属性：应该提取到日期信息
    assert info["has_time_info"] is True, "包含日期的文本应该标记has_time_info为True"
    assert info["date"] is not None, "应该提取到日期信息"
    
    # 属性：提取的日期应该是标准格式 YYYY-MM-DD
    if info["date"]:
        assert isinstance(info["date"], str), "日期应该是字符串类型"
        # 验证格式（应该是YYYY-MM-DD）
        parts = info["date"].split("-")
        assert len(parts) == 3, "日期格式应该是YYYY-MM-DD"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_extraction_without_time_info_property(text):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：没有时间信息的文本应该正确标记has_time_info为False
    """
    # 确保文本不包含明显的时间/日期关键词
    time_keywords = ["点", "时", "分", "上午", "下午", "明天", "今天", "后天", ":", "：", "am", "pm", "年", "月", "日"]
    assume(not any(keyword in text.lower() for keyword in time_keywords))
    
    service = ClassificationService()
    
    # 提取日程信息
    info = service.extract_schedule_info(text)
    
    # 属性：没有时间信息时，has_time_info应该为False
    if info["date"] is None and info["time"] is None:
        assert info["has_time_info"] is False, "没有日期和时间时，has_time_info应该为False"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_description_preservation_property(text):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：事件描述应该保留原始文本的主要内容
    """
    service = ClassificationService()
    
    # 提取日程信息
    info = service.extract_schedule_info(text)
    
    # 属性：description应该存在且不为空
    assert "description" in info, "应该包含description字段"
    assert info["description"] is not None, "description不应该为None"
    assert isinstance(info["description"], str), "description应该是字符串类型"
    
    # 属性：如果原文本不为空，description也不应该为空
    if text.strip():
        assert info["description"].strip(), "非空文本的description不应该为空"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_extraction_consistency_property(text):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：对同一文本的多次提取应该返回相同的结果
    """
    service = ClassificationService()
    
    # 多次提取
    info1 = service.extract_schedule_info(text)
    info2 = service.extract_schedule_info(text)
    info3 = service.extract_schedule_info(text)
    
    # 属性：结果应该一致
    assert info1["date"] == info2["date"] == info3["date"], "日期提取应该一致"
    assert info1["time"] == info2["time"] == info3["time"], "时间提取应该一致"
    assert info1["has_time_info"] == info2["has_time_info"] == info3["has_time_info"], "has_time_info应该一致"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.sampled_from(["14:30", "14点30分", "下午2点30分", "上午10点", "晚上8点", "2 pm", "10 am"])
)
def test_time_normalization_property(time_str):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：时间标准化应该将各种格式转换为HH:MM格式
    """
    service = ClassificationService()
    
    # 标准化时间
    normalized = service._normalize_time(time_str)
    
    # 属性：标准化后应该是HH:MM格式或None
    if normalized is not None:
        assert isinstance(normalized, str), "标准化后的时间应该是字符串"
        parts = normalized.split(":")
        assert len(parts) == 2, "标准化后的时间应该是HH:MM格式"
        
        # 验证小时和分钟的范围
        hour = int(parts[0])
        minute = int(parts[1])
        assert 0 <= hour <= 23, "小时应该在0-23之间"
        assert 0 <= minute <= 59, "分钟应该在0-59之间"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.sampled_from(["2025-12-01", "2025年12月1日", "明天", "今天", "后天", "昨天"])
)
def test_date_normalization_property(date_str):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：日期标准化应该将各种格式转换为YYYY-MM-DD格式
    """
    service = ClassificationService()
    
    # 标准化日期
    normalized = service._normalize_date(date_str)
    
    # 属性：标准化后应该是YYYY-MM-DD格式或None
    if normalized is not None:
        assert isinstance(normalized, str), "标准化后的日期应该是字符串"
        parts = normalized.split("-")
        assert len(parts) == 3, "标准化后的日期应该是YYYY-MM-DD格式"
        
        # 验证年月日的范围
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        assert 1900 <= year <= 2100, "年份应该在合理范围内"
        assert 1 <= month <= 12, "月份应该在1-12之间"
        assert 1 <= day <= 31, "日期应该在1-31之间"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.sampled_from(["14:30", "2025-12-01"]),
    st.sampled_from(["14点30分", "2025年12月1日"])
)
def test_multiple_time_date_formats_property(description, format1, format2):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：文本中包含多种时间/日期格式时，应该能提取出至少一个
    """
    service = ClassificationService()
    
    # 构造包含多种格式的文本
    text = f"{format1} {format2} {description}"
    
    # 提取日程信息
    info = service.extract_schedule_info(text)
    
    # 属性：应该提取到至少一个时间或日期信息
    assert info["has_time_info"] is True, "包含时间/日期格式的文本应该标记has_time_info为True"
    assert info["date"] is not None or info["time"] is not None, "应该提取到至少一个时间或日期信息"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_extraction_determinism_property(text):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：提取算法应该是确定性的（相同输入产生相同输出）
    """
    service1 = ClassificationService()
    service2 = ClassificationService()
    
    # 使用不同实例提取
    info1 = service1.extract_schedule_info(text)
    info2 = service2.extract_schedule_info(text)
    
    # 属性：不同实例的提取结果应该一致
    assert info1["date"] == info2["date"], "不同实例的日期提取应该一致"
    assert info1["time"] == info2["time"], "不同实例的时间提取应该一致"
    assert info1["has_time_info"] == info2["has_time_info"], "不同实例的has_time_info应该一致"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.lists(
        st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
        min_size=1,
        max_size=10
    )
)
def test_batch_extraction_property(text_list):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：批量提取应该为每个文本返回独立的结果
    """
    service = ClassificationService()
    
    results = []
    for text in text_list:
        info = service.extract_schedule_info(text)
        results.append(info)
    
    # 属性：每个文本都应该有有效的提取结果
    assert len(results) == len(text_list), "结果数量应该与输入文本数量一致"
    
    for i, info in enumerate(results):
        # 验证每个结果都包含必需字段
        required_fields = ["date", "time", "description", "has_time_info"]
        for field in required_fields:
            assert field in info, f"第{i}个文本的提取结果必须包含 {field} 字段"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.sampled_from(["14:30", "14点30分", "下午2点30分"]),
    st.sampled_from(["2025-12-01", "2025年12月1日", "明天"])
)
def test_complete_schedule_extraction_property(description, time_str, date_str):
    """
    Feature: text-archive-assistant, Property 10: 日程信息提取
    Validates: Requirements 4.1
    
    属性：包含完整时间和日期信息的文本应该能提取出所有信息
    """
    service = ClassificationService()
    
    # 构造包含完整信息的文本
    text = f"{date_str} {time_str} {description}"
    
    # 提取日程信息
    info = service.extract_schedule_info(text)
    
    # 属性：应该提取到日期和时间
    assert info["has_time_info"] is True, "包含完整信息的文本应该标记has_time_info为True"
    assert info["date"] is not None, "应该提取到日期信息"
    assert info["time"] is not None, "应该提取到时间信息"
    
    # 属性：描述应该包含原始描述内容
    assert info["description"] is not None, "应该有事件描述"



# ============================================================================
# Property 11: 归档内容存储完整性测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_schedule_storage_integrity_property(username, email, description, original_text):
    """
    Feature: text-archive-assistant, Property 11: 归档内容存储完整性
    Validates: Requirements 4.2, 5.2
    
    对于任意创建的日程项或备忘录，归档存储应该保存所有必需字段（时间、内容、原始文本等），且查询时能完整返回
    
    属性：创建的日程项应该能够完整存储和检索所有字段
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_storage_integrity.db"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    
    try:
        # 清理用户名和邮箱，确保有效
        clean_username = ''.join(c for c in username if c.isalnum() or c in '_-')[:50] or "testuser"
        clean_email = f"{clean_username}@test.com"
        password = "TestPass123!"
        
        # 注册用户
        register_response = client.post("/api/v1/auth/register", json={
            "username": clean_username,
            "email": clean_email,
            "password": password
        })
        
        # 如果用户已存在，直接登录
        if register_response.status_code != 201:
            # 尝试登录
            login_response = client.post("/api/v1/auth/login", json={
                "username": clean_username,
                "password": password
            })
            if login_response.status_code != 200:
                # 如果登录失败，跳过这个测试用例
                assume(False)
        else:
            login_response = client.post("/api/v1/auth/login", json={
                "username": clean_username,
                "password": password
            })
        
        token = login_response.json()["token"]
        
        # 创建日程
        schedule_data = {
            "date": "2025-12-01",
            "time": "14:30",
            "description": description,
            "original_text": original_text
        }
        
        create_response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert create_response.status_code == 201, f"创建日程失败: {create_response.json()}"
        created_schedule = create_response.json()
        schedule_id = created_schedule["id"]
        
        # 属性1：创建响应应该包含所有必需字段
        required_fields = ["id", "user_id", "date", "time", "description", "original_text", "created_at", "updated_at"]
        for field in required_fields:
            assert field in created_schedule, f"创建响应缺少必需字段: {field}"
        
        # 属性2：存储的数据应该与输入一致
        assert created_schedule["date"] == "2025-12-01", "存储的日期应该与输入一致"
        assert created_schedule["time"] == "14:30:00", "存储的时间应该与输入一致"
        assert created_schedule["description"] == description, "存储的描述应该与输入一致"
        assert created_schedule["original_text"] == original_text, "存储的原始文本应该与输入一致"
        
        # 属性3：查询单个日程应该返回完整数据
        get_response = client.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_response.status_code == 200, "查询日程应该成功"
        retrieved_schedule = get_response.json()
        
        # 属性4：检索的数据应该与创建的数据完全一致
        assert retrieved_schedule["id"] == created_schedule["id"], "ID应该一致"
        assert retrieved_schedule["date"] == created_schedule["date"], "日期应该一致"
        assert retrieved_schedule["time"] == created_schedule["time"], "时间应该一致"
        assert retrieved_schedule["description"] == created_schedule["description"], "描述应该一致"
        assert retrieved_schedule["original_text"] == created_schedule["original_text"], "原始文本应该一致"
        
        # 属性5：查询列表应该包含创建的日程
        list_response = client.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        schedule_list = list_response.json()
        
        # 在列表中查找创建的日程
        found = False
        for schedule in schedule_list["schedules"]:
            if schedule["id"] == schedule_id:
                found = True
                # 验证列表中的数据也是完整的
                assert schedule["date"] == created_schedule["date"], "列表中的日期应该一致"
                assert schedule["time"] == created_schedule["time"], "列表中的时间应该一致"
                assert schedule["description"] == created_schedule["description"], "列表中的描述应该一致"
                break
        
        assert found, "创建的日程应该出现在列表中"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
        ),
        min_size=1,
        max_size=5
    )
)
def test_multiple_schedules_storage_integrity_property(schedule_data_list):
    """
    Feature: text-archive-assistant, Property 11: 归档内容存储完整性
    Validates: Requirements 4.2, 5.2
    
    属性：批量创建的日程项应该都能完整存储和检索
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_multiple_storage.db"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    
    try:
        # 注册并登录用户
        username = "batchuser"
        password = "TestPass123!"
        
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        if register_response.status_code != 201:
            login_response = client.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        else:
            login_response = client.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        
        token = login_response.json()["token"]
        
        # 创建多个日程
        created_ids = []
        for i, (description, original_text) in enumerate(schedule_data_list):
            schedule_data = {
                "date": f"2025-12-{(i % 28) + 1:02d}",
                "time": f"{(i % 24):02d}:00",
                "description": description,
                "original_text": original_text
            }
            
            create_response = client.post(
                "/api/v1/schedules",
                json=schedule_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert create_response.status_code == 201, f"创建第{i}个日程失败"
            created_ids.append(create_response.json()["id"])
        
        # 属性：查询列表应该返回所有创建的日程
        list_response = client.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        schedule_list = list_response.json()
        
        # 属性：列表中的日程数量应该至少等于创建的数量
        assert schedule_list["total"] >= len(created_ids), "列表中的日程数量应该至少等于创建的数量"
        
        # 属性：所有创建的日程都应该在列表中
        list_ids = [s["id"] for s in schedule_list["schedules"]]
        for created_id in created_ids:
            assert created_id in list_ids, f"创建的日程 {created_id} 应该在列表中"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_schedule_update_integrity_property(description1, original_text1, description2, original_text2):
    """
    Feature: text-archive-assistant, Property 11: 归档内容存储完整性
    Validates: Requirements 4.2, 5.2
    
    属性：更新日程后，新数据应该完整存储并能正确检索
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_update_integrity.db"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    
    try:
        # 注册并登录用户
        username = "updateuser"
        password = "TestPass123!"
        
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        if register_response.status_code != 201:
            login_response = client.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        else:
            login_response = client.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        
        token = login_response.json()["token"]
        
        # 创建日程
        schedule_data = {
            "date": "2025-12-01",
            "time": "14:30",
            "description": description1,
            "original_text": original_text1
        }
        
        create_response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert create_response.status_code == 201, "创建日程应该成功"
        schedule_id = create_response.json()["id"]
        
        # 更新日程
        update_data = {
            "description": description2,
            "original_text": original_text2
        }
        
        update_response = client.put(
            f"/api/v1/schedules/{schedule_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert update_response.status_code == 200, "更新日程应该成功"
        updated_schedule = update_response.json()
        
        # 属性：更新后的数据应该反映新值
        assert updated_schedule["description"] == description2, "更新后的描述应该是新值"
        assert updated_schedule["original_text"] == original_text2, "更新后的原始文本应该是新值"
        
        # 属性：查询应该返回更新后的数据
        get_response = client.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_response.status_code == 200, "查询应该成功"
        retrieved_schedule = get_response.json()
        
        assert retrieved_schedule["description"] == description2, "检索的描述应该是更新后的值"
        assert retrieved_schedule["original_text"] == original_text2, "检索的原始文本应该是更新后的值"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_schedule_deletion_integrity_property(description, original_text):
    """
    Feature: text-archive-assistant, Property 11: 归档内容存储完整性
    Validates: Requirements 4.2, 5.2
    
    属性：删除日程后，该日程不应该再出现在查询结果中
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_deletion_integrity.db"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    
    try:
        # 注册并登录用户
        username = "deleteuser"
        password = "TestPass123!"
        
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        if register_response.status_code != 201:
            login_response = client.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        else:
            login_response = client.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        
        token = login_response.json()["token"]
        
        # 创建日程
        schedule_data = {
            "date": "2025-12-01",
            "time": "14:30",
            "description": description,
            "original_text": original_text
        }
        
        create_response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert create_response.status_code == 201, "创建日程应该成功"
        schedule_id = create_response.json()["id"]
        
        # 删除日程
        delete_response = client.delete(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert delete_response.status_code == 204, "删除日程应该成功"
        
        # 属性：查询已删除的日程应该返回404
        get_response = client.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_response.status_code == 404, "查询已删除的日程应该返回404"
        
        # 属性：列表中不应该包含已删除的日程
        list_response = client.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        schedule_list = list_response.json()
        
        list_ids = [s["id"] for s in schedule_list["schedules"]]
        assert schedule_id not in list_ids, "已删除的日程不应该出现在列表中"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
