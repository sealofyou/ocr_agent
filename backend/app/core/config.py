from typing import Optional, Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl
import os


class Settings(BaseSettings):
    # 项目配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Text Archive Assistant"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 1  # 进程数

    # 项目路径
    PROJECT_PATH: str = ""

    # 跨域配置
    allow_origins: list[str] = [
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://192.168.1.4:5173"
    ]
    allow_credentials: bool = True
    allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE"]
    allow_headers: list[str] = ["*"]

    # 日志配置
    LOG_NAME: str = "app"
    LOG_LEVEL: int = 20  # DEBUG = 10, INFO = 20, WARNING = 30, ERROR = 40, CRITICAL = 50
    LOG_WHEN: str = "D"
    LOG_BACKUP_COUNT: int = 5

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./text_archive.db"
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_FORMATS: list[str] = ["jpg", "jpeg", "png", "bmp"]
    UPLOAD_DIR: str = "uploads"

    # OCR配置
    OCR_LANG: str = "ch"  # 中文
    OCR_USE_GPU: bool = False

    # LLM配置
    LLM_API_URL: str = "http://localhost:3001/v1/chat/completions"
    LLM_MODEL: str = "Qwen/Qwen2-VL-7B-Instruct"
    LLM_ENABLED: bool = True

    # Redis配置(可选)
    REDIS_URL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
