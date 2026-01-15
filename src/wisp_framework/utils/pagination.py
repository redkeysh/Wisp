"""Pagination utilities for Discord embeds and messages."""

from typing import Any, Callable, Optional

import discord
from discord import Interaction


class Paginator:
    """Paginator for Discord embeds with button navigation."""

    def __init__(
        self,
        interaction: Interaction,
        pages: list[discord.Embed],
        timeout: float = 300.0,
        ephemeral: bool = False,
    ) -> None:
        """Initialize paginator.

        Args:
            interaction: Discord interaction
            pages: List of embeds (one per page)
            timeout: Button timeout in seconds
            ephemeral: Whether response is ephemeral
        """
        self.interaction = interaction
        self.pages = pages
        self.timeout = timeout
        self.ephemeral = ephemeral
        self.current_page = 0
        self.view: Optional[PaginatorView] = None

    async def start(self) -> None:
        """Start the paginator."""
        if not self.pages:
            await self.interaction.response.send_message(
                "No pages to display.", ephemeral=True
            )
            return

        self.view = PaginatorView(self, self.timeout)
        await self.interaction.response.send_message(
            embed=self.pages[0], view=self.view, ephemeral=self.ephemeral
        )

    async def update_page(self, page: int) -> None:
        """Update to a specific page."""
        if 0 <= page < len(self.pages):
            self.current_page = page
            if self.view:
                await self.interaction.edit_original_response(
                    embed=self.pages[page], view=self.view
                )


class PaginatorView(discord.ui.View):
    """View for paginator buttons."""

    def __init__(self, paginator: Paginator, timeout: float = 300.0) -> None:
        """Initialize paginator view."""
        super().__init__(timeout=timeout)
        self.paginator = paginator
        self._update_buttons()

    def _update_buttons(self) -> None:
        """Update button states."""
        # Clear existing buttons
        self.clear_items()

        # First page button
        first_btn = discord.ui.Button(
            label="⏮️",
            style=discord.ButtonStyle.secondary,
            disabled=self.paginator.current_page == 0,
        )
        first_btn.callback = lambda i: self._on_first(i)
        self.add_item(first_btn)

        # Previous page button
        prev_btn = discord.ui.Button(
            label="◀️",
            style=discord.ButtonStyle.secondary,
            disabled=self.paginator.current_page == 0,
        )
        prev_btn.callback = lambda i: self._on_prev(i)
        self.add_item(prev_btn)

        # Page indicator
        page_btn = discord.ui.Button(
            label=f"{self.paginator.current_page + 1}/{len(self.paginator.pages)}",
            style=discord.ButtonStyle.primary,
            disabled=True,
        )
        self.add_item(page_btn)

        # Next page button
        next_btn = discord.ui.Button(
            label="▶️",
            style=discord.ButtonStyle.secondary,
            disabled=self.paginator.current_page >= len(self.paginator.pages) - 1,
        )
        next_btn.callback = lambda i: self._on_next(i)
        self.add_item(next_btn)

        # Last page button
        last_btn = discord.ui.Button(
            label="⏭️",
            style=discord.ButtonStyle.secondary,
            disabled=self.paginator.current_page >= len(self.paginator.pages) - 1,
        )
        last_btn.callback = lambda i: self._on_last(i)
        self.add_item(last_btn)

    async def _on_first(self, interaction: Interaction) -> None:
        """Handle first page button."""
        await self.paginator.update_page(0)
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.paginator.pages[self.paginator.current_page], view=self
        )

    async def _on_prev(self, interaction: Interaction) -> None:
        """Handle previous page button."""
        if self.paginator.current_page > 0:
            await self.paginator.update_page(self.paginator.current_page - 1)
            self._update_buttons()
            await interaction.response.edit_message(
                embed=self.paginator.pages[self.paginator.current_page], view=self
            )

    async def _on_next(self, interaction: Interaction) -> None:
        """Handle next page button."""
        if self.paginator.current_page < len(self.paginator.pages) - 1:
            await self.paginator.update_page(self.paginator.current_page + 1)
            self._update_buttons()
            await interaction.response.edit_message(
                embed=self.paginator.pages[self.paginator.current_page], view=self
            )

    async def _on_last(self, interaction: Interaction) -> None:
        """Handle last page button."""
        await self.paginator.update_page(len(self.paginator.pages) - 1)
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.paginator.pages[self.paginator.current_page], view=self
        )

    async def on_timeout(self) -> None:
        """Handle view timeout."""
        # Disable all buttons
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        # Try to edit the message to remove buttons
        try:
            await self.paginator.interaction.edit_original_response(view=self)
        except Exception:
            pass


async def paginate_embeds(
    interaction: Interaction,
    embeds: list[discord.Embed],
    timeout: float = 300.0,
    ephemeral: bool = False,
) -> None:
    """Convenience function to paginate embeds.

    Args:
        interaction: Discord interaction
        embeds: List of embeds to paginate
        timeout: Button timeout in seconds
        ephemeral: Whether response is ephemeral
    """
    paginator = Paginator(interaction, embeds, timeout, ephemeral)
    await paginator.start()
