"""Health check service."""

import logging
from typing import Any, Dict

from wisp_framework.services.base import BaseService

logger = logging.getLogger(__name__)


class HealthService(BaseService):
    """Service for health checks."""

    def __init__(self, config: Any) -> None:
        """Initialize the health service."""
        super().__init__(config)
        self._service_statuses: Dict[str, Dict[str, Any]] = {}

    async def startup(self) -> None:
        """Start up the health service."""
        self._mark_initialized()
        logger.info("Health service started")

    async def shutdown(self) -> None:
        """Shut down the health service."""
        self._service_statuses.clear()
        logger.info("Health service shut down")

    def register_service(self, name: str, status: Dict[str, Any]) -> None:
        """Register a service status."""
        self._service_statuses[name] = status

    def get_health(self) -> Dict[str, Any]:
        """Get overall health status."""
        all_healthy = all(
            status.get("healthy", False) for status in self._service_statuses.values()
        )
        return {
            "healthy": all_healthy,
            "services": self._service_statuses,
        }
