"""日程相关的Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date as date_type, time as time_type, datetime


class ScheduleCreateRequest(BaseModel):
    """创建日程请求"""
    date: Optional[str] = Field(default=None, description="日期 (YYYY-MM-DD)")
    time: Optional[str] = Field(default=None, description="时间 (HH:MM)")
    description: str = Field(..., min_length=1, description="事件描述")
    original_text: str = Field(..., min_length=1, description="原始文本")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "time": "14:30",
                "description": "团队会议",
                "original_text": "明天下午2点30分团队会议"
            }
        }


class ScheduleResponse(BaseModel):
    """日程响应"""
    id: str = Field(..., description="日程ID")
    user_id: str = Field(..., description="用户ID")
    date: Optional[date_type] = Field(default=None, description="日期")
    time: Optional[time_type] = Field(default=None, description="时间")
    description: str = Field(..., description="事件描述")
    original_text: str = Field(..., description="原始文本")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class ScheduleUpdateRequest(BaseModel):
    """更新日程请求"""
    date: Optional[str] = Field(default=None, description="日期 (YYYY-MM-DD)")
    time: Optional[str] = Field(default=None, description="时间 (HH:MM)")
    description: Optional[str] = Field(default=None, min_length=1, description="事件描述")
    original_text: Optional[str] = Field(default=None, min_length=1, description="原始文本")


class ScheduleListResponse(BaseModel):
    """日程列表响应"""
    schedules: list[ScheduleResponse] = Field(..., description="日程列表")
    total: int = Field(..., description="总数")
