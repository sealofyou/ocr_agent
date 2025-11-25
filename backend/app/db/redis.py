from redis import Redis
from app.core.config import settings

# 按需初始化Redis
redis_client = None
if settings.REDIS_URL:
    redis_client = Redis.from_url(settings.REDIS_URL)

def get_redis():
    """获取Redis连接"""
    if not redis_client:
        raise RuntimeError("Redis not configured")
    return redis_client