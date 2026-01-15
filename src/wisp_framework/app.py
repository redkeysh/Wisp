"""Application factory and convenience functions."""

from typing import Optional

from wisp_framework.bot import WispBot
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
from wisp_framework.registry import ModuleRegistry


def create_app(
    config: Optional[AppConfig] = None,
    auto_discover_modules: bool = False,
    module_package: str = "wisp_framework.modules",
) -> tuple[WispBot, LifecycleManager, BotContext]:
    """Create and configure a Discord bot application.
    
    Args:
        config: Optional AppConfig instance (creates new one if not provided)
        auto_discover_modules: Whether to auto-discover modules from package
        module_package: Package path for module discovery
    
    Returns:
        Tuple of (bot, lifecycle_manager, context)
    """
    if config is None:
        config = AppConfig()
    
    setup_logging(config)
    
    # Create services
    services = create_services(config)
    
    # Create feature flags
    feature_flags = create_feature_flags(services)
    
    # Create module registry
    module_registry = ModuleRegistry(feature_flags)
    
    # Auto-discover modules if requested
    if auto_discover_modules:
        module_registry.discover_modules(module_package)
    
    # Create bot context
    ctx = create_bot_context(config, services)
    
    # Create lifecycle manager
    lifecycle = LifecycleManager()
    
    # Create bot (but don't start it yet)
    bot = WispBot(config, services, module_registry, ctx)
    
    return bot, lifecycle, ctx
