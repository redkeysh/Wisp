"""Event router for centralized event handling."""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from wisp_framework.context import WispContext
from wisp_framework.core.pipeline import Pipeline, create_default_pipeline
from wisp_framework.observability.metrics import record_event_metric

logger = logging.getLogger(__name__)


@dataclass
class EventHandler:
    """Represents a registered event handler with metadata."""

    handler: Callable[[WispContext, Any], Awaitable[None]]
    priority: int = 0  # Higher priority handlers run first
    module_name: str | None = None  # Module that registered this handler
    enabled: bool = True  # Can be disabled per-guild or globally


class EventRouter:
    """Centralized event router with gating, filtering, and pipeline integration.

    Features:
    - Request ID tracking for all events
    - Pipeline integration (rate limiting, metrics, logging, error handling)
    - Per-guild enable/disable
    - Handler priority ordering
    - Automatic bot/DM filtering
    - Error isolation (one handler failure doesn't affect others)
    """

    def __init__(
        self,
        ignore_bots: bool = True,
        ignore_dms: bool = True,
        pipeline: Pipeline | None = None,
    ) -> None:
        """Initialize event router.

        Args:
            ignore_bots: Whether to ignore bot messages/users
            ignore_dms: Whether to ignore DMs
            pipeline: Optional pipeline for event processing
        """
        self.ignore_bots = ignore_bots
        self.ignore_dms = ignore_dms
        self._handlers: dict[str, list[EventHandler]] = {}
        self._pipeline = pipeline or create_default_pipeline()
        self._enabled_guilds: set[int] = set()  # Empty set means all enabled
        self._disabled_guilds: set[int] = set()  # Explicitly disabled guilds

    def register(
        self,
        event_name: str,
        handler: Callable[[WispContext, Any], Awaitable[None]],
        priority: int = 0,
        module_name: str | None = None,
    ) -> None:
        """Register an event handler.

        Args:
            event_name: Event name (e.g., "on_message", "on_member_join")
            handler: Handler function that takes (WispContext, event) -> None
            priority: Handler priority (higher = runs first, default: 0)
            module_name: Optional module name for tracking
        """
        if event_name not in self._handlers:
            self._handlers[event_name] = []

        handler_obj = EventHandler(
            handler=handler,
            priority=priority,
            module_name=module_name,
        )
        self._handlers[event_name].append(handler_obj)

        # Sort by priority (higher first)
        self._handlers[event_name].sort(key=lambda h: h.priority, reverse=True)

        logger.info(
            f"Registered handler for event '{event_name}' "
            f"(priority={priority}, module={module_name or 'unknown'})"
        )

    def unregister(
        self,
        event_name: str,
        handler: Callable[[WispContext, Any], Awaitable[None]] | None = None,
        module_name: str | None = None,
    ) -> bool:
        """Unregister event handler(s).

        Args:
            event_name: Event name
            handler: Specific handler to remove (if None, removes all for module)
            module_name: Remove all handlers for this module

        Returns:
            True if any handlers were removed
        """
        if event_name not in self._handlers:
            return False

        original_count = len(self._handlers[event_name])
        if handler:
            # Remove specific handler
            self._handlers[event_name] = [
                h for h in self._handlers[event_name] if h.handler != handler
            ]
        elif module_name:
            # Remove all handlers for module
            self._handlers[event_name] = [
                h for h in self._handlers[event_name] if h.module_name != module_name
            ]
        else:
            # Remove all handlers for event
            self._handlers[event_name] = []

        removed = len(self._handlers[event_name]) < original_count
        if removed:
            logger.info(f"Unregistered handler(s) for event '{event_name}'")
        return removed

    def enable_for_guild(self, guild_id: int) -> None:
        """Enable event router for a specific guild.

        Args:
            guild_id: Guild ID to enable
        """
        self._disabled_guilds.discard(guild_id)
        self._enabled_guilds.add(guild_id)
        logger.debug(f"Enabled event router for guild {guild_id}")

    def disable_for_guild(self, guild_id: int) -> None:
        """Disable event router for a specific guild.

        Args:
            guild_id: Guild ID to disable
        """
        self._enabled_guilds.discard(guild_id)
        self._disabled_guilds.add(guild_id)
        logger.debug(f"Disabled event router for guild {guild_id}")

    def is_enabled_for_guild(self, guild_id: int | None) -> bool:
        """Check if event router is enabled for a guild.

        Args:
            guild_id: Guild ID (None for global/DM events)

        Returns:
            True if enabled for this guild
        """
        if guild_id is None:
            # DMs are enabled unless ignore_dms is True
            return not self.ignore_dms

        if self._disabled_guilds:
            return guild_id not in self._disabled_guilds

        if self._enabled_guilds:
            return guild_id in self._enabled_guilds

        # Default: enabled for all guilds
        return True

    async def route(self, event_name: str, event: Any, ctx: WispContext) -> None:
        """Route an event through registered handlers with pipeline integration.

        Args:
            event_name: Event name (e.g., "on_message")
            event: Event object (discord.Message, discord.Member, etc.)
            ctx: WispContext for this event
        """
        # Apply global filters
        if not await self._should_process(event, ctx):
            return

        # Check per-guild enable/disable
        if not self.is_enabled_for_guild(ctx.guild_id):
            ctx.bound_logger.debug(f"Event router disabled for guild {ctx.guild_id}")
            return

        # Get handlers
        handlers = self._handlers.get(event_name, [])
        if not handlers:
            return

        # Filter to enabled handlers
        enabled_handlers = [h for h in handlers if h.enabled]
        if not enabled_handlers:
            return

        ctx.bound_logger.debug(f"Routing event '{event_name}' to {len(enabled_handlers)} handler(s)")

        # Route each handler through pipeline
        success_count = 0
        error_count = 0

        for handler_obj in enabled_handlers:
            try:
                # Set event_name in context for metrics (create a copy to avoid mutation)
                handler_ctx = WispContext(
                    config=ctx.config,
                    services=ctx.services,
                    invocation_type=ctx.invocation_type,
                    guild_id=ctx.guild_id,
                    channel_id=ctx.channel_id,
                    user_id=ctx.user_id,
                    request_id=ctx.request_id,
                    guild_data=ctx.guild_data,
                    feature_flags=ctx.feature_flags,
                )
                # Store event_name as attribute for metrics middleware
                handler_ctx.event_name = event_name

                # Create handler wrapper that captures handler_obj and event properly
                # Use default parameter to avoid closure issues
                async def handler_wrapper(
                    wisp_ctx: WispContext, h=handler_obj, ev=event
                ) -> None:
                    await h.handler(wisp_ctx, ev)

                # Execute through pipeline (includes rate limiting, metrics, logging, error handling)
                await self._pipeline.execute(handler_ctx, handler_wrapper)
                success_count += 1

            except Exception as e:
                error_count += 1
                ctx.bound_logger.error(
                    f"Error in event handler '{event_name}' "
                    f"(module={handler_obj.module_name or 'unknown'}): {e}",
                    exc_info=True,
                )

        # Record aggregate metrics
        if ctx.metrics:
            record_event_metric(ctx.metrics, event_name, "routed")
            if success_count > 0:
                record_event_metric(ctx.metrics, event_name, "success")
            if error_count > 0:
                record_event_metric(ctx.metrics, event_name, "error")

    async def _should_process(self, event: Any, ctx: WispContext) -> bool:
        """Check if event should be processed based on filters.

        Args:
            event: Event object
            ctx: WispContext

        Returns:
            True if event should be processed
        """
        # Ignore bots
        if self.ignore_bots:
            if hasattr(event, "author") and hasattr(event.author, "bot") and event.author.bot:
                if ctx.metrics:
                    ctx.metrics.increment("wisp.events.filtered.bot_message")
                return False
            if hasattr(event, "user") and hasattr(event.user, "bot") and event.user.bot:
                if ctx.metrics:
                    ctx.metrics.increment("wisp.events.filtered.bot_user")
                return False

        # Ignore DMs
        if self.ignore_dms:
            if ctx.guild_id is None:
                if ctx.metrics:
                    ctx.metrics.increment("wisp.events.filtered.dm")
                return False

        return True

    def list_handlers(self, event_name: str | None = None) -> dict[str, list[dict[str, Any]]]:
        """List registered handlers.

        Args:
            event_name: Optional event name to filter by

        Returns:
            Dictionary mapping event names to lists of handler info
        """
        if event_name:
            handlers = self._handlers.get(event_name, [])
            return {
                event_name: [
                    {
                        "priority": h.priority,
                        "module": h.module_name,
                        "enabled": h.enabled,
                    }
                    for h in handlers
                ]
            }

        return {
            name: [
                {
                    "priority": h.priority,
                    "module": h.module_name,
                    "enabled": h.enabled,
                }
                for h in handlers
            ]
            for name, handlers in self._handlers.items()
        }
