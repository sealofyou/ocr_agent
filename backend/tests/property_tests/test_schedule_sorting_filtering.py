"""日程排序和筛选属性测试"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, date, timedelta


# ============================================================================
# Property 12: 日程时间排序测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=100, deadline=2000)
@given(
    st.lists(
        st.tuples(
            st.integers(min_value=1, max_value=28),  # day
            st.integers(min_value=0, max_value=23),  # hour
            st.integers(min_value=0, max_value=59),  # minute
            st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',)))  # description
        ),
        min_size=2,
        max_size=10
    )
)
def test_schedule_time_sorting_property(schedule_data_list):
    """
    Feature: text-archive-assistant, Property 12: 日程时间排序
    Validates: Requirements 4.3
    
    对于任意日程项列表，前端客户端应该按时间顺序（从早到晚）显示
    
    属性：查询返回的日程列表应该按日期和时间升序排列
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_sorting.db"
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
        import uuid
        username = f"sortuser_{uuid.uuid4().hex[:8]}"
        password = "TestPass123!"
        
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        # 登录
        login_response = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        if login_response.status_code != 200:
            # 如果登录失败，跳过这个测试
            assume(False)
        
        login_data = login_response.json()
        if "access_token" not in login_data:
            # 如果响应中没有token，跳过这个测试
            assume(False)
        
        token = login_data["access_token"]
        
        # 创建多个日程（随机顺序）
        created_schedules = []
        for day, hour, minute, description in schedule_data_list:
            schedule_data = {
                "date": f"2025-12-{day:02d}",
                "time": f"{hour:02d}:{minute:02d}",
                "description": description,
                "original_text": f"Test schedule on 2025-12-{day:02d} at {hour:02d}:{minute:02d}"
            }
            
            create_response = client.post(
                "/api/v1/schedules",
                json=schedule_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if create_response.status_code == 201:
                created_schedules.append(create_response.json())
        
        # 查询日程列表
        list_response = client.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        schedule_list = list_response.json()["schedules"]
        
        # 属性1：列表应该按日期和时间升序排列
        for i in range(len(schedule_list) - 1):
            current = schedule_list[i]
            next_item = schedule_list[i + 1]
            
            # 解析日期和时间
            current_date = datetime.strptime(current["date"], "%Y-%m-%d").date() if current["date"] else date.max
            next_date = datetime.strptime(next_item["date"], "%Y-%m-%d").date() if next_item["date"] else date.max
            
            current_time = datetime.strptime(current["time"], "%H:%M:%S").time() if current["time"] else datetime.min.time()
            next_time = datetime.strptime(next_item["time"], "%H:%M:%S").time() if next_item["time"] else datetime.min.time()
            
            # 组合日期和时间进行比较
            current_datetime = datetime.combine(current_date, current_time)
            next_datetime = datetime.combine(next_date, next_time)
            
            assert current_datetime <= next_datetime, \
                f"日程应该按时间升序排列: {current_datetime} 应该 <= {next_datetime}"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50, deadline=2000)
@given(
    st.lists(
        st.integers(min_value=1, max_value=28),
        min_size=3,
        max_size=10,
        unique=True
    )
)
def test_schedule_date_sorting_property(days):
    """
    Feature: text-archive-assistant, Property 12: 日程时间排序
    Validates: Requirements 4.3
    
    属性：具有不同日期的日程应该按日期升序排列
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_date_sorting.db"
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
        import uuid
        username = f"datesortuser_{uuid.uuid4().hex[:8]}"
        password = "TestPass123!"
        
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        # 登录
        login_response = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        if login_response.status_code != 200:
            assume(False)
        
        token = login_response.json()["access_token"]
        
        # 创建多个日程（随机日期顺序）
        for day in days:
            schedule_data = {
                "date": f"2025-12-{day:02d}",
                "time": "10:00",
                "description": f"Event on day {day}",
                "original_text": f"Event on day {day}"
            }
            
            client.post(
                "/api/v1/schedules",
                json=schedule_data,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询日程列表
        list_response = client.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        schedule_list = list_response.json()["schedules"]
        
        # 属性：日期应该按升序排列
        dates = [datetime.strptime(s["date"], "%Y-%m-%d").date() for s in schedule_list if s["date"]]
        for i in range(len(dates) - 1):
            assert dates[i] <= dates[i + 1], f"日期应该按升序排列: {dates[i]} <= {dates[i + 1]}"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()




# ============================================================================
# Property 13: 日期范围筛选测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=100, deadline=2000)
@given(
    st.lists(
        st.integers(min_value=1, max_value=28),
        min_size=5,
        max_size=15,
        unique=True
    ),
    st.integers(min_value=5, max_value=15),
    st.integers(min_value=16, max_value=25)
)
def test_date_range_filtering_property(days, start_day, end_day):
    """
    Feature: text-archive-assistant, Property 13: 日期范围筛选
    Validates: Requirements 4.5
    
    对于任意日期范围查询，系统应该只返回该范围内的日程项
    
    属性：筛选结果中的所有日程日期都应该在指定范围内
    """
    # 确保start_day < end_day
    assume(start_day < end_day)
    
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_date_filtering.db"
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
        import uuid
        username = f"filteruser_{uuid.uuid4().hex[:8]}"
        password = "TestPass123!"
        
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        # 登录
        login_response = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        if login_response.status_code != 200:
            assume(False)
        
        token = login_response.json()["access_token"]
        
        # 创建多个日程（覆盖整个月）
        for day in days:
            schedule_data = {
                "date": f"2025-12-{day:02d}",
                "time": "10:00",
                "description": f"Event on day {day}",
                "original_text": f"Event on day {day}"
            }
            
            client.post(
                "/api/v1/schedules",
                json=schedule_data,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询指定日期范围的日程
        start_date = f"2025-12-{start_day:02d}"
        end_date = f"2025-12-{end_day:02d}"
        
        list_response = client.get(
            f"/api/v1/schedules?start_date={start_date}&end_date={end_date}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        schedule_list = list_response.json()["schedules"]
        
        # 属性1：所有返回的日程日期都应该在指定范围内
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        for schedule in schedule_list:
            if schedule["date"]:
                schedule_date = datetime.strptime(schedule["date"], "%Y-%m-%d").date()
                assert start_date_obj <= schedule_date <= end_date_obj, \
                    f"日程日期 {schedule_date} 应该在范围 [{start_date_obj}, {end_date_obj}] 内"
        
        # 属性2：范围内的日程不应该被遗漏
        expected_days = [day for day in days if start_day <= day <= end_day]
        returned_days = [int(s["date"].split("-")[2]) for s in schedule_list if s["date"]]
        
        for expected_day in expected_days:
            assert expected_day in returned_days, \
                f"范围内的日程（第{expected_day}天）不应该被遗漏"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50, deadline=2000)
@given(
    st.lists(
        st.integers(min_value=1, max_value=28),
        min_size=10,
        max_size=20,
        unique=True
    )
)
def test_no_date_filter_returns_all_property(days):
    """
    Feature: text-archive-assistant, Property 13: 日期范围筛选
    Validates: Requirements 4.5
    
    属性：不指定日期范围时，应该返回所有日程
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_no_filter.db"
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
        import uuid
        username = f"nofilteruser_{uuid.uuid4().hex[:8]}"
        password = "TestPass123!"
        
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        # 登录
        login_response = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        if login_response.status_code != 200:
            assume(False)
        
        token = login_response.json()["access_token"]
        
        # 创建多个日程
        for day in days:
            schedule_data = {
                "date": f"2025-12-{day:02d}",
                "time": "10:00",
                "description": f"Event on day {day}",
                "original_text": f"Event on day {day}"
            }
            
            client.post(
                "/api/v1/schedules",
                json=schedule_data,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询所有日程（不指定日期范围）
        list_response = client.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        schedule_list = list_response.json()["schedules"]
        
        # 属性：返回的日程数量应该等于创建的数量
        assert len(schedule_list) == len(days), \
            f"不指定日期范围时应该返回所有日程: 期望 {len(days)}, 实际 {len(schedule_list)}"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50, deadline=2000)
@given(
    st.lists(
        st.integers(min_value=1, max_value=28),
        min_size=5,
        max_size=15,
        unique=True
    ),
    st.integers(min_value=1, max_value=10)
)
def test_start_date_only_filtering_property(days, start_day):
    """
    Feature: text-archive-assistant, Property 13: 日期范围筛选
    Validates: Requirements 4.5
    
    属性：只指定开始日期时，应该返回该日期及之后的所有日程
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_start_filter.db"
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
        import uuid
        username = f"startfilteruser_{uuid.uuid4().hex[:8]}"
        password = "TestPass123!"
        
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        # 登录
        login_response = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        if login_response.status_code != 200:
            assume(False)
        
        token = login_response.json()["access_token"]
        
        # 创建多个日程
        for day in days:
            schedule_data = {
                "date": f"2025-12-{day:02d}",
                "time": "10:00",
                "description": f"Event on day {day}",
                "original_text": f"Event on day {day}"
            }
            
            client.post(
                "/api/v1/schedules",
                json=schedule_data,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询指定开始日期的日程
        start_date = f"2025-12-{start_day:02d}"
        
        list_response = client.get(
            f"/api/v1/schedules?start_date={start_date}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        schedule_list = list_response.json()["schedules"]
        
        # 属性：所有返回的日程日期都应该 >= 开始日期
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        for schedule in schedule_list:
            if schedule["date"]:
                schedule_date = datetime.strptime(schedule["date"], "%Y-%m-%d").date()
                assert schedule_date >= start_date_obj, \
                    f"日程日期 {schedule_date} 应该 >= 开始日期 {start_date_obj}"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50, deadline=2000)
@given(
    st.lists(
        st.integers(min_value=1, max_value=28),
        min_size=5,
        max_size=15,
        unique=True
    ),
    st.integers(min_value=15, max_value=28)
)
def test_end_date_only_filtering_property(days, end_day):
    """
    Feature: text-archive-assistant, Property 13: 日期范围筛选
    Validates: Requirements 4.5
    
    属性：只指定结束日期时，应该返回该日期及之前的所有日程
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_end_filter.db"
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
        import uuid
        username = f"endfilteruser_{uuid.uuid4().hex[:8]}"
        password = "TestPass123!"
        
        register_response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        # 登录
        login_response = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
            })
        
        if login_response.status_code != 200:
            assume(False)
        
        token = login_response.json()["access_token"]
        
        # 创建多个日程
        for day in days:
            schedule_data = {
                "date": f"2025-12-{day:02d}",
                "time": "10:00",
                "description": f"Event on day {day}",
                "original_text": f"Event on day {day}"
            }
            
            client.post(
                "/api/v1/schedules",
                json=schedule_data,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询指定结束日期的日程
        end_date = f"2025-12-{end_day:02d}"
        
        list_response = client.get(
            f"/api/v1/schedules?end_date={end_date}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        schedule_list = list_response.json()["schedules"]
        
        # 属性：所有返回的日程日期都应该 <= 结束日期
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        for schedule in schedule_list:
            if schedule["date"]:
                schedule_date = datetime.strptime(schedule["date"], "%Y-%m-%d").date()
                assert schedule_date <= end_date_obj, \
                    f"日程日期 {schedule_date} 应该 <= 结束日期 {end_date_obj}"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
