"""Confirmation dialogs for destructive actions."""

from collections.abc import Callable

import discord
from discord import Interaction


class ConfirmationView(discord.ui.View):
    """View for confirmation dialogs."""

    def __init__(
        self,
        on_confirm: Callable[[Interaction], None],
        on_cancel: Callable[[Interaction], None] | None = None,
        timeout: float = 60.0,
    ) -> None:
        """Initialize confirmation view.

        Args:
            on_confirm: Callback when confirmed
            on_cancel: Optional callback when cancelled
            timeout: View timeout in seconds
        """
        super().__init__(timeout=timeout)
        self.on_confirm_callback = on_confirm
        self.on_cancel_callback = on_cancel
        self.confirmed = False

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Handle confirm button."""
        self.confirmed = True
        self.stop()
        await self.on_confirm_callback(interaction)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Handle cancel button."""
        self.stop()
        if self.on_cancel_callback:
            await self.on_cancel_callback(interaction)
        else:
            await interaction.response.edit_message(
                content="❌ Action cancelled.", view=None
            )

    async def on_timeout(self) -> None:
        """Handle view timeout."""
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True


async def confirm_action(
    interaction: Interaction,
    message: str,
    on_confirm: Callable[[Interaction], None],
    embed: discord.Embed | None = None,
    on_cancel: Callable[[Interaction], None] | None = None,
    timeout: float = 60.0,
) -> None:
    """Show a confirmation dialog.

    Args:
        interaction: Discord interaction
        message: Confirmation message
        embed: Optional embed
        on_confirm: Callback when confirmed
        on_cancel: Optional callback when cancelled
        timeout: View timeout in seconds
    """
    view = ConfirmationView(on_confirm, on_cancel, timeout)

    if interaction.response.is_done():
        await interaction.followup.send(content=message, embed=embed, view=view)
    else:
        await interaction.response.send_message(content=message, embed=embed, view=view)
