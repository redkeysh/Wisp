"""Decorators for commands and modules."""

import functools
from typing import Any, Callable, Optional

import discord
from discord import Interaction

from wisp_framework.utils.permissions import is_admin, is_owner
from wisp_framework.utils.responses import respond_error


def require_guild(func: Callable) -> Callable:
    """Decorator to require command to be used in a guild.

    Args:
        func: Command function

    Returns:
        Decorated function
    """

    @functools.wraps(func)
    async def wrapper(interaction: Interaction, *args: Any, **kwargs: Any) -> Any:
        if not interaction.guild:
            await respond_error(
                interaction, "This command can only be used in a server.", ephemeral=True
            )
            return
        return await func(interaction, *args, **kwargs)

    return wrapper


def require_owner(config: Any):
    """Decorator factory to require bot owner.

    Args:
        config: AppConfig instance

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(interaction: Interaction, *args: Any, **kwargs: Any) -> Any:
            if not is_owner(interaction, config):
                await respond_error(
                    interaction, "Only the bot owner can use this command.", ephemeral=True
                )
                return
            return await func(interaction, *args, **kwargs)

        return wrapper

    return decorator


def require_admin(func: Callable) -> Callable:
    """Decorator to require administrator permissions.

    Args:
        func: Command function

    Returns:
        Decorated function
    """

    @functools.wraps(func)
    async def wrapper(interaction: Interaction, *args: Any, **kwargs: Any) -> Any:
        if not is_admin(interaction):
            await respond_error(
                interaction,
                "You don't have permission to use this command.",
                ephemeral=True,
            )
            return
        return await func(interaction, *args, **kwargs)

    return wrapper


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors gracefully.

    Args:
        func: Command function

    Returns:
        Decorated function
    """

    @functools.wraps(func)
    async def wrapper(interaction: Interaction, *args: Any, **kwargs: Any) -> Any:
        try:
            return await func(interaction, *args, **kwargs)
        except Exception as e:
            import logging

            logger = logging.getLogger(func.__module__)
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)

            await respond_error(
                interaction,
                f"An error occurred: {str(e)}",
                ephemeral=True,
            )

    return wrapper
