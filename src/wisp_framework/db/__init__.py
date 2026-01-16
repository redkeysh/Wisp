"""Database utilities and models for Wisp Framework."""

from wisp_framework.db.base import Base
from wisp_framework.db.models import GuildConfig, GuildData, ModuleState

__all__ = ["Base", "GuildConfig", "GuildData", "ModuleState"]


def get_wisp_metadata() -> Base.metadata.__class__:
    """Get Wisp Framework's SQLAlchemy metadata for Alembic integration.

    This function allows downstream bots to include Wisp Framework's
    database models in their Alembic migrations.

    Example usage in alembic/env.py:
        from wisp_framework.db import get_wisp_metadata

        # Merge Wisp Framework metadata with your bot's metadata
        from your_bot.models import Base as YourBase
        target_metadata = [YourBase.metadata, get_wisp_metadata()]

        # Or if using a single Base:
        # target_metadata = YourBase.metadata
        # YourBase.metadata.merge(get_wisp_metadata())

    Returns:
        SQLAlchemy MetaData object containing Wisp Framework's models
    """
    return Base.metadata
