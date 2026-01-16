"""Tests for execution pipeline."""

import pytest

from wisp_framework.context import WispContext
from wisp_framework.core.pipeline import Pipeline, RequestIdMiddleware
from wisp_framework.exceptions import RateLimitedError


@pytest.mark.asyncio
async def test_pipeline_execution():
    """Test pipeline execution."""
    from wisp_framework.config import AppConfig
    from wisp_framework.services.base import ServiceContainer

    config = AppConfig()
    services = ServiceContainer(config)
    ctx = WispContext(
        config=config,
        services=services,
        invocation_type="slash",
    )

    pipeline = Pipeline(RequestIdMiddleware())

    async def handler(ctx: WispContext) -> str:
        return "success"

    result = await pipeline.execute(ctx, handler)
    assert result == "success"


@pytest.mark.asyncio
async def test_pipeline_error_handling():
    """Test pipeline error handling."""
    from wisp_framework.config import AppConfig
    from wisp_framework.services.base import ServiceContainer

    config = AppConfig()
    services = ServiceContainer(config)
    ctx = WispContext(
        config=config,
        services=services,
        invocation_type="slash",
    )

    pipeline = Pipeline(RequestIdMiddleware())

    async def handler(ctx: WispContext) -> str:
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        await pipeline.execute(ctx, handler)
