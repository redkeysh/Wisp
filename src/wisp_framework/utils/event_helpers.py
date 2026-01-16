"""Helper functions for registering event handlers with EventRouter."""

from collections.abc import Awaitable, Callable
from typing import Any

from wisp_framework.context import WispContext


def register_event_handler(
    bot: Any,
    event_name: str,
    handler: Callable[[WispContext, Any], Awaitable[None]],
    priority: int = 0,
    module_name: str | None = None,
) -> bool:
    """Register an event handler with the bot's EventRouter.

    Helper function for modules to easily register event handlers.

    Args:
        bot: Bot instance (must have event_router attribute)
        event_name: Event name (e.g., "on_message", "on_member_join")
        handler: Handler function that takes (WispContext, event) -> None
        priority: Handler priority (higher = runs first, default: 0)
        module_name: Optional module name for tracking

    Returns:
        True if registration was successful, False if EventRouter not available

    Example:
        ```python
        async def setup(self, bot: Any, ctx: Any) -> None:
            async def handle_member_join(wisp_ctx: WispContext, member: discord.Member) -> None:
                wisp_ctx.bound_logger.info(f"Member joined: {member.name}")
                # Your handler logic here

            register_event_handler(
                bot,
                "on_member_join",
                handle_member_join,
                priority=10,
                module_name=self.name
            )
        ```
    """
    event_router = getattr(bot, "event_router", None)
    if not event_router:
        return False

    event_router.register(event_name, handler, priority=priority, module_name=module_name)
    return True


def unregister_event_handler(
    bot: Any,
    event_name: str,
    handler: Callable[[WispContext, Any], Awaitable[None]] | None = None,
    module_name: str | None = None,
) -> bool:
    """Unregister an event handler from the bot's EventRouter.

    Args:
        bot: Bot instance (must have event_router attribute)
        event_name: Event name
        handler: Specific handler to remove (if None, removes all for module)
        module_name: Remove all handlers for this module

    Returns:
        True if any handlers were removed, False otherwise
    """
    event_router = getattr(bot, "event_router", None)
    if not event_router:
        return False

    return event_router.unregister(event_name, handler=handler, module_name=module_name)


def list_event_handlers(bot: Any, event_name: str | None = None) -> dict[str, list[dict[str, Any]]]:
    """List registered event handlers.

    Args:
        bot: Bot instance (must have event_router attribute)
        event_name: Optional event name to filter by

    Returns:
        Dictionary mapping event names to lists of handler info
    """
    event_router = getattr(bot, "event_router", None)
    if not event_router:
        return {}

    return event_router.list_handlers(event_name=event_name)
