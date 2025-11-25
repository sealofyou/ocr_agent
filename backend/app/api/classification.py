"""分类API路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User
from app.schemas.classification import (
    ClassifyRequest,
    ClassifyResponse,
    ManualClassifyRequest
)
from app.dependencies.auth import get_current_user
from app.services.classification_service import get_classification_service
from app.utils.logger import logging

router = APIRouter(prefix="/classify", tags=["文本分类"])


@router.post(
    "",
    response_model=ClassifyResponse,
    summary="分类文本内容",
    description="使用AI模型自动判断文本类型（日程/备忘录）"
)
async def classify_text(
    request: ClassifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分类文本内容
    
    - **text**: 待分类的文本
    - 需要认证
    - 返回分类类型、置信度和提取的结构化数据
    """
    try:
        # 获取分类服务
        classification_service = get_classification_service()
        
        # 执行分类（优先使用LLM）
        try:
            result = await classification_service.classify_text_with_llm(request.text)
        except Exception as llm_error:
            logging.warning(f"LLM分类失败，使用规则方法: {str(llm_error)}")
            result = classification_service.classify_text(request.text)
        
        # 判断是否需要手动选择
        needs_manual = classification_service.needs_manual_selection(result["confidence"])
        
        logging.info(
            f"用户 {current_user.username} 对文本进行分类: "
            f"类型={result['type']}, 置信度={result['confidence']:.2f}"
        )
        
        return ClassifyResponse(
            type=result["type"],
            confidence=result["confidence"],
            extracted_data=result["extracted_data"],
            needs_manual_selection=needs_manual
        )
        
    except Exception as e:
        logging.error(f"文本分类失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文本分类失败"
        )


@router.post(
    "/manual",
    status_code=status.HTTP_200_OK,
    summary="手动选择分类",
    description="当AI无法确定分类时，用户手动选择类型"
)
def manual_classify(
    request: ManualClassifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    手动选择分类
    
    - **text**: 文本内容
    - **type**: 用户选择的类型（schedule 或 memo）
    - 需要认证
    """
    try:
        # 获取分类服务
        classification_service = get_classification_service()
        
        # 根据用户选择的类型提取信息
        if request.type == "schedule":
            extracted_data = classification_service.extract_schedule_info(request.text)
        else:
            extracted_data = classification_service.extract_memo_info(request.text)
        
        logging.info(
            f"用户 {current_user.username} 手动选择分类: 类型={request.type}"
        )
        
        return {
            "success": True,
            "type": request.type,
            "extracted_data": extracted_data,
            "message": "分类已确认"
        }
        
    except Exception as e:
        logging.error(f"手动分类失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="手动分类失败"
        )
