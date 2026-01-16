"""Complete example bot with custom modules and services."""

import asyncio
import logging
from typing import Any

import discord
from discord import app_commands

from wisp_framework.config import AppConfig
from wisp_framework.lifecycle import (
    LifecycleManager,
    create_bot_context,
    create_feature_flags,
    create_services,
)
from wisp_framework.logging import setup_logging
from wisp_framework.module import Module
from wisp_framework.registry import ModuleRegistry
from wisp_framework.utils.permissions import is_admin

logger = logging.getLogger(__name__)


class BotConfig(AppConfig):
    """Example bot-specific configuration extending AppConfig."""

    @property
    def feature_stats(self) -> bool:
        """Whether stats module is enabled."""
        return self._get_bool("FEATURE_STATS", True)


class StatsModule(Module):
    """Module that tracks command usage stats."""

    @property
    def name(self) -> str:
        return "stats"

    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree

        @tree.command(name="stats", description="View server statistics")
        async def stats(interaction: discord.Interaction):
            """Show server stats."""
            if not interaction.guild:
                await interaction.response.send_message(
                    "This command only works in servers.", ephemeral=True
                )
                return

            # Get stats from guild data
            command_count = await ctx.guild_data.get(
                interaction.guild.id, "command_count", module_name="stats"
            ) or 0

            embed = discord.Embed(
                title=f"Stats for {interaction.guild.name}",
                color=discord.Color.blue(),
            )
            embed.add_field(name="Commands Executed", value=str(command_count))
            embed.add_field(name="Members", value=str(interaction.guild.member_count))

            await interaction.response.send_message(embed=embed, ephemeral=True)

        @tree.command(name="reset-stats", description="Reset statistics (admin only)")
        async def reset_stats(interaction: discord.Interaction):
            """Reset stats."""
            if not interaction.guild:
                await interaction.response.send_message(
                    "This command only works in servers.", ephemeral=True
                )
                return

            if not is_admin(interaction):
                await interaction.response.send_message(
                    "You don't have permission to reset stats.", ephemeral=True
                )
                return

            await ctx.guild_data.delete(
                interaction.guild.id, "command_count", module_name="stats"
            )

            await interaction.response.send_message(
                "Stats reset!", ephemeral=True
            )

        # Track command usage
        @bot.event
        async def on_app_command_completion(
            interaction: discord.Interaction, command: app_commands.Command
        ):
            """Track command usage."""
            if interaction.guild and ctx.guild_data:
                current = await ctx.guild_data.get(
                    interaction.guild.id, "command_count", module_name="stats"
                ) or 0
                await ctx.guild_data.set(
                    interaction.guild.id,
                    "command_count",
                    current + 1,
                    module_name="stats",
                )


class CacheExampleModule(Module):
    """Module demonstrating cache usage."""

    @property
    def name(self) -> str:
        return "cache_example"

    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        cache = ctx.services.get("cache")

        @tree.command(name="cache-set", description="Set a cached value")
        @app_commands.describe(key="Cache key", value="Value to cache", ttl="TTL in seconds")
        async def cache_set(
            interaction: discord.Interaction,
            key: str,
            value: str,
            ttl: int = 60,
        ):
            """Set cache value."""
            if cache:
                await cache.set(key, value, ttl=ttl)
                await interaction.response.send_message(
                    f"Cached '{key}' = '{value}' for {ttl} seconds", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "Cache service not available", ephemeral=True
                )

        @tree.command(name="cache-get", description="Get a cached value")
        @app_commands.describe(key="Cache key")
        async def cache_get(interaction: discord.Interaction, key: str):
            """Get cache value."""
            if cache:
                value = await cache.get(key)
                if value is None:
                    await interaction.response.send_message(
                        f"No value found for key: {key}", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        f"{key} = {value}", ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    "Cache service not available", ephemeral=True
                )


def main():
    """Main entry point."""
    try:
        # Load configuration
        # Using custom config class that extends AppConfig
        config = BotConfig()
        setup_logging(config)

        logger.info("Starting complete bot example...")

        # Create services
        services = create_services(config)

        # Create feature flags
        feature_flags = create_feature_flags(services)

        # Create module registry
        module_registry = ModuleRegistry(feature_flags)

        # Register custom modules
        if config.feature_stats:
            module_registry.register(StatsModule())
        module_registry.register(CacheExampleModule())

        # Register built-in modules
        # These include prefixed commands (!ping, !sync) that work automatically
        from wisp_framework.modules.core_admin import CoreAdminModule
        from wisp_framework.modules.ping import PingModule

        module_registry.register(PingModule())
        module_registry.register(CoreAdminModule())

        # Create bot context
        ctx = create_bot_context(config, services)

        # Create lifecycle manager
        lifecycle = LifecycleManager()

        # Start bot
        # Commands will sync automatically on startup (SYNC_ON_STARTUP=true by default)
        # You can disable with SYNC_ON_STARTUP=false or use !sync command manually
        async def run():
            bot = await lifecycle.startup(config, services, module_registry, ctx)
            await bot.start(config.discord_token)

        asyncio.run(run())

    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
