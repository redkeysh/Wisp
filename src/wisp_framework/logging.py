"""Structured logging setup with module awareness and correlation IDs."""

import contextvars
import logging
import sys
import uuid
from typing import TYPE_CHECKING

from wisp_framework.config import AppConfig

if TYPE_CHECKING:
    from wisp_framework.context import WispContext

# Context variable for correlation_id in async contexts
_correlation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("correlation_id", default=None)


class CorrelationFilter(logging.Filter):
    """Logging filter that adds correlation ID and request_id to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID and request_id if not already present."""
        if not hasattr(record, "correlation_id"):
            correlation_id = _correlation_id_var.get()
            record.correlation_id = correlation_id or "no-correlation-id"
        if not hasattr(record, "request_id"):
            # Try to get request_id from context variable (set by observability.logging)
            from wisp_framework.observability.logging import _request_id_var

            request_id = _request_id_var.get()
            record.request_id = request_id or "no-request-id"
        return True


def setup_logging(
    config: AppConfig,
    formatter: logging.Formatter | None = None,
    handler: logging.Handler | None = None,
) -> None:
    """Set up structured logging with module awareness.

    Args:
        config: Application configuration
        formatter: Optional custom formatter. If not provided, uses default structured formatter.
        handler: Optional custom handler. If not provided, uses StreamHandler to stdout.

    Log levels can be controlled via environment variables:
    - LOG_LEVEL: Root log level (default: INFO)
    - LOG_LEVEL_WISP_FRAMEWORK: Wisp Framework log level (default: same as LOG_LEVEL)
    """
    import os

    # Get root log level
    root_log_level_str = config.log_level
    root_log_level = getattr(logging, root_log_level_str, logging.INFO)

    # Get Wisp Framework specific log level (if set)
    wisp_log_level_str = os.getenv("LOG_LEVEL_WISP_FRAMEWORK", root_log_level_str).upper()
    wisp_log_level = getattr(logging, wisp_log_level_str, root_log_level)

    # Create formatter if not provided
    if formatter is None:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)8s] [%(name)s] [%(correlation_id)s] [%(request_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Create handler if not provided
    if handler is None:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(root_log_level)
        handler.setFormatter(formatter)
        handler.addFilter(CorrelationFilter())

    # Ensure handler has formatter and filter
    if handler.formatter is None:
        handler.setFormatter(formatter)
    # handler.filters is a list, not a dict, so iterate directly
    if not any(isinstance(f, CorrelationFilter) for f in handler.filters):
        handler.addFilter(CorrelationFilter())

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(root_log_level)
    root_logger.addHandler(handler)

    # Suppress noisy loggers
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)

    # Set Wisp Framework logger level (allows suppressing WF logs separately)
    logging.getLogger("wisp_framework").setLevel(wisp_log_level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module."""
    return logging.getLogger(name)


class CorrelationContext:
    """Context manager for correlation IDs using contextvars for async safety."""

    def __init__(self, correlation_id: str | None = None) -> None:
        """Initialize with optional correlation ID."""
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self._token: contextvars.Token[str | None] | None = None

    def __enter__(self) -> "CorrelationContext":
        """Enter context and set correlation ID."""
        self._token = _correlation_id_var.set(self.correlation_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        """Exit context and restore old correlation ID."""
        if self._token is not None:
            _correlation_id_var.reset(self._token)


def get_context_logger(ctx: "WispContext") -> logging.Logger:
    """Get a logger bound to the WispContext with request_id.

    This is a convenience wrapper that uses the observability module.

    Args:
        ctx: WispContext instance

    Returns:
        Logger instance with request_id in context
    """
    from wisp_framework.observability.logging import get_logger as _get_logger

    return _get_logger(ctx)
