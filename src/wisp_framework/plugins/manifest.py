"""Plugin manifest definition and parsing."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PluginManifest:
    """Plugin manifest containing metadata and configuration."""

    name: str
    version: str
    description: str
    entrypoint: str
    framework_min_version: str | None = None
    dependencies: list[str] = field(default_factory=list)
    config_schema: str | None = None
    migrations_path: str | None = None
    capabilities_provided: list[str] = field(default_factory=list)
    capabilities_required: list[str] = field(default_factory=list)
    default_enabled: bool = True
    guild_scoped: bool = True

    @classmethod
    def from_toml(cls, path: Path) -> "PluginManifest":
        """Load plugin manifest from TOML file.

        Args:
            path: Path to plugin.toml file

        Returns:
            PluginManifest instance

        Raises:
            ValueError: If manifest is invalid
        """
        if not path.exists():
            raise ValueError(f"Manifest file not found: {path}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        plugin_data = data.get("plugin", {})
        if not plugin_data:
            raise ValueError("Missing [plugin] section in manifest")

        return cls(
            name=plugin_data.get("name", ""),
            version=plugin_data.get("version", "0.0.0"),
            description=plugin_data.get("description", ""),
            entrypoint=plugin_data.get("entrypoint", ""),
            framework_min_version=plugin_data.get("framework_min_version"),
            dependencies=plugin_data.get("dependencies", []),
            config_schema=plugin_data.get("config_schema"),
            migrations_path=plugin_data.get("migrations_path"),
            capabilities_provided=plugin_data.get("capabilities_provided", []),
            capabilities_required=plugin_data.get("capabilities_required", []),
            default_enabled=plugin_data.get("default_enabled", True),
            guild_scoped=plugin_data.get("guild_scoped", True),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PluginManifest":
        """Create PluginManifest from dictionary.

        Args:
            data: Dictionary with manifest data

        Returns:
            PluginManifest instance
        """
        plugin_data = data.get("plugin", data)
        return cls(
            name=plugin_data.get("name", ""),
            version=plugin_data.get("version", "0.0.0"),
            description=plugin_data.get("description", ""),
            entrypoint=plugin_data.get("entrypoint", ""),
            framework_min_version=plugin_data.get("framework_min_version"),
            dependencies=plugin_data.get("dependencies", []),
            config_schema=plugin_data.get("config_schema"),
            migrations_path=plugin_data.get("migrations_path"),
            capabilities_provided=plugin_data.get("capabilities_provided", []),
            capabilities_required=plugin_data.get("capabilities_required", []),
            default_enabled=plugin_data.get("default_enabled", True),
            guild_scoped=plugin_data.get("guild_scoped", True),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert manifest to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "plugin": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "entrypoint": self.entrypoint,
                "framework_min_version": self.framework_min_version,
                "dependencies": self.dependencies,
                "config_schema": self.config_schema,
                "migrations_path": self.migrations_path,
                "capabilities_provided": self.capabilities_provided,
                "capabilities_required": self.capabilities_required,
                "default_enabled": self.default_enabled,
                "guild_scoped": self.guild_scoped,
            }
        }
