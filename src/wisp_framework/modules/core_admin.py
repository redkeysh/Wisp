"""Core admin module - module management and bot info commands."""

from typing import Any

import discord
from discord import app_commands

from wisp_framework.module import Module
from wisp_framework.utils.decorators import (
    handle_errors,
    require_admin,
    require_guild,
    require_owner,
)
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.pagination import paginate_embeds
from wisp_framework.utils.responses import respond_error, respond_success
from wisp_framework.utils.time import format_uptime


class CoreAdminModule(Module):
    """Core admin module for managing modules and bot info."""

    @property
    def name(self) -> str:
        """Module name."""
        return "core_admin"

    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the core admin module."""
        tree = bot.tree

        @tree.command(name="modules", description="Manage modules")
        @require_guild
        @handle_errors
        @app_commands.describe(
            action="Action to perform",
            module_name="Module name (required for enable/disable)",
        )
        @app_commands.choices(
            action=[
                app_commands.Choice(name="list", value="list"),
                app_commands.Choice(name="enable", value="enable"),
                app_commands.Choice(name="disable", value="disable"),
            ]
        )
        async def modules_command(
            interaction: discord.Interaction,
            action: app_commands.Choice[str],
            module_name: str | None = None,
        ) -> None:
            """Module management command."""
            if action.value == "list":
                modules = bot.module_registry.list_modules()
                enabled = await bot.module_registry._feature_flags.get_all_enabled(
                    interaction.guild.id
                )

                module_list = []
                for mod_name in modules:
                    status = "✅" if enabled.get(mod_name, True) else "❌"
                    module_list.append(f"{status} {mod_name}")

                # Use pagination if many modules
                if len(module_list) > 10:
                    embeds = []
                    items_per_page = 10
                    for i in range(0, len(module_list), items_per_page):
                        page_items = module_list[i : i + items_per_page]
                        embed = EmbedBuilder.list_embed(
                            title="Modules",
                            items=page_items,
                            page=(i // items_per_page) + 1,
                            items_per_page=items_per_page,
                        )
                        embeds.append(embed)
                    await paginate_embeds(interaction, embeds, ephemeral=True)
                else:
                    embed = EmbedBuilder.info(
                        title="Modules",
                        description="\n".join(module_list) or "No modules available",
                    )
                    await respond_success(interaction, "Module list:", embed=embed)

            elif action.value == "enable":
                if not require_admin(lambda: None)(lambda: None) and not require_owner(ctx.config)(
                    lambda: None
                ):
                    await respond_error(
                        interaction, "You don't have permission to enable modules."
                    )
                    return

                if not module_name:
                    await respond_error(interaction, "Please specify a module name.")
                    return

                await bot.module_registry._feature_flags.set_enabled(
                    interaction.guild.id, module_name, True
                )
                embed = EmbedBuilder.success(
                    title="Module Enabled",
                    description=f"Module '{module_name}' has been enabled.",
                )
                await respond_success(interaction, f"Enabled '{module_name}'", embed=embed)

            elif action.value == "disable":
                if not require_admin(lambda: None)(lambda: None) and not require_owner(ctx.config)(
                    lambda: None
                ):
                    await respond_error(
                        interaction, "You don't have permission to disable modules."
                    )
                    return

                if not module_name:
                    await respond_error(interaction, "Please specify a module name.")
                    return

                # Use confirmation for disable
                from wisp_framework.utils.confirmations import confirm_action

                async def on_confirm(i: discord.Interaction) -> None:
                    await bot.module_registry._feature_flags.set_enabled(
                        i.guild.id, module_name, False
                    )
                    embed = EmbedBuilder.success(
                        title="Module Disabled",
                        description=f"Module '{module_name}' has been disabled.",
                    )
                    await respond_success(i, f"Disabled '{module_name}'", embed=embed)

                await confirm_action(
                    interaction,
                    f"⚠️ Are you sure you want to disable module '{module_name}'?",
                    on_confirm=on_confirm,
                )


        @tree.command(name="sync", description="Sync bot commands (owner only)")
        @require_owner(ctx.config)
        @handle_errors
        async def sync_command(interaction: discord.Interaction) -> None:
            """Sync commands manually."""
            from wisp_framework.utils.responses import ResponseHelper

            await ResponseHelper.defer(interaction, ephemeral=True)
            synced = await bot.sync_commands()

            embed = EmbedBuilder.success(
                title="Commands Synced",
                description=f"Successfully synced {len(synced)} command(s).",
                fields=[{"name": "Commands", "value": str(len(synced)), "inline": True}]
            )
            await respond_success(interaction, f"Synced {len(synced)} command(s)", embed=embed)

        @tree.command(name="botinfo", description="Show bot information")
        @handle_errors
        async def botinfo_command(interaction: discord.Interaction) -> None:
            """Bot info command."""
            if not bot.started_at:
                uptime_str = "Unknown"
            else:
                uptime_str = format_uptime(bot.started_at)

            latency = round(bot.latency * 1000)
            guild_count = len(bot.guilds)
            user_count = len(bot.users)
            module_count = len(bot.module_registry.list_modules())

            embed = EmbedBuilder.info(
                title="Bot Information",
                description=f"Information about {bot.user.display_name if bot.user else 'the bot'}",
                fields=[
                    {"name": "Uptime", "value": uptime_str, "inline": True},
                    {"name": "Latency", "value": f"{latency}ms", "inline": True},
                    {"name": "Guilds", "value": str(guild_count), "inline": True},
                    {"name": "Users", "value": str(user_count), "inline": True},
                    {"name": "Modules", "value": str(module_count), "inline": True},
                ],
            )

            await respond_success(interaction, "Bot Information", embed=embed)

        @tree.command(name="uptime", description="Show bot uptime")
        @handle_errors
        async def uptime_command(interaction: discord.Interaction) -> None:
            """Uptime command."""
            if not bot.started_at:
                await respond_error(interaction, "Uptime not available.")
                return

            uptime_str = format_uptime(bot.started_at)
            embed = EmbedBuilder.info(
                title="Bot Uptime",
                description=f"The bot has been running for **{uptime_str}**",
                fields=[{"name": "Uptime", "value": uptime_str, "inline": False}],
            )
            await respond_success(interaction, f"Bot uptime: {uptime_str}", embed=embed)
