"""Plugin base class."""

from abc import ABC, abstractmethod
from typing import Any

from wisp_framework.plugins.manifest import PluginManifest


class Plugin(ABC):
    """Abstract base class for framework plugins.

    Plugins extend the framework with new functionality.
    They have a manifest, lifecycle hooks, and can provide capabilities.
    """

    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Plugin manifest."""
        pass

    @property
    def name(self) -> str:
        """Plugin name (from manifest)."""
        return self.manifest.name

    @property
    def version(self) -> str:
        """Plugin version (from manifest)."""
        return self.manifest.version

    @property
    def default_enabled(self) -> bool:
        """Whether the plugin is enabled by default."""
        return self.manifest.default_enabled

    @property
    def guild_scoped(self) -> bool:
        """Whether the plugin is guild-scoped."""
        return self.manifest.guild_scoped

    @property
    def capabilities_provided(self) -> list[str]:
        """Capabilities provided by this plugin."""
        return self.manifest.capabilities_provided

    @property
    def capabilities_required(self) -> list[str]:
        """Capabilities required by this plugin."""
        return self.manifest.capabilities_required

    @property
    def dependencies(self) -> list[str]:
        """Plugin dependencies (other plugin names)."""
        return self.manifest.dependencies

    async def on_load(self, app: Any, services: Any) -> None:
        """Called when the plugin is loaded (before enable).

        Args:
            app: Application instance (bot)
            services: Service container
        """
        pass

    @abstractmethod
    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the plugin (called when enabled).

        This is similar to Module.setup() and is called for each guild
        when the plugin is enabled.

        Args:
            bot: The Discord bot instance
            ctx: Bot context with services and config
        """
        pass

    async def on_enable(self, guild_id: int | None) -> None:
        """Called when plugin is enabled for a guild.

        Args:
            guild_id: Guild ID (None for global)
        """
        pass

    async def on_disable(self, guild_id: int | None) -> None:
        """Called when plugin is disabled for a guild.

        Args:
            guild_id: Guild ID (None for global)
        """
        pass

    async def teardown(self, bot: Any, ctx: Any) -> None:
        """Tear down the plugin (called when disabled).

        Args:
            bot: The Discord bot instance
            ctx: Bot context with services and config
        """
        pass

    async def on_unload(self) -> None:
        """Called when the plugin is unloaded.

        This is called during bot shutdown or when the plugin is removed.
        """
        pass
