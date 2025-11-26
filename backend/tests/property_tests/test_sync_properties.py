"""跨端数据同步属性测试"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from fastapi.testclient import TestClient
from main import app
from app.db.base import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# ============================================================================
# Property 18: 用户数据访问测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
        ),
        min_size=1,
        max_size=5
    ),
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))), min_size=0, max_size=3)
        ),
        min_size=1,
        max_size=5
    )
)
def test_user_data_access_property(username, schedule_data_list, memo_data_list):
    """
    Feature: text-archive-assistant, Property 18: 用户数据访问
    Validates: Requirements 6.1
    
    对于任意用户在任意设备上登录，系统应该显示该用户的所有归档内容
    
    属性：用户在不同设备（模拟为不同客户端实例）上登录后，应该能访问相同的归档内容
    """
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_user_data_access.db"
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
    
    # 创建两个客户端实例，模拟不同设备
    client1 = TestClient(app)
    client2 = TestClient(app)
    
    try:
        # 清理用户名，确保有效
        clean_username = ''.join(c for c in username if c.isalnum() or c in '_-')[:50] or "testuser"
        clean_email = f"{clean_username}@test.com"
        password = "TestPass123!"
        
        # 在设备1上注册用户
        register_response = client1.post("/api/v1/auth/register", json={
            "username": clean_username,
            "email": clean_email,
            "password": password
        })
        
        # 如果用户已存在，直接登录
        if register_response.status_code != 201:
            login_response1 = client1.post("/api/v1/auth/login", json={
                "username": clean_username,
                "password": password
            })
            if login_response1.status_code != 200:
                assume(False)
        else:
            login_response1 = client1.post("/api/v1/auth/login", json={
                "username": clean_username,
                "password": password
            })
        
        token1 = login_response1.json()["access_token"]
        
        # 在设备1上创建日程
        created_schedule_ids = []
        for i, (description, original_text) in enumerate(schedule_data_list):
            schedule_data = {
                "date": f"2025-12-{(i % 28) + 1:02d}",
                "time": f"{(i % 24):02d}:00",
                "description": description,
                "original_text": original_text
            }
            
            create_response = client1.post(
                "/api/v1/schedules",
                json=schedule_data,
                headers={"Authorization": f"Bearer {token1}"}
            )
            
            if create_response.status_code == 201:
                created_schedule_ids.append(create_response.json()["id"])
        
        # 在设备1上创建备忘录
        created_memo_ids = []
        for content, tags in memo_data_list:
            memo_data = {
                "content": content,
                "tags": tags if tags else None
            }
            
            create_response = client1.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token1}"}
            )
            
            if create_response.status_code == 201:
                created_memo_ids.append(create_response.json()["id"])
        
        # 在设备2上登录同一用户
        login_response2 = client2.post("/api/v1/auth/login", json={
            "username": clean_username,
            "password": password
        })
        
        assert login_response2.status_code == 200, "设备2上登录应该成功"
        token2 = login_response2.json()["access_token"]
        
        # 属性1：设备2应该能查询到设备1创建的所有日程
        schedules_response = client2.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert schedules_response.status_code == 200, "设备2查询日程应该成功"
        schedules_on_device2 = schedules_response.json()
        
        device2_schedule_ids = [s["id"] for s in schedules_on_device2["schedules"]]
        for schedule_id in created_schedule_ids:
            assert schedule_id in device2_schedule_ids, f"设备2应该能访问设备1创建的日程 {schedule_id}"
        
        # 属性2：设备2应该能查询到设备1创建的所有备忘录
        memos_response = client2.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert memos_response.status_code == 200, "设备2查询备忘录应该成功"
        memos_on_device2 = memos_response.json()
        
        device2_memo_ids = [m["id"] for m in memos_on_device2["memos"]]
        for memo_id in created_memo_ids:
            assert memo_id in device2_memo_ids, f"设备2应该能访问设备1创建的备忘录 {memo_id}"
        
        # 属性3：设备2应该能访问单个日程的详情
        for schedule_id in created_schedule_ids:
            get_response = client2.get(
                f"/api/v1/schedules/{schedule_id}",
                headers={"Authorization": f"Bearer {token2}"}
            )
            assert get_response.status_code == 200, f"设备2应该能访问日程 {schedule_id} 的详情"
        
        # 属性4：设备2应该能访问单个备忘录的详情
        for memo_id in created_memo_ids:
            get_response = client2.get(
                f"/api/v1/memos/{memo_id}",
                headers={"Authorization": f"Bearer {token2}"}
            )
            assert get_response.status_code == 200, f"设备2应该能访问备忘录 {memo_id} 的详情"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()



@pytest.mark.property
@settings(max_examples=50)
@given(
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_user_data_isolation_between_users_property(username1, username2, content):
    """
    Feature: text-archive-assistant, Property 18: 用户数据访问
    Validates: Requirements 6.1
    
    属性：不同用户应该只能访问自己的数据，不能访问其他用户的数据
    """
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_user_isolation.db"
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
        # 清理用户名
        clean_username1 = ''.join(c for c in username1 if c.isalnum() or c in '_-')[:50] or "testuser1"
        clean_username2 = ''.join(c for c in username2 if c.isalnum() or c in '_-')[:50] or "testuser2"
        
        # 确保用户名不同
        if clean_username1 == clean_username2:
            clean_username2 = clean_username2 + "2"
        
        password = "TestPass123!"
        
        # 注册用户1
        register_response1 = client.post("/api/v1/auth/register", json={
            "username": clean_username1,
            "email": f"{clean_username1}@test.com",
            "password": password
        })
        
        if register_response1.status_code != 201:
            login_response1 = client.post("/api/v1/auth/login", json={
                "username": clean_username1,
                "password": password
            })
            if login_response1.status_code != 200:
                assume(False)
        else:
            login_response1 = client.post("/api/v1/auth/login", json={
                "username": clean_username1,
                "password": password
            })
        
        token1 = login_response1.json()["access_token"]
        
        # 注册用户2
        register_response2 = client.post("/api/v1/auth/register", json={
            "username": clean_username2,
            "email": f"{clean_username2}@test.com",
            "password": password
        })
        
        if register_response2.status_code != 201:
            login_response2 = client.post("/api/v1/auth/login", json={
                "username": clean_username2,
                "password": password
            })
            if login_response2.status_code != 200:
                assume(False)
        else:
            login_response2 = client.post("/api/v1/auth/login", json={
                "username": clean_username2,
                "password": password
            })
        
        token2 = login_response2.json()["access_token"]
        
        # 用户1创建备忘录
        memo_data = {
            "content": content
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert create_response.status_code == 201, "用户1创建备忘录应该成功"
        memo_id = create_response.json()["id"]
        
        # 属性：用户2不应该能访问用户1的备忘录
        get_response = client.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert get_response.status_code == 404, "用户2不应该能访问用户1的备忘录"
        
        # 属性：用户2查询列表时不应该看到用户1的备忘录
        list_response = client.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert list_response.status_code == 200, "用户2查询列表应该成功"
        user2_memos = list_response.json()
        
        user2_memo_ids = [m["id"] for m in user2_memos["memos"]]
        assert memo_id not in user2_memo_ids, "用户2的列表中不应该包含用户1的备忘录"
        
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
def test_user_data_persistence_across_sessions_property(description, original_text):
    """
    Feature: text-archive-assistant, Property 18: 用户数据访问
    Validates: Requirements 6.1
    
    属性：用户数据应该在会话之间持久化（登出后再登录仍能访问）
    """
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_data_persistence.db"
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
        username = "persistuser"
        password = "TestPass123!"
        
        # 注册并登录
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
        
        token1 = login_response.json()["access_token"]
        
        # 创建日程
        schedule_data = {
            "date": "2025-12-15",
            "time": "10:00",
            "description": description,
            "original_text": original_text
        }
        
        create_response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert create_response.status_code == 201, "创建日程应该成功"
        schedule_id = create_response.json()["id"]
        
        # 模拟登出（不使用旧token）并重新登录
        login_response2 = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        assert login_response2.status_code == 200, "重新登录应该成功"
        token2 = login_response2.json()["access_token"]
        
        # 属性：使用新token应该能访问之前创建的日程
        get_response = client.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert get_response.status_code == 200, "重新登录后应该能访问之前创建的日程"
        retrieved_schedule = get_response.json()
        
        # 属性：数据应该完整保留
        assert retrieved_schedule["id"] == schedule_id, "日程ID应该一致"
        assert retrieved_schedule["description"] == description, "描述应该一致"
        assert retrieved_schedule["original_text"] == original_text, "原始文本应该一致"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()



# ============================================================================
# Property 19: 数据同步一致性测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_data_sync_consistency_property(description1, original_text1, description2, original_text2):
    """
    Feature: text-archive-assistant, Property 19: 数据同步一致性
    Validates: Requirements 6.2, 6.3
    
    对于任意用户在一个设备上创建或修改的内容，在另一个设备上刷新后应该能看到最新的更改
    
    属性：设备1上的修改应该立即持久化，设备2查询时应该能看到最新数据
    """
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_sync_consistency.db"
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
    
    # 创建两个客户端实例，模拟不同设备
    client1 = TestClient(app)
    client2 = TestClient(app)
    
    try:
        username = "syncuser"
        password = "TestPass123!"
        
        # 在设备1上注册并登录
        register_response = client1.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        if register_response.status_code != 201:
            login_response1 = client1.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        else:
            login_response1 = client1.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        
        token1 = login_response1.json()["access_token"]
        
        # 在设备2上登录
        login_response2 = client2.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        token2 = login_response2.json()["access_token"]
        
        # 设备1创建日程
        schedule_data = {
            "date": "2025-12-20",
            "time": "15:00",
            "description": description1,
            "original_text": original_text1
        }
        
        create_response = client1.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert create_response.status_code == 201, "设备1创建日程应该成功"
        schedule_id = create_response.json()["id"]
        
        # 属性1：设备2立即查询应该能看到设备1创建的日程
        get_response = client2.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert get_response.status_code == 200, "设备2应该能立即访问设备1创建的日程"
        retrieved_schedule = get_response.json()
        assert retrieved_schedule["description"] == description1, "设备2应该看到原始描述"
        assert retrieved_schedule["original_text"] == original_text1, "设备2应该看到原始文本"
        
        # 设备1修改日程
        update_data = {
            "description": description2,
            "original_text": original_text2
        }
        
        update_response = client1.put(
            f"/api/v1/schedules/{schedule_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert update_response.status_code == 200, "设备1更新日程应该成功"
        
        # 属性2：设备2刷新后应该能看到设备1的修改
        get_response2 = client2.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert get_response2.status_code == 200, "设备2应该能访问更新后的日程"
        updated_schedule = get_response2.json()
        assert updated_schedule["description"] == description2, "设备2应该看到更新后的描述"
        assert updated_schedule["original_text"] == original_text2, "设备2应该看到更新后的文本"
        
        # 属性3：设备2查询列表也应该看到最新数据
        list_response = client2.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert list_response.status_code == 200, "设备2查询列表应该成功"
        schedules = list_response.json()["schedules"]
        
        found_schedule = None
        for s in schedules:
            if s["id"] == schedule_id:
                found_schedule = s
                break
        
        assert found_schedule is not None, "列表中应该包含该日程"
        assert found_schedule["description"] == description2, "列表中应该显示最新的描述"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))), min_size=1, max_size=3),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))), min_size=1, max_size=3)
)
def test_memo_sync_consistency_property(content1, tags1, content2, tags2):
    """
    Feature: text-archive-assistant, Property 19: 数据同步一致性
    Validates: Requirements 6.2, 6.3
    
    属性：备忘录的创建和修改也应该在设备间同步
    """
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_memo_sync.db"
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
    
    # 创建两个客户端实例，模拟不同设备
    client1 = TestClient(app)
    client2 = TestClient(app)
    
    try:
        username = "memosyncuser"
        password = "TestPass123!"
        
        # 在设备1上注册并登录
        register_response = client1.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        if register_response.status_code != 201:
            login_response1 = client1.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        else:
            login_response1 = client1.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        
        token1 = login_response1.json()["access_token"]
        
        # 在设备2上登录
        login_response2 = client2.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        token2 = login_response2.json()["access_token"]
        
        # 设备1创建备忘录
        memo_data = {
            "content": content1,
            "tags": tags1
        }
        
        create_response = client1.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert create_response.status_code == 201, "设备1创建备忘录应该成功"
        memo_id = create_response.json()["id"]
        
        # 属性1：设备2立即查询应该能看到设备1创建的备忘录
        get_response = client2.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert get_response.status_code == 200, "设备2应该能立即访问设备1创建的备忘录"
        retrieved_memo = get_response.json()
        assert retrieved_memo["content"] == content1, "设备2应该看到原始内容"
        for tag in tags1:
            assert tag in retrieved_memo["tags"], f"设备2应该看到标签 {tag}"
        
        # 设备1修改备忘录
        update_data = {
            "content": content2,
            "tags": tags2
        }
        
        update_response = client1.put(
            f"/api/v1/memos/{memo_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert update_response.status_code == 200, "设备1更新备忘录应该成功"
        
        # 属性2：设备2刷新后应该能看到设备1的修改
        get_response2 = client2.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert get_response2.status_code == 200, "设备2应该能访问更新后的备忘录"
        updated_memo = get_response2.json()
        assert updated_memo["content"] == content2, "设备2应该看到更新后的内容"
        for tag in tags2:
            assert tag in updated_memo["tags"], f"设备2应该看到更新后的标签 {tag}"
        
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
def test_deletion_sync_consistency_property(description, original_text):
    """
    Feature: text-archive-assistant, Property 19: 数据同步一致性
    Validates: Requirements 6.2, 6.3
    
    属性：设备1删除数据后，设备2应该立即无法访问该数据
    """
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_deletion_sync.db"
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
    
    # 创建两个客户端实例，模拟不同设备
    client1 = TestClient(app)
    client2 = TestClient(app)
    
    try:
        username = "deletesyncuser"
        password = "TestPass123!"
        
        # 在设备1上注册并登录
        register_response = client1.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        })
        
        if register_response.status_code != 201:
            login_response1 = client1.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        else:
            login_response1 = client1.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
        
        token1 = login_response1.json()["access_token"]
        
        # 在设备2上登录
        login_response2 = client2.post("/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        
        token2 = login_response2.json()["access_token"]
        
        # 设备1创建日程
        schedule_data = {
            "date": "2025-12-25",
            "time": "18:00",
            "description": description,
            "original_text": original_text
        }
        
        create_response = client1.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert create_response.status_code == 201, "设备1创建日程应该成功"
        schedule_id = create_response.json()["id"]
        
        # 设备2确认能访问
        get_response = client2.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert get_response.status_code == 200, "设备2应该能访问日程"
        
        # 设备1删除日程
        delete_response = client1.delete(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert delete_response.status_code == 204, "设备1删除日程应该成功"
        
        # 属性：设备2立即查询应该返回404
        get_response2 = client2.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert get_response2.status_code == 404, "设备2应该无法访问已删除的日程"
        
        # 属性：设备2查询列表也不应该包含已删除的日程
        list_response = client2.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert list_response.status_code == 200, "设备2查询列表应该成功"
        schedules = list_response.json()["schedules"]
        
        schedule_ids = [s["id"] for s in schedules]
        assert schedule_id not in schedule_ids, "列表中不应该包含已删除的日程"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()



# ============================================================================
# Property 30: 数据隔离测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
        ),
        min_size=1,
        max_size=3
    ),
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
            st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))), min_size=0, max_size=2)
        ),
        min_size=1,
        max_size=3
    )
)
def test_data_isolation_property(username1, username2, schedule_data_list, memo_data_list):
    """
    Feature: text-archive-assistant, Property 30: 数据隔离
    Validates: Requirements 10.4
    
    对于任意用户，该用户只能访问自己创建的归档内容，不能访问其他用户的数据
    
    属性：用户1创建的数据不应该出现在用户2的查询结果中
    """
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_data_isolation.db"
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
        # 清理用户名
        clean_username1 = ''.join(c for c in username1 if c.isalnum() or c in '_-')[:50] or "user1"
        clean_username2 = ''.join(c for c in username2 if c.isalnum() or c in '_-')[:50] or "user2"
        
        # 确保用户名不同
        if clean_username1 == clean_username2:
            clean_username2 = clean_username2 + "_2"
        
        password = "TestPass123!"
        
        # 注册用户1
        register_response1 = client.post("/api/v1/auth/register", json={
            "username": clean_username1,
            "email": f"{clean_username1}@test.com",
            "password": password
        })
        
        if register_response1.status_code != 201:
            login_response1 = client.post("/api/v1/auth/login", json={
                "username": clean_username1,
                "password": password
            })
            if login_response1.status_code != 200:
                assume(False)
        else:
            login_response1 = client.post("/api/v1/auth/login", json={
                "username": clean_username1,
                "password": password
            })
        
        token1 = login_response1.json()["access_token"]
        
        # 注册用户2
        register_response2 = client.post("/api/v1/auth/register", json={
            "username": clean_username2,
            "email": f"{clean_username2}@test.com",
            "password": password
        })
        
        if register_response2.status_code != 201:
            login_response2 = client.post("/api/v1/auth/login", json={
                "username": clean_username2,
                "password": password
            })
            if login_response2.status_code != 200:
                assume(False)
        else:
            login_response2 = client.post("/api/v1/auth/login", json={
                "username": clean_username2,
                "password": password
            })
        
        token2 = login_response2.json()["access_token"]
        
        # 用户1创建日程
        user1_schedule_ids = []
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
                headers={"Authorization": f"Bearer {token1}"}
            )
            
            if create_response.status_code == 201:
                user1_schedule_ids.append(create_response.json()["id"])
        
        # 用户1创建备忘录
        user1_memo_ids = []
        for content, tags in memo_data_list:
            memo_data = {
                "content": content,
                "tags": tags if tags else None
            }
            
            create_response = client.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token1}"}
            )
            
            if create_response.status_code == 201:
                user1_memo_ids.append(create_response.json()["id"])
        
        # 属性1：用户2不应该能访问用户1的任何日程
        for schedule_id in user1_schedule_ids:
            get_response = client.get(
                f"/api/v1/schedules/{schedule_id}",
                headers={"Authorization": f"Bearer {token2}"}
            )
            assert get_response.status_code == 404, f"用户2不应该能访问用户1的日程 {schedule_id}"
        
        # 属性2：用户2不应该能访问用户1的任何备忘录
        for memo_id in user1_memo_ids:
            get_response = client.get(
                f"/api/v1/memos/{memo_id}",
                headers={"Authorization": f"Bearer {token2}"}
            )
            assert get_response.status_code == 404, f"用户2不应该能访问用户1的备忘录 {memo_id}"
        
        # 属性3：用户2查询日程列表时不应该看到用户1的日程
        schedules_response = client.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert schedules_response.status_code == 200, "用户2查询日程列表应该成功"
        user2_schedules = schedules_response.json()["schedules"]
        user2_schedule_ids = [s["id"] for s in user2_schedules]
        
        for schedule_id in user1_schedule_ids:
            assert schedule_id not in user2_schedule_ids, f"用户2的日程列表不应该包含用户1的日程 {schedule_id}"
        
        # 属性4：用户2查询备忘录列表时不应该看到用户1的备忘录
        memos_response = client.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert memos_response.status_code == 200, "用户2查询备忘录列表应该成功"
        user2_memos = memos_response.json()["memos"]
        user2_memo_ids = [m["id"] for m in user2_memos]
        
        for memo_id in user1_memo_ids:
            assert memo_id not in user2_memo_ids, f"用户2的备忘录列表不应该包含用户1的备忘录 {memo_id}"
        
        # 属性5：用户2不应该能修改用户1的日程
        if user1_schedule_ids:
            update_data = {
                "description": "尝试修改"
            }
            
            update_response = client.put(
                f"/api/v1/schedules/{user1_schedule_ids[0]}",
                json=update_data,
                headers={"Authorization": f"Bearer {token2}"}
            )
            
            assert update_response.status_code == 404, "用户2不应该能修改用户1的日程"
        
        # 属性6：用户2不应该能删除用户1的日程
        if user1_schedule_ids:
            delete_response = client.delete(
                f"/api/v1/schedules/{user1_schedule_ids[0]}",
                headers={"Authorization": f"Bearer {token2}"}
            )
            
            assert delete_response.status_code == 404, "用户2不应该能删除用户1的日程"
        
        # 属性7：用户2不应该能修改用户1的备忘录
        if user1_memo_ids:
            update_data = {
                "content": "尝试修改"
            }
            
            update_response = client.put(
                f"/api/v1/memos/{user1_memo_ids[0]}",
                json=update_data,
                headers={"Authorization": f"Bearer {token2}"}
            )
            
            assert update_response.status_code == 404, "用户2不应该能修改用户1的备忘录"
        
        # 属性8：用户2不应该能删除用户1的备忘录
        if user1_memo_ids:
            delete_response = client.delete(
                f"/api/v1/memos/{user1_memo_ids[0]}",
                headers={"Authorization": f"Bearer {token2}"}
            )
            
            assert delete_response.status_code == 404, "用户2不应该能删除用户1的备忘录"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.lists(
        st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
        min_size=2,
        max_size=5,
        unique=True
    ),
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_multi_user_isolation_property(usernames, content):
    """
    Feature: text-archive-assistant, Property 30: 数据隔离
    Validates: Requirements 10.4
    
    属性：多个用户之间的数据应该完全隔离
    """
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_multi_user_isolation.db"
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
        password = "TestPass123!"
        user_tokens = []
        user_memo_ids = []
        
        # 注册所有用户并为每个用户创建备忘录
        for i, username in enumerate(usernames):
            clean_username = ''.join(c for c in username if c.isalnum() or c in '_-')[:50] or f"user{i}"
            
            # 注册并登录
            register_response = client.post("/api/v1/auth/register", json={
                "username": clean_username,
                "email": f"{clean_username}@test.com",
                "password": password
            })
            
            if register_response.status_code != 201:
                login_response = client.post("/api/v1/auth/login", json={
                    "username": clean_username,
                    "password": password
                })
                if login_response.status_code != 200:
                    continue
            else:
                login_response = client.post("/api/v1/auth/login", json={
                    "username": clean_username,
                    "password": password
                })
            
            token = login_response.json()["access_token"]
            user_tokens.append(token)
            
            # 创建备忘录
            memo_data = {
                "content": f"{content}_{i}"
            }
            
            create_response = client.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if create_response.status_code == 201:
                user_memo_ids.append(create_response.json()["id"])
            else:
                user_memo_ids.append(None)
        
        # 属性：每个用户只能看到自己的备忘录
        for i, token in enumerate(user_tokens):
            memos_response = client.get(
                "/api/v1/memos",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if memos_response.status_code == 200:
                user_memos = memos_response.json()["memos"]
                user_visible_ids = [m["id"] for m in user_memos]
                
                # 应该能看到自己的备忘录
                if user_memo_ids[i] is not None:
                    assert user_memo_ids[i] in user_visible_ids, f"用户{i}应该能看到自己的备忘录"
                
                # 不应该能看到其他用户的备忘录
                for j, other_memo_id in enumerate(user_memo_ids):
                    if i != j and other_memo_id is not None:
                        assert other_memo_id not in user_visible_ids, f"用户{i}不应该能看到用户{j}的备忘录"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_user_cannot_guess_other_user_ids_property(username1, username2, content):
    """
    Feature: text-archive-assistant, Property 30: 数据隔离
    Validates: Requirements 10.4
    
    属性：即使用户2知道用户1的资源ID，也不应该能访问
    """
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_id_guessing.db"
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
        # 清理用户名
        clean_username1 = ''.join(c for c in username1 if c.isalnum() or c in '_-')[:50] or "user1"
        clean_username2 = ''.join(c for c in username2 if c.isalnum() or c in '_-')[:50] or "user2"
        
        # 确保用户名不同
        if clean_username1 == clean_username2:
            clean_username2 = clean_username2 + "_2"
        
        password = "TestPass123!"
        
        # 注册用户1
        register_response1 = client.post("/api/v1/auth/register", json={
            "username": clean_username1,
            "email": f"{clean_username1}@test.com",
            "password": password
        })
        
        if register_response1.status_code != 201:
            login_response1 = client.post("/api/v1/auth/login", json={
                "username": clean_username1,
                "password": password
            })
            if login_response1.status_code != 200:
                assume(False)
        else:
            login_response1 = client.post("/api/v1/auth/login", json={
                "username": clean_username1,
                "password": password
            })
        
        token1 = login_response1.json()["access_token"]
        
        # 注册用户2
        register_response2 = client.post("/api/v1/auth/register", json={
            "username": clean_username2,
            "email": f"{clean_username2}@test.com",
            "password": password
        })
        
        if register_response2.status_code != 201:
            login_response2 = client.post("/api/v1/auth/login", json={
                "username": clean_username2,
                "password": password
            })
            if login_response2.status_code != 200:
                assume(False)
        else:
            login_response2 = client.post("/api/v1/auth/login", json={
                "username": clean_username2,
                "password": password
            })
        
        token2 = login_response2.json()["access_token"]
        
        # 用户1创建备忘录
        memo_data = {
            "content": content
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert create_response.status_code == 201, "用户1创建备忘录应该成功"
        memo_id = create_response.json()["id"]
        
        # 属性：即使用户2知道memo_id，也不应该能访问
        get_response = client.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert get_response.status_code == 404, "用户2即使知道ID也不应该能访问用户1的备忘录"
        
        # 属性：用户2也不应该能修改
        update_response = client.put(
            f"/api/v1/memos/{memo_id}",
            json={"content": "尝试修改"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert update_response.status_code == 404, "用户2即使知道ID也不应该能修改用户1的备忘录"
        
        # 属性：用户2也不应该能删除
        delete_response = client.delete(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert delete_response.status_code == 404, "用户2即使知道ID也不应该能删除用户1的备忘录"
        
        # 属性：用户1应该仍然能访问（确保数据没有被破坏）
        get_response_user1 = client.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert get_response_user1.status_code == 200, "用户1应该仍然能访问自己的备忘录"
        assert get_response_user1.json()["content"] == content, "备忘录内容应该未被修改"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
