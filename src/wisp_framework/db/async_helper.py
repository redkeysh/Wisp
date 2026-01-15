"""Async database helper for raw SQL execution."""

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


class AsyncDatabase:
    """Helper class for raw SQL execution."""

    def __init__(self, engine: AsyncEngine | None) -> None:
        """Initialize the async database helper."""
        self._engine = engine

    async def execute(
        self, query: str, *args: Any, **kwargs: Any
    ) -> Any | None:
        """Execute a raw SQL query."""
        if not self._engine:
            raise RuntimeError("Database engine is not available")

        async with self._engine.begin() as conn:
            result = await conn.execute(text(query), *args, **kwargs)
            return result

    async def fetchone(
        self, query: str, *args: Any, **kwargs: Any
    ) -> Any | None:
        """Fetch one row from a query."""
        if not self._engine:
            raise RuntimeError("Database engine is not available")

        async with self._engine.connect() as conn:
            result = await conn.execute(text(query), *args, **kwargs)
            return result.fetchone()

    async def fetchall(
        self, query: str, *args: Any, **kwargs: Any
    ) -> list[Any]:
        """Fetch all rows from a query."""
        if not self._engine:
            raise RuntimeError("Database engine is not available")

        async with self._engine.connect() as conn:
            result = await conn.execute(text(query), *args, **kwargs)
            return result.fetchall()
