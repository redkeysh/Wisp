"""Job runner for processing background jobs."""

import asyncio
import logging
import uuid
from collections.abc import Callable
from typing import Any

from wisp_framework.context import WispContext
from wisp_framework.db.models import Job
from wisp_framework.jobs.queue import JobQueue
from wisp_framework.services.base import BaseService

logger = logging.getLogger(__name__)


class JobRunner(BaseService):
    """Service for running background jobs."""

    def __init__(
        self,
        config: Any,
        job_queue: JobQueue,
        services: Any | None = None,
        job_handlers: dict[str, Callable[[WispContext, dict[str, Any]], Any]] | None = None,
    ) -> None:
        """Initialize job runner.

        Args:
            config: Application configuration
            job_queue: Job queue instance
            services: Service container
            job_handlers: Dictionary mapping job_type to handler function
        """
        super().__init__(config)
        self._job_queue = job_queue
        self._services = services
        self._job_handlers = job_handlers or {}
        self._worker_id = str(uuid.uuid4())
        self._running = False
        self._task: asyncio.Task | None = None
        self._concurrency_limit = getattr(config, "job_concurrency_limit", 5)
        self._running_jobs: set[int] = set()

    async def startup(self) -> None:
        """Start up the job runner."""
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        self._mark_initialized()
        logger.info(f"Job runner started (worker_id: {self._worker_id})")

    async def shutdown(self) -> None:
        """Shut down the job runner."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Job runner shut down")

    def register_handler(
        self, job_type: str, handler: Callable[[WispContext, dict[str, Any]], Any]
    ) -> None:
        """Register a job handler.

        Args:
            job_type: Job type name
            handler: Handler function that takes (ctx, payload) and returns result
        """
        self._job_handlers[job_type] = handler
        logger.info(f"Registered job handler for type '{job_type}'")

    async def _run_loop(self) -> None:
        """Main job processing loop."""
        while self._running:
            try:
                # Check concurrency limit
                if len(self._running_jobs) >= self._concurrency_limit:
                    await asyncio.sleep(1)
                    continue

                # Get pending jobs
                pending_jobs = await self._job_queue.get_pending_jobs(
                    limit=self._concurrency_limit - len(self._running_jobs)
                )

                if not pending_jobs:
                    await asyncio.sleep(1)
                    continue

                # Process jobs
                for job in pending_jobs:
                    if len(self._running_jobs) >= self._concurrency_limit:
                        break

                    # Mark as running
                    await self._job_queue.mark_running(job, self._worker_id)
                    self._running_jobs.add(job.id)

                    # Process in background
                    asyncio.create_task(self._process_job(job))

            except Exception as e:
                logger.error(f"Error in job runner loop: {e}", exc_info=True)
                await asyncio.sleep(5)

    async def _process_job(self, job: Job) -> None:
        """Process a single job.

        Args:
            job: Job instance
        """
        try:
            # Get handler
            handler = self._job_handlers.get(job.job_type)
            if not handler:
                logger.warning(f"No handler registered for job type '{job.job_type}'")
                await self._job_queue.mark_failed(job, f"No handler for job type '{job.job_type}'")
                self._running_jobs.discard(job.id)
                return

            # Create WispContext for job execution
            from wisp_framework.config import AppConfig

            # Get services
            config = self.config if isinstance(self.config, AppConfig) else AppConfig()
            services = self._services

            if not services:
                logger.error("Services not available for job execution")
                await self._job_queue.mark_failed(job, "Services not available")
                self._running_jobs.discard(job.id)
                return

            ctx = WispContext.from_job(
                config=config,
                services=services,
                job_id=str(job.id),
                guild_id=job.payload.get("guild_id") if isinstance(job.payload, dict) else None,
            )

            # Execute handler
            ctx.bound_logger.info(f"Processing job {job.id} of type '{job.job_type}'")
            await handler(ctx, job.payload)

            # Mark as completed
            await self._job_queue.mark_completed(job)
            ctx.bound_logger.info(f"Completed job {job.id}")

            # Record metrics
            if ctx.metrics:
                from wisp_framework.observability.metrics import record_job_metric

                record_job_metric(ctx.metrics, job.job_type, "completed")

        except Exception as e:
            logger.error(f"Error processing job {job.id}: {e}", exc_info=True)
            await self._job_queue.mark_failed(job, str(e))

            # Record metrics
            if hasattr(self, "config") and hasattr(self.config, "services"):
                # Would record error metric here
                pass

        finally:
            self._running_jobs.discard(job.id)
