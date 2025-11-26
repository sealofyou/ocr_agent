"""备忘录API路由"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from app.db.base import get_db
from app.models.user import User
from app.models.memo import Memo
from app.schemas.memo import (
    MemoCreateRequest,
    MemoResponse,
    MemoUpdateRequest,
    MemoListResponse
)
from app.dependencies.auth import get_current_user
from app.utils.logger import logging

router = APIRouter(prefix="/memos", tags=["备忘录管理"])


def tags_to_string(tags: Optional[List[str]]) -> Optional[str]:
    """将标签列表转换为逗号分隔的字符串"""
    if not tags:
        return None
    return ','.join(tag.strip() for tag in tags if tag.strip())


def generate_summary(content: str, max_length: int = 100) -> str:
    """生成内容摘要"""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


@router.post(
    "",
    response_model=MemoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建备忘录",
    description="创建新的备忘录"
)
def create_memo(
    request: MemoCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建备忘录
    
    - **content**: 备忘录内容
    - **summary**: 内容摘要（可选，如果不提供则自动生成）
    - **tags**: 标签列表（可选）
    - 需要认证
    """
    try:
        # 生成摘要（如果未提供）
        summary = request.summary if request.summary else generate_summary(request.content)
        
        # 转换标签
        tags_str = tags_to_string(request.tags)
        
        # 创建备忘录
        memo = Memo(
            user_id=current_user.id,
            content=request.content,
            summary=summary,
            tags=tags_str
        )
        
        db.add(memo)
        db.commit()
        db.refresh(memo)
        
        logging.info(
            f"用户 {current_user.username} 创建备忘录: "
            f"ID={memo.id}, 标签={tags_str or '无'}"
        )
        
        return memo
        
    except Exception as e:
        db.rollback()
        logging.error(f"创建备忘录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建备忘录失败"
        )


@router.get(
    "",
    response_model=MemoListResponse,
    summary="查询备忘录列表",
    description="查询用户的备忘录列表，支持按标签筛选"
)
def get_memos(
    tags: Optional[str] = Query(None, description="标签筛选（逗号分隔）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询备忘录列表
    
    - **tags**: 标签筛选（可选，逗号分隔）
    - 需要认证
    - 返回按创建时间倒序排序的备忘录列表
    """
    try:
        # 构建查询
        query = db.query(Memo).filter(Memo.user_id == current_user.id)
        
        # 应用标签筛选
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if tag_list:
                # 构建标签筛选条件（任意一个标签匹配即可）
                tag_conditions = []
                for tag in tag_list:
                    tag_conditions.append(Memo.tags.like(f'%{tag}%'))
                query = query.filter(or_(*tag_conditions))
        
        # 按创建时间倒序排序
        query = query.order_by(Memo.created_at.desc())
        
        memos = query.all()
        
        logging.info(
            f"用户 {current_user.username} 查询备忘录: "
            f"数量={len(memos)}, 标签筛选={tags or '无'}"
        )
        
        return MemoListResponse(
            memos=memos,
            total=len(memos)
        )
        
    except Exception as e:
        logging.error(f"查询备忘录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询备忘录失败"
        )


@router.get(
    "/{memo_id}",
    response_model=MemoResponse,
    summary="获取备忘录详情",
    description="根据ID获取备忘录详情"
)
def get_memo(
    memo_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取备忘录详情
    
    - **memo_id**: 备忘录ID
    - 需要认证
    """
    try:
        memo = db.query(Memo).filter(
            and_(
                Memo.id == memo_id,
                Memo.user_id == current_user.id
            )
        ).first()
        
        if not memo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="备忘录不存在"
            )
        
        return memo
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"获取备忘录详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取备忘录详情失败"
        )


@router.put(
    "/{memo_id}",
    response_model=MemoResponse,
    summary="更新备忘录",
    description="更新备忘录信息"
)
def update_memo(
    memo_id: str,
    request: MemoUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新备忘录
    
    - **memo_id**: 备忘录ID
    - **content**: 备忘录内容（可选）
    - **summary**: 内容摘要（可选）
    - **tags**: 标签列表（可选）
    - 需要认证
    """
    try:
        memo = db.query(Memo).filter(
            and_(
                Memo.id == memo_id,
                Memo.user_id == current_user.id
            )
        ).first()
        
        if not memo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="备忘录不存在"
            )
        
        # 更新字段
        if request.content is not None:
            memo.content = request.content
            # 如果内容更新但摘要未提供，重新生成摘要
            if request.summary is None:
                memo.summary = generate_summary(request.content)
        
        if request.summary is not None:
            memo.summary = request.summary
        
        if request.tags is not None:
            memo.tags = tags_to_string(request.tags)
        
        db.commit()
        db.refresh(memo)
        
        logging.info(f"用户 {current_user.username} 更新备忘录: ID={memo_id}")
        
        return memo
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"更新备忘录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新备忘录失败"
        )


@router.delete(
    "/{memo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除备忘录",
    description="删除备忘录"
)
def delete_memo(
    memo_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除备忘录
    
    - **memo_id**: 备忘录ID
    - 需要认证
    """
    try:
        memo = db.query(Memo).filter(
            and_(
                Memo.id == memo_id,
                Memo.user_id == current_user.id
            )
        ).first()
        
        if not memo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="备忘录不存在"
            )
        
        db.delete(memo)
        db.commit()
        
        logging.info(f"用户 {current_user.username} 删除备忘录: ID={memo_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"删除备忘录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除备忘录失败"
        )
