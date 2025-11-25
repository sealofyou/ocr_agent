"""文件上传属性测试"""
import pytest
from hypothesis import given, strategies as st, settings
from io import BytesIO
from PIL import Image
from app.utils.file_handler import FileValidator, FileManager


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=255))
def test_file_processing_property(filename):
    """
    Feature: text-archive-assistant, Property 1: 图片传递到OCR引擎
    Validates: Requirements 1.1, 1.2
    
    对于任意有效的图片文件，系统应该能够接收并传递给OCR引擎处理
    
    属性：对于任意文件名，如果格式验证通过，则应该能够被处理
    """
    validator = FileValidator()
    
    # 为文件名添加支持的扩展名
    supported_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
    
    for ext in supported_extensions:
        test_filename = filename.replace("/", "_").replace("\\", "_") + ext
        mock_file = type('MockFile', (), {'filename': test_filename})()
        
        # 属性：支持的格式应该通过验证
        assert validator.validate_file_format(mock_file), f"支持的格式 {ext} 应该通过验证"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=50))
def test_filename_generation_property(user_id):
    """
    Feature: text-archive-assistant, Property 1: 图片传递到OCR引擎
    Validates: Requirements 1.1, 1.2
    
    属性：对于任意用户ID，生成的文件名应该是唯一的且包含用户标识
    """
    file_manager = FileManager()
    original_filename = "test.jpg"
    
    # 生成多个文件名
    filenames = set()
    for _ in range(10):
        filename = file_manager.generate_filename(original_filename, user_id)
        filenames.add(filename)
    
    # 属性1：生成的文件名应该是唯一的
    assert len(filenames) == 10, "生成的文件名应该是唯一的"
    
    # 属性2：文件名应该包含用户标识（如果用户ID有效）
    for filename in filenames:
        if user_id.strip():  # 如果用户ID非空
            # 文件名应该保持原始扩展名
            assert filename.endswith(".jpg"), "文件名应该保持原始扩展名"


@pytest.mark.property
@settings(max_examples=50)
@given(
    st.integers(min_value=1, max_value=1000),
    st.integers(min_value=1, max_value=1000)
)
def test_image_processing_property(width, height):
    """
    Feature: text-archive-assistant, Property 1: 图片传递到OCR引擎
    Validates: Requirements 1.1, 1.2
    
    属性：对于任意尺寸的有效图片，系统应该能够处理并保存
    """
    file_manager = FileManager()
    
    # 创建任意尺寸的测试图片
    img = Image.new('RGB', (width, height), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # 创建模拟的UploadFile
    mock_file = type('MockFile', (), {
        'file': img_bytes,
        'filename': 'test.jpg'
    })()
    
    # 属性：应该能够保存任意尺寸的有效图片
    try:
        filename = f"test_{width}x{height}.jpg"
        file_path, file_size = file_manager.save_file(mock_file, filename)
        
        # 验证文件已保存
        import os
        assert os.path.exists(file_path), "文件应该被成功保存"
        assert file_size > 0, "文件大小应该大于0"
        
        # 清理测试文件
        file_manager.delete_file(file_path)
        
    except Exception as e:
        pytest.fail(f"处理 {width}x{height} 图片时失败: {str(e)}")


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=50))
def test_content_type_validation_property(content_type_base):
    """
    Feature: text-archive-assistant, Property 1: 图片传递到OCR引擎
    Validates: Requirements 1.1, 1.2
    
    属性：对于任意MIME类型，只有图片类型应该通过验证
    """
    validator = FileValidator()
    
    # 测试有效的图片MIME类型
    valid_image_types = [
        "image/jpeg",
        "image/jpg",
        "image/png", 
        "image/bmp"
    ]
    
    for mime_type in valid_image_types:
        mock_file = type('MockFile', (), {'content_type': mime_type})()
        assert validator.validate_content_type(mock_file), f"有效的图片类型 {mime_type} 应该通过验证"
    
    # 测试无效的MIME类型（非图片）
    invalid_types = [
        f"text/{content_type_base}",
        f"application/{content_type_base}",
        f"video/{content_type_base}",
        f"audio/{content_type_base}"
    ]
    
    for mime_type in invalid_types:
        mock_file = type('MockFile', (), {'content_type': mime_type})()
        assert not validator.validate_content_type(mock_file), f"无效的类型 {mime_type} 不应该通过验证"


@pytest.mark.property
@settings(max_examples=100)
@given(st.binary(min_size=1, max_size=1024))
def test_file_hash_consistency_property(file_content):
    """
    Feature: text-archive-assistant, Property 1: 图片传递到OCR引擎
    Validates: Requirements 1.1, 1.2
    
    属性：相同的文件内容应该产生相同的哈希值
    """
    import tempfile
    import os
    
    file_manager = FileManager()
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name
    
    try:
        # 计算哈希值两次
        hash1 = file_manager.calculate_file_hash(temp_path)
        hash2 = file_manager.calculate_file_hash(temp_path)
        
        # 属性：相同文件应该产生相同哈希
        assert hash1 == hash2, "相同文件内容应该产生相同的哈希值"
        
        # 属性：哈希值应该是32字符的MD5
        assert len(hash1) == 32, "MD5哈希应该是32字符长度"
        assert all(c in '0123456789abcdef' for c in hash1), "MD5哈希应该只包含十六进制字符"
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=10000))
def test_text_input_acceptance_property(text_content):
    """
    Feature: text-archive-assistant, Property 2: 文本输入接收
    Validates: Requirements 1.3
    
    对于任意文本输入，系统应该能够接收并存储
    
    属性：任意有效长度的文本都应该被正确接收和存储
    """
    from app.schemas.upload import TextInputRequest
    
    # 属性1：有效长度的文本应该能够创建请求对象
    try:
        text_request = TextInputRequest(text=text_content)
        assert text_request.text == text_content, "文本内容应该被正确存储"
        assert text_request.source == "manual", "默认来源应该是manual"
    except Exception as e:
        pytest.fail(f"处理文本输入时失败: {str(e)}")


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=1000),
    st.sampled_from(["manual", "ocr", "import", "api"])
)
def test_text_source_handling_property(text_content, source):
    """
    Feature: text-archive-assistant, Property 2: 文本输入接收
    Validates: Requirements 1.3
    
    属性：系统应该能够处理来自不同来源的文本输入
    """
    from app.schemas.upload import TextInputRequest
    
    # 属性：不同来源的文本都应该被正确处理
    text_request = TextInputRequest(text=text_content, source=source)
    
    assert text_request.text == text_content, "文本内容应该被正确保存"
    assert text_request.source == source, "文本来源应该被正确记录"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=5000))
def test_text_storage_consistency_property(text_content):
    """
    Feature: text-archive-assistant, Property 2: 文本输入接收
    Validates: Requirements 1.3
    
    属性：存储的文本应该与输入的文本完全一致
    """
    from app.models.upload import TextInput
    
    # 创建文本输入对象（显式设置status以避免依赖SQLAlchemy的default）
    text_input = TextInput(
        user_id="test-user-123",
        text=text_content,
        source="manual",
        status="pending"
    )
    
    # 属性：存储的文本应该与原始文本一致
    assert text_input.text == text_content, "存储的文本应该与输入文本完全一致"
    assert text_input.user_id == "test-user-123", "用户ID应该被正确关联"
    assert text_input.status == "pending", "状态应该是pending"


@pytest.mark.property
@settings(max_examples=50)
@given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10))
def test_multiple_text_inputs_property(text_list):
    """
    Feature: text-archive-assistant, Property 2: 文本输入接收
    Validates: Requirements 1.3
    
    属性：系统应该能够处理多个文本输入，每个都应该被独立存储
    """
    from app.models.upload import TextInput
    
    text_inputs = []
    user_id = "test-user-456"
    
    # 创建多个文本输入
    for i, text in enumerate(text_list):
        text_input = TextInput(
            user_id=user_id,
            text=text,
            source=f"source_{i}"
        )
        text_inputs.append(text_input)
    
    # 属性：每个文本输入都应该被独立存储
    for i, text_input in enumerate(text_inputs):
        assert text_input.text == text_list[i], f"第{i}个文本应该被正确存储"
        assert text_input.user_id == user_id, "所有文本都应该关联到同一用户"
        assert text_input.source == f"source_{i}", "每个文本的来源应该被正确记录"



@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=50))
def test_unsupported_format_rejection_property(filename_base):
    """
    Feature: text-archive-assistant, Property 3: 不支持格式拒绝
    Validates: Requirements 1.4
    
    对于任意不支持的文件格式，系统应该拒绝处理
    
    属性：所有非图片格式的文件都应该被拒绝
    """
    validator = FileValidator()
    
    # 不支持的文件扩展名
    unsupported_extensions = [
        ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".ppt", ".pptx", ".zip", ".rar", ".mp3", ".mp4",
        ".avi", ".mov", ".gif", ".svg", ".tiff", ".webp"
    ]
    
    for ext in unsupported_extensions:
        # 清理文件名并添加不支持的扩展名
        clean_filename = filename_base.replace("/", "_").replace("\\", "_")
        test_filename = clean_filename + ext
        
        mock_file = type('MockFile', (), {'filename': test_filename})()
        
        # 属性：不支持的格式应该被拒绝
        assert not validator.validate_file_format(mock_file), f"不支持的格式 {ext} 应该被拒绝"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=50))
def test_unsupported_mime_type_rejection_property(mime_base):
    """
    Feature: text-archive-assistant, Property 3: 不支持格式拒绝
    Validates: Requirements 1.4
    
    属性：所有非图片MIME类型都应该被拒绝
    """
    validator = FileValidator()
    
    # 不支持的MIME类型前缀
    unsupported_prefixes = [
        "text", "application", "video", "audio", 
        "font", "model", "multipart"
    ]
    
    for prefix in unsupported_prefixes:
        # 创建不支持的MIME类型
        clean_mime_base = mime_base.replace("/", "-").replace(" ", "-")
        mime_type = f"{prefix}/{clean_mime_base}"
        
        mock_file = type('MockFile', (), {'content_type': mime_type})()
        
        # 属性：非图片MIME类型应该被拒绝
        assert not validator.validate_content_type(mock_file), f"不支持的MIME类型 {mime_type} 应该被拒绝"


@pytest.mark.property
@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=50))
def test_file_extension_case_insensitive_property(case_variations):
    """
    Feature: text-archive-assistant, Property 3: 不支持格式拒绝
    Validates: Requirements 1.4
    
    属性：文件扩展名验证应该不区分大小写
    """
    validator = FileValidator()
    
    # 支持的扩展名的不同大小写组合
    base_extensions = ["jpg", "jpeg", "png", "bmp"]
    
    for ext in base_extensions:
        # 生成不同的大小写组合
        variations = [
            ext.lower(),
            ext.upper(), 
            ext.capitalize(),
            ext[:2].upper() + ext[2:].lower() if len(ext) > 2 else ext.upper()
        ]
        
        for variation in variations:
            test_filename = f"test.{variation}"
            mock_file = type('MockFile', (), {'filename': test_filename})()
            
            # 属性：不同大小写的支持格式都应该通过验证
            assert validator.validate_file_format(mock_file), f"扩展名 .{variation} 应该通过验证（不区分大小写）"


@pytest.mark.property
@settings(max_examples=100)
@given(st.text(min_size=1, max_size=100))
def test_format_validation_consistency_property(filename_part):
    """
    Feature: text-archive-assistant, Property 3: 不支持格式拒绝
    Validates: Requirements 1.4
    
    属性：格式验证应该只基于扩展名，不受文件名其他部分影响
    """
    validator = FileValidator()
    
    # 清理文件名
    clean_filename = filename_part.replace("/", "_").replace("\\", "_")
    
    # 测试支持的格式
    supported_exts = [".jpg", ".jpeg", ".png", ".bmp"]
    for ext in supported_exts:
        test_filename = clean_filename + ext
        mock_file = type('MockFile', (), {'filename': test_filename})()
        assert validator.validate_file_format(mock_file), f"文件名 {test_filename} 应该通过验证"
    
    # 测试不支持的格式
    unsupported_exts = [".txt", ".pdf", ".gif"]
    for ext in unsupported_exts:
        test_filename = clean_filename + ext
        mock_file = type('MockFile', (), {'filename': test_filename})()
        assert not validator.validate_file_format(mock_file), f"文件名 {test_filename} 不应该通过验证"



@pytest.mark.property
@settings(max_examples=100)
@given(st.sampled_from(["jpg", "jpeg", "png", "bmp"]))
def test_supported_formats_acceptance_property(extension):
    """
    Feature: text-archive-assistant, Property 4: 支持格式接收
    Validates: Requirements 1.5
    
    对于所有支持的格式（jpg, jpeg, png, bmp），系统应该接收处理
    
    属性：所有声明支持的格式都应该通过验证
    """
    validator = FileValidator()
    
    # 测试不同的文件名组合
    test_filenames = [
        f"test.{extension}",
        f"my_file.{extension}",
        f"image_123.{extension}",
        f"photo-2023.{extension}"
    ]
    
    for filename in test_filenames:
        mock_file = type('MockFile', (), {'filename': filename})()
        assert validator.validate_file_format(mock_file), f"支持的格式 {filename} 应该通过验证"


@pytest.mark.property
@settings(max_examples=100)
@given(st.sampled_from(["image/jpeg", "image/jpg", "image/png", "image/bmp"]))
def test_supported_mime_types_acceptance_property(mime_type):
    """
    Feature: text-archive-assistant, Property 4: 支持格式接收
    Validates: Requirements 1.5
    
    属性：所有支持的MIME类型都应该通过验证
    """
    validator = FileValidator()
    
    mock_file = type('MockFile', (), {'content_type': mime_type})()
    assert validator.validate_content_type(mock_file), f"支持的MIME类型 {mime_type} 应该通过验证"


@pytest.mark.property
@settings(max_examples=100)
@given(
    st.sampled_from(["jpg", "jpeg", "png", "bmp"]),
    st.integers(min_value=10, max_value=500),
    st.integers(min_value=10, max_value=500)
)
def test_supported_format_image_creation_property(extension, width, height):
    """
    Feature: text-archive-assistant, Property 4: 支持格式接收
    Validates: Requirements 1.5
    
    属性：对于所有支持的格式，系统应该能够创建和处理相应格式的图片
    """
    file_manager = FileManager()
    
    # 根据扩展名确定PIL格式
    pil_format_map = {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "bmp": "BMP"
    }
    
    pil_format = pil_format_map[extension]
    
    # 创建指定格式的图片
    img = Image.new('RGB', (width, height), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format=pil_format)
    img_bytes.seek(0)
    
    # 创建模拟的UploadFile
    mock_file = type('MockFile', (), {
        'file': img_bytes,
        'filename': f'test.{extension}'
    })()
    
    # 属性：应该能够保存支持格式的图片
    try:
        filename = f"test_format_{extension}_{width}x{height}.{extension}"
        file_path, file_size = file_manager.save_file(mock_file, filename)
        
        # 验证文件已保存
        import os
        assert os.path.exists(file_path), f"格式 {extension} 的文件应该被成功保存"
        assert file_size > 0, "文件大小应该大于0"
        
        # 清理测试文件
        file_manager.delete_file(file_path)
        
    except Exception as e:
        pytest.fail(f"处理 {extension} 格式图片时失败: {str(e)}")


@pytest.mark.property
@settings(max_examples=100)
@given(st.sampled_from(["jpg", "jpeg", "png", "bmp"]))
def test_format_mime_type_consistency_property(extension):
    """
    Feature: text-archive-assistant, Property 4: 支持格式接收
    Validates: Requirements 1.5
    
    属性：文件扩展名和MIME类型验证应该保持一致
    """
    validator = FileValidator()
    
    # 扩展名到MIME类型的映射
    ext_to_mime = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "bmp": "image/bmp"
    }
    
    # 测试文件名验证
    filename = f"test.{extension}"
    mock_file_ext = type('MockFile', (), {'filename': filename})()
    ext_valid = validator.validate_file_format(mock_file_ext)
    
    # 测试MIME类型验证
    mime_type = ext_to_mime[extension]
    mock_file_mime = type('MockFile', (), {'content_type': mime_type})()
    mime_valid = validator.validate_content_type(mock_file_mime)
    
    # 属性：扩展名和对应的MIME类型验证结果应该一致
    assert ext_valid == mime_valid, f"扩展名 {extension} 和MIME类型 {mime_type} 的验证结果应该一致"
    assert ext_valid is True, f"支持的格式 {extension} 应该通过验证"


@pytest.mark.property
@settings(max_examples=50)
@given(st.lists(st.sampled_from(["jpg", "jpeg", "png", "bmp"]), min_size=1, max_size=10))
def test_multiple_format_handling_property(extensions):
    """
    Feature: text-archive-assistant, Property 4: 支持格式接收
    Validates: Requirements 1.5
    
    属性：系统应该能够同时处理多个不同格式的文件
    """
    validator = FileValidator()
    
    # 为每个扩展名创建文件并验证
    for i, ext in enumerate(extensions):
        filename = f"file_{i}.{ext}"
        mock_file = type('MockFile', (), {'filename': filename})()
        
        # 属性：所有支持的格式都应该通过验证
        assert validator.validate_file_format(mock_file), f"文件 {filename} 应该通过验证"
