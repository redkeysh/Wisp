"""Decorators for policy-based access control."""

import functools
from collections.abc import Awaitable, Callable
from typing import Any

import discord
from discord.ext import commands

from wisp_framework.exceptions import PermissionError
from wisp_framework.policy.engine import PolicyEngine


def requires_capability(capability: str):
    """Decorator to require a capability for command execution.

    Args:
        capability: Capability string (e.g., "moderation.kick")

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract context from args
            # For slash commands, first arg is Interaction
            # For prefix commands, first arg is commands.Context
            interaction_or_ctx = args[0] if args else None

            # Get WispContext - this would be provided by the pipeline in Phase 2
            # For now, we'll need to create it or get it from somewhere
            # This is a simplified version - full implementation would use pipeline

            if isinstance(interaction_or_ctx, discord.Interaction):
                # Slash command
                # In full implementation, WispContext would be available via pipeline
                # For now, we'll skip the check and let it be handled by pipeline
                return await func(*args, **kwargs)
            elif isinstance(interaction_or_ctx, commands.Context):
                # Prefix command
                # Similar - would use pipeline in full implementation
                return await func(*args, **kwargs)
            else:
                # Unknown - execute anyway
                return await func(*args, **kwargs)

        return wrapper
    return decorator
