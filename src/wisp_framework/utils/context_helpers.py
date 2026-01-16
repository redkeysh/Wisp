"""Helper functions for working with WispContext in modules."""

from typing import Any

import discord
from discord.ext import commands

from wisp_framework.context import WispContext


def get_wisp_context_from_interaction(
    bot: Any,
    interaction: discord.Interaction,
    invocation_type: str = "slash",
) -> WispContext:
    """Get WispContext from an interaction.

    Helper function for modules to create WispContext in command handlers.

    Args:
        bot: Bot instance (must have config, services, module_registry)
        interaction: Discord interaction
        invocation_type: Type of invocation ("slash" or "prefix")

    Returns:
        WispContext instance
    """
    return WispContext.from_interaction(
        config=bot.config,
        services=bot.services,
        interaction=interaction,
        invocation_type=invocation_type,
        feature_flags=bot.module_registry._feature_flags,
    )


def get_wisp_context_from_command_context(
    bot: Any,
    ctx: commands.Context,
) -> WispContext:
    """Get WispContext from a commands.Context.

    Helper function for modules to create WispContext in prefix command handlers.

    Args:
        bot: Bot instance (must have config, services, module_registry)
        ctx: Discord commands.Context

    Returns:
        WispContext instance
    """
    return WispContext.from_interaction(
        config=bot.config,
        services=bot.services,
        interaction=ctx,
        invocation_type="prefix",
        feature_flags=bot.module_registry._feature_flags,
    )


def get_wisp_context_from_event(
    bot: Any,
    event: Any,
) -> WispContext:
    """Get WispContext from a Discord event.

    Helper function for modules to create WispContext in event handlers.

    Args:
        bot: Bot instance (must have config, services, module_registry)
        event: Discord event object (message, member, etc.)

    Returns:
        WispContext instance
    """
    return WispContext.from_event(
        config=bot.config,
        services=bot.services,
        event=event,
        feature_flags=bot.module_registry._feature_flags,
    )
