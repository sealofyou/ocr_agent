"""文件上传相关的Pydantic schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_id: str
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class TextInputRequest(BaseModel):
    """文本输入请求"""
    text: str = Field(..., min_length=1, max_length=10000, description="输入的文本内容")
    source: str = Field(default="manual", description="文本来源")


class TextInputResponse(BaseModel):
    """文本输入响应"""
    text_id: str
    text: str
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileValidationError(BaseModel):
    """文件验证错误"""
    error_type: str
    message: str
    details: Optional[dict] = None
