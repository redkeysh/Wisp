"""Middleware system for commands."""

from typing import Any, Awaitable, Callable

import discord
from discord import Interaction


class Middleware:
    """Base class for middleware."""

    async def process(
        self, interaction: Interaction, next_handler: Callable[[Interaction], Awaitable[Any]]
    ) -> Any:
        """Process the middleware.

        Args:
            interaction: Discord interaction
            next_handler: Next handler in the chain

        Returns:
            Result from next handler
        """
        return await next_handler(interaction)


class MiddlewareChain:
    """Chain of middleware to process interactions."""

    def __init__(self, *middlewares: Middleware) -> None:
        """Initialize middleware chain.

        Args:
            *middlewares: Middleware instances
        """
        self.middlewares = list(middlewares)

    def add(self, middleware: Middleware) -> None:
        """Add middleware to chain.

        Args:
            middleware: Middleware instance
        """
        self.middlewares.append(middleware)

    async def execute(
        self, interaction: Interaction, handler: Callable[[Interaction], Awaitable[Any]]
    ) -> Any:
        """Execute middleware chain.

        Args:
            interaction: Discord interaction
            handler: Final handler

        Returns:
            Result from handler
        """
        async def next_handler(i: Interaction) -> Any:
            if not self.middlewares:
                return await handler(i)
            middleware = self.middlewares.pop(0)
            return await middleware.process(i, next_handler)

        middlewares_copy = self.middlewares.copy()
        self.middlewares.clear()
        return await next_handler(interaction)


class LoggingMiddleware(Middleware):
    """Middleware to log command execution."""

    async def process(
        self, interaction: Interaction, next_handler: Callable[[Interaction], Awaitable[Any]]
    ) -> Any:
        """Log command execution."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info(
            f"Command executed: {interaction.command.name if interaction.command else 'unknown'} "
            f"by {interaction.user.id} in {interaction.guild_id}"
        )
        return await next_handler(interaction)


class MetricsMiddleware(Middleware):
    """Middleware to track command metrics."""

    def __init__(self, metrics_service: Any) -> None:
        """Initialize metrics middleware.

        Args:
            metrics_service: Metrics service instance
        """
        self.metrics = metrics_service

    async def process(
        self, interaction: Interaction, next_handler: Callable[[Interaction], Awaitable[Any]]
    ) -> Any:
        """Track command metrics."""
        if self.metrics:
            import time

            start_time = time.time()
            try:
                result = await next_handler(interaction)
                duration = time.time() - start_time
                self.metrics.timing("command.duration", duration)
                self.metrics.increment("command.success")
                return result
            except Exception:
                self.metrics.increment("command.error")
                raise
        else:
            return await next_handler(interaction)
