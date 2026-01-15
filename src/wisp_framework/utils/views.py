"""View helpers for Discord UI components."""

from collections.abc import Callable
from typing import Any

import discord
from discord import Interaction


class ButtonView(discord.ui.View):
    """Helper view for creating button-based interactions."""

    def __init__(self, timeout: float = 300.0) -> None:
        """Initialize button view.

        Args:
            timeout: View timeout in seconds
        """
        super().__init__(timeout=timeout)
        self._callbacks: dict[str, Callable[[Interaction], Any]] = {}

    def add_button(
        self,
        label: str,
        style: discord.ButtonStyle = discord.ButtonStyle.primary,
        emoji: str | None = None,
        callback: Callable[[Interaction], Any] | None = None,
        row: int | None = None,
    ) -> discord.ui.Button:
        """Add a button to the view.

        Args:
            label: Button label
            style: Button style
            emoji: Optional emoji
            callback: Callback function
            row: Optional row number

        Returns:
            Created button
        """
        button = discord.ui.Button(
            label=label, style=style, emoji=emoji, row=row
        )

        if callback:
            button_id = f"button_{len(self._callbacks)}"
            self._callbacks[button_id] = callback

            async def button_callback(i: Interaction) -> None:
                await callback(i)

            button.callback = button_callback

        self.add_item(button)
        return button


class SelectMenuView(discord.ui.View):
    """Helper view for select menu interactions."""

    def __init__(self, timeout: float = 300.0) -> None:
        """Initialize select menu view.

        Args:
            timeout: View timeout in seconds
        """
        super().__init__(timeout=timeout)

    def add_select(
        self,
        placeholder: str,
        options: list[discord.SelectOption],
        callback: Callable[[Interaction, discord.ui.Select], Any],
        min_values: int = 1,
        max_values: int = 1,
        row: int | None = None,
    ) -> discord.ui.Select:
        """Add a select menu to the view.

        Args:
            placeholder: Placeholder text
            options: List of select options
            callback: Callback function
            min_values: Minimum selections
            max_values: Maximum selections
            row: Optional row number

        Returns:
            Created select menu
        """
        select = discord.ui.Select(
            placeholder=placeholder,
            options=options,
            min_values=min_values,
            max_values=max_values,
            row=row,
        )

        async def select_callback(i: Interaction) -> None:
            await callback(i, select)

        select.callback = select_callback
        self.add_item(select)
        return select
