"""Module registry for managing and loading modules."""

import importlib
import logging
import pkgutil
from typing import Any, Dict, List, Optional

from wisp_framework.feature_flags import FeatureFlags
from wisp_framework.module import Module

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """Registry for managing framework modules."""

    def __init__(self, feature_flags: FeatureFlags) -> None:
        """Initialize the module registry."""
        self._modules: Dict[str, Module] = {}
        self._feature_flags = feature_flags

    def register(self, module: Module) -> None:
        """Register a module."""
        if module.name in self._modules:
            raise ValueError(f"Module '{module.name}' is already registered")
        self._modules[module.name] = module
        logger.info(f"Registered module: {module.name}")

    def discover_modules(self, package_path: str) -> None:
        """Automatically discover and register modules from a package.

        Args:
            package_path: Python package path (e.g., 'wisp_framework.modules')
        """
        try:
            package = importlib.import_module(package_path)
            for _, modname, ispkg in pkgutil.iter_modules(package.__path__):
                if not ispkg:
                    try:
                        full_name = f"{package_path}.{modname}"
                        mod = importlib.import_module(full_name)
                        # Look for Module subclass
                        for attr_name in dir(mod):
                            attr = getattr(mod, attr_name)
                            if (
                                isinstance(attr, type)
                                and issubclass(attr, Module)
                                and attr is not Module
                            ):
                                instance = attr()
                                self.register(instance)
                                logger.info(f"Discovered module: {instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to load module {modname}: {e}")
        except Exception as e:
            logger.error(f"Failed to discover modules from {package_path}: {e}")

    def list_modules(self) -> List[str]:
        """List all registered module names."""
        return list(self._modules.keys())

    def get_module(self, name: str) -> Optional[Module]:
        """Get a module by name."""
        return self._modules.get(name)

    async def load_enabled_modules(
        self, bot: Any, ctx: Any, guild_id: Optional[int] = None
    ) -> None:
        """Load all enabled modules for a guild.

        Args:
            bot: The Discord bot instance
            ctx: Bot context with services and config
            guild_id: Guild ID (None for global modules)
        """
        # Resolve dependencies
        modules_to_load = self._resolve_dependencies()

        for module_name in modules_to_load:
            module = self._modules[module_name]

            # Check if enabled for this guild
            if guild_id is not None:
                enabled = await self._feature_flags.is_enabled(
                    guild_id, module_name, module.default_enabled
                )
                if not enabled:
                    logger.debug(
                        f"Module '{module_name}' is disabled for guild {guild_id}"
                    )
                    continue

            # Check required services
            for service_name in module.required_services:
                if not ctx.services.get(service_name):
                    logger.warning(
                        f"Module '{module_name}' requires service '{service_name}' "
                        "which is not available"
                    )
                    continue

            try:
                logger.info(f"Loading module: {module_name}")
                await module.setup(bot, ctx)
            except Exception as e:
                logger.error(f"Failed to load module '{module_name}': {e}", exc_info=True)

    def _resolve_dependencies(self) -> List[str]:
        """Resolve module dependencies and return load order."""
        # Simple topological sort
        visited = set()
        result = []

        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            module = self._modules.get(name)
            if module:
                for dep in module.depends_on:
                    if dep not in self._modules:
                        logger.warning(
                            f"Module '{name}' depends on '{dep}' which is not registered"
                        )
                    else:
                        visit(dep)
            result.append(name)

        for module_name in self._modules:
            if module_name not in visited:
                visit(module_name)

        return result
