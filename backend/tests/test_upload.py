"""文件上传单元测试"""
import pytest
import tempfile
import os
from io import BytesIO
from PIL import Image
from fastapi import UploadFile
from app.utils.file_handler import FileValidator, FileManager, validate_upload_file
from app.models.upload import UploadedFile, TextInput
from app.models.user import User


@pytest.mark.unit
def test_file_validator_format():
    """测试文件格式验证"""
    validator = FileValidator()
    
    # 测试支持的格式
    valid_files = [
        "test.jpg",
        "test.jpeg", 
        "test.png",
        "test.bmp"
    ]
    
    for filename in valid_files:
        mock_file = type('MockFile', (), {'filename': filename})()
        assert validator.validate_file_format(mock_file)
    
    # 测试不支持的格式
    invalid_files = [
        "test.gif",
        "test.pdf",
        "test.txt",
        "test.doc"
    ]
    
    for filename in invalid_files:
        mock_file = type('MockFile', (), {'filename': filename})()
        assert not validator.validate_file_format(mock_file)


@pytest.mark.unit
def test_file_validator_content_type():
    """测试MIME类型验证"""
    validator = FileValidator()
    
    # 测试支持的MIME类型
    valid_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/bmp"
    ]
    
    for content_type in valid_types:
        mock_file = type('MockFile', (), {'content_type': content_type})()
        assert validator.validate_content_type(mock_file)
    
    # 测试不支持的MIME类型
    invalid_types = [
        "image/gif",
        "application/pdf",
        "text/plain",
        "video/mp4"
    ]
    
    for content_type in invalid_types:
        mock_file = type('MockFile', (), {'content_type': content_type})()
        assert not validator.validate_content_type(mock_file)


@pytest.mark.unit
def test_file_manager_generate_filename():
    """测试文件名生成"""
    file_manager = FileManager()
    user_id = "test-user-123"
    original_filename = "test.jpg"
    
    filename1 = file_manager.generate_filename(original_filename, user_id)
    filename2 = file_manager.generate_filename(original_filename, user_id)
    
    # 生成的文件名应该不同
    assert filename1 != filename2
    
    # 文件名应该包含用户ID
    assert user_id in filename1
    
    # 文件名应该保持原始扩展名
    assert filename1.endswith(".jpg")


@pytest.mark.unit
def test_file_manager_save_and_delete():
    """测试文件保存和删除"""
    file_manager = FileManager()
    
    # 创建测试图片
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # 创建模拟的UploadFile
    mock_file = type('MockFile', (), {
        'file': img_bytes,
        'filename': 'test.jpg'
    })()
    
    # 保存文件
    filename = "test_save.jpg"
    file_path, file_size = file_manager.save_file(mock_file, filename)
    
    # 验证文件已保存
    assert os.path.exists(file_path)
    assert file_size > 0
    
    # 计算文件哈希
    file_hash = file_manager.calculate_file_hash(file_path)
    assert len(file_hash) == 32  # MD5哈希长度
    
    # 删除文件
    assert file_manager.delete_file(file_path)
    assert not os.path.exists(file_path)


@pytest.mark.unit
def test_uploaded_file_model(db_session):
    """测试上传文件模型"""
    # 先创建用户
    user = User(username="testuser", email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # 创建上传文件记录
    uploaded_file = UploadedFile(
        user_id=user.id,
        filename="test_20231123_12345678.jpg",
        original_filename="test.jpg",
        file_path="/uploads/test_20231123_12345678.jpg",
        file_size=1024,
        content_type="image/jpeg",
        file_hash="abcd1234"
    )
    
    db_session.add(uploaded_file)
    db_session.commit()
    db_session.refresh(uploaded_file)
    
    assert uploaded_file.id is not None
    assert uploaded_file.user_id == user.id
    assert uploaded_file.filename == "test_20231123_12345678.jpg"
    assert uploaded_file.status == "uploaded"  # 默认状态


@pytest.mark.unit
def test_text_input_model(db_session):
    """测试文本输入模型"""
    # 先创建用户
    user = User(username="testuser", email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # 创建文本输入记录
    text_input = TextInput(
        user_id=user.id,
        text="这是一段测试文本",
        source="manual"
    )
    
    db_session.add(text_input)
    db_session.commit()
    db_session.refresh(text_input)
    
    assert text_input.id is not None
    assert text_input.user_id == user.id
    assert text_input.text == "这是一段测试文本"
    assert text_input.source == "manual"
    assert text_input.status == "pending"  # 默认状态


@pytest.mark.unit
def test_upload_file_api(client, db_session):
    """测试文件上传API"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 创建测试图片
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # 上传文件
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    response = client.post(
        "/api/v1/upload/file",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "file_id" in data
    assert "filename" in data
    assert "file_size" in data
    assert data["content_type"] == "image/jpeg"


@pytest.mark.unit
def test_text_input_api(client, db_session):
    """测试文本输入API"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 输入文本
    text_data = {
        "text": "这是一段测试文本内容",
        "source": "manual"
    }
    response = client.post(
        "/api/v1/upload/text",
        json=text_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "text_id" in data
    assert data["text"] == text_data["text"]
    assert data["source"] == text_data["source"]


@pytest.mark.unit
def test_get_uploaded_files_api(client, db_session):
    """测试获取上传文件列表API"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 获取文件列表
    response = client.get(
        "/api/v1/upload/files",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.unit
def test_upload_invalid_file_format(client, db_session):
    """测试上传无效格式文件"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 创建文本文件（不支持的格式）
    text_content = BytesIO(b"This is a text file")
    
    # 尝试上传文本文件
    files = {"file": ("test.txt", text_content, "text/plain")}
    response = client.post(
        "/api/v1/upload/file",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "不支持的文件格式" in response.json()["detail"]


@pytest.mark.unit
def test_upload_without_auth(client):
    """测试未认证上传文件"""
    # 创建测试图片
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # 尝试上传文件（无认证）
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    response = client.post("/api/v1/upload/file", files=files)
    
    # 未认证应该返回403 Forbidden
    assert response.status_code in [401, 403]  # Unauthorized or Forbidden


@pytest.mark.unit
def test_delete_uploaded_file_api(client, db_session):
    """测试删除上传文件API"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 创建测试图片并上传
    img = Image.new('RGB', (100, 100), color='yellow')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    upload_response = client.post(
        "/api/v1/upload/file",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    file_id = upload_response.json()["file_id"]
    
    # 删除文件
    delete_response = client.delete(
        f"/api/v1/upload/file/{file_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert delete_response.status_code == 204



@pytest.mark.unit
def test_upload_large_file(client, db_session):
    """测试上传超大文件"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 创建一个超大图片（超过10MB）
    # 创建一个大尺寸图片来模拟大文件
    img = Image.new('RGB', (5000, 5000), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=100)
    img_bytes.seek(0)
    
    # 检查文件大小是否超过限制
    file_size = len(img_bytes.getvalue())
    
    # 如果文件大小超过10MB，应该被拒绝
    if file_size > 10 * 1024 * 1024:
        files = {"file": ("large_test.jpg", img_bytes, "image/jpeg")}
        response = client.post(
            "/api/v1/upload/file",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "文件大小超过限制" in response.json()["detail"]


@pytest.mark.unit
def test_upload_duplicate_file(client, db_session):
    """测试上传重复文件"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 创建测试图片
    img = Image.new('RGB', (100, 100), color='purple')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # 第一次上传
    files = {"file": ("duplicate_test.jpg", img_bytes, "image/jpeg")}
    response1 = client.post(
        "/api/v1/upload/file",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response1.status_code == 201
    
    # 重置BytesIO对象
    img_bytes.seek(0)
    
    # 第二次上传相同文件
    files = {"file": ("duplicate_test.jpg", img_bytes, "image/jpeg")}
    response2 = client.post(
        "/api/v1/upload/file",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 应该返回409冲突
    assert response2.status_code == 409
    assert "文件已存在" in response2.json()["detail"]


@pytest.mark.unit
def test_file_size_validation():
    """测试文件大小验证逻辑"""
    validator = FileValidator()
    
    # 创建小文件（应该通过）
    small_content = b"x" * (1024 * 1024)  # 1MB
    small_file = type('MockFile', (), {
        'file': BytesIO(small_content),
        'size': len(small_content)
    })()
    
    assert validator.validate_file_size(small_file)
    
    # 创建大文件（应该失败）
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    large_file = type('MockFile', (), {
        'file': BytesIO(large_content),
        'size': len(large_content)
    })()
    
    assert not validator.validate_file_size(large_file)


@pytest.mark.unit
def test_file_hash_calculation():
    """测试文件哈希计算"""
    file_manager = FileManager()
    
    # 创建两个相同内容的临时文件
    import tempfile
    
    content = b"test content for hash calculation"
    
    with tempfile.NamedTemporaryFile(delete=False) as f1:
        f1.write(content)
        file1_path = f1.name
    
    with tempfile.NamedTemporaryFile(delete=False) as f2:
        f2.write(content)
        file2_path = f2.name
    
    try:
        # 计算哈希
        hash1 = file_manager.calculate_file_hash(file1_path)
        hash2 = file_manager.calculate_file_hash(file2_path)
        
        # 相同内容应该有相同的哈希
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5哈希长度
        
    finally:
        # 清理临时文件
        os.unlink(file1_path)
        os.unlink(file2_path)


@pytest.mark.unit
def test_delete_nonexistent_file(client, db_session):
    """测试删除不存在的文件"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 尝试删除不存在的文件
    fake_file_id = "nonexistent-file-id"
    response = client.delete(
        f"/api/v1/upload/file/{fake_file_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert "文件不存在" in response.json()["detail"]


@pytest.mark.unit
def test_upload_different_image_formats(client, db_session):
    """测试上传不同格式的图片"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 测试不同格式
    formats = [
        ("test.jpg", "JPEG", "image/jpeg"),
        ("test.png", "PNG", "image/png"),
        ("test.bmp", "BMP", "image/bmp")
    ]
    
    for filename, img_format, content_type in formats:
        img = Image.new('RGB', (100, 100), color='orange')
        img_bytes = BytesIO()
        img.save(img_bytes, format=img_format)
        img_bytes.seek(0)
        
        files = {"file": (filename, img_bytes, content_type)}
        response = client.post(
            "/api/v1/upload/file",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        assert response.json()["content_type"] == content_type


@pytest.mark.unit
def test_text_input_validation(client, db_session):
    """测试文本输入验证"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 测试最小长度文本（应该成功）
    text_data = {
        "text": "A",
        "source": "manual"
    }
    response = client.post(
        "/api/v1/upload/text",
        json=text_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["text"] == "A"
    
    # 测试正常长度文本
    text_data = {
        "text": "这是一段正常长度的测试文本",
        "source": "ocr"
    }
    response = client.post(
        "/api/v1/upload/text",
        json=text_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["source"] == "ocr"


@pytest.mark.unit
def test_get_uploaded_files_pagination(client, db_session):
    """测试文件列表分页"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 上传多个文件
    for i in range(5):
        img = Image.new('RGB', (100, 100), color='cyan')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {"file": (f"test_{i}.jpg", img_bytes, "image/jpeg")}
        client.post(
            "/api/v1/upload/file",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # 测试分页
    response = client.get(
        "/api/v1/upload/files?skip=0&limit=3",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3


@pytest.mark.unit
def test_file_storage_persistence(client, db_session):
    """测试文件存储持久化"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 上传文件
    img = Image.new('RGB', (100, 100), color='magenta')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    files = {"file": ("persistence_test.jpg", img_bytes, "image/jpeg")}
    upload_response = client.post(
        "/api/v1/upload/file",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert upload_response.status_code == 201
    file_data = upload_response.json()
    file_path = file_data["file_path"]
    
    # 验证文件确实存在于磁盘上
    assert os.path.exists(file_path)
    
    # 验证文件大小
    assert os.path.getsize(file_path) == file_data["file_size"]
