"""FrameworkBot - The main bot class."""

import logging
from datetime import datetime
from typing import Any, Optional

import discord
from discord import app_commands
from discord.ext import commands

from wisp_framework.config import AppConfig
from wisp_framework.context import BotContext
from wisp_framework.exceptions import FrameworkError
from wisp_framework.logging import CorrelationContext
from wisp_framework.registry import ModuleRegistry
from wisp_framework.services.audit import AuditService
from wisp_framework.services.base import ServiceContainer

logger = logging.getLogger(__name__)


class FrameworkBot(commands.Bot):
    """Main bot class extending discord.py Bot."""

    def __init__(
        self,
        config: AppConfig,
        services: ServiceContainer,
        module_registry: ModuleRegistry,
        ctx: BotContext,
    ) -> None:
        """Initialize the framework bot."""
        intents = config.intents
        super().__init__(command_prefix="!", intents=intents)

        self.config = config
        self.services = services
        self.module_registry = module_registry
        self.ctx = ctx
        self.started_at: Optional[datetime] = None

        # Set up error handlers
        self.tree.on_error = self._on_app_command_error

    async def setup_hook(self) -> None:
        """Called when the bot is starting up."""
        self.started_at = datetime.utcnow()
        logger.info("Bot setup hook called")

        # Sync commands if configured
        if self.config.sync_on_startup:
            try:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} command(s)")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}", exc_info=True)

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"Bot ready: {self.user} (ID: {self.user.id if self.user else None})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Load modules for each guild
        for guild in self.guilds:
            await self.module_registry.load_enabled_modules(self, self.ctx, guild.id)

    async def on_app_command_completion(
        self, interaction: discord.Interaction, command: app_commands.Command[Any, Any, Any]
    ) -> None:
        """Called when an app command completes successfully."""
        # Log to audit service if available
        audit_service = self.services.get("audit")
        if audit_service:
            audit_service.log_action(
                action="command_completed",
                user_id=interaction.user.id if interaction.user else None,
                guild_id=interaction.guild_id,
                channel_id=interaction.channel_id if interaction.channel else None,
                metadata={"command": command.name},
            )

        # Update metrics
        metrics_service = self.services.get("metrics")
        if metrics_service:
            metrics_service.increment("commands.executed")
            metrics_service.increment(f"commands.{command.name}")

    async def _on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Handle app command errors."""
        logger.error(f"Command error: {error}", exc_info=True)

        # Log to audit service
        audit_service = self.services.get("audit")
        if audit_service:
            audit_service.log_action(
                action="command_error",
                user_id=interaction.user.id if interaction.user else None,
                guild_id=interaction.guild_id,
                channel_id=interaction.channel_id if interaction.channel else None,
                metadata={"error": str(error), "error_type": type(error).__name__},
            )

        # Send user-friendly error message
        if interaction.response.is_done():
            await interaction.followup.send(
                "An error occurred while executing the command.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An error occurred while executing the command.", ephemeral=True
            )

    async def sync_commands(self) -> None:
        """Manually sync commands."""
        try:
            synced = await self.tree.sync()
            logger.info(f"Manually synced {len(synced)} command(s)")
            return synced
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}", exc_info=True)
            raise

    async def close(self) -> None:
        """Close the bot and clean up resources."""
        logger.info("Closing bot...")
        await super().close()
