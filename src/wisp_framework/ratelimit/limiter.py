"""Token bucket rate limiter."""

import logging
import time

from wisp_framework.context import WispContext
from wisp_framework.services.cache import CacheService

logger = logging.getLogger(__name__)


class RateLimiter:
    """Base rate limiter interface."""

    async def check(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Check if request is within rate limit.

        Args:
            key: Rate limit key (e.g., "user:123", "guild:456")
            limit: Maximum requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (allowed, remaining)
        """
        raise NotImplementedError


class TokenBucketLimiter(RateLimiter):
    """Token bucket rate limiter with Redis backend."""

    def __init__(self, cache_service: CacheService | None = None) -> None:
        """Initialize token bucket limiter.

        Args:
            cache_service: Optional cache service (Redis) for distributed limiting
        """
        self._cache = cache_service
        self._memory_buckets: dict[str, tuple[float, int]] = {}  # key -> (last_refill, tokens)

    async def check(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Check if request is within rate limit using token bucket algorithm.

        Args:
            key: Rate limit key
            limit: Maximum tokens (requests)
            window: Refill window in seconds

        Returns:
            Tuple of (allowed, remaining_tokens)
        """
        cache_key = f"ratelimit:{key}"

        if self._cache:
            # Try Redis first
            try:
                return await self._check_redis(cache_key, limit, window)
            except Exception as e:
                logger.warning(f"Redis rate limit check failed: {e}, falling back to memory")

        # Fall back to memory
        return self._check_memory(key, limit, window)

    async def _check_redis(
        self, cache_key: str, limit: int, window: int
    ) -> tuple[bool, int]:
        """Check rate limit using Redis.

        Args:
            cache_key: Cache key
            limit: Maximum tokens
            window: Refill window

        Returns:
            Tuple of (allowed, remaining)
        """
        # Simplified Redis implementation
        # In production, would use Lua script for atomic operations
        import json

        data_str = await self._cache.get(cache_key)
        if data_str:
            data = json.loads(data_str)
            tokens = data.get("tokens", limit)
            last_refill = data.get("last_refill", time.time())
        else:
            tokens = limit
            last_refill = time.time()

        # Refill tokens
        now = time.time()
        elapsed = now - last_refill
        refill_amount = int((elapsed / window) * limit)
        if refill_amount > 0:
            tokens = min(limit, tokens + refill_amount)
            last_refill = now

        # Check if we can consume a token
        if tokens > 0:
            tokens -= 1
            allowed = True
        else:
            allowed = False

        # Store updated state
        await self._cache.set(
            cache_key,
            json.dumps({"tokens": tokens, "last_refill": last_refill}),
            ttl=window * 2,
        )

        return (allowed, tokens)

    def _check_memory(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Check rate limit using in-memory storage.

        Args:
            key: Rate limit key
            limit: Maximum tokens
            window: Refill window

        Returns:
            Tuple of (allowed, remaining)
        """
        now = time.time()

        if key in self._memory_buckets:
            last_refill, tokens = self._memory_buckets[key]
            # Refill tokens
            elapsed = now - last_refill
            refill_amount = int((elapsed / window) * limit)
            if refill_amount > 0:
                tokens = min(limit, tokens + refill_amount)
                last_refill = now
        else:
            tokens = limit
            last_refill = now

        # Check if we can consume a token
        if tokens > 0:
            tokens -= 1
            allowed = True
        else:
            allowed = False

        # Store updated state
        self._memory_buckets[key] = (last_refill, tokens)

        # Clean up old entries
        if len(self._memory_buckets) > 10000:
            # Keep only recent entries
            cutoff = now - window * 10
            self._memory_buckets = {
                k: v
                for k, v in self._memory_buckets.items()
                if v[0] > cutoff
            }

        return (allowed, tokens)


def get_rate_limit_key(ctx: WispContext, scope: str = "user") -> str:
    """Get rate limit key for context.

    Args:
        ctx: WispContext
        scope: Scope type ("user", "guild", "channel", "command")

    Returns:
        Rate limit key string
    """
    if scope == "user" and ctx.user_id:
        return f"user:{ctx.user_id}"
    elif scope == "guild" and ctx.guild_id:
        return f"guild:{ctx.guild_id}"
    elif scope == "channel" and ctx.channel_id:
        return f"channel:{ctx.channel_id}"
    else:
        return f"global:{scope}"
