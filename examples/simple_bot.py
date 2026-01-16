"""Simple example bot using the Wisp Framework."""

import asyncio
import logging

from wisp_framework.config import AppConfig
from wisp_framework.lifecycle import (
    LifecycleManager,
    create_bot_context,
    create_feature_flags,
    create_services,
)
from wisp_framework.logging import setup_logging
from wisp_framework.modules.core_admin import CoreAdminModule

# Import built-in modules
from wisp_framework.modules.ping import PingModule
from wisp_framework.registry import ModuleRegistry

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    try:
        # Load configuration
        # AppConfig automatically loads .env.local, .env.{APP_ENV}, or .env
        config = AppConfig()

        # Set up logging
        # You can pass a custom formatter: setup_logging(config, formatter=custom_formatter)
        setup_logging(config)

        logger.info("Starting simple bot example...")

        # Create services
        services = create_services(config)

        # Create feature flags
        feature_flags = create_feature_flags(services)

        # Create module registry
        module_registry = ModuleRegistry(feature_flags)

        # Register built-in modules
        module_registry.register(PingModule())
        module_registry.register(CoreAdminModule())

        # Create bot context
        ctx = create_bot_context(config, services)

        # Create lifecycle manager
        lifecycle = LifecycleManager()

        # Start bot
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
