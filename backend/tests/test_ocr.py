"""OCR服务单元测试"""
import pytest
import os
from io import BytesIO
from PIL import Image
from app.services.ocr_service import OCRService


@pytest.mark.unit
def test_ocr_service_initialization():
    """测试OCR服务初始化"""
    # 由于OCR初始化需要下载模型，这里只测试导入
    from app.services.ocr_service import get_ocr_service
    assert get_ocr_service is not None


@pytest.mark.unit
def test_ocr_validate_image_not_exists():
    """测试验证不存在的图片"""
    ocr_service = OCRService()
    is_valid, error = ocr_service.validate_image("nonexistent.jpg")
    assert not is_valid
    assert "不存在" in error


@pytest.mark.unit
def test_ocr_validate_image_too_small():
    """测试验证尺寸过小的图片"""
    ocr_service = OCRService()
    
    # 创建一个很小的测试图片
    img = Image.new('RGB', (5, 5), color='white')
    test_path = "test_small.jpg"
    img.save(test_path)
    
    try:
        is_valid, error = ocr_service.validate_image(test_path)
        assert not is_valid
        assert "过小" in error
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)


@pytest.mark.unit
def test_ocr_validate_valid_image():
    """测试验证有效图片"""
    ocr_service = OCRService()
    
    # 创建一个有效的测试图片
    img = Image.new('RGB', (100, 100), color='white')
    test_path = "test_valid.jpg"
    img.save(test_path)
    
    try:
        is_valid, error = ocr_service.validate_image(test_path)
        assert is_valid
        assert error is None
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)


@pytest.mark.unit
def test_ocr_recognize_nonexistent_file():
    """测试识别不存在的文件"""
    ocr_service = OCRService()
    result = ocr_service.recognize_text("nonexistent.jpg")
    
    assert not result["success"]
    assert result["text"] == ""
    assert "不存在" in result["error"]


@pytest.mark.unit
def test_ocr_api_recognize_without_auth(client):
    """测试未认证调用OCR API"""
    response = client.post(
        "/api/v1/ocr/recognize",
        json={"file_id": "test-file-id"}
    )
    
    # 未认证应该返回401或403
    assert response.status_code in [401, 403]


@pytest.mark.unit
def test_ocr_api_recognize_file_not_found(client, db_session):
    """测试识别不存在的文件"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 尝试识别不存在的文件
    response = client.post(
        "/api/v1/ocr/recognize",
        json={"file_id": "nonexistent-file-id"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


@pytest.mark.unit
def test_ocr_api_edit_result(client, db_session):
    """测试编辑OCR结果API"""
    # 先注册用户并获取token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    token = register_response.json()["access_token"]
    
    # 尝试编辑不存在的文件
    response = client.post(
        "/api/v1/ocr/edit",
        json={
            "file_id": "nonexistent-file-id",
            "edited_text": "编辑后的文本"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
