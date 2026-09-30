from typing import Optional
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger

redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> Optional[aioredis.Redis]:
    """Initialize Redis connection pool."""
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info("Redis connection established successfully.")
        return redis_client
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        return None


async def close_redis() -> None:
    """Close Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed.")


def get_redis() -> Optional[aioredis.Redis]:
    """Dependency to retrieve the active Redis client."""
    return redis_client
