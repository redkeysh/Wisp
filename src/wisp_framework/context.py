"""Bot context holding services and configuration."""

from typing import Any, Optional

from wisp_framework.config import AppConfig
from wisp_framework.db.guild_data import GuildDataService
from wisp_framework.services.base import ServiceContainer


class BotContext:
    """Context object passed to modules with services and configuration."""

    def __init__(
        self,
        config: AppConfig,
        services: ServiceContainer,
        guild_data: Optional[GuildDataService] = None,
    ) -> None:
        """Initialize bot context."""
        self.config = config
        self.services = services
        self.guild_data = guild_data or GuildDataService(services.get("db"))
