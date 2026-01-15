"""Database session management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from wisp_framework.services.db import DatabaseService


@asynccontextmanager
async def get_session(
    db_service: Optional[DatabaseService] = None,
) -> AsyncGenerator[Optional[AsyncSession], None]:
    """Get a database session context manager."""
    if not db_service or not db_service.session_factory:
        yield None
        return

    async with db_service.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
