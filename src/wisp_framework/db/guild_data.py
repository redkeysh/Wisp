"""GuildDataService for easy per-guild data storage."""

import logging
from typing import Any

from sqlalchemy import select

from wisp_framework.db.models import GuildData
from wisp_framework.services.db import DatabaseService

logger = logging.getLogger(__name__)


class GuildDataService:
    """Service for storing and retrieving per-guild data."""

    def __init__(self, db_service: DatabaseService | None) -> None:
        """Initialize the guild data service."""
        self._db_service = db_service
        self._memory_cache: dict[tuple[int, str, str | None], Any] = {}

    async def get(
        self,
        guild_id: int,
        key: str,
        module_name: str | None = None,
    ) -> Any | None:
        """Get a value for a guild."""
        cache_key = (guild_id, key, module_name)

        # Try database first
        if self._db_service and self._db_service.session_factory:
            try:
                async with self._db_service.session_factory() as session:
                    stmt = select(GuildData).where(
                        GuildData.guild_id == guild_id,
                        GuildData.key == key,
                        GuildData.module_name == module_name,
                    )
                    result = await session.execute(stmt)
                    row = result.scalar_one_or_none()
                    if row:
                        value = row.value
                        # Cache it
                        self._memory_cache[cache_key] = value
                        return value
            except Exception as e:
                logger.warning(f"Database get failed: {e}, using memory cache")

        # Fall back to memory cache
        return self._memory_cache.get(cache_key)

    async def set(
        self,
        guild_id: int,
        key: str,
        value: Any,
        module_name: str | None = None,
    ) -> None:
        """Set a value for a guild."""
        cache_key = (guild_id, key, module_name)

        # Update memory cache
        self._memory_cache[cache_key] = value

        # Try database
        if self._db_service and self._db_service.session_factory:
            try:
                async with self._db_service.session_factory() as session:
                    stmt = select(GuildData).where(
                        GuildData.guild_id == guild_id,
                        GuildData.key == key,
                        GuildData.module_name == module_name,
                    )
                    result = await session.execute(stmt)
                    row = result.scalar_one_or_none()

                    if row:
                        row.value = value
                    else:
                        row = GuildData(
                            guild_id=guild_id,
                            key=key,
                            value=value,
                            module_name=module_name,
                        )
                        session.add(row)

                    await session.commit()
            except Exception as e:
                logger.warning(f"Database set failed: {e}, using memory cache only")

    async def delete(
        self,
        guild_id: int,
        key: str,
        module_name: str | None = None,
    ) -> None:
        """Delete a value for a guild."""
        cache_key = (guild_id, key, module_name)

        # Remove from memory cache
        self._memory_cache.pop(cache_key, None)

        # Try database
        if self._db_service and self._db_service.session_factory:
            try:
                async with self._db_service.session_factory() as session:
                    stmt = select(GuildData).where(
                        GuildData.guild_id == guild_id,
                        GuildData.key == key,
                        GuildData.module_name == module_name,
                    )
                    result = await session.execute(stmt)
                    row = result.scalar_one_or_none()
                    if row:
                        await session.delete(row)
                        await session.commit()
            except Exception as e:
                logger.warning(f"Database delete failed: {e}")

    async def get_all(
        self,
        guild_id: int,
        module_name: str | None = None,
    ) -> dict[str, Any]:
        """Get all data for a guild, optionally filtered by module."""
        result: dict[str, Any] = {}

        # Try database first
        if self._db_service and self._db_service.session_factory:
            try:
                async with self._db_service.session_factory() as session:
                    stmt = select(GuildData).where(GuildData.guild_id == guild_id)
                    if module_name:
                        stmt = stmt.where(GuildData.module_name == module_name)
                    db_result = await session.execute(stmt)
                    rows = db_result.scalars().all()
                    for row in rows:
                        result[row.key] = row.value
                        # Update memory cache
                        cache_key = (guild_id, row.key, row.module_name)
                        self._memory_cache[cache_key] = row.value
            except Exception as e:
                logger.warning(f"Database get_all failed: {e}, using memory cache")

        # Merge with memory cache
        for (gid, key, mod_name), value in self._memory_cache.items():
            if gid == guild_id and (module_name is None or mod_name == module_name):
                if key not in result:
                    result[key] = value

        return result
