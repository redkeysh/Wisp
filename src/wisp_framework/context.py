"""Bot context holding services and configuration."""

import logging
import uuid
from typing import TYPE_CHECKING, Any

from wisp_framework.config import AppConfig
from wisp_framework.db.guild_data import GuildDataService
from wisp_framework.feature_flags import FeatureFlags
from wisp_framework.services.base import ServiceContainer

if TYPE_CHECKING:
    from wisp_framework.policy.engine import PolicyEngine


class BotContext:
    """Context object passed to modules with services and configuration."""

    def __init__(
        self,
        config: AppConfig,
        services: ServiceContainer,
        guild_data: GuildDataService | None = None,
    ) -> None:
        """Initialize bot context."""
        self.config = config
        self.services = services
        self.guild_data = guild_data or GuildDataService(services.get("db"))


class WispContext(BotContext):
    """Extended context with request tracking, logging, and framework features.

    This context is created for every command, event, or job execution.
    It provides request_id tracking, bound logger, and lazy handles to services.
    """

    def __init__(
        self,
        config: AppConfig,
        services: ServiceContainer,
        invocation_type: str,
        guild_id: int | None = None,
        channel_id: int | None = None,
        user_id: int | None = None,
        request_id: str | None = None,
        guild_data: GuildDataService | None = None,
        feature_flags: FeatureFlags | None = None,
    ) -> None:
        """Initialize Wisp context.

        Args:
            config: Application configuration
            services: Service container
            invocation_type: Type of invocation ("slash", "prefix", "event", "job")
            guild_id: Optional guild ID
            channel_id: Optional channel ID
            user_id: Optional user ID
            request_id: Optional request ID (generated if not provided)
            guild_data: Optional guild data service
            feature_flags: Optional feature flags instance
        """
        super().__init__(config, services, guild_data)
        self.request_id = request_id or str(uuid.uuid4())
        self.invocation_type = invocation_type
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.user_id = user_id
        self._feature_flags = feature_flags
        self._bound_logger: logging.Logger | None = None
        self._db_session: Any | None = None
        self._policy: "PolicyEngine | None" = None

    @property
    def bound_logger(self) -> logging.Logger:
        """Get logger bound with request_id context."""
        if self._bound_logger is None:
            from wisp_framework.observability.logging import get_logger

            self._bound_logger = get_logger(self)
        return self._bound_logger

    @property
    def db_session(self) -> Any:
        """Get lazy database session handle."""
        if self._db_session is None:
            db_service = self.services.get("db")
            if db_service and hasattr(db_service, "session_factory"):
                self._db_session = db_service.session_factory()
        return self._db_session

    @property
    def cache(self) -> Any:
        """Get cache service handle."""
        return self.services.get("cache")

    @property
    def metrics(self) -> Any:
        """Get metrics service handle."""
        return self.services.get("metrics")

    @property
    def feature_flags(self) -> FeatureFlags | None:
        """Get feature flags instance."""
        return self._feature_flags

    @property
    def policy(self) -> "PolicyEngine | None":
        """Get policy evaluation handle (available after Phase 4)."""
        if self._policy is None:
            # Lazy import to avoid circular dependency
            try:
                from wisp_framework.policy.engine import PolicyEngine

                policy_service = self.services.get("policy")
                if isinstance(policy_service, PolicyEngine):
                    self._policy = policy_service
            except ImportError:
                # Policy engine not yet implemented
                pass
        return self._policy

    @classmethod
    def from_interaction(
        cls,
        config: AppConfig,
        services: ServiceContainer,
        interaction: Any,
        invocation_type: str = "slash",
        feature_flags: FeatureFlags | None = None,
    ) -> "WispContext":
        """Create WispContext from Discord interaction.

        Args:
            config: Application configuration
            services: Service container
            interaction: Discord interaction object or commands.Context
            invocation_type: Type of invocation ("slash" or "prefix")
            feature_flags: Optional feature flags instance

        Returns:
            WispContext instance
        """
        # Handle both Interaction and commands.Context
        if hasattr(interaction, "guild_id"):
            # Discord Interaction
            guild_id = interaction.guild_id
            channel_id = interaction.channel_id if hasattr(interaction, "channel_id") else None
            user_id = interaction.user.id if hasattr(interaction, "user") and interaction.user else None
        elif hasattr(interaction, "guild"):
            # commands.Context
            guild_id = interaction.guild.id if interaction.guild else None
            channel_id = interaction.channel.id if interaction.channel else None
            user_id = interaction.author.id if interaction.author else None
        else:
            guild_id = None
            channel_id = None
            user_id = None

        return cls(
            config=config,
            services=services,
            invocation_type=invocation_type,
            guild_id=guild_id,
            channel_id=channel_id,
            user_id=user_id,
            feature_flags=feature_flags,
        )

    @classmethod
    def from_event(
        cls,
        config: AppConfig,
        services: ServiceContainer,
        event: Any,
        feature_flags: FeatureFlags | None = None,
    ) -> "WispContext":
        """Create WispContext from Discord event.

        Args:
            config: Application configuration
            services: Service container
            event: Discord event object (message, member, etc.)
            feature_flags: Optional feature flags instance

        Returns:
            WispContext instance
        """
        guild_id = getattr(event, "guild_id", None) or (
            getattr(event.guild, "id", None) if hasattr(event, "guild") and event.guild else None
        )
        channel_id = getattr(event, "channel_id", None) or (
            getattr(event.channel, "id", None) if hasattr(event, "channel") and event.channel else None
        )
        user_id = getattr(event, "author", None) and getattr(event.author, "id", None) or (
            getattr(event, "user", None) and getattr(event.user, "id", None)
        )

        return cls(
            config=config,
            services=services,
            invocation_type="event",
            guild_id=guild_id,
            channel_id=channel_id,
            user_id=user_id,
            feature_flags=feature_flags,
        )

    @classmethod
    def from_job(
        cls,
        config: AppConfig,
        services: ServiceContainer,
        job_id: str,
        guild_id: int | None = None,
        feature_flags: FeatureFlags | None = None,
    ) -> "WispContext":
        """Create WispContext for background job execution.

        Args:
            config: Application configuration
            services: Service container
            job_id: Job identifier (used as request_id)
            guild_id: Optional guild ID
            feature_flags: Optional feature flags instance

        Returns:
            WispContext instance
        """
        return cls(
            config=config,
            services=services,
            invocation_type="job",
            guild_id=guild_id,
            request_id=job_id,
            feature_flags=feature_flags,
        )
