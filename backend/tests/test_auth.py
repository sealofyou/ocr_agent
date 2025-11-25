"""用户认证单元测试"""
import pytest
from app.utils.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.models.user import User


@pytest.mark.unit
def test_password_hashing():
    """测试密码加密"""
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    # 加密后的密码不应该等于原密码
    assert hashed != password
    # 应该能够验证密码
    assert verify_password(password, hashed)
    # 错误的密码不应该通过验证
    assert not verify_password("WrongPassword", hashed)


@pytest.mark.unit
def test_create_and_decode_token():
    """测试JWT令牌创建和解码"""
    user_id = "test-user-id-123"
    token = create_access_token(data={"sub": user_id})
    
    # 令牌应该是字符串
    assert isinstance(token, str)
    assert len(token) > 0
    
    # 解码令牌
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id


@pytest.mark.unit
def test_decode_invalid_token():
    """测试解码无效令牌"""
    invalid_token = "invalid.token.here"
    payload = decode_access_token(invalid_token)
    
    # 无效令牌应该返回None
    assert payload is None


@pytest.mark.unit
def test_user_registration(client, db_session):
    """测试用户注册API"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "user_id" in data
    assert data["token_type"] == "bearer"
    
    # 验证用户已创建
    user = db_session.query(User).filter(User.username == user_data["username"]).first()
    assert user is not None
    assert user.email == user_data["email"]
    # 密码应该被加密
    assert user.password_hash != user_data["password"]


@pytest.mark.unit
def test_duplicate_username_registration(client, db_session):
    """测试重复用户名注册"""
    user_data = {
        "username": "testuser",
        "email": "test1@example.com",
        "password": "TestPassword123!"
    }
    
    # 第一次注册
    response1 = client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # 第二次注册相同用户名
    user_data2 = {
        "username": "testuser",
        "email": "test2@example.com",
        "password": "TestPassword456!"
    }
    response2 = client.post("/api/v1/auth/register", json=user_data2)
    assert response2.status_code == 400
    assert "用户名已存在" in response2.json()["detail"]


@pytest.mark.unit
def test_duplicate_email_registration(client, db_session):
    """测试重复邮箱注册"""
    user_data = {
        "username": "testuser1",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    # 第一次注册
    response1 = client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # 第二次注册相同邮箱
    user_data2 = {
        "username": "testuser2",
        "email": "test@example.com",
        "password": "TestPassword456!"
    }
    response2 = client.post("/api/v1/auth/register", json=user_data2)
    assert response2.status_code == 400
    assert "邮箱已被注册" in response2.json()["detail"]


@pytest.mark.unit
def test_user_login(client, db_session):
    """测试用户登录API"""
    # 先注册用户
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    client.post("/api/v1/auth/register", json=register_data)
    
    # 登录
    login_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user_id" in data
    assert data["token_type"] == "bearer"


@pytest.mark.unit
def test_login_with_wrong_password(client, db_session):
    """测试错误密码登录"""
    # 先注册用户
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    client.post("/api/v1/auth/register", json=register_data)
    
    # 使用错误密码登录
    login_data = {
        "username": "testuser",
        "password": "WrongPassword!"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"]


@pytest.mark.unit
def test_login_with_nonexistent_user(client):
    """测试不存在的用户登录"""
    login_data = {
        "username": "nonexistent",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"]


@pytest.mark.unit
def test_get_current_user(client, db_session):
    """测试获取当前用户信息"""
    # 先注册用户
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 使用令牌获取用户信息
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.unit
def test_get_current_user_without_token(client):
    """测试未认证访问"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 403  # Forbidden without credentials


@pytest.mark.unit
def test_get_current_user_with_invalid_token(client):
    """测试使用无效令牌访问"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    
    assert response.status_code == 401
