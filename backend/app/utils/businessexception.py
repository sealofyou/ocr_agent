from enum import Enum
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel


# 定义错误码枚举（与Java枚举对应）
class ErrorCode(Enum):
    SUCCESS = (200, "ok")
    PARAMS_ERROR = (400, "请求参数错误")
    NOT_LOGIN_ERROR = (401, "未登录")
    NO_AUTH_ERROR = (402, "无权限")
    NOT_FOUND_ERROR = (404, "请求数据不存在")
    FORBIDDEN_ERROR = (403, "禁止访问")
    SYSTEM_ERROR = (500, "系统内部异常")
    OPERATION_ERROR = (501, "操作失败")

    def __init__(self, code: int, message: str):
        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message


# 自定义异常基类
class CustomException(HTTPException):
    def __init__(self, error_code: ErrorCode, detail: str = None):
        super().__init__(
            status_code=status.HTTP_200_OK,  # 统一返回200，通过code区分实际状态
            detail=detail or error_code.message,
            headers=None
        )
        self.error_code = error_code


# 各业务异常类
class ParamsError(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(ErrorCode.PARAMS_ERROR, detail)


class NotLoginError(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(ErrorCode.NOT_LOGIN_ERROR, detail)


class NoAuthError(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(ErrorCode.NO_AUTH_ERROR, detail)


class NotFoundError(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(ErrorCode.NOT_FOUND_ERROR, detail)


class ForbiddenError(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(ErrorCode.FORBIDDEN_ERROR, detail)


class SystemError(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(ErrorCode.SYSTEM_ERROR, detail)


class OperationError(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(ErrorCode.OPERATION_ERROR, detail)


# 统一响应模型
class ErrorResponse(BaseModel):
    code: int
    message: str
    data: dict = None


# 注册全局异常处理器
def register_exception_handlers(app: FastAPI):
    # 处理自定义异常
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.error_code.code,
                "message": exc.detail,
                "data": None
            }
        )

    # 处理请求验证错误（参数校验失败）
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        error_details = []
        for error in errors:
            loc = "->".join(str(l) for l in error["loc"])
            error_details.append(f"{loc}: {error['msg']}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": ErrorCode.PARAMS_ERROR.code,
                "message": f"参数校验失败: {'; '.join(error_details)}",
                "data": None
            }
        )

    # 处理其他未捕获异常
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": ErrorCode.SYSTEM_ERROR.code,
                "message": f"系统内部错误: {str(exc)}",
                "data": None
            }
        )


if __name__ == "__main__":
    # 使用示例
    app = FastAPI()
    register_exception_handlers(app)


    @app.get("/test/{item_id}")
    async def test_item(item_id: int):
        if item_id == 0:
            # 抛出参数错误异常
            raise ParamsError("ID不能为0")
        elif item_id == 1:
            # 抛出未登录异常
            raise NotLoginError()
        elif item_id == 2:
            # 抛出无权限异常
            raise NoAuthError("需要管理员权限")
        elif item_id == 3:
            # 抛出数据不存在异常
            raise NotFoundError("用户不存在")
        elif item_id == 4:
            # 抛出禁止访问异常
            raise ForbiddenError("IP被限制访问")
        elif item_id == 5:
            # 抛出操作失败异常
            raise OperationError("数据库更新失败")
        elif item_id == 999:
            # 触发未处理异常
            1 / 0

        return {"code": 0, "message": "成功", "data": {"id": item_id}}