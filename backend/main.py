import os
import time
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.utils.logger import logging
from app.utils.businessexception import register_exception_handlers
from app.core.cors import CORSSetup

app = FastAPI(title=settings.PROJECT_NAME, docs_url=None)

# 路径配置
settings.PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
logging.info(f"{settings.PROJECT_PATH} 已启动")

# 注册异常处理
register_exception_handlers(app)
logging.info("注册异常处理")

# 使用封装类配置 CORS
cors_setup = CORSSetup(
    app=app,
    allow_origins=settings.allow_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
).setup()
logging.info("CORS 配置完成")

# 挂载静态文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")

# 挂载认证路由
from app.api.auth import router as auth_router
app.include_router(auth_router, prefix=settings.API_V1_STR)

# 挂载文件上传路由
from app.api.upload import router as upload_router
app.include_router(upload_router, prefix=settings.API_V1_STR)

# 挂载OCR识别路由
from app.api.ocr import router as ocr_router
app.include_router(ocr_router, prefix=settings.API_V1_STR)

# 挂载分类路由
from app.api.classification import router as classification_router
app.include_router(classification_router, prefix=settings.API_V1_STR)

# 挂载日程路由
from app.api.schedule import router as schedule_router
app.include_router(schedule_router, prefix=settings.API_V1_STR)


# 自定义 Swagger 文档路由，指向本地的 Swagger UI 文件
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css"
    )


logging.info("路由配置完成")


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


# 添加中间件判断程序运行时间
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time) + "s"
    return response


if __name__ == "__main__":
    import uvicorn

    try:
        uvicorn.run(app, host=settings.HOST, port=settings.PORT)
        # uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
    except KeyboardInterrupt as e:
        print(f"{settings.API_V1_STR} 已关闭")
