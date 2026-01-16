"""Plugin registry for managing plugin lifecycle and state."""

import importlib
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import select

from wisp_framework.db.models import PluginState
from wisp_framework.feature_flags import FeatureFlags
from wisp_framework.plugins.manifest import PluginManifest
from wisp_framework.plugins.plugin import Plugin
from wisp_framework.services.db import DatabaseService

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Registry for managing framework plugins with lifecycle and state."""

    def __init__(
        self,
        feature_flags: FeatureFlags,
        db_service: DatabaseService | None = None,
    ) -> None:
        """Initialize the plugin registry.

        Args:
            feature_flags: Feature flags instance
            db_service: Optional database service for plugin state persistence
        """
        self._plugins: dict[str, Plugin] = {}
        self._feature_flags = feature_flags
        self._db_service = db_service
        # Track which plugins have been set up per guild_id
        # Key: (plugin_name, guild_id) where guild_id can be None for global
        self._setup_complete: set[tuple[str, int | None]] = set()
        # Track loaded plugins (on_load called)
        self._loaded_plugins: set[str] = set()

    def register(self, plugin: Plugin) -> None:
        """Register a plugin.

        Args:
            plugin: Plugin instance

        Raises:
            ValueError: If plugin is already registered
        """
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin '{plugin.name}' is already registered")
        self._plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")

    def discover_plugins(self, plugin_dir: Path) -> None:
        """Discover plugins from a directory.

        Looks for plugin.toml files and loads plugins.

        Args:
            plugin_dir: Directory containing plugins
        """
        if not plugin_dir.exists():
            logger.warning(f"Plugin directory does not exist: {plugin_dir}")
            return

        for plugin_path in plugin_dir.iterdir():
            if not plugin_path.is_dir():
                continue

            manifest_path = plugin_path / "plugin.toml"
            if not manifest_path.exists():
                continue

            try:
                manifest = PluginManifest.from_toml(manifest_path)
                # Load plugin entrypoint
                plugin_module = importlib.import_module(manifest.entrypoint)
                # Find Plugin subclass
                plugin_class = None
                for attr_name in dir(plugin_module):
                    attr = getattr(plugin_module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, Plugin)
                        and attr is not Plugin
                    ):
                        plugin_class = attr
                        break

                if not plugin_class:
                    logger.warning(f"No Plugin class found in {manifest.entrypoint}")
                    continue

                plugin_instance = plugin_class()
                # Verify manifest matches
                if plugin_instance.manifest.name != manifest.name:
                    logger.warning(
                        f"Plugin manifest name mismatch: {manifest.name} != {plugin_instance.manifest.name}"
                    )
                    continue

                self.register(plugin_instance)
                logger.info(f"Discovered plugin: {manifest.name} from {plugin_path}")
            except Exception as e:
                logger.error(f"Failed to discover plugin from {plugin_path}: {e}", exc_info=True)

    def list_plugins(self) -> list[str]:
        """List all registered plugin names.

        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())

    def get_plugin(self, name: str) -> Plugin | None:
        """Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(name)

    async def load_plugin(self, plugin_name: str, app: Any, services: Any) -> None:
        """Load a plugin (call on_load).

        Args:
            plugin_name: Plugin name
            app: Application instance
            services: Service container
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")

        if plugin_name in self._loaded_plugins:
            logger.debug(f"Plugin '{plugin_name}' already loaded")
            return

        try:
            await plugin.on_load(app, services)
            self._loaded_plugins.add(plugin_name)
            logger.info(f"Loaded plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"Failed to load plugin '{plugin_name}': {e}", exc_info=True)
            await self._mark_plugin_degraded(plugin_name, str(e))
            raise

    async def enable_plugin(
        self, plugin_name: str, guild_id: int | None = None
    ) -> None:
        """Enable a plugin for a guild or globally.

        Args:
            plugin_name: Plugin name
            guild_id: Guild ID (None for global)
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")

        # Update database state
        await self._set_plugin_enabled(plugin_name, guild_id, True)

        # Call on_enable hook
        try:
            await plugin.on_enable(guild_id)
            logger.info(f"Enabled plugin '{plugin_name}' for guild {guild_id}")
        except Exception as e:
            logger.error(f"Error in on_enable for plugin '{plugin_name}': {e}", exc_info=True)
            await self._mark_plugin_degraded(plugin_name, str(e))

    async def disable_plugin(
        self, plugin_name: str, guild_id: int | None = None
    ) -> None:
        """Disable a plugin for a guild or globally.

        Args:
            plugin_name: Plugin name
            guild_id: Guild ID (None for global)
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' not found")

        # Update database state
        await self._set_plugin_enabled(plugin_name, guild_id, False)

        # Call on_disable hook
        try:
            await plugin.on_disable(guild_id)
            logger.info(f"Disabled plugin '{plugin_name}' for guild {guild_id}")
        except Exception as e:
            logger.error(f"Error in on_disable for plugin '{plugin_name}': {e}", exc_info=True)

    async def load_enabled_plugins(
        self, bot: Any, ctx: Any, guild_id: int | None = None
    ) -> None:
        """Load all enabled plugins for a guild.

        Args:
            bot: The Discord bot instance
            ctx: Bot context with services and config
            guild_id: Guild ID (None for global plugins)
        """
        # Resolve dependencies
        plugins_to_load = self._resolve_dependencies()

        for plugin_name in plugins_to_load:
            plugin = self._plugins[plugin_name]

            # Check if enabled for this guild
            if guild_id is not None and plugin.guild_scoped:
                enabled = await self._is_plugin_enabled(plugin_name, guild_id)
                if not enabled:
                    logger.debug(
                        f"Plugin '{plugin_name}' is disabled for guild {guild_id}"
                    )
                    continue

            # Check if plugin is degraded
            if await self._is_plugin_degraded(plugin_name):
                logger.warning(f"Plugin '{plugin_name}' is degraded, skipping")
                continue

            # Check if already set up
            if guild_id is None:
                setup_key = (plugin_name, None)
            else:
                global_setup_key = (plugin_name, None)
                if global_setup_key in self._setup_complete:
                    logger.debug(
                        f"Plugin '{plugin_name}' already set up globally, skipping guild {guild_id} setup"
                    )
                    continue
                setup_key = (plugin_name, guild_id)

            if setup_key in self._setup_complete:
                logger.debug(
                    f"Plugin '{plugin_name}' already set up for guild {guild_id}, skipping"
                )
                continue

            try:
                logger.info(f"Loading plugin: {plugin_name} (guild: {guild_id})")
                await plugin.setup(bot, ctx)
                self._setup_complete.add(setup_key)
            except Exception as e:
                logger.error(f"Failed to load plugin '{plugin_name}': {e}", exc_info=True)
                await self._mark_plugin_degraded(plugin_name, str(e))

    async def unload_plugin(self, plugin_name: str) -> None:
        """Unload a plugin (call on_unload).

        Args:
            plugin_name: Plugin name
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return

        if plugin_name not in self._loaded_plugins:
            return

        try:
            await plugin.on_unload()
            self._loaded_plugins.discard(plugin_name)
            logger.info(f"Unloaded plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"Error unloading plugin '{plugin_name}': {e}", exc_info=True)

    def _resolve_dependencies(self) -> list[str]:
        """Resolve plugin dependencies and return load order."""
        visited = set()
        result = []

        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            plugin = self._plugins.get(name)
            if plugin:
                for dep in plugin.dependencies:
                    if dep not in self._plugins:
                        logger.warning(
                            f"Plugin '{name}' depends on '{dep}' which is not registered"
                        )
                    else:
                        visit(dep)
            result.append(name)

        for plugin_name in self._plugins:
            if plugin_name not in visited:
                visit(plugin_name)

        return result

    async def _is_plugin_enabled(
        self, plugin_name: str, guild_id: int | None = None
    ) -> bool:
        """Check if plugin is enabled for a guild.

        Args:
            plugin_name: Plugin name
            guild_id: Guild ID (None for global)

        Returns:
            True if enabled, False otherwise
        """
        if not self._db_service or not self._db_service.session_factory:
            # Fallback to feature flags
            return await self._feature_flags.is_enabled(
                guild_id or 0, plugin_name, True
            )

        try:
            async with self._db_service.session_factory() as session:
                stmt = select(PluginState).where(
                    PluginState.plugin_name == plugin_name,
                    PluginState.guild_id == guild_id,
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                if row:
                    return row.enabled
                # Default to plugin's default_enabled
                plugin = self._plugins.get(plugin_name)
                return plugin.default_enabled if plugin else True
        except Exception as e:
            logger.warning(f"Database check failed: {e}, using default")
            plugin = self._plugins.get(plugin_name)
            return plugin.default_enabled if plugin else True

    async def _set_plugin_enabled(
        self, plugin_name: str, guild_id: int | None, enabled: bool
    ) -> None:
        """Set plugin enabled state in database.

        Args:
            plugin_name: Plugin name
            guild_id: Guild ID (None for global)
            enabled: Whether to enable
        """
        if not self._db_service or not self._db_service.session_factory:
            # Fallback to feature flags
            await self._feature_flags.set_enabled(guild_id or 0, plugin_name, enabled)
            return

        try:
            async with self._db_service.session_factory() as session:
                stmt = select(PluginState).where(
                    PluginState.plugin_name == plugin_name,
                    PluginState.guild_id == guild_id,
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()

                plugin = self._plugins.get(plugin_name)
                if row:
                    row.enabled = enabled
                else:
                    row = PluginState(
                        plugin_name=plugin_name,
                        version=plugin.version if plugin else "0.0.0",
                        guild_id=guild_id,
                        enabled=enabled,
                    )
                    session.add(row)

                await session.commit()
        except Exception as e:
            logger.warning(f"Database set failed: {e}")

    async def _is_plugin_degraded(self, plugin_name: str) -> bool:
        """Check if plugin is degraded.

        Args:
            plugin_name: Plugin name

        Returns:
            True if degraded, False otherwise
        """
        if not self._db_service or not self._db_service.session_factory:
            return False

        try:
            async with self._db_service.session_factory() as session:
                stmt = select(PluginState).where(
                    PluginState.plugin_name == plugin_name,
                    PluginState.guild_id.is_(None),  # Check global state
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                return row.degraded if row else False
        except Exception as e:
            logger.warning(f"Database check failed: {e}")
            return False

    async def _mark_plugin_degraded(self, plugin_name: str, error: str) -> None:
        """Mark plugin as degraded with error.

        Args:
            plugin_name: Plugin name
            error: Error message
        """
        if not self._db_service or not self._db_service.session_factory:
            return

        try:
            async with self._db_service.session_factory() as session:
                stmt = select(PluginState).where(
                    PluginState.plugin_name == plugin_name,
                    PluginState.guild_id.is_(None),  # Update global state
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()

                plugin = self._plugins.get(plugin_name)
                if row:
                    row.degraded = True
                    row.last_error = error[:1000]  # Truncate if too long
                else:
                    row = PluginState(
                        plugin_name=plugin_name,
                        version=plugin.version if plugin else "0.0.0",
                        guild_id=None,
                        enabled=False,
                        degraded=True,
                        last_error=error[:1000],
                    )
                    session.add(row)

                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to mark plugin degraded: {e}")
