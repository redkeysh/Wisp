"""Database models for the Wisp Framework."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from wisp_framework.db.base import Base, TimestampMixin


class GuildConfig(Base, TimestampMixin):
    """Guild configuration model."""

    __tablename__ = "guild_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    welcome_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


class ModuleState(Base, TimestampMixin):
    """Module state per guild."""

    __tablename__ = "module_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    module_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        {"comment": "Tracks which modules are enabled/disabled per guild"},
    )


class GuildData(Base, TimestampMixin):
    """Generic key-value storage for per-guild stats/data."""

    __tablename__ = "guild_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[Any] = mapped_column(JSONB, nullable=False)
    module_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )

    __table_args__ = (
        {"comment": "Generic key-value storage for per-guild data"},
    )
