"""Plugin system for Wisp Framework."""

from wisp_framework.plugins.manifest import PluginManifest
from wisp_framework.plugins.plugin import Plugin
from wisp_framework.plugins.registry import PluginRegistry

__all__ = ["Plugin", "PluginManifest", "PluginRegistry"]
