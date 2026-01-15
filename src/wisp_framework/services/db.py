"""Database service with async SQLAlchemy and connection pooling."""

import logging
from typing import Any

from wisp_framework.services.base import BaseService

logger = logging.getLogger(__name__)


class DatabaseService(BaseService):
    """Database service with async SQLAlchemy engine and connection pooling."""

    def __init__(self, config: Any) -> None:
        """Initialize the database service."""
        super().__init__(config)
        self._engine: Any | None = None
        self._session_factory: Any | None = None

    async def startup(self) -> None:
        """Start up the database service."""
        database_url = self.config.database_url
        if not database_url:
            logger.warning("No DATABASE_URL configured, database service will not be available")
            self._mark_initialized()
            return

        from sqlalchemy import text as sa_text
        from sqlalchemy.ext.asyncio import (
            AsyncSession,
            async_sessionmaker,
            create_async_engine,
        )

        try:

            # Create async engine with connection pooling
            self._engine = create_async_engine(
                database_url,
                pool_size=self.config.db_pool_size,
                max_overflow=self.config.db_max_overflow,
                pool_timeout=self.config.db_pool_timeout,
                pool_recycle=self.config.db_pool_recycle,
                pool_pre_ping=True,
                echo=False,
            )

            # Create session factory
            self._session_factory = async_sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False
            )

            # Test connection
            async with self._engine.begin() as conn:
                await conn.execute(sa_text("SELECT 1"))

            logger.info("Database service started successfully")
            self._mark_initialized()

            # Update health service if available
            # Note: This requires accessing the service container, which we don't have here
            # Health status will be checked dynamically

        except Exception as e:
            logger.error(f"Failed to start database service: {e}", exc_info=True)
            raise

    async def shutdown(self) -> None:
        """Shut down the database service."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database service shut down")

    @property
    def engine(self) -> Any | None:
        """Get the database engine."""
        return self._engine

    @property
    def session_factory(self) -> Any | None:
        """Get the session factory."""
        return self._session_factory

    def get_session(self) -> Any | None:
        """Get a new database session."""
        if not self._session_factory:
            return None
        return self._session_factory()

    def get_async_db(self) -> Any | None:
        """Get AsyncDatabase helper for raw SQL."""
        if not self._engine:
            return None
        from wisp_framework.db.async_helper import AsyncDatabase
        return AsyncDatabase(self._engine)
