"""分类相关的Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


class ClassifyRequest(BaseModel):
    """分类请求"""
    text: str = Field(..., min_length=1, description="待分类的文本")


class ClassifyResponse(BaseModel):
    """分类响应"""
    type: Literal['schedule', 'memo'] = Field(..., description="分类类型")
    confidence: float = Field(..., ge=0, le=1, description="置信度(0-1)")
    extracted_data: Dict[str, Any] = Field(..., description="提取的结构化数据")
    needs_manual_selection: bool = Field(..., description="是否需要用户手动选择")
    
    class Config:
        from_attributes = True


class ManualClassifyRequest(BaseModel):
    """手动分类请求"""
    text: str = Field(..., min_length=1, description="文本内容")
    type: Literal['schedule', 'memo'] = Field(..., description="用户选择的类型")
