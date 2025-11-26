"""备忘录排序和筛选属性测试"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime
import time


# ============================================================================
# Property 15: 备忘录时间倒序测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=20, deadline=5000)
@given(
    st.lists(
        st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
        min_size=2,
        max_size=5
    )
)
def test_memo_time_descending_property(content_list):
    """
    Feature: text-archive-assistant, Property 15: 备忘录时间倒序
    Validates: Requirements 5.3
    
    对于任意备忘录列表，前端客户端应该按创建时间倒序（最新的在前）显示
    
    属性：查询返回的备忘录列表应该按创建时间降序排列
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_memo_sorting.db"
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
        username = f"memosortuser_{uuid.uuid4().hex[:8]}"
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
        
        # 创建多个备忘录（按顺序创建，确保时间戳不同）
        created_memos = []
        for i, content in enumerate(content_list):
            memo_data = {
                "content": content,
                "summary": f"Summary {i}",
                "tags": [f"tag{i}"]
            }
            
            create_response = client.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if create_response.status_code == 201:
                created_memos.append(create_response.json())
                # 添加小延迟确保时间戳不同
                time.sleep(0.05)
        
        # 查询备忘录列表
        list_response = client.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        memo_list = list_response.json()["memos"]
        
        # 属性1：列表应该按创建时间降序排列（最新的在前）
        # 注意：如果两个备忘录的创建时间完全相同，它们之间的顺序是未定义的
        for i in range(len(memo_list) - 1):
            current = memo_list[i]
            next_item = memo_list[i + 1]
            
            # 解析创建时间
            current_time = datetime.fromisoformat(current["created_at"].replace('Z', '+00:00'))
            next_time = datetime.fromisoformat(next_item["created_at"].replace('Z', '+00:00'))
            
            # 使用 >= 因为相同时间戳的顺序是未定义的
            assert current_time >= next_time, \
                f"备忘录应该按创建时间降序排列: {current_time} 应该 >= {next_time}"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=20, deadline=5000)
@given(
    st.integers(min_value=3, max_value=5)
)
def test_memo_descending_order_consistency_property(num_memos):
    """
    Feature: text-archive-assistant, Property 15: 备忘录时间倒序
    Validates: Requirements 5.3
    
    属性：多次查询应该返回一致的降序排列
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_memo_consistency.db"
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
        username = f"memoconsistuser_{uuid.uuid4().hex[:8]}"
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
        
        # 创建多个备忘录
        for i in range(num_memos):
            memo_data = {
                "content": f"Memo content {i}",
                "summary": f"Summary {i}",
                "tags": [f"tag{i}"]
            }
            
            client.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            time.sleep(0.05)
        
        # 多次查询
        list_response_1 = client.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        list_response_2 = client.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response_1.status_code == 200, "第一次查询应该成功"
        assert list_response_2.status_code == 200, "第二次查询应该成功"
        
        memo_list_1 = list_response_1.json()["memos"]
        memo_list_2 = list_response_2.json()["memos"]
        
        # 属性：两次查询的顺序应该一致
        assert len(memo_list_1) == len(memo_list_2), "两次查询的数量应该一致"
        
        for i in range(len(memo_list_1)):
            assert memo_list_1[i]["id"] == memo_list_2[i]["id"], \
                f"两次查询的顺序应该一致: 位置{i}的备忘录ID应该相同"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=20, deadline=5000)
@given(
    st.lists(
        st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
        min_size=1,
        max_size=3
    )
)
def test_newest_memo_appears_first_property(content_list):
    """
    Feature: text-archive-assistant, Property 15: 备忘录时间倒序
    Validates: Requirements 5.3
    
    属性：最后创建的备忘录应该出现在列表的第一位
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_newest_first.db"
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
        username = f"newestfirstuser_{uuid.uuid4().hex[:8]}"
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
        
        # 创建多个备忘录
        last_memo_id = None
        for i, content in enumerate(content_list):
            memo_data = {
                "content": content,
                "summary": f"Summary {i}"
            }
            
            create_response = client.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if create_response.status_code == 201:
                last_memo_id = create_response.json()["id"]
                time.sleep(1.0)  # 确保时间戳不同（SQLite datetime精度为秒）
        
        # 查询备忘录列表
        list_response = client.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        memo_list = list_response.json()["memos"]
        
        # 属性：最后创建的备忘录应该在列表第一位（如果时间戳不同）
        assert len(memo_list) > 0, "列表不应该为空"
        
        # 检查最后创建的备忘录的时间戳
        last_memo_time = None
        for memo in memo_list:
            if memo["id"] == last_memo_id:
                last_memo_time = datetime.fromisoformat(memo["created_at"].replace('Z', '+00:00'))
                break
        
        # 如果最后创建的备忘录的时间戳是最新的，它应该在第一位
        first_memo_time = datetime.fromisoformat(memo_list[0]["created_at"].replace('Z', '+00:00'))
        if last_memo_time and last_memo_time > first_memo_time:
            assert memo_list[0]["id"] == last_memo_id, \
                "时间戳最新的备忘录应该出现在列表第一位"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


# ============================================================================
# Property 17: 标签筛选测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=20, deadline=5000)
@given(
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
            st.lists(
                st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))).filter(lambda x: x.strip()),
                min_size=1,
                max_size=3
            )
        ),
        min_size=3,
        max_size=5
    )
)
def test_tag_filtering_property(memo_data_list):
    """
    Feature: text-archive-assistant, Property 17: 标签筛选
    Validates: Requirements 5.5
    
    对于任意标签筛选查询，系统应该只返回包含指定标签的备忘录
    
    属性：筛选结果中的所有备忘录都应该包含指定的标签
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_tag_filtering.db"
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
        username = f"tagfilteruser_{uuid.uuid4().hex[:8]}"
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
        
        # 创建多个备忘录（带有不同的标签）
        created_memos = []
        all_tags = set()
        for content, tags in memo_data_list:
            memo_data = {
                "content": content,
                "tags": tags
            }
            
            create_response = client.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if create_response.status_code == 201:
                created_memos.append((create_response.json(), tags))
                all_tags.update(tags)
        
        # 如果没有创建成功的备忘录，跳过测试
        if not created_memos or not all_tags:
            assume(False)
        
        # 选择一个标签进行筛选
        filter_tag = list(all_tags)[0]
        
        # 查询带有指定标签的备忘录
        list_response = client.get(
            f"/api/v1/memos?tags={filter_tag}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        filtered_memos = list_response.json()["memos"]
        
        # 属性1：所有返回的备忘录都应该包含指定的标签
        for memo in filtered_memos:
            assert filter_tag in memo["tags"], \
                f"筛选结果中的备忘录应该包含标签 {filter_tag}"
        
        # 属性2：所有包含该标签的备忘录都应该被返回
        expected_memo_ids = [memo["id"] for memo, tags in created_memos if filter_tag in tags]
        returned_memo_ids = [memo["id"] for memo in filtered_memos]
        
        for expected_id in expected_memo_ids:
            assert expected_id in returned_memo_ids, \
                f"包含标签 {filter_tag} 的备忘录不应该被遗漏"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=20, deadline=5000)
@given(
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
            st.lists(
                st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))).filter(lambda x: x.strip()),
                min_size=1,
                max_size=3
            )
        ),
        min_size=3,
        max_size=5
    ),
    st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))).filter(lambda x: x.strip()),
        min_size=2,
        max_size=3
    )
)
def test_multiple_tag_filtering_property(memo_data_list, filter_tags):
    """
    Feature: text-archive-assistant, Property 17: 标签筛选
    Validates: Requirements 5.5
    
    属性：使用多个标签筛选时，应该返回包含任意一个标签的备忘录
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_multiple_tag_filtering.db"
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
        username = f"multitaguser_{uuid.uuid4().hex[:8]}"
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
        
        # 创建多个备忘录
        created_memos = []
        for content, tags in memo_data_list:
            memo_data = {
                "content": content,
                "tags": tags
            }
            
            create_response = client.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if create_response.status_code == 201:
                created_memos.append((create_response.json(), tags))
        
        if not created_memos:
            assume(False)
        
        # 使用多个标签进行筛选
        filter_tags_str = ','.join(filter_tags)
        
        list_response = client.get(
            f"/api/v1/memos?tags={filter_tags_str}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        filtered_memos = list_response.json()["memos"]
        
        # 属性：所有返回的备忘录都应该至少包含一个筛选标签
        for memo in filtered_memos:
            has_matching_tag = any(tag in memo["tags"] for tag in filter_tags)
            assert has_matching_tag, \
                f"筛选结果中的备忘录应该至少包含一个筛选标签: {filter_tags}"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=20, deadline=5000)
@given(
    st.lists(
        st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
        min_size=3,
        max_size=5
    )
)
def test_no_tag_filter_returns_all_property(content_list):
    """
    Feature: text-archive-assistant, Property 17: 标签筛选
    Validates: Requirements 5.5
    
    属性：不指定标签筛选时，应该返回所有备忘录
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_no_tag_filter.db"
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
        username = f"notagfilteruser_{uuid.uuid4().hex[:8]}"
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
        
        # 创建多个备忘录（带有不同的标签）
        created_count = 0
        for i, content in enumerate(content_list):
            memo_data = {
                "content": content,
                "tags": [f"tag{i}"]
            }
            
            create_response = client.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if create_response.status_code == 201:
                created_count += 1
        
        # 查询所有备忘录（不指定标签筛选）
        list_response = client.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        memo_list = list_response.json()["memos"]
        
        # 属性：返回的备忘录数量应该等于创建的数量
        assert len(memo_list) == created_count, \
            f"不指定标签筛选时应该返回所有备忘录: 期望 {created_count}, 实际 {len(memo_list)}"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=20, deadline=5000)
@given(
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
            st.lists(
                st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))).filter(lambda x: x.strip()),
                min_size=1,
                max_size=3
            )
        ),
        min_size=3,
        max_size=5
    ),
    st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))).filter(lambda x: x.strip())
)
def test_nonexistent_tag_returns_empty_property(memo_data_list, nonexistent_tag):
    """
    Feature: text-archive-assistant, Property 17: 标签筛选
    Validates: Requirements 5.5
    
    属性：使用不存在的标签筛选时，应该返回空列表
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_nonexistent_tag.db"
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
        username = f"nonexisttaguser_{uuid.uuid4().hex[:8]}"
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
        
        # 创建多个备忘录
        all_tags = set()
        for content, tags in memo_data_list:
            memo_data = {
                "content": content,
                "tags": tags
            }
            
            create_response = client.post(
                "/api/v1/memos",
                json=memo_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if create_response.status_code == 201:
                all_tags.update(tags)
        
        # 确保nonexistent_tag不在任何备忘录的标签中
        if nonexistent_tag in all_tags:
            assume(False)
        
        # 使用不存在的标签进行筛选
        list_response = client.get(
            f"/api/v1/memos?tags={nonexistent_tag}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询应该成功"
        filtered_memos = list_response.json()["memos"]
        
        # 属性：应该返回空列表
        assert len(filtered_memos) == 0, \
            f"使用不存在的标签筛选应该返回空列表"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
