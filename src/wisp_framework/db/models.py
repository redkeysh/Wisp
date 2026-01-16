"""Database models for the Wisp Framework."""

from typing import Any

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
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


class PluginState(Base, TimestampMixin):
    """Plugin state per guild and globally."""

    __tablename__ = "plugin_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    guild_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    degraded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    loaded_at: Mapped[Any] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        {"comment": "Tracks plugin state per guild and globally"},
    )


class PolicyRule(Base, TimestampMixin):
    """Policy rule for capability-based access control."""

    __tablename__ = "policy_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scope_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    scope_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    capability: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(10), nullable=False)  # "allow" or "deny"
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        {"comment": "Policy rules for capability-based access control"},
    )


class Job(Base, TimestampMixin):
    """Background job for durable task execution."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    locked_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    payload: Mapped[Any] = mapped_column(JSONB, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        {"comment": "Background jobs for durable task execution"},
    )