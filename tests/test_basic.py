"""Basic tests for Wisp Framework."""

import pytest


def test_imports():
    """Test that core modules can be imported."""
    from wisp_framework import WispBot, create_app, Module
    from wisp_framework.config import AppConfig
    from wisp_framework.context import BotContext

    assert WispBot is not None
    assert create_app is not None
    assert Module is not None
    assert AppConfig is not None
    assert BotContext is not None


def test_module_base():
    """Test Module base class."""
    from wisp_framework.module import Module

    # Module is abstract, so we can't instantiate it directly
    assert Module is not None


def test_config_class():
    """Test AppConfig class exists."""
    from wisp_framework.config import AppConfig

    assert AppConfig is not None
    assert hasattr(AppConfig, "discord_token")


@pytest.mark.asyncio
async def test_module_setup_teardown():
    """Test that Module setup/teardown methods exist."""
    from wisp_framework.module import Module
    from unittest.mock import MagicMock

    # Create a concrete implementation
    class TestModule(Module):
        @property
        def name(self) -> str:
            return "test"

        async def setup(self, bot, ctx):
            pass

    module = TestModule()
    assert module.name == "test"
    assert hasattr(module, "setup")
    assert hasattr(module, "teardown")

    # Test teardown can be called (it's optional)
    mock_bot = MagicMock()
    mock_ctx = MagicMock()
    await module.teardown(mock_bot, mock_ctx)  # Should not raise
