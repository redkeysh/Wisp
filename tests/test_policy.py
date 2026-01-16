"""Tests for policy engine."""

import pytest

from wisp_framework.context import WispContext
from wisp_framework.policy.engine import PolicyEngine, PolicyResult


@pytest.mark.asyncio
async def test_policy_engine_no_db():
    """Test policy engine without database defaults to allow."""
    engine = PolicyEngine(None)
    from wisp_framework.config import AppConfig
    from wisp_framework.services.base import ServiceContainer

    config = AppConfig()
    services = ServiceContainer(config)
    ctx = WispContext(
        config=config,
        services=services,
        invocation_type="slash",
        guild_id=123,
        channel_id=456,
        user_id=789,
    )

    result = await engine.check("moderation.kick", ctx)
    assert result.allowed is True
    assert "defaulting to allow" in result.reason


@pytest.mark.asyncio
async def test_policy_result():
    """Test PolicyResult creation."""
    result = PolicyResult(
        allowed=True,
        reason="Test reason",
        explain_trace=[{"rule_id": 1, "action": "allow"}],
    )
    assert result.allowed is True
    assert result.reason == "Test reason"
    assert len(result.explain_trace) == 1
