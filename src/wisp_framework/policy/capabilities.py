"""Capability definitions and registry."""


class CapabilityRegistry:
    """Registry for capability strings."""

    # Core capabilities
    ADMIN_CONFIG = "admin.config"
    ADMIN_MODULES = "admin.modules"
    ADMIN_PLUGINS = "admin.plugins"
    ADMIN_POLICY = "admin.policy"

    # Moderation capabilities
    MODERATION_KICK = "moderation.kick"
    MODERATION_BAN = "moderation.ban"
    MODERATION_MUTE = "moderation.mute"
    MODERATION_WARN = "moderation.warn"

    # Config capabilities
    CONFIG_READ = "config.read"
    CONFIG_WRITE = "config.write"

    # Plugin capabilities
    PLUGINS_MANAGE = "plugins.manage"
    PLUGINS_ENABLE = "plugins.enable"
    PLUGINS_DISABLE = "plugins.disable"

    @classmethod
    def validate(cls, capability: str) -> bool:
        """Validate a capability string format.

        Args:
            capability: Capability string (e.g., "moderation.kick")

        Returns:
            True if valid format
        """
        if not capability or not isinstance(capability, str):
            return False
        parts = capability.split(".")
        return len(parts) >= 2 and all(part.isalnum() or "_" in part for part in parts)
