"""文件上传API路由"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.base import get_db
from app.models.user import User
from app.models.upload import UploadedFile, TextInput
from app.schemas.upload import (
    FileUploadResponse, 
    TextInputRequest, 
    TextInputResponse,
    FileValidationError
)
from app.dependencies.auth import get_current_user
from app.utils.file_handler import validate_upload_file, FileManager
from app.utils.logger import logging

router = APIRouter(prefix="/upload", tags=["文件上传"])


@router.post(
    "/file",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="上传文件",
    description="上传图片文件进行OCR识别"
)
def upload_file(
    file: UploadFile = File(..., description="要上传的图片文件"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传文件
    
    - **file**: 图片文件（支持jpg, jpeg, png, bmp格式）
    - 文件大小限制: 10MB
    - 需要认证
    """
    try:
        # 验证文件
        validate_upload_file(file)
        
        # 初始化文件管理器
        file_manager = FileManager()
        
        # 生成唯一文件名
        filename = file_manager.generate_filename(file.filename, current_user.id)
        
        # 保存文件
        file_path, file_size = file_manager.save_file(file, filename)
        
        # 计算文件哈希
        file_hash = file_manager.calculate_file_hash(file_path)
        
        # 检查是否已存在相同文件
        existing_file = db.query(UploadedFile).filter(
            UploadedFile.user_id == current_user.id,
            UploadedFile.file_hash == file_hash
        ).first()
        
        if existing_file:
            # 删除刚上传的重复文件
            file_manager.delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="文件已存在"
            )
        
        # 保存文件信息到数据库
        uploaded_file = UploadedFile(
            user_id=current_user.id,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            content_type=file.content_type,
            file_hash=file_hash
        )
        
        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)
        
        logging.info(f"用户 {current_user.username} 上传文件: {file.filename}")
        
        return FileUploadResponse(
            file_id=uploaded_file.id,
            filename=uploaded_file.filename,
            file_path=uploaded_file.file_path,
            file_size=uploaded_file.file_size,
            content_type=uploaded_file.content_type,
            uploaded_at=uploaded_file.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"文件上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传失败"
        )


@router.post(
    "/text",
    response_model=TextInputResponse,
    status_code=status.HTTP_201_CREATED,
    summary="输入文本",
    description="直接输入文本内容"
)
def input_text(
    text_data: TextInputRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    输入文本
    
    - **text**: 文本内容（1-10000字符）
    - **source**: 文本来源（默认为manual）
    - 需要认证
    """
    try:
        # 创建文本输入记录
        text_input = TextInput(
            user_id=current_user.id,
            text=text_data.text,
            source=text_data.source
        )
        
        db.add(text_input)
        db.commit()
        db.refresh(text_input)
        
        logging.info(f"用户 {current_user.username} 输入文本: {len(text_data.text)} 字符")
        
        return TextInputResponse(
            text_id=text_input.id,
            text=text_input.text,
            source=text_input.source,
            created_at=text_input.created_at
        )
        
    except Exception as e:
        logging.error(f"文本输入失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文本输入失败"
        )


@router.get(
    "/files",
    response_model=List[FileUploadResponse],
    summary="获取上传文件列表",
    description="获取当前用户的上传文件列表"
)
def get_uploaded_files(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取上传文件列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数限制
    - 需要认证
    """
    files = db.query(UploadedFile).filter(
        UploadedFile.user_id == current_user.id
    ).order_by(
        UploadedFile.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        FileUploadResponse(
            file_id=file.id,
            filename=file.filename,
            file_path=file.file_path,
            file_size=file.file_size,
            content_type=file.content_type,
            uploaded_at=file.created_at
        )
        for file in files
    ]


@router.delete(
    "/file/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除上传文件",
    description="删除指定的上传文件"
)
def delete_uploaded_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除上传文件
    
    - **file_id**: 文件ID
    - 需要认证
    - 只能删除自己上传的文件
    """
    # 查找文件
    file_record = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    try:
        # 删除物理文件
        file_manager = FileManager()
        file_manager.delete_file(file_record.file_path)
        
        # 删除数据库记录
        db.delete(file_record)
        db.commit()
        
        logging.info(f"用户 {current_user.username} 删除文件: {file_record.filename}")
        
    except Exception as e:
        logging.error(f"删除文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除文件失败"
        )
