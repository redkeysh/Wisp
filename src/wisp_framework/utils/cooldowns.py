"""Cooldown system for commands and users."""

import time
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from discord import Interaction


class CooldownManager:
    """Manages cooldowns for commands and users."""

    def __init__(self) -> None:
        """Initialize cooldown manager."""
        self._cooldowns: dict[str, dict[int, float]] = defaultdict(dict)

    def check_cooldown(
        self, key: str, user_id: int, cooldown_seconds: float
    ) -> tuple[bool, float]:
        """Check if a cooldown has expired.

        Args:
            key: Cooldown key (e.g., command name)
            user_id: User ID
            cooldown_seconds: Cooldown duration in seconds

        Returns:
            Tuple of (is_ready, remaining_seconds)
        """
        now = time.time()
        last_used = self._cooldowns[key].get(user_id, 0)
        elapsed = now - last_used

        if elapsed >= cooldown_seconds:
            return True, 0.0
        else:
            remaining = cooldown_seconds - elapsed
            return False, remaining

    def set_cooldown(self, key: str, user_id: int) -> None:
        """Set a cooldown for a key and user.

        Args:
            key: Cooldown key
            user_id: User ID
        """
        self._cooldowns[key][user_id] = time.time()

    def reset_cooldown(self, key: str, user_id: int | None = None) -> None:
        """Reset cooldown for a key and optionally a user.

        Args:
            key: Cooldown key
            user_id: Optional user ID (resets all users if None)
        """
        if user_id is None:
            self._cooldowns[key].clear()
        else:
            self._cooldowns[key].pop(user_id, None)


# Global cooldown manager instance
_cooldown_manager = CooldownManager()


def cooldown(seconds: float, per_user: bool = True):
    """Decorator to add cooldown to a command.

    Args:
        seconds: Cooldown duration in seconds
        per_user: Whether cooldown is per-user (True) or global (False)

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(interaction: Interaction, *args: Any, **kwargs: Any) -> Any:
            key = f"{func.__module__}.{func.__name__}"
            user_id = interaction.user.id if per_user else 0

            is_ready, remaining = _cooldown_manager.check_cooldown(key, user_id, seconds)

            if not is_ready:
                from wisp_framework.utils.responses import respond_error

                await respond_error(
                    interaction,
                    f"⏱️ Please wait {remaining:.1f} seconds before using this command again.",
                    ephemeral=True,
                )
                return

            _cooldown_manager.set_cooldown(key, user_id)
            return await func(interaction, *args, **kwargs)

        return wrapper

    return decorator
