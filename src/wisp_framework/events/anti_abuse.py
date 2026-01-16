"""Anti-abuse filters for event processing."""

import logging
from typing import Any

from wisp_framework.context import WispContext

logger = logging.getLogger(__name__)


class AntiAbuseFilter:
    """Anti-abuse filter to prevent loops and abuse."""

    def __init__(self) -> None:
        """Initialize anti-abuse filter."""
        self._recent_messages: dict[int, list[float]] = {}  # user_id -> timestamps
        self._bot_responses: set[int] = set()  # message IDs we've responded to

    async def should_process_message(
        self, message: Any, ctx: WispContext, bot_user_id: int
    ) -> bool:
        """Check if a message should be processed.

        Args:
            message: Discord message object
            ctx: WispContext
            bot_user_id: Bot's user ID

        Returns:
            True if message should be processed
        """
        # Prevent responding to own messages
        if hasattr(message, "author") and message.author.id == bot_user_id:
            return False

        # Prevent ping-pong with other bots
        if hasattr(message, "author") and hasattr(message.author, "bot") and message.author.bot:
            # Check if this is a response to our message
            if hasattr(message, "reference") and message.reference:
                if message.reference.message_id in self._bot_responses:
                    return False

        return True

    def record_response(self, message_id: int) -> None:
        """Record that we responded to a message.

        Args:
            message_id: Message ID we responded to
        """
        self._bot_responses.add(message_id)
        # Clean up old entries (keep last 1000)
        if len(self._bot_responses) > 1000:
            self._bot_responses = set(list(self._bot_responses)[-1000:])
