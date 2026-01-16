"""WispBot - The main bot class for Wisp Framework."""

import logging
from datetime import datetime
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from wisp_framework.config import AppConfig
from wisp_framework.context import BotContext
from wisp_framework.registry import ModuleRegistry
from wisp_framework.services.base import ServiceContainer

logger = logging.getLogger(__name__)


class WispBot(commands.Bot):
    """Main bot class for Wisp Framework, extending discord.py Bot."""

    def __init__(
        self,
        config: AppConfig,
        services: ServiceContainer,
        module_registry: ModuleRegistry,
        ctx: BotContext,
    ) -> None:
        """Initialize the framework bot."""
        intents = config.intents

        # Set owner IDs for prefixed command owner checks
        owner_ids = config.owner_ids if config.owner_ids else None

        super().__init__(command_prefix="!", intents=intents, owner_ids=owner_ids)

        self.config = config
        self.services = services
        self.module_registry = module_registry
        self.ctx = ctx
        self.started_at: datetime | None = None

        # Set up error handlers
        self.tree.on_error = self._on_app_command_error
        # Prefix command error handler will be added via on_command_error

        # Set up pipeline for command execution
        from wisp_framework.core.pipeline import create_default_pipeline
        from wisp_framework.events.router import EventRouter

        self.pipeline = create_default_pipeline()
        self.event_router = EventRouter(
            ignore_bots=True,
            ignore_dms=True,
            pipeline=self.pipeline,
        )

    async def setup_hook(self) -> None:
        """Called when the bot is starting up."""
        self.started_at = datetime.utcnow()
        logger.info("Bot setup hook called")

        # Load modules globally before bot starts processing messages
        # This ensures prefixed commands are registered early
        await self.module_registry.load_enabled_modules(self, self.ctx, guild_id=None)

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"Bot ready: {self.user} (ID: {self.user.id if self.user else None})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")

        # Sync commands if configured (must happen after on_ready when application_id is available)
        if self.config.sync_on_startup:
            try:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} command(s)")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}", exc_info=True)

        # Load modules for each guild (for guild-specific features)
        for guild in self.guilds:
            await self.module_registry.load_enabled_modules(self, self.ctx, guild.id)

    async def on_app_command_completion(
        self, interaction: discord.Interaction, command: app_commands.Command[Any, Any, Any]
    ) -> None:
        """Called when an app command completes successfully."""
        # Create WispContext for this command execution
        from wisp_framework.context import WispContext

        ctx = WispContext.from_interaction(
            config=self.config,
            services=self.services,
            interaction=interaction,
            invocation_type="slash",
            feature_flags=self.module_registry._feature_flags,
        )

        # Log to audit service if available
        audit_service = self.services.get("audit")
        if audit_service:
            audit_service.log_action(
                action="command_completed",
                user_id=interaction.user.id if interaction.user else None,
                guild_id=interaction.guild_id,
                channel_id=interaction.channel_id if interaction.channel else None,
                metadata={"command": command.name, "request_id": ctx.request_id},
            )

        # Update metrics using normalized naming
        if ctx.metrics:
            from wisp_framework.observability.metrics import record_command_metric

            record_command_metric(ctx.metrics, command.name, "success")

    async def _on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Handle app command errors."""
        # Create WispContext for this command execution
        from wisp_framework.context import WispContext

        ctx = WispContext.from_interaction(
            config=self.config,
            services=self.services,
            interaction=interaction,
            invocation_type="slash",
            feature_flags=self.module_registry._feature_flags,
        )

        # Use bound logger for error logging
        ctx.bound_logger.error(f"Command error: {error}", exc_info=True)

        # Log to audit service
        audit_service = self.services.get("audit")
        if audit_service:
            audit_service.log_action(
                action="command_error",
                user_id=interaction.user.id if interaction.user else None,
                guild_id=interaction.guild_id,
                channel_id=interaction.channel_id if interaction.channel else None,
                metadata={
                    "error": str(error),
                    "error_type": type(error).__name__,
                    "request_id": ctx.request_id,
                },
            )

        # Update metrics
        if ctx.metrics:
            from wisp_framework.observability.metrics import record_command_metric

            record_command_metric(ctx.metrics, "unknown", "error")

        # Map error to user-friendly response
        from wisp_framework.exceptions import map_error_to_response

        message, ephemeral = map_error_to_response(error)

        # Send user-friendly error message
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(message, ephemeral=ephemeral)

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Handle prefix command errors."""
        # Create WispContext for this command execution
        from wisp_framework.context import WispContext

        wisp_ctx = WispContext.from_interaction(
            config=self.config,
            services=self.services,
            interaction=ctx,
            invocation_type="prefix",
            feature_flags=self.module_registry._feature_flags,
        )

        # Use bound logger for error logging
        wisp_ctx.bound_logger.error(f"Prefix command error: {error}", exc_info=True)

        # Log to audit service
        audit_service = self.services.get("audit")
        if audit_service:
            audit_service.log_action(
                action="command_error",
                user_id=ctx.author.id if ctx.author else None,
                guild_id=ctx.guild.id if ctx.guild else None,
                channel_id=ctx.channel.id if ctx.channel else None,
                metadata={
                    "error": str(error),
                    "error_type": type(error).__name__,
                    "command": ctx.command.name if ctx.command else "unknown",
                    "request_id": wisp_ctx.request_id,
                },
            )

        # Update metrics
        if wisp_ctx.metrics:
            from wisp_framework.observability.metrics import record_command_metric

            record_command_metric(wisp_ctx.metrics, ctx.command.name if ctx.command else "unknown", "error")

        # Map error to user-friendly response
        from wisp_framework.exceptions import map_error_to_response

        message, _ = map_error_to_response(error)

        # Send user-friendly error message
        await ctx.send(message)

    async def sync_commands(self) -> None:
        """Manually sync commands."""
        try:
            synced = await self.tree.sync()
            logger.info(f"Manually synced {len(synced)} command(s)")
            return synced
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}", exc_info=True)
            raise

    async def on_message(self, message: discord.Message) -> None:
        """Handle message events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext.from_event(
                config=self.config,
                services=self.services,
                event=message,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_message", message, ctx)
        # Call super() to allow modules using @bot.event to still work
        await super().on_message(message)

    async def on_member_join(self, member: discord.Member) -> None:
        """Handle member join events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext.from_event(
                config=self.config,
                services=self.services,
                event=member,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_member_join", member, ctx)
        # Call super() to allow modules using @bot.event to still work
        await super().on_member_join(member)

    async def on_member_remove(self, member: discord.Member) -> None:
        """Handle member leave events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext.from_event(
                config=self.config,
                services=self.services,
                event=member,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_member_remove", member, ctx)
        await super().on_member_remove(member)

    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        """Handle member update events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext.from_event(
                config=self.config,
                services=self.services,
                event=after,  # Use 'after' for context extraction
                feature_flags=self.module_registry._feature_flags,
            )
            # Pass both before and after as a tuple
            await self.event_router.route("on_member_update", (before, after), ctx)
        await super().on_member_update(before, after)

    async def on_reaction_add(
        self, reaction: discord.Reaction, user: discord.Member | discord.User
    ) -> None:
        """Handle reaction add events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext.from_event(
                config=self.config,
                services=self.services,
                event=reaction,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_reaction_add", (reaction, user), ctx)
        await super().on_reaction_add(reaction, user)

    async def on_reaction_remove(
        self, reaction: discord.Reaction, user: discord.Member | discord.User
    ) -> None:
        """Handle reaction remove events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext.from_event(
                config=self.config,
                services=self.services,
                event=reaction,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_reaction_remove", (reaction, user), ctx)
        await super().on_reaction_remove(reaction, user)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Handle guild join events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext(
                config=self.config,
                services=self.services,
                invocation_type="event",
                guild_id=guild.id,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_guild_join", guild, ctx)
        await super().on_guild_join(guild)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Handle guild leave events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext(
                config=self.config,
                services=self.services,
                invocation_type="event",
                guild_id=guild.id,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_guild_remove", guild, ctx)
        await super().on_guild_remove(guild)

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild) -> None:
        """Handle guild update events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext(
                config=self.config,
                services=self.services,
                invocation_type="event",
                guild_id=after.id,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_guild_update", (before, after), ctx)
        await super().on_guild_update(before, after)

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        """Handle message edit events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext.from_event(
                config=self.config,
                services=self.services,
                event=after,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_message_edit", (before, after), ctx)
        await super().on_message_edit(before, after)

    async def on_message_delete(self, message: discord.Message) -> None:
        """Handle message delete events through event router."""
        if self.event_router:
            from wisp_framework.context import WispContext

            ctx = WispContext.from_event(
                config=self.config,
                services=self.services,
                event=message,
                feature_flags=self.module_registry._feature_flags,
            )
            await self.event_router.route("on_message_delete", message, ctx)
        await super().on_message_delete(message)

    async def close(self) -> None:
        """Close the bot and clean up resources."""
        logger.info("Closing bot...")
        await super().close()
