from app.core.config import settings
import redis

def init_cache():
    cache = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    return cache


cache = init_cache()
