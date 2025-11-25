from typing import Optional, Any

from pydantic import BaseModel
from app.utils.businessexception import ErrorCode

class ResponseData(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None  # 默认为 None

# 统一响应模型
class ResponseModel(BaseModel):
    
    @staticmethod
    def success(data: Any = None, message: str = None):
        code = ErrorCode.SUCCESS.code
        message = message or ErrorCode.SUCCESS.message
        data = data
        return ResponseData(code=code, message=message, data=data)
    @ staticmethod
    def error(error_code: ErrorCode, message: str = None, data: Any = None):
        code = error_code.code
        message = message or error_code.message
        data = data
        return ResponseData(code=code, message=message, data=data)