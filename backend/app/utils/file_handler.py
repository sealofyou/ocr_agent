"""文件处理工具函数"""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Tuple, Optional, List
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings


class FileValidator:
    """文件验证器"""
    
    @staticmethod
    def validate_file_format(file: UploadFile) -> bool:
        """
        验证文件格式
        
        Args:
            file: 上传的文件
            
        Returns:
            是否为支持的格式
        """
        if not file.filename:
            return False
            
        # 获取文件扩展名
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        
        # 检查是否为支持的图片格式
        return file_ext in settings.ALLOWED_IMAGE_FORMATS
    
    @staticmethod
    def validate_file_size(file: UploadFile) -> bool:
        """
        验证文件大小
        
        Args:
            file: 上传的文件
            
        Returns:
            文件大小是否符合要求
        """
        if not hasattr(file, 'size') or file.size is None:
            # 如果无法获取文件大小，尝试读取内容来检查
            content = file.file.read()
            file.file.seek(0)  # 重置文件指针
            return len(content) <= settings.MAX_FILE_SIZE
        
        return file.size <= settings.MAX_FILE_SIZE
    
    @staticmethod
    def validate_content_type(file: UploadFile) -> bool:
        """
        验证文件MIME类型
        
        Args:
            file: 上传的文件
            
        Returns:
            MIME类型是否正确
        """
        if not file.content_type:
            return False
            
        # 支持的MIME类型
        allowed_mime_types = [
            "image/jpeg",
            "image/jpg", 
            "image/png",
            "image/bmp"
        ]
        
        return file.content_type.lower() in allowed_mime_types


class FileManager:
    """文件管理器"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
    
    def generate_filename(self, original_filename: str, user_id: str) -> str:
        """
        生成唯一的文件名
        
        Args:
            original_filename: 原始文件名
            user_id: 用户ID
            
        Returns:
            生成的唯一文件名
        """
        import uuid
        from datetime import datetime
        
        # 获取文件扩展名
        file_ext = Path(original_filename).suffix
        
        # 生成时间戳和UUID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # 组合文件名
        return f"{user_id}_{timestamp}_{unique_id}{file_ext}"
    
    def save_file(self, file: UploadFile, filename: str) -> Tuple[str, int]:
        """
        保存文件到磁盘
        
        Args:
            file: 上传的文件
            filename: 保存的文件名
            
        Returns:
            (文件路径, 文件大小)
        """
        file_path = self.upload_dir / filename
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        content = file.file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 重置文件指针
        file.file.seek(0)
        
        return str(file_path), len(content)
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        计算文件MD5哈希
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件MD5哈希值
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False


def validate_upload_file(file: UploadFile) -> None:
    """
    验证上传文件
    
    Args:
        file: 上传的文件
        
    Raises:
        HTTPException: 如果文件验证失败
    """
    validator = FileValidator()
    
    # 检查文件是否存在
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未选择文件"
        )
    
    # 验证文件格式
    if not validator.validate_file_format(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式。支持的格式: {', '.join(settings.ALLOWED_IMAGE_FORMATS)}"
        )
    
    # 验证文件大小
    if not validator.validate_file_size(file):
        max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制。最大允许: {max_size_mb:.1f}MB"
        )
    
    # 验证MIME类型
    if not validator.validate_content_type(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的文件类型"
        )
