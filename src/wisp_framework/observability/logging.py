"""Enhanced logging with context binding."""

import contextvars
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wisp_framework.context import WispContext

# Context variable for request_id in async contexts
_request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Logging filter that adds request_id from context variable."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id if not already present."""
        if not hasattr(record, "request_id"):
            request_id = _request_id_var.get()
            record.request_id = request_id or "no-request-id"
        return True


def get_logger(ctx: "WispContext") -> logging.Logger:
    """Get a logger bound to the WispContext with request_id.

    Args:
        ctx: WispContext instance

    Returns:
        Logger instance with request_id in context
    """
    logger = logging.getLogger(ctx.__class__.__module__)

    # Set request_id in context variable for this async context
    _request_id_var.set(ctx.request_id)

    # Ensure logger has RequestIdFilter
    if not any(isinstance(f, RequestIdFilter) for f in logger.filters):
        logger.addFilter(RequestIdFilter())

    return logger
