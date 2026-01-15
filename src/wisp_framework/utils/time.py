"""Time utilities including uptime formatting."""

from datetime import datetime, timedelta
from typing import Optional


def format_uptime(start_time: datetime) -> str:
    """Format uptime as a human-readable string.

    Args:
        start_time: The time when the bot started

    Returns:
        Formatted uptime string (e.g., "2 days, 3 hours, 15 minutes")
    """
    delta = datetime.utcnow() - start_time
    total_seconds = int(delta.total_seconds())

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return ", ".join(parts)
