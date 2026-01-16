"""Example module using enhanced framework utilities."""

from typing import Any

import discord

from wisp_framework.module import Module
from wisp_framework.utils.cooldowns import cooldown
from wisp_framework.utils.decorators import handle_errors, require_admin, require_guild
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.pagination import paginate_embeds
from wisp_framework.utils.responses import respond_success


class EnhancedModule(Module):
    """Example module demonstrating enhanced utilities."""

    @property
    def name(self) -> str:
        return "enhanced"

    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree

        @tree.command(name="success", description="Show success message")
        @require_guild
        @handle_errors
        async def success_command(interaction: discord.Interaction) -> None:
            """Success command with embed."""
            embed = EmbedBuilder.success(
                title="Operation Complete",
                description="The operation completed successfully!",
                fields=[
                    {"name": "Status", "value": "✅ Success", "inline": True},
                    {"name": "Time", "value": "Just now", "inline": True},
                ],
            )
            await respond_success(interaction, "Done!", embed=embed)

        @tree.command(name="list-items", description="List items with pagination")
        @require_guild
        async def list_items(interaction: discord.Interaction) -> None:
            """List items with pagination."""
            items = [f"Item {i}" for i in range(1, 26)]  # 25 items

            # Create embeds for pagination
            embeds = []
            items_per_page = 10
            for i in range(0, len(items), items_per_page):
                embed = EmbedBuilder.list_embed(
                    title="Items List",
                    items=items,
                    page=(i // items_per_page) + 1,
                    items_per_page=items_per_page,
                )
                embeds.append(embed)

            await paginate_embeds(interaction, embeds, ephemeral=True)

        @tree.command(name="cooldown-test", description="Test cooldown")
        @cooldown(seconds=10.0)
        async def cooldown_test(interaction: discord.Interaction) -> None:
            """Command with cooldown."""
            await respond_success(interaction, "Cooldown test successful!")

        @tree.command(name="admin-only", description="Admin only command")
        @require_admin
        async def admin_command(interaction: discord.Interaction) -> None:
            """Admin-only command."""
            await respond_success(interaction, "Admin command executed!")
