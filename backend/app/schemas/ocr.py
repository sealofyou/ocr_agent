"""OCR相关的Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional


class OCRTextDetail(BaseModel):
    """OCR识别的单行文本详情"""
    text: str = Field(..., description="识别的文本")
    confidence: float = Field(..., description="置信度(0-1)")
    box: List[List[float]] = Field(..., description="文本框坐标")


class OCRRecognizeRequest(BaseModel):
    """OCR识别请求"""
    file_id: str = Field(..., description="已上传的文件ID")


class OCRRecognizeResponse(BaseModel):
    """OCR识别响应"""
    success: bool = Field(..., description="是否识别成功")
    text: str = Field(..., description="识别的完整文本")
    details: List[OCRTextDetail] = Field(default=[], description="详细识别结果")
    error: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        from_attributes = True


class OCREditRequest(BaseModel):
    """OCR结果编辑请求"""
    file_id: str = Field(..., description="文件ID")
    edited_text: str = Field(..., min_length=1, description="编辑后的文本")
