"""Core admin module - module management and bot info commands."""

from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from wisp_framework.module import Module
from wisp_framework.utils.context_helpers import (
    get_wisp_context_from_command_context,
    get_wisp_context_from_interaction,
)
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
            # Create WispContext for this command execution
            wisp_ctx = get_wisp_context_from_interaction(bot, interaction, "slash")
            wisp_ctx.bound_logger.debug(f"Executing modules command: {action.value}")

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

                # Record metrics
                if wisp_ctx.metrics:
                    from wisp_framework.observability.metrics import record_command_metric

                    record_command_metric(wisp_ctx.metrics, "modules", "success")

            elif action.value == "enable":
                # Check permissions - simplified for now
                # Full implementation would use policy engine
                if interaction.user.id not in (bot.owner_ids or []):
                    await respond_error(
                        interaction, "You don't have permission to enable modules."
                    )
                    if wisp_ctx.metrics:
                        from wisp_framework.observability.metrics import record_command_metric

                        record_command_metric(wisp_ctx.metrics, "modules", "permission_denied")
                    return

                if not module_name:
                    await respond_error(interaction, "Please specify a module name.")
                    return

                await bot.module_registry._feature_flags.set_enabled(
                    interaction.guild.id, module_name, True
                )
                wisp_ctx.bound_logger.info(f"Enabled module '{module_name}' for guild {interaction.guild.id}")

                embed = EmbedBuilder.success(
                    title="Module Enabled",
                    description=f"Module '{module_name}' has been enabled.",
                )
                await respond_success(interaction, f"Enabled '{module_name}'", embed=embed)

                # Record metrics
                if wisp_ctx.metrics:
                    from wisp_framework.observability.metrics import record_command_metric

                    record_command_metric(wisp_ctx.metrics, "modules", "success")

            elif action.value == "disable":
                # Check permissions - simplified for now
                if interaction.user.id not in (bot.owner_ids or []):
                    await respond_error(
                        interaction, "You don't have permission to disable modules."
                    )
                    if wisp_ctx.metrics:
                        from wisp_framework.observability.metrics import record_command_metric

                        record_command_metric(wisp_ctx.metrics, "modules", "permission_denied")
                    return

                if not module_name:
                    await respond_error(interaction, "Please specify a module name.")
                    return

                # Use confirmation for disable
                from wisp_framework.utils.confirmations import confirm_action

                async def on_confirm(i: discord.Interaction) -> None:
                    # Create context for confirmation handler
                    confirm_ctx = get_wisp_context_from_interaction(bot, i, "slash")
                    await bot.module_registry._feature_flags.set_enabled(
                        i.guild.id, module_name, False
                    )
                    confirm_ctx.bound_logger.info(f"Disabled module '{module_name}' for guild {i.guild.id}")

                    embed = EmbedBuilder.success(
                        title="Module Disabled",
                        description=f"Module '{module_name}' has been disabled.",
                    )
                    await respond_success(i, f"Disabled '{module_name}'", embed=embed)

                    # Record metrics
                    if confirm_ctx.metrics:
                        from wisp_framework.observability.metrics import record_command_metric

                        record_command_metric(confirm_ctx.metrics, "modules", "success")

                await confirm_action(
                    interaction,
                    f"⚠️ Are you sure you want to disable module '{module_name}'?",
                    on_confirm=on_confirm,
                )


        @tree.command(name="sync", description="Sync bot commands (owner only)")
        @require_owner(bot.config)
        @handle_errors
        async def sync_command(interaction: discord.Interaction) -> None:
            """Sync commands manually."""
            # Create WispContext for this command execution
            wisp_ctx = get_wisp_context_from_interaction(bot, interaction, "slash")
            wisp_ctx.bound_logger.info("Executing sync command")

            from wisp_framework.utils.responses import ResponseHelper

            await ResponseHelper.defer(interaction, ephemeral=True)
            synced = await bot.sync_commands()

            wisp_ctx.bound_logger.info(f"Synced {len(synced)} command(s)")

            embed = EmbedBuilder.success(
                title="Commands Synced",
                description=f"Successfully synced {len(synced)} command(s).",
                fields=[{"name": "Commands", "value": str(len(synced)), "inline": True}]
            )
            await respond_success(interaction, f"Synced {len(synced)} command(s)", embed=embed)

            # Record metrics
            if wisp_ctx.metrics:
                from wisp_framework.observability.metrics import record_command_metric

                record_command_metric(wisp_ctx.metrics, "sync", "success")

        # Prefixed sync command
        async def sync_prefixed_command(ctx: commands.Context) -> None:
            """Sync commands manually (prefixed command)."""
            # Create WispContext for this command execution
            wisp_ctx = get_wisp_context_from_command_context(bot, ctx)
            wisp_ctx.bound_logger.info("Executing sync command (prefix)")

            try:
                synced = await bot.sync_commands()
                wisp_ctx.bound_logger.info(f"Synced {len(synced)} command(s)")

                embed = EmbedBuilder.success(
                    title="Commands Synced",
                    description=f"Successfully synced {len(synced)} command(s).",
                    fields=[{"name": "Commands", "value": str(len(synced)), "inline": True}]
                )
                await ctx.send(embed=embed)

                # Record metrics
                if wisp_ctx.metrics:
                    from wisp_framework.observability.metrics import record_command_metric

                    record_command_metric(wisp_ctx.metrics, "sync", "success")
            except Exception as e:
                wisp_ctx.bound_logger.error(f"Failed to sync commands: {e}", exc_info=True)
                embed = EmbedBuilder.error(
                    title="Sync Failed",
                    description=f"Failed to sync commands: {str(e)}"
                )
                await ctx.send(embed=embed)

                # Record metrics
                if wisp_ctx.metrics:
                    from wisp_framework.observability.metrics import record_command_metric

                    record_command_metric(wisp_ctx.metrics, "sync", "error")

        # Register prefixed command explicitly
        sync_cmd = commands.Command(
            sync_prefixed_command,
            name="sync"
        )
        # Add owner check
        sync_cmd.checks.append(commands.is_owner().predicate)
        bot.add_command(sync_cmd)

        @tree.command(name="botinfo", description="Show bot information")
        @handle_errors
        async def botinfo_command(interaction: discord.Interaction) -> None:
            """Bot info command."""
            # Create WispContext for this command execution
            wisp_ctx = get_wisp_context_from_interaction(bot, interaction, "slash")
            wisp_ctx.bound_logger.debug("Executing botinfo command")

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

            # Record metrics
            if wisp_ctx.metrics:
                from wisp_framework.observability.metrics import record_command_metric

                record_command_metric(wisp_ctx.metrics, "botinfo", "success")

        @tree.command(name="uptime", description="Show bot uptime")
        @handle_errors
        async def uptime_command(interaction: discord.Interaction) -> None:
            """Uptime command."""
            # Create WispContext for this command execution
            wisp_ctx = get_wisp_context_from_interaction(bot, interaction, "slash")
            wisp_ctx.bound_logger.debug("Executing uptime command")

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

            # Record metrics
            if wisp_ctx.metrics:
                from wisp_framework.observability.metrics import record_command_metric

                record_command_metric(wisp_ctx.metrics, "uptime", "success")

        # Policy commands
        @tree.command(name="policy", description="Manage policy rules")
        @handle_errors
        @app_commands.describe(
            action="Action to perform",
            capability="Capability name",
            scope_type="Scope type (global, guild, channel)",
            action_type="Action type (allow, deny)",
        )
        @app_commands.choices(
            action=[
                app_commands.Choice(name="set", value="set"),
                app_commands.Choice(name="list", value="list"),
                app_commands.Choice(name="explain", value="explain"),
            ]
        )
        async def policy_command(
            interaction: discord.Interaction,
            action: app_commands.Choice[str],
            capability: str | None = None,
            scope_type: str | None = None,
            action_type: str | None = None,
        ) -> None:
            """Policy management command."""
            # Create WispContext for this command execution
            wisp_ctx = get_wisp_context_from_interaction(bot, interaction, "slash")
            wisp_ctx.bound_logger.debug(f"Executing policy command: {action.value}")

            policy_service = wisp_ctx.services.get("policy")
            if not policy_service:
                await respond_error(interaction, "Policy service not available.")
                return

            if action.value == "set":
                if not capability or not scope_type or not action_type:
                    await respond_error(
                        interaction, "Please specify capability, scope_type, and action_type."
                    )
                    return

                scope_id = interaction.guild_id if scope_type == "guild" else (
                    interaction.channel_id if scope_type == "channel" else None
                )

                try:
                    rule = await policy_service.add_rule(
                        scope_type=scope_type,
                        scope_id=scope_id,
                        capability=capability,
                        action=action_type,
                    )
                    wisp_ctx.bound_logger.info(
                        f"Added policy rule {rule.id}: {action_type} {capability} at {scope_type} scope"
                    )
                    embed = EmbedBuilder.success(
                        title="Policy Rule Added",
                        description=f"Rule {rule.id} added: {action_type} {capability} at {scope_type} scope",
                    )
                    await respond_success(interaction, "Policy rule added", embed=embed)

                    # Record metrics
                    if wisp_ctx.metrics:
                        from wisp_framework.observability.metrics import record_command_metric

                        record_command_metric(wisp_ctx.metrics, "policy", "success")
                except Exception as e:
                    wisp_ctx.bound_logger.error(f"Failed to add policy rule: {e}", exc_info=True)
                    await respond_error(interaction, f"Failed to add rule: {str(e)}")

                    # Record metrics
                    if wisp_ctx.metrics:
                        from wisp_framework.observability.metrics import record_command_metric

                        record_command_metric(wisp_ctx.metrics, "policy", "error")

            elif action.value == "list":
                rules = await policy_service.list_rules(capability=capability)
                if not rules:
                    await respond_success(interaction, "No policy rules found.")
                    return

                rule_list = []
                for rule in rules[:20]:  # Limit to 20 for display
                    scope = f"{rule.scope_type}:{rule.scope_id}" if rule.scope_id else rule.scope_type
                    rule_list.append(f"{rule.action.upper()} {rule.capability} @ {scope}")

                wisp_ctx.bound_logger.debug(f"Listed {len(rules)} policy rules")

                embed = EmbedBuilder.info(
                    title="Policy Rules",
                    description="\n".join(rule_list) or "No rules found",
                )
                await respond_success(interaction, f"Found {len(rules)} rule(s)", embed=embed)

                # Record metrics
                if wisp_ctx.metrics:
                    from wisp_framework.observability.metrics import record_command_metric

                    record_command_metric(wisp_ctx.metrics, "policy", "success")

            elif action.value == "explain":
                if not capability:
                    await respond_error(interaction, "Please specify a capability.")
                    return

                result = await policy_service.check(capability, wisp_ctx)
                wisp_ctx.bound_logger.debug(
                    f"Policy explanation for {capability}: {'allowed' if result.allowed else 'denied'}"
                )

                embed = EmbedBuilder.info(
                    title=f"Policy Explanation: {capability}",
                    description=result.reason,
                    fields=[
                        {"name": "Allowed", "value": "Yes" if result.allowed else "No", "inline": True},
                        {"name": "Rules Evaluated", "value": str(len(result.explain_trace)), "inline": True},
                    ],
                )
                await respond_success(interaction, "Policy explanation", embed=embed)

                # Record metrics
                if wisp_ctx.metrics:
                    from wisp_framework.observability.metrics import record_command_metric

                    record_command_metric(wisp_ctx.metrics, "policy", "success")
