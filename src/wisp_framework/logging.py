"""Structured logging setup with module awareness and correlation IDs."""

import logging
import sys
import uuid

from wisp_framework.config import AppConfig


class CorrelationFilter(logging.Filter):
    """Logging filter that adds correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID if not already present."""
        if not hasattr(record, "correlation_id"):
            record.correlation_id = getattr(
                logging.currentframe(), "correlation_id", None
            )
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
            fmt="%(asctime)s [%(levelname)8s] [%(name)s] [%(correlation_id)s] %(message)s",
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
    if not any(isinstance(f, CorrelationFilter) for f in handler.filters.values()):
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
    """Context manager for correlation IDs."""

    def __init__(self, correlation_id: str | None = None) -> None:
        """Initialize with optional correlation ID."""
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.old_id: str | None = None

    def __enter__(self) -> "CorrelationContext":
        """Enter context and set correlation ID."""
        # Store in thread-local or context variable
        # For simplicity, we'll use a module-level variable
        # In production, consider using contextvars
        import wisp_framework.logging as logging_module

        self.old_id = getattr(logging_module, "_current_correlation_id", None)
        logging_module._current_correlation_id = self.correlation_id
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        """Exit context and restore old correlation ID."""
        import wisp_framework.logging as logging_module

        if self.old_id is None:
            if hasattr(logging_module, "_current_correlation_id"):
                delattr(logging_module, "_current_correlation_id")
        else:
            logging_module._current_correlation_id = self.old_id
