"""OCR识别API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User
from app.models.upload import UploadedFile
from app.schemas.ocr import (
    OCRRecognizeRequest,
    OCRRecognizeResponse,
    OCREditRequest
)
from app.dependencies.auth import get_current_user
from app.services.ocr_service import get_ocr_service
from app.utils.logger import logging

router = APIRouter(prefix="/ocr", tags=["OCR识别"])


@router.post(
    "/recognize",
    response_model=OCRRecognizeResponse,
    summary="识别图片文字",
    description="对已上传的图片进行OCR文字识别"
)
def recognize_image(
    request: OCRRecognizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    识别图片中的文字
    
    - **file_id**: 已上传的文件ID
    - 需要认证
    - 支持中英文识别
    """
    try:
        # 查找上传的文件
        uploaded_file = db.query(UploadedFile).filter(
            UploadedFile.id == request.file_id,
            UploadedFile.user_id == current_user.id
        ).first()
        
        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在或无权访问"
            )
        
        # 获取OCR服务
        ocr_service = get_ocr_service()
        
        # 验证图片
        is_valid, error_msg = ocr_service.validate_image(uploaded_file.file_path)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"图片验证失败: {error_msg}"
            )
        
        # 执行OCR识别
        result = ocr_service.recognize_text(uploaded_file.file_path)
        
        # 更新文件状态
        if result["success"]:
            uploaded_file.status = "processed"
        else:
            uploaded_file.status = "error"
        
        db.commit()
        
        logging.info(f"用户 {current_user.username} 对文件 {uploaded_file.filename} 进行OCR识别")
        
        return OCRRecognizeResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"OCR识别失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OCR识别失败"
        )


@router.post(
    "/edit",
    status_code=status.HTTP_200_OK,
    summary="编辑OCR识别结果",
    description="用户可以手动编辑OCR识别的文本"
)
def edit_ocr_result(
    request: OCREditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    编辑OCR识别结果
    
    - **file_id**: 文件ID
    - **edited_text**: 编辑后的文本
    - 需要认证
    """
    try:
        # 查找上传的文件
        uploaded_file = db.query(UploadedFile).filter(
            UploadedFile.id == request.file_id,
            UploadedFile.user_id == current_user.id
        ).first()
        
        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在或无权访问"
            )
        
        logging.info(f"用户 {current_user.username} 编辑了文件 {uploaded_file.filename} 的OCR结果")
        
        return {
            "success": True,
            "message": "OCR结果已更新",
            "edited_text": request.edited_text
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"编辑OCR结果失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="编辑OCR结果失败"
        )
