"""Helper functions for creating branded embeds with WispContext."""

from typing import Any

import discord

from wisp_framework.context import WispContext
from wisp_framework.utils.embeds import EmbedBuilder


def create_branded_embed(
    ctx: WispContext,
    embed_type: str = "info",
    title: str = "",
    description: str | None = None,
    fields: list[dict[str, Any]] | None = None,
    footer: str | None = None,
    **kwargs: Any,
) -> discord.Embed:
    """Create a branded embed using WispContext's config.

    This is a convenience function that automatically applies branding
    from the bot's AppConfig.

    Args:
        ctx: WispContext (provides config for branding)
        embed_type: Type of embed ("success", "error", "info", "warning")
        title: Embed title
        description: Embed description
        fields: List of field dicts
        footer: Footer text (appended to branded footer)
        **kwargs: Additional arguments passed to EmbedBuilder

    Returns:
        Branded Discord embed

    Example:
        ```python
        wisp_ctx = get_wisp_context_from_interaction(bot, interaction, "slash")
        embed = create_branded_embed(
            wisp_ctx,
            embed_type="success",
            title="Operation Complete",
            description="Your operation was successful!",
            footer="Request ID: " + wisp_ctx.request_id
        )
        await interaction.response.send_message(embed=embed)
        ```
    """
    config = ctx.config

    if embed_type == "success":
        return EmbedBuilder.success(
            title=title,
            description=description,
            fields=fields,
            footer=footer,
            config=config,
            use_branding=True,
            **kwargs,
        )
    elif embed_type == "error":
        return EmbedBuilder.error(
            title=title,
            description=description,
            fields=fields,
            footer=footer,
            config=config,
            use_branding=True,
            **kwargs,
        )
    elif embed_type == "warning":
        return EmbedBuilder.warning(
            title=title,
            description=description,
            fields=fields,
            footer=footer,
            config=config,
            use_branding=True,
            **kwargs,
        )
    else:  # info or default
        return EmbedBuilder.info(
            title=title,
            description=description,
            fields=fields,
            footer=footer,
            config=config,
            use_branding=True,
            **kwargs,
        )
