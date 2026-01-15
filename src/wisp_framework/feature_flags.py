"""Feature flags for per-guild module enable/disable."""

import logging

from sqlalchemy import select

from wisp_framework.db.models import ModuleState
from wisp_framework.services.db import DatabaseService

logger = logging.getLogger(__name__)


class FeatureFlags:
    """Manages feature flags (module enable/disable) per guild."""

    def __init__(self, db_service: DatabaseService | None) -> None:
        """Initialize feature flags."""
        self._db_service = db_service
        self._memory_cache: dict[tuple[int, str], bool] = {}

    async def is_enabled(
        self, guild_id: int, module_name: str, default: bool = True
    ) -> bool:
        """Check if a module is enabled for a guild."""
        cache_key = (guild_id, module_name)

        # Try database first
        if self._db_service and self._db_service.session_factory:
            try:
                async with self._db_service.session_factory() as session:
                    stmt = select(ModuleState).where(
                        ModuleState.guild_id == guild_id,
                        ModuleState.module_name == module_name,
                    )
                    result = await session.execute(stmt)
                    row = result.scalar_one_or_none()
                    if row:
                        enabled = row.enabled
                        self._memory_cache[cache_key] = enabled
                        return enabled
            except Exception as e:
                logger.warning(f"Database check failed: {e}, using memory cache")

        # Fall back to memory cache or default
        return self._memory_cache.get(cache_key, default)

    async def set_enabled(
        self, guild_id: int, module_name: str, enabled: bool
    ) -> None:
        """Set whether a module is enabled for a guild."""
        cache_key = (guild_id, module_name)

        # Update memory cache
        self._memory_cache[cache_key] = enabled

        # Try database
        if self._db_service and self._db_service.session_factory:
            try:
                async with self._db_service.session_factory() as session:
                    stmt = select(ModuleState).where(
                        ModuleState.guild_id == guild_id,
                        ModuleState.module_name == module_name,
                    )
                    result = await session.execute(stmt)
                    row = result.scalar_one_or_none()

                    if row:
                        row.enabled = enabled
                    else:
                        row = ModuleState(
                            guild_id=guild_id,
                            module_name=module_name,
                            enabled=enabled,
                        )
                        session.add(row)

                    await session.commit()
            except Exception as e:
                logger.warning(f"Database set failed: {e}, using memory cache only")

    async def get_all_enabled(self, guild_id: int) -> dict[str, bool]:
        """Get all module states for a guild."""
        result: dict[str, bool] = {}

        # Try database first
        if self._db_service and self._db_service.session_factory:
            try:
                async with self._db_service.session_factory() as session:
                    stmt = select(ModuleState).where(ModuleState.guild_id == guild_id)
                    db_result = await session.execute(stmt)
                    rows = db_result.scalars().all()
                    for row in rows:
                        result[row.module_name] = row.enabled
                        cache_key = (guild_id, row.module_name)
                        self._memory_cache[cache_key] = row.enabled
            except Exception as e:
                logger.warning(f"Database get_all failed: {e}, using memory cache")

        # Merge with memory cache
        for (gid, module_name), enabled in self._memory_cache.items():
            if gid == guild_id:
                if module_name not in result:
                    result[module_name] = enabled

        return result
