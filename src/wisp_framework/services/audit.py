"""Audit logging service with Discord object serialization."""

import json
import logging
from datetime import datetime
from typing import Any

from wisp_framework.services.base import BaseService

logger = logging.getLogger(__name__)


class AuditService(BaseService):
    """Service for audit logging with Discord object serialization."""

    def __init__(self, config: Any) -> None:
        """Initialize the audit service."""
        super().__init__(config)
        self._logger = logging.getLogger("audit")

    async def startup(self) -> None:
        """Start up the audit service."""
        self._mark_initialized()
        logger.info("Audit service started")

    async def shutdown(self) -> None:
        """Shut down the audit service."""
        logger.info("Audit service shut down")

    def log_action(
        self,
        action: str,
        user_id: int | None = None,
        guild_id: int | None = None,
        channel_id: int | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Log an audit action.

        Args:
            action: The action being performed
            user_id: Discord user ID who performed the action
            guild_id: Discord guild ID where action occurred
            channel_id: Discord channel ID where action occurred
            metadata: Additional metadata dictionary
            **kwargs: Additional fields to include in the log
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
        }

        if metadata:
            # Serialize Discord objects in metadata
            serialized_metadata = self._serialize_objects(metadata)
            log_data["metadata"] = serialized_metadata

        # Add any additional kwargs
        log_data.update(kwargs)

        self._logger.info(json.dumps(log_data, default=str))

    def _serialize_objects(self, obj: Any) -> Any:
        """Recursively serialize Discord objects to dictionaries."""
        if hasattr(obj, "__dict__"):
            # Discord object
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith("_"):
                    result[key] = self._serialize_objects(value)
            return result
        elif isinstance(obj, dict):
            return {k: self._serialize_objects(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_objects(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
