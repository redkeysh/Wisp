"""Complete example showing all enhanced utilities."""

from typing import Any

import discord

from wisp_framework.module import Module
from wisp_framework.utils.command_groups import CommandGroup
from wisp_framework.utils.confirmations import confirm_action
from wisp_framework.utils.cooldowns import cooldown
from wisp_framework.utils.decorators import handle_errors, require_admin, require_guild
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.pagination import paginate_embeds
from wisp_framework.utils.responses import respond_success


class CompleteEnhancedModule(Module):
    """Module demonstrating all enhanced utilities."""

    @property
    def name(self) -> str:
        return "complete_enhanced"

    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree

        # Example 1: Simple command with embed builder
        @tree.command(name="status", description="Show status")
        @require_guild
        @handle_errors
        async def status(interaction: discord.Interaction) -> None:
            embed = EmbedBuilder.success(
                title="System Status",
                description="All systems operational",
                fields=[
                    {"name": "Uptime", "value": "2 days", "inline": True},
                    {"name": "Users", "value": "1,234", "inline": True},
                ],
            )
            await respond_success(interaction, "Status check complete!", embed=embed)

        # Example 2: Command with cooldown
        @tree.command(name="spam-protected", description="Cooldown example")
        @cooldown(seconds=5.0)
        async def spam_protected(interaction: discord.Interaction) -> None:
            await respond_success(interaction, "Command executed!")

        # Example 3: Paginated list
        @tree.command(name="list-all", description="List items with pagination")
        @require_guild
        async def list_all(interaction: discord.Interaction) -> None:
            items = [f"Item {i:03d}" for i in range(1, 51)]  # 50 items

            # Create paginated embeds
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

        # Example 4: Confirmation dialog
        @tree.command(name="dangerous", description="Dangerous action")
        @require_admin
        async def dangerous(interaction: discord.Interaction) -> None:
            async def on_confirm(i: discord.Interaction) -> None:
                await respond_success(i, "Dangerous action executed!")

            await confirm_action(
                interaction,
                "⚠️ Are you sure you want to perform this dangerous action?",
                on_confirm=on_confirm,
            )

        # Example 5: Command group
        mod_group = CommandGroup("mod", "Moderation commands", guild_only=True)
        mod_group.create_group(tree)

        @mod_group.command(name="kick", description="Kick a user")
        @require_admin
        async def kick(
            interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"
        ) -> None:
            embed = EmbedBuilder.success(
                title="User Kicked",
                description=f"{user.mention} has been kicked",
                fields=[{"name": "Reason", "value": reason, "inline": False}],
            )
            await respond_success(interaction, f"Kicked {user.mention}", embed=embed)

        @mod_group.command(name="ban", description="Ban a user")
        @require_admin
        async def ban(
            interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"
        ) -> None:
            async def on_confirm(i: discord.Interaction) -> None:
                embed = EmbedBuilder.success(
                    title="User Banned",
                    description=f"{user.mention} has been banned",
                    fields=[{"name": "Reason", "value": reason, "inline": False}],
                )
                await respond_success(i, f"Banned {user.mention}", embed=embed)

            await confirm_action(
                interaction,
                f"⚠️ Are you sure you want to ban {user.mention}?",
                on_confirm=on_confirm,
            )

        # Example 6: Error handling
        @tree.command(name="error-test", description="Test error handling")
        @handle_errors
        async def error_test(interaction: discord.Interaction) -> None:
            raise ValueError("This error will be caught and displayed nicely!")

        # Example 7: Table display
        @tree.command(name="stats-table", description="Show stats as table")
        @require_guild
        async def stats_table(interaction: discord.Interaction) -> None:
            embed = EmbedBuilder.table_embed(
                title="Server Statistics",
                headers=["Metric", "Value"],
                rows=[
                    ["Members", "1,234"],
                    ["Channels", "45"],
                    ["Roles", "23"],
                    ["Messages", "567,890"],
                ],
            )
            await respond_success(interaction, "Statistics:", embed=embed)
