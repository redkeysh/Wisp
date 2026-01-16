"""Sentry SDK initialization and configuration."""

import logging

from wisp_framework.config import AppConfig
from wisp_framework.version import __version__

logger = logging.getLogger(__name__)


def init_sentry(config: AppConfig) -> None:
    """Initialize Sentry SDK with release/version tags.

    Args:
        config: Application configuration
    """
    sentry_dsn = config.sentry_dsn
    if not sentry_dsn:
        logger.debug("Sentry DSN not configured, skipping Sentry initialization")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        # Configure Sentry
        sentry_sdk.init(
            dsn=sentry_dsn,
            release=f"wisp-framework@{__version__}",
            environment=config.app_env,
            traces_sample_rate=config.sentry_traces_sample_rate,
            integrations=[
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            ],
        )

        logger.info(f"Sentry initialized for environment: {config.app_env}")
    except ImportError:
        logger.warning("sentry-sdk not installed, skipping Sentry initialization")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}", exc_info=True)
