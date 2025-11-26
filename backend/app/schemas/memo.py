"""备忘录相关的Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MemoCreateRequest(BaseModel):
    """创建备忘录请求"""
    content: str = Field(..., min_length=1, description="备忘录内容")
    summary: Optional[str] = Field(default=None, description="内容摘要")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "今天学习了Python的异步编程，理解了async/await的工作原理",
                "summary": "学习Python异步编程",
                "tags": ["学习", "Python"]
            }
        }


class MemoResponse(BaseModel):
    """备忘录响应"""
    id: str = Field(..., description="备忘录ID")
    user_id: str = Field(..., description="用户ID")
    content: str = Field(..., description="备忘录内容")
    summary: str = Field(..., description="内容摘要")
    tags: Optional[str] = Field(default=None, description="标签（逗号分隔）")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
    
    @property
    def tags_list(self) -> List[str]:
        """将标签字符串转换为列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class MemoUpdateRequest(BaseModel):
    """更新备忘录请求"""
    content: Optional[str] = Field(default=None, min_length=1, description="备忘录内容")
    summary: Optional[str] = Field(default=None, description="内容摘要")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")


class MemoListResponse(BaseModel):
    """备忘录列表响应"""
    memos: list[MemoResponse] = Field(..., description="备忘录列表")
    total: int = Field(..., description="总数")
