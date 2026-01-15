"""Permission check utilities for owner/admin checks."""


import discord
from discord import Interaction

from wisp_framework.config import AppConfig


def is_owner(interaction: Interaction, config: AppConfig) -> bool:
    """Check if the user is the bot owner.

    Args:
        interaction: Discord interaction
        config: Application configuration

    Returns:
        True if user is owner, False otherwise
    """
    if not config.owner_id:
        return False
    return interaction.user.id == config.owner_id


def is_admin(interaction: Interaction) -> bool:
    """Check if the user has administrator permissions.

    Args:
        interaction: Discord interaction

    Returns:
        True if user has admin permissions, False otherwise
    """
    if not interaction.guild:
        return False

    if not isinstance(interaction.user, discord.Member):
        return False

    return interaction.user.guild_permissions.administrator
