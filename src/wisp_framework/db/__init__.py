"""Database package for the Wisp Framework."""

# Import stub first (no dependencies)
from wisp_framework.db.stub import DatabaseStub

# Conditional imports for SQLAlchemy-dependent modules
try:
    from wisp_framework.db.async_helper import AsyncDatabase
    from wisp_framework.db.base import Base
    from wisp_framework.db.models import GuildConfig, GuildData, ModuleState
    from wisp_framework.db.session import get_session

    __all__ = [
        "Base",
        "GuildConfig",
        "ModuleState",
        "GuildData",
        "get_session",
        "DatabaseStub",
        "AsyncDatabase",
    ]
except ImportError:
    # SQLAlchemy not installed - provide stub implementations
    Base = None  # type: ignore[assignment]
    GuildConfig = None  # type: ignore[assignment]
    GuildData = None  # type: ignore[assignment]
    ModuleState = None  # type: ignore[assignment]
    AsyncDatabase = None  # type: ignore[assignment]

    def get_session(*args, **kwargs):  # type: ignore[misc]
        """Stub get_session when SQLAlchemy is not installed."""
        from collections.abc import AsyncGenerator
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def _stub_session() -> AsyncGenerator[None]:
            yield None

        return _stub_session()

    __all__ = [
        "DatabaseStub",
    ]
