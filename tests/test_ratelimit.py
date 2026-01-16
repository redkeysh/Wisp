"""Tests for rate limiting."""

import pytest

from wisp_framework.ratelimit.limiter import TokenBucketLimiter, get_rate_limit_key


def test_get_rate_limit_key():
    """Test rate limit key generation."""
    from wisp_framework.config import AppConfig
    from wisp_framework.services.base import ServiceContainer

    config = AppConfig()
    services = ServiceContainer(config)
    ctx = WispContext(
        config=config,
        services=services,
        invocation_type="slash",
        user_id=123,
        guild_id=456,
        channel_id=789,
    )

    assert get_rate_limit_key(ctx, "user") == "user:123"
    assert get_rate_limit_key(ctx, "guild") == "guild:456"
    assert get_rate_limit_key(ctx, "channel") == "channel:789"


@pytest.mark.asyncio
async def test_token_bucket_limiter():
    """Test token bucket limiter."""
    limiter = TokenBucketLimiter(None)  # No cache, use memory

    # First request should be allowed
    allowed, remaining = limiter._check_memory("test_key", limit=10, window=60)
    assert allowed is True
    assert remaining == 9

    # Exhaust tokens
    for _ in range(9):
        allowed, remaining = limiter._check_memory("test_key", limit=10, window=60)
    assert remaining == 0

    # Next request should be denied
    allowed, remaining = limiter._check_memory("test_key", limit=10, window=60)
    assert allowed is False
    assert remaining == 0
