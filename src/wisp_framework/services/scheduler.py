"""Async scheduler service for periodic tasks."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from wisp_framework.services.base import BaseService

logger = logging.getLogger(__name__)


class SchedulerService(BaseService):
    """Service for scheduling periodic async tasks."""

    def __init__(self, config: Any) -> None:
        """Initialize the scheduler service."""
        super().__init__(config)
        self._tasks: list[asyncio.Task] = []
        self._running = False

    async def startup(self) -> None:
        """Start up the scheduler service."""
        self._running = True
        self._mark_initialized()
        logger.info("Scheduler service started")

    async def shutdown(self) -> None:
        """Shut down the scheduler service."""
        self._running = False
        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        # Wait for tasks to complete cancellation
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        logger.info("Scheduler service shut down")

    def register(
        self,
        coro: Callable[[], Awaitable[None]],
        interval: float,
        name: str | None = None,
    ) -> None:
        """Register a periodic task.

        Args:
            coro: Coroutine function to run periodically
            interval: Interval in seconds between runs
            name: Optional name for the task (for logging)
        """
        if not self._running:
            raise RuntimeError("Scheduler is not running")

        task_name = name or coro.__name__

        async def run_periodic() -> None:
            while self._running:
                try:
                    await coro()
                except Exception as e:
                    logger.error(
                        f"Error in scheduled task '{task_name}': {e}", exc_info=True
                    )
                await asyncio.sleep(interval)

        task = asyncio.create_task(run_periodic())
        self._tasks.append(task)
        logger.info(f"Registered scheduled task '{task_name}' with interval {interval}s")
