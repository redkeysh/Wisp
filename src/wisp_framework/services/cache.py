"""Cache service with in-memory and optional Redis support."""

import logging
from typing import Any

from wisp_framework.services.base import BaseService

logger = logging.getLogger(__name__)


class CacheService(BaseService):
    """Cache service with in-memory storage and optional Redis backend."""

    def __init__(self, config: Any) -> None:
        """Initialize the cache service."""
        super().__init__(config)
        self._memory_cache: dict[str, tuple[Any, float | None]] = {}
        self._redis_client: Any | None = None
        self._use_redis = False

    async def startup(self) -> None:
        """Start up the cache service."""
        redis_url = self.config.redis_url
        if redis_url:
            try:
                import redis.asyncio as redis

                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                await self._redis_client.ping()
                self._use_redis = True
                logger.info("Cache service started with Redis backend")
            except ImportError:
                logger.warning(
                    "Redis URL provided but redis package not installed. "
                    "Falling back to in-memory cache."
                )
            except Exception as e:
                logger.warning(
                    f"Failed to connect to Redis: {e}. Falling back to in-memory cache."
                )
                self._redis_client = None

        if not self._use_redis:
            logger.info("Cache service started with in-memory backend")
        self._mark_initialized()

    async def shutdown(self) -> None:
        """Shut down the cache service."""
        if self._redis_client:
            await self._redis_client.aclose()
            self._redis_client = None
        self._memory_cache.clear()
        logger.info("Cache service shut down")

    async def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        if self._use_redis and self._redis_client:
            try:
                value = await self._redis_client.get(key)
                return value if value is not None else None
            except Exception as e:
                logger.warning(f"Redis get failed: {e}, falling back to memory")
                return self._memory_get(key)

        return self._memory_get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in cache with optional TTL."""
        if self._use_redis and self._redis_client:
            try:
                if ttl:
                    await self._redis_client.setex(key, ttl, str(value))
                else:
                    await self._redis_client.set(key, str(value))
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}, falling back to memory")

        self._memory_set(key, value, ttl)

    async def delete(self, key: str) -> None:
        """Delete a value from cache."""
        if self._use_redis and self._redis_client:
            try:
                await self._redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")

        self._memory_cache.pop(key, None)

    async def clear(self) -> None:
        """Clear all cache."""
        if self._use_redis and self._redis_client:
            try:
                await self._redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Redis clear failed: {e}")

        self._memory_cache.clear()

    def _memory_get(self, key: str) -> Any | None:
        """Get from memory cache."""
        if key not in self._memory_cache:
            return None

        value, expiry = self._memory_cache[key]
        if expiry is not None:
            import time

            if time.time() > expiry:
                del self._memory_cache[key]
                return None

        return value

    def _memory_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set in memory cache."""
        import time

        expiry = None
        if ttl:
            expiry = time.time() + ttl

        self._memory_cache[key] = (value, expiry)
