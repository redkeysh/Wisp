"""Base service classes and service container."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar

from wisp_framework.exceptions import ServiceError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="BaseService")


class BaseService(ABC):
    """Abstract base class for all services."""

    def __init__(self, config: Any) -> None:
        """Initialize the service with configuration."""
        self.config = config
        self._initialized = False

    @abstractmethod
    async def startup(self) -> None:
        """Initialize the service. Called during bot startup."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up the service. Called during bot shutdown."""
        pass

    @property
    def initialized(self) -> bool:
        """Check if the service has been initialized."""
        return self._initialized

    def _mark_initialized(self) -> None:
        """Mark the service as initialized."""
        self._initialized = True


class ServiceContainer:
    """Container for managing framework services."""

    def __init__(self, config: Any) -> None:
        """Initialize the service container."""
        self.config = config
        self._services: Dict[str, BaseService] = {}
        self._logger = logging.getLogger(__name__)

    def register(self, name: str, service: BaseService) -> None:
        """Register a service with the container."""
        if name in self._services:
            raise ServiceError(f"Service '{name}' is already registered")
        self._services[name] = service
        self._logger.debug(f"Registered service: {name}")

    def get(self, name: str) -> Optional[BaseService]:
        """Get a service by name."""
        return self._services.get(name)

    def get_typed(self, name: str, service_type: Type[T]) -> Optional[T]:
        """Get a service by name with type checking."""
        service = self.get(name)
        if service is None:
            return None
        if not isinstance(service, service_type):
            raise ServiceError(
                f"Service '{name}' is not of type {service_type.__name__}"
            )
        return service

    async def startup_all(self) -> None:
        """Start up all registered services."""
        self._logger.info("Starting up all services...")
        for name, service in self._services.items():
            try:
                self._logger.debug(f"Starting service: {name}")
                await service.startup()
                self._logger.info(f"Service '{name}' started successfully")
            except Exception as e:
                self._logger.error(f"Failed to start service '{name}': {e}", exc_info=True)
                raise ServiceError(f"Failed to start service '{name}'") from e

    async def shutdown_all(self) -> None:
        """Shut down all registered services."""
        self._logger.info("Shutting down all services...")
        # Shutdown in reverse order
        for name, service in reversed(list(self._services.items())):
            try:
                self._logger.debug(f"Shutting down service: {name}")
                await service.shutdown()
                self._logger.info(f"Service '{name}' shut down successfully")
            except Exception as e:
                self._logger.error(
                    f"Error shutting down service '{name}': {e}", exc_info=True
                )

    def list_services(self) -> list[str]:
        """List all registered service names."""
        return list(self._services.keys())
