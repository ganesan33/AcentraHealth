from typing import Optional, Any
from app.core.redis import get_redis
from app.core.logging import logger


class RedisIntegrationService:
    """Service wrapper for interacting with Redis cache and velocity keys."""

    async def get_key(self, key: str) -> Optional[str]:
        redis = get_redis()
        if not redis:
            logger.warning("Redis client not initialized.")
            return None
        return await redis.get(key)

    async def set_key(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        redis = get_redis()
        if not redis:
            logger.warning("Redis client not initialized.")
            return False
        if expire_seconds:
            await redis.setex(key, expire_seconds, str(value))
        else:
            await redis.set(key, str(value))
        return True

    async def increment_key(self, key: str, amount: int = 1) -> Optional[int]:
        redis = get_redis()
        if not redis:
            logger.warning("Redis client not initialized.")
            return None
        return await redis.incrby(key, amount)


redis_service = RedisIntegrationService()
