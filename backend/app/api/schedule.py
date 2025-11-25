"""日程API路由"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, time, datetime
from typing import Optional
from app.db.base import get_db
from app.models.user import User
from app.models.schedule import ScheduleItem
from app.schemas.schedule import (
    ScheduleCreateRequest,
    ScheduleResponse,
    ScheduleUpdateRequest,
    ScheduleListResponse
)
from app.dependencies.auth import get_current_user
from app.utils.logger import logging

router = APIRouter(prefix="/schedules", tags=["日程管理"])


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """解析日期字符串"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的日期格式: {date_str}，应为 YYYY-MM-DD"
        )


def parse_time(time_str: Optional[str]) -> Optional[time]:
    """解析时间字符串"""
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的时间格式: {time_str}，应为 HH:MM"
        )


@router.post(
    "",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建日程",
    description="创建新的日程项"
)
def create_schedule(
    request: ScheduleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建日程
    
    - **date**: 日期 (可选，格式: YYYY-MM-DD)
    - **time**: 时间 (可选，格式: HH:MM)
    - **description**: 事件描述
    - **original_text**: 原始文本
    - 需要认证
    """
    try:
        # 解析日期和时间
        schedule_date = parse_date(request.date)
        schedule_time = parse_time(request.time)
        
        # 检查是否缺少时间信息
        if not schedule_date and not schedule_time:
            logging.warning(f"用户 {current_user.username} 创建日程缺少时间信息")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日程缺少时间信息，请补充日期或时间"
            )
        
        # 创建日程项
        schedule = ScheduleItem(
            user_id=current_user.id,
            date=schedule_date,
            time=schedule_time,
            description=request.description,
            original_text=request.original_text
        )
        
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        
        logging.info(
            f"用户 {current_user.username} 创建日程: "
            f"ID={schedule.id}, 日期={schedule_date}, 时间={schedule_time}"
        )
        
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"创建日程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建日程失败"
        )


@router.get(
    "",
    response_model=ScheduleListResponse,
    summary="查询日程列表",
    description="查询用户的日程列表，支持按日期范围筛选"
)
def get_schedules(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询日程列表
    
    - **start_date**: 开始日期 (可选)
    - **end_date**: 结束日期 (可选)
    - 需要认证
    - 返回按时间顺序排序的日程列表
    """
    try:
        # 构建查询
        query = db.query(ScheduleItem).filter(ScheduleItem.user_id == current_user.id)
        
        # 应用日期范围筛选
        if start_date:
            start = parse_date(start_date)
            query = query.filter(ScheduleItem.date >= start)
        
        if end_date:
            end = parse_date(end_date)
            query = query.filter(ScheduleItem.date <= end)
        
        # 按日期和时间排序
        query = query.order_by(
            ScheduleItem.date.asc().nullslast(),
            ScheduleItem.time.asc().nullslast()
        )
        
        schedules = query.all()
        
        logging.info(
            f"用户 {current_user.username} 查询日程: "
            f"数量={len(schedules)}, 日期范围={start_date or '无'} 到 {end_date or '无'}"
        )
        
        return ScheduleListResponse(
            schedules=schedules,
            total=len(schedules)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"查询日程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询日程失败"
        )


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="获取日程详情",
    description="根据ID获取日程详情"
)
def get_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取日程详情
    
    - **schedule_id**: 日程ID
    - 需要认证
    """
    try:
        schedule = db.query(ScheduleItem).filter(
            and_(
                ScheduleItem.id == schedule_id,
                ScheduleItem.user_id == current_user.id
            )
        ).first()
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日程不存在"
            )
        
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"获取日程详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日程详情失败"
        )


@router.put(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="更新日程",
    description="更新日程信息"
)
def update_schedule(
    schedule_id: str,
    request: ScheduleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新日程
    
    - **schedule_id**: 日程ID
    - **date**: 日期 (可选)
    - **time**: 时间 (可选)
    - **description**: 事件描述 (可选)
    - **original_text**: 原始文本 (可选)
    - 需要认证
    """
    try:
        schedule = db.query(ScheduleItem).filter(
            and_(
                ScheduleItem.id == schedule_id,
                ScheduleItem.user_id == current_user.id
            )
        ).first()
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日程不存在"
            )
        
        # 更新字段
        if request.date is not None:
            schedule.date = parse_date(request.date)
        if request.time is not None:
            schedule.time = parse_time(request.time)
        if request.description is not None:
            schedule.description = request.description
        if request.original_text is not None:
            schedule.original_text = request.original_text
        
        db.commit()
        db.refresh(schedule)
        
        logging.info(f"用户 {current_user.username} 更新日程: ID={schedule_id}")
        
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"更新日程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新日程失败"
        )


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除日程",
    description="删除日程"
)
def delete_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除日程
    
    - **schedule_id**: 日程ID
    - 需要认证
    """
    try:
        schedule = db.query(ScheduleItem).filter(
            and_(
                ScheduleItem.id == schedule_id,
                ScheduleItem.user_id == current_user.id
            )
        ).first()
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日程不存在"
            )
        
        db.delete(schedule)
        db.commit()
        
        logging.info(f"用户 {current_user.username} 删除日程: ID={schedule_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"删除日程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除日程失败"
        )
