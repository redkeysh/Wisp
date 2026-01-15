"""Testing utilities for Discord bots."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock


class MockInteraction:
    """Mock Discord interaction for testing."""

    def __init__(
        self,
        user_id: int = 123456789,
        guild_id: int | None = 123456789,
        channel_id: int | None = 123456789,
    ) -> None:
        """Initialize mock interaction.

        Args:
            user_id: Mock user ID
            guild_id: Mock guild ID
            channel_id: Mock channel ID
        """
        self.user = MagicMock()
        self.user.id = user_id
        self.user.mention = f"<@{user_id}>"
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.guild = MagicMock() if guild_id else None
        if self.guild:
            self.guild.id = guild_id
        self.channel = MagicMock() if channel_id else None
        if self.channel:
            self.channel.id = channel_id
        self.response = AsyncMock()
        self.response.is_done = MagicMock(return_value=False)
        self.followup = AsyncMock()
        self.command = MagicMock()
        self.command.name = "test_command"


class MockBot:
    """Mock Discord bot for testing."""

    def __init__(self) -> None:
        """Initialize mock bot."""
        self.user = MagicMock()
        self.user.id = 987654321
        self.guilds = []
        self.users = []
        self.tree = MagicMock()
        self.latency = 0.05


class MockContext:
    """Mock bot context for testing."""

    def __init__(self) -> None:
        """Initialize mock context."""
        self.config = MagicMock()
        self.services = MagicMock()
        self.guild_data = AsyncMock()


def create_mock_interaction(**kwargs: Any) -> MockInteraction:
    """Create a mock interaction.

    Args:
        **kwargs: Optional parameters for MockInteraction

    Returns:
        Mock interaction
    """
    return MockInteraction(**kwargs)


def create_mock_bot(**kwargs: Any) -> MockBot:
    """Create a mock bot.

    Args:
        **kwargs: Optional parameters for MockBot

    Returns:
        Mock bot
    """
    return MockBot(**kwargs)


def create_mock_context(**kwargs: Any) -> MockContext:
    """Create a mock context.

    Args:
        **kwargs: Optional parameters for MockContext

    Returns:
        Mock context
    """
    return MockContext(**kwargs)
