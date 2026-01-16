"""Module registry for managing and loading modules."""

import importlib
import logging
import pkgutil
from typing import Any

from wisp_framework.feature_flags import FeatureFlags
from wisp_framework.module import Module

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """Registry for managing framework modules."""

    def __init__(self, feature_flags: FeatureFlags) -> None:
        """Initialize the module registry."""
        self._modules: dict[str, Module] = {}
        self._feature_flags = feature_flags
        # Track which modules have been set up per guild_id
        # Key: (module_name, guild_id) where guild_id can be None for global
        self._setup_complete: set[tuple[str, int | None]] = set()

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

    def list_modules(self) -> list[str]:
        """List all registered module names."""
        return list(self._modules.keys())

    def get_module(self, name: str) -> Module | None:
        """Get a module by name."""
        return self._modules.get(name)

    def reset_setup_state(self, module_name: str | None = None) -> None:
        """Reset setup state for a module or all modules.

        Args:
            module_name: Module name to reset, or None to reset all modules
        """
        if module_name is None:
            self._setup_complete.clear()
            logger.debug("Reset setup state for all modules")
        else:
            # Remove all setup states for this module (all guilds)
            self._setup_complete = {
                (name, gid) for name, gid in self._setup_complete if name != module_name
            }
            logger.debug(f"Reset setup state for module '{module_name}'")

    async def load_enabled_modules(
        self, bot: Any, ctx: Any, guild_id: int | None = None
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

            # Check if module has already been set up
            # For global modules (guild_id=None), only set up once globally
            # For guild-specific modules, check if already set up for this guild
            # Also prevent re-setting up global modules when loading per-guild
            if guild_id is None:
                # Global setup - check if already set up globally
                setup_key = (module_name, None)
            else:
                # Guild-specific setup - check if already set up for this guild
                # Also check if module was already set up globally (most commands are global)
                global_setup_key = (module_name, None)
                if global_setup_key in self._setup_complete:
                    logger.debug(
                        f"Module '{module_name}' already set up globally, skipping guild {guild_id} setup"
                    )
                    continue
                setup_key = (module_name, guild_id)

            if setup_key in self._setup_complete:
                logger.debug(
                    f"Module '{module_name}' already set up for guild {guild_id}, skipping"
                )
                continue

            try:
                logger.info(f"Loading module: {module_name} (guild: {guild_id})")
                await module.setup(bot, ctx)
                # Mark module as set up for this guild
                self._setup_complete.add(setup_key)
            except Exception as e:
                logger.error(f"Failed to load module '{module_name}': {e}", exc_info=True)

    def _resolve_dependencies(self) -> list[str]:
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
