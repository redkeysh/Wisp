"""Example of creating a custom module."""

from typing import Any

import discord
from discord import app_commands

from wisp_framework.module import Module


class GreetingModule(Module):
    """Example custom module that greets users."""

    @property
    def name(self) -> str:
        """Module name."""
        return "greeting"

    @property
    def default_enabled(self) -> bool:
        """Enabled by default."""
        return True

    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the greeting module."""
        tree = bot.tree

        @tree.command(name="greet", description="Greet a user")
        @app_commands.describe(user="User to greet")
        async def greet(interaction: discord.Interaction, user: discord.Member):
            """Greet command handler."""
            await interaction.response.send_message(
                f"Hello, {user.mention}! 👋"
            )

        @tree.command(name="goodbye", description="Say goodbye")
        async def goodbye(interaction: discord.Interaction):
            """Goodbye command handler."""
            await interaction.response.send_message(
                f"Goodbye, {interaction.user.mention}! 👋"
            )

        # Event listener example
        @bot.event
        async def on_member_join(member: discord.Member):
            """Welcome new members."""
            if member.guild:
                # Try to send welcome message
                channel = member.guild.system_channel
                if channel:
                    await channel.send(
                        f"Welcome to {member.guild.name}, {member.mention}! 🎉"
                    )
