"""Adapter for converting Module to Plugin for backward compatibility."""

from typing import Any

from wisp_framework.module import Module
from wisp_framework.plugins.manifest import PluginManifest
from wisp_framework.plugins.plugin import Plugin


class ModulePluginAdapter(Plugin):
    """Adapter that wraps a Module as a Plugin."""

    def __init__(self, module: Module) -> None:
        """Initialize adapter.

        Args:
            module: Module instance to wrap
        """
        self._module = module
        # Create a minimal manifest
        self._manifest = PluginManifest(
            name=module.name,
            version="0.0.0",
            description=f"Module '{module.name}' (legacy)",
            entrypoint=f"wisp_framework.modules.{module.name}",
            default_enabled=module.default_enabled,
            guild_scoped=True,
        )

    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest."""
        return self._manifest

    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the plugin (delegates to module.setup)."""
        await self._module.setup(bot, ctx)

    async def teardown(self, bot: Any, ctx: Any) -> None:
        """Tear down the plugin (delegates to module.teardown)."""
        await self._module.teardown(bot, ctx)
