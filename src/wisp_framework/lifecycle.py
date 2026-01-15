"""Lifecycle management for bot startup and shutdown."""

import asyncio
import logging
import signal
from typing import Any, Optional

from wisp_framework.bot import FrameworkBot
from wisp_framework.config import AppConfig
from wisp_framework.context import BotContext
from wisp_framework.feature_flags import FeatureFlags
from wisp_framework.registry import ModuleRegistry
from wisp_framework.services.audit import AuditService
from wisp_framework.services.base import ServiceContainer
from wisp_framework.services.cache import CacheService
from wisp_framework.services.db import DatabaseService
from wisp_framework.services.health import HealthService
from wisp_framework.services.metrics import MetricsService
from wisp_framework.services.scheduler import SchedulerService
from wisp_framework.services.webhook_logger import WebhookLoggerService

logger = logging.getLogger(__name__)


class LifecycleManager:
    """Manages bot lifecycle (startup, shutdown, graceful cleanup)."""

    def __init__(self) -> None:
        """Initialize lifecycle manager."""
        self.bot: Optional[FrameworkBot] = None
        self._shutdown_event = asyncio.Event()

    async def startup(
        self,
        config: AppConfig,
        services: ServiceContainer,
        module_registry: ModuleRegistry,
        ctx: BotContext,
    ) -> FrameworkBot:
        """Start up the bot and all services."""
        logger.info("Starting bot lifecycle...")

        # Start all services
        await services.startup_all()

        # Create bot
        bot = FrameworkBot(config, services, module_registry, ctx)
        self.bot = bot

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._signal_handler)

        # Modules will be loaded after bot is ready

        logger.info("Bot lifecycle startup complete")
        return bot

    async def shutdown(self) -> None:
        """Shut down the bot and all services gracefully."""
        logger.info("Shutting down bot lifecycle...")

        if self.bot:
            # Unload modules
            for module_name in self.bot.module_registry.list_modules():
                module = self.bot.module_registry.get_module(module_name)
                if module:
                    try:
                        await module.teardown(self.bot, self.bot.ctx)
                    except Exception as e:
                        logger.error(f"Error tearing down module '{module_name}': {e}")

            # Close bot
            if not self.bot.is_closed():
                await self.bot.close()

        # Shutdown all services
        if self.bot:
            await self.bot.services.shutdown_all()

        logger.info("Bot lifecycle shutdown complete")

    def _signal_handler(self) -> None:
        """Handle shutdown signals."""
        logger.info("Received shutdown signal")
        self._shutdown_event.set()

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()


def create_services(config: AppConfig) -> ServiceContainer:
    """Create and register all services."""
    services = ServiceContainer(config)

    # Core services (always available)
    health_service = HealthService(config)
    services.register("health", health_service)
    services.register("cache", CacheService(config))
    services.register("metrics", MetricsService(config))
    services.register("scheduler", SchedulerService(config))
    services.register("audit", AuditService(config))
    services.register("webhook_logger", WebhookLoggerService(config))
    
    # Register service health statuses
    health_service.register_service("cache", {"healthy": True})
    health_service.register_service("metrics", {"healthy": True})
    health_service.register_service("scheduler", {"healthy": True})
    health_service.register_service("audit", {"healthy": True})

    # Optional database service
    db_service = DatabaseService(config)
    services.register("db", db_service)
    
    # Register database health (will be updated when DB starts)
    health_service.register_service("db", {"healthy": False})

    return services


def create_feature_flags(services: ServiceContainer) -> FeatureFlags:
    """Create feature flags with database service if available."""
    db_service = services.get_typed("db", DatabaseService)
    return FeatureFlags(db_service)


def create_bot_context(
    config: AppConfig, services: ServiceContainer
) -> BotContext:
    """Create bot context with all services."""
    from wisp_framework.db.guild_data import GuildDataService

    db_service = services.get_typed("db", DatabaseService)
    guild_data = GuildDataService(db_service)

    return BotContext(config, services, guild_data)
