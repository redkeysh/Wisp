"""Main entrypoint for the runner bot."""

import asyncio
import logging
import sys

from wisp_framework.config import AppConfig
from wisp_framework.context import BotContext
from wisp_framework.feature_flags import FeatureFlags
from wisp_framework.lifecycle import (
    LifecycleManager,
    create_bot_context,
    create_feature_flags,
    create_services,
)
from wisp_framework.logging import setup_logging
from wisp_framework.module import Module
from wisp_framework.modules.core_admin import CoreAdminModule
from wisp_framework.modules.health import HealthModule
from wisp_framework.modules.insights import InsightsModule
from wisp_framework.modules.onboarding import OnboardingModule
from wisp_framework.modules.ping import PingModule
from wisp_framework.registry import ModuleRegistry

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entrypoint."""
    try:
        # Load configuration
        config = AppConfig()

        # Set up logging
        setup_logging(config)

        logger.info("Starting Wisp Framework runner...")

        # Create services
        services = create_services(config)

        # Create feature flags
        feature_flags = create_feature_flags(services)

        # Create module registry
        module_registry = ModuleRegistry(feature_flags)

        # Register built-in modules
        module_registry.register(CoreAdminModule())
        module_registry.register(HealthModule())
        module_registry.register(PingModule())
        module_registry.register(OnboardingModule())
        module_registry.register(InsightsModule())

        # Optionally discover additional modules
        # module_registry.discover_modules("wisp_framework.modules")

        # Create bot context
        ctx = create_bot_context(config, services)

        # Create lifecycle manager
        lifecycle = LifecycleManager()

        # Start bot
        async def run() -> None:
            bot = await lifecycle.startup(config, services, module_registry, ctx)
            await bot.start(config.discord_token)

        # Run bot
        asyncio.run(run())

    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
