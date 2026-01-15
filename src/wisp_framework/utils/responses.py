"""Response helpers for Discord interactions."""


import discord
from discord import Interaction, Webhook


class ResponseHelper:
    """Helper class for sending common response patterns."""

    @staticmethod
    async def success(
        interaction: Interaction,
        message: str,
        embed: discord.Embed | None = None,
        ephemeral: bool = True,
    ) -> Webhook | None:
        """Send a success response.

        Args:
            interaction: Discord interaction
            message: Success message
            embed: Optional embed
            ephemeral: Whether response is ephemeral

        Returns:
            Webhook message
        """
        if interaction.response.is_done():
            return await interaction.followup.send(
                content=message, embed=embed, ephemeral=ephemeral
            )
        else:
            await interaction.response.send_message(
                content=message, embed=embed, ephemeral=ephemeral
            )
            return None

    @staticmethod
    async def error(
        interaction: Interaction,
        message: str,
        embed: discord.Embed | None = None,
        ephemeral: bool = True,
    ) -> Webhook | None:
        """Send an error response.

        Args:
            interaction: Discord interaction
            message: Error message
            embed: Optional embed
            ephemeral: Whether response is ephemeral

        Returns:
            Webhook message
        """
        if interaction.response.is_done():
            return await interaction.followup.send(
                content=message, embed=embed, ephemeral=ephemeral
            )
        else:
            await interaction.response.send_message(
                content=message, embed=embed, ephemeral=ephemeral
            )
            return None

    @staticmethod
    async def info(
        interaction: Interaction,
        message: str,
        embed: discord.Embed | None = None,
        ephemeral: bool = True,
    ) -> Webhook | None:
        """Send an info response.

        Args:
            interaction: Discord interaction
            message: Info message
            embed: Optional embed
            ephemeral: Whether response is ephemeral

        Returns:
            Webhook message
        """
        if interaction.response.is_done():
            return await interaction.followup.send(
                content=message, embed=embed, ephemeral=ephemeral
            )
        else:
            await interaction.response.send_message(
                content=message, embed=embed, ephemeral=ephemeral
            )
            return None

    @staticmethod
    async def send_embed(
        interaction: Interaction,
        embed: discord.Embed,
        ephemeral: bool = True,
    ) -> Webhook | None:
        """Send an embed response.

        Args:
            interaction: Discord interaction
            embed: Embed to send
            ephemeral: Whether response is ephemeral

        Returns:
            Webhook message
        """
        if interaction.response.is_done():
            return await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
            return None

    @staticmethod
    async def defer(
        interaction: Interaction,
        ephemeral: bool = True,
    ) -> None:
        """Defer the interaction response.

        Args:
            interaction: Discord interaction
            ephemeral: Whether response is ephemeral
        """
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=ephemeral)

    @staticmethod
    async def edit_response(
        interaction: Interaction,
        content: str | None = None,
        embed: discord.Embed | None = None,
    ) -> discord.Message:
        """Edit the original interaction response.

        Args:
            interaction: Discord interaction
            content: New content
            embed: New embed

        Returns:
            Edited message
        """
        return await interaction.edit_original_response(content=content, embed=embed)


# Convenience functions
async def respond_success(
    interaction: Interaction,
    message: str,
    embed: discord.Embed | None = None,
    ephemeral: bool = True,
) -> Webhook | None:
    """Send a success response."""
    return await ResponseHelper.success(interaction, message, embed, ephemeral)


async def respond_error(
    interaction: Interaction,
    message: str,
    embed: discord.Embed | None = None,
    ephemeral: bool = True,
) -> Webhook | None:
    """Send an error response."""
    return await ResponseHelper.error(interaction, message, embed, ephemeral)


async def respond_info(
    interaction: Interaction,
    message: str,
    embed: discord.Embed | None = None,
    ephemeral: bool = True,
) -> Webhook | None:
    """Send an info response."""
    return await ResponseHelper.info(interaction, message, embed, ephemeral)


async def respond_embed(
    interaction: Interaction,
    embed: discord.Embed,
    ephemeral: bool = True,
) -> Webhook | None:
    """Send an embed response."""
    return await ResponseHelper.send_embed(interaction, embed, ephemeral)
