"""Database stub for graceful degradation when DB is unavailable."""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DatabaseStub:
    """Stub database interface that warns but doesn't crash when DB is unavailable."""

    def __init__(self) -> None:
        """Initialize the database stub."""
        self._warned = False

    def _warn_once(self, operation: str) -> None:
        """Warn once about database unavailability."""
        if not self._warned:
            logger.warning(
                f"Database operation '{operation}' called but database is not available. "
                "Install with: pip install wisp-framework[db]"
            )
            self._warned = True

    async def execute(self, query: str, *args: Any, **kwargs: Any) -> None:
        """Stub execute method."""
        self._warn_once("execute")

    async def fetchone(self, query: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        """Stub fetchone method."""
        self._warn_once("fetchone")
        return None

    async def fetchall(self, query: str, *args: Any, **kwargs: Any) -> list[Any]:
        """Stub fetchall method."""
        self._warn_once("fetchall")
        return []
