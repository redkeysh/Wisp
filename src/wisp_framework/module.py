"""Module base class for framework modules."""

from abc import ABC, abstractmethod
from typing import Any


class Module(ABC):
    """Abstract base class for framework modules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Module name."""
        pass

    @property
    def default_enabled(self) -> bool:
        """Whether the module is enabled by default."""
        return True

    @property
    def required_services(self) -> set[str]:
        """Set of required service names."""
        return set()

    @property
    def depends_on(self) -> list[str]:
        """List of module names this module depends on."""
        return []

    @abstractmethod
    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the module.

        Args:
            bot: The Discord bot instance
            ctx: Bot context with services and config
        """
        pass

    async def teardown(self, bot: Any, ctx: Any) -> None:  # noqa: B027
        """Tear down the module.

        Optional method - subclasses can override if cleanup is needed.

        Args:
            bot: The Discord bot instance
            ctx: Bot context with services and config
        """
        pass
