"""Base database model class."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Any = DateTime(timezone=True, server_default=func.now())
    updated_at: Any = DateTime(timezone=True, onupdate=func.now())
