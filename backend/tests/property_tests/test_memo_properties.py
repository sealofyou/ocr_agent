"""备忘录管理属性测试"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from app.services.classification_service import ClassificationService


# ============================================================================
# Property 14: 备忘录信息提取测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_memo_info_extraction_property(text):
    """
    Feature: text-archive-assistant, Property 14: 备忘录信息提取
    Validates: Requirements 5.1
    
    对于任意被分类为备忘录的文本，后端服务应该提取创建时间和内容摘要
    
    属性：提取的备忘录信息应该包含所有必需字段
    """
    service = ClassificationService()
    
    # 提取备忘录信息
    info = service.extract_memo_info(text)
    
    # 属性1：必须包含所有必需字段
    required_fields = ["content", "summary", "tags"]
    for field in required_fields:
        assert field in info, f"备忘录信息必须包含 {field} 字段"
    
    # 属性2：content应该等于原始文本
    assert info["content"] == text, "content应该等于原始文本"
    
    # 属性3：summary不应该为空
    assert info["summary"] is not None, "summary不应该为None"
    assert isinstance(info["summary"], str), "summary应该是字符串类型"
    assert len(info["summary"]) > 0, "summary不应该为空字符串"
    
    # 属性4：tags应该是列表
    assert isinstance(info["tags"], list), "tags应该是列表类型"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_memo_extraction_always_returns_structure_property(text):
    """
    Feature: text-archive-assistant, Property 14: 备忘录信息提取
    Validates: Requirements 5.1
    
    属性：对于任意文本，备忘录信息提取应该总是返回完整的数据结构
    """
    service = ClassificationService()
    
    # 提取备忘录信息
    info = service.extract_memo_info(text)
    
    # 属性：必须返回字典
    assert isinstance(info, dict), "提取结果应该是字典类型"
    
    # 属性：必须包含所有必需字段
    required_fields = ["content", "summary", "tags"]
    for field in required_fields:
        assert field in info, f"备忘录信息必须包含 {field} 字段"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_summary_generation_short_text_property(text):
    """
    Feature: text-archive-assistant, Property 14: 备忘录信息提取
    Validates: Requirements 5.1
    
    属性：短文本的摘要应该等于原文本
    """
    service = ClassificationService()
    
    # 生成摘要
    summary = service._generate_summary(text, max_length=100)
    
    # 属性：短文本的摘要应该等于原文本
    if len(text) <= 100:
        assert summary == text, "短文本的摘要应该等于原文本"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=101, max_size=500, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_summary_generation_long_text_property(text):
    """
    Feature: text-archive-assistant, Property 14: 备忘录信息提取
    Validates: Requirements 5.1
    
    属性：长文本的摘要应该被截断并添加省略号
    """
    service = ClassificationService()
    
    # 生成摘要
    summary = service._generate_summary(text, max_length=100)
    
    # 属性：长文本的摘要应该被截断
    assert len(summary) <= 103, "摘要长度不应超过100+3（省略号）"
    assert summary.endswith("..."), "长文本的摘要应该以省略号结尾"
    assert summary.startswith(text[:100]), "摘要应该以原文本的前100个字符开始"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_content_preservation_property(text):
    """
    Feature: text-archive-assistant, Property 14: 备忘录信息提取
    Validates: Requirements 5.1
    
    属性：提取的content字段应该完整保留原始文本
    """
    service = ClassificationService()
    
    # 提取备忘录信息
    info = service.extract_memo_info(text)
    
    # 属性：content应该完全等于原始文本
    assert info["content"] == text, "content应该完整保留原始文本"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_extraction_consistency_property(text):
    """
    Feature: text-archive-assistant, Property 14: 备忘录信息提取
    Validates: Requirements 5.1
    
    属性：对同一文本的多次提取应该返回相同的结果
    """
    service = ClassificationService()
    
    # 多次提取
    info1 = service.extract_memo_info(text)
    info2 = service.extract_memo_info(text)
    info3 = service.extract_memo_info(text)
    
    # 属性：结果应该一致
    assert info1["content"] == info2["content"] == info3["content"], "content提取应该一致"
    assert info1["summary"] == info2["summary"] == info3["summary"], "summary提取应该一致"
    assert info1["tags"] == info2["tags"] == info3["tags"], "tags提取应该一致"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
def test_extraction_determinism_property(text):
    """
    Feature: text-archive-assistant, Property 14: 备忘录信息提取
    Validates: Requirements 5.1
    
    属性：提取算法应该是确定性的（相同输入产生相同输出）
    """
    service1 = ClassificationService()
    service2 = ClassificationService()
    
    # 使用不同实例提取
    info1 = service1.extract_memo_info(text)
    info2 = service2.extract_memo_info(text)
    
    # 属性：不同实例的提取结果应该一致
    assert info1["content"] == info2["content"], "不同实例的content提取应该一致"
    assert info1["summary"] == info2["summary"], "不同实例的summary提取应该一致"
    assert info1["tags"] == info2["tags"], "不同实例的tags提取应该一致"


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
    Feature: text-archive-assistant, Property 14: 备忘录信息提取
    Validates: Requirements 5.1
    
    属性：批量提取应该为每个文本返回独立的结果
    """
    service = ClassificationService()
    
    results = []
    for text in text_list:
        info = service.extract_memo_info(text)
        results.append(info)
    
    # 属性：每个文本都应该有有效的提取结果
    assert len(results) == len(text_list), "结果数量应该与输入文本数量一致"
    
    for i, info in enumerate(results):
        # 验证每个结果都包含必需字段
        required_fields = ["content", "summary", "tags"]
        for field in required_fields:
            assert field in info, f"第{i}个文本的提取结果必须包含 {field} 字段"
        
        # 验证content与原文本一致
        assert info["content"] == text_list[i], f"第{i}个文本的content应该与原文本一致"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.integers(min_value=10, max_value=200)
)
def test_summary_max_length_property(text, max_length):
    """
    Feature: text-archive-assistant, Property 14: 备忘录信息提取
    Validates: Requirements 5.1
    
    属性：摘要长度应该不超过指定的最大长度
    """
    service = ClassificationService()
    
    # 生成摘要
    summary = service._generate_summary(text, max_length=max_length)
    
    # 属性：摘要长度不应超过max_length + 3（省略号）
    assert len(summary) <= max_length + 3, f"摘要长度不应超过{max_length + 3}"
    
    # 属性：如果原文本长度小于等于max_length，摘要应该等于原文本
    if len(text) <= max_length:
        assert summary == text, "短文本的摘要应该等于原文本"
    else:
        assert summary.endswith("..."), "长文本的摘要应该以省略号结尾"



# ============================================================================
# Property 16: 备忘录标签保存测试
# ============================================================================


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))), min_size=1, max_size=5)
)
def test_memo_tags_storage_property(username, email, content, tags):
    """
    Feature: text-archive-assistant, Property 16: 备忘录标签保存
    Validates: Requirements 5.4
    
    对于任意带有标签的备忘录，系统应该正确保存这些标签，且查询时能返回
    
    属性：创建的备忘录标签应该能够完整存储和检索
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_memo_tags.db"
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
            login_response = client.post("/api/v1/auth/login", json={
                "username": clean_username,
                "password": password
            })
            if login_response.status_code != 200:
                assume(False)
        else:
            login_response = client.post("/api/v1/auth/login", json={
                "username": clean_username,
                "password": password
            })
        
        token = login_response.json()["token"]
        
        # 创建备忘录
        memo_data = {
            "content": content,
            "tags": tags
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert create_response.status_code == 201, f"创建备忘录失败: {create_response.json()}"
        created_memo = create_response.json()
        memo_id = created_memo["id"]
        
        # 属性1：创建响应应该包含标签
        assert "tags" in created_memo, "创建响应应该包含tags字段"
        
        # 属性2：所有标签都应该被保存
        for tag in tags:
            assert tag in created_memo["tags"], f"标签 {tag} 应该被保存"
        
        # 属性3：查询单个备忘录应该返回标签
        get_response = client.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_response.status_code == 200, "查询备忘录应该成功"
        retrieved_memo = get_response.json()
        
        # 属性4：检索的标签应该与创建的标签一致
        for tag in tags:
            assert tag in retrieved_memo["tags"], f"检索时标签 {tag} 应该存在"
        
        # 属性5：查询列表应该包含创建的备忘录及其标签
        list_response = client.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert list_response.status_code == 200, "查询列表应该成功"
        memo_list = list_response.json()
        
        # 在列表中查找创建的备忘录
        found = False
        for memo in memo_list["memos"]:
            if memo["id"] == memo_id:
                found = True
                # 验证列表中的标签也是完整的
                for tag in tags:
                    assert tag in memo["tags"], f"列表中标签 {tag} 应该存在"
                break
        
        assert found, "创建的备忘录应该出现在列表中"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()



@pytest.mark.property
@settings(max_examples=50)
@given(
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))), min_size=1, max_size=3)
)
def test_memo_tag_filtering_property(content, tags):
    """
    Feature: text-archive-assistant, Property 16: 备忘录标签保存
    Validates: Requirements 5.4
    
    属性：按标签筛选应该只返回包含指定标签的备忘录
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
        username = "tagfilteruser"
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
        
        # 创建备忘录
        memo_data = {
            "content": content,
            "tags": tags
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert create_response.status_code == 201, "创建备忘录应该成功"
        memo_id = create_response.json()["id"]
        
        # 使用第一个标签进行筛选
        filter_tag = tags[0]
        filter_response = client.get(
            f"/api/v1/memos?tags={filter_tag}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert filter_response.status_code == 200, "标签筛选应该成功"
        filtered_memos = filter_response.json()
        
        # 属性：筛选结果应该包含创建的备忘录
        found = False
        for memo in filtered_memos["memos"]:
            if memo["id"] == memo_id:
                found = True
                # 验证备忘录包含筛选标签
                assert filter_tag in memo["tags"], f"筛选结果应该包含标签 {filter_tag}"
                break
        
        assert found, "使用备忘录的标签筛选应该能找到该备忘录"
        
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
    st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))), min_size=1, max_size=3)
)
def test_memo_tag_update_property(content, original_tags, new_tags):
    """
    Feature: text-archive-assistant, Property 16: 备忘录标签保存
    Validates: Requirements 5.4
    
    属性：更新备忘录标签后，新标签应该正确保存
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_tag_update.db"
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
        username = "tagupdateuser"
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
        
        # 创建备忘录
        memo_data = {
            "content": content,
            "tags": original_tags
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert create_response.status_code == 201, "创建备忘录应该成功"
        memo_id = create_response.json()["id"]
        
        # 更新标签
        update_data = {
            "tags": new_tags
        }
        
        update_response = client.put(
            f"/api/v1/memos/{memo_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert update_response.status_code == 200, "更新备忘录应该成功"
        updated_memo = update_response.json()
        
        # 属性：更新后的标签应该是新标签
        for tag in new_tags:
            assert tag in updated_memo["tags"], f"更新后应该包含新标签 {tag}"
        
        # 属性：查询应该返回更新后的标签
        get_response = client.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_response.status_code == 200, "查询应该成功"
        retrieved_memo = get_response.json()
        
        for tag in new_tags:
            assert tag in retrieved_memo["tags"], f"检索时应该包含新标签 {tag}"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))), min_size=0, max_size=0)
)
def test_memo_without_tags_property(content, empty_tags):
    """
    Feature: text-archive-assistant, Property 16: 备忘录标签保存
    Validates: Requirements 5.4
    
    属性：没有标签的备忘录应该正确保存（tags为空或None）
    """
    from fastapi.testclient import TestClient
    from main import app
    from app.db.base import Base, get_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite:///./test_no_tags.db"
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
        username = "notagsuser"
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
        
        # 创建没有标签的备忘录
        memo_data = {
            "content": content
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert create_response.status_code == 201, "创建备忘录应该成功"
        created_memo = create_response.json()
        memo_id = created_memo["id"]
        
        # 属性：tags字段应该存在且为空或None
        assert "tags" in created_memo, "应该包含tags字段"
        assert created_memo["tags"] is None or created_memo["tags"] == "", "没有标签时tags应该为None或空字符串"
        
        # 属性：查询应该返回相同的结果
        get_response = client.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_response.status_code == 200, "查询应该成功"
        retrieved_memo = get_response.json()
        
        assert retrieved_memo["tags"] is None or retrieved_memo["tags"] == "", "检索时tags应该为None或空字符串"
        
    finally:
        # 清理
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
