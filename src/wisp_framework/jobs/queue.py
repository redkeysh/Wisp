"""Job queue for enqueueing and managing background jobs."""

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select

from wisp_framework.db.models import Job
from wisp_framework.services.base import BaseService
from wisp_framework.services.cache import CacheService
from wisp_framework.services.db import DatabaseService

logger = logging.getLogger(__name__)


class JobQueue(BaseService):
    """Job queue for enqueueing and managing background jobs."""

    def __init__(self, config: Any, db_service: DatabaseService | None = None) -> None:
        """Initialize job queue.

        Args:
            config: Application configuration
            db_service: Database service for job persistence
        """
        super().__init__(config)
        self._db_service = db_service
        self._cache_service: CacheService | None = None

    async def startup(self) -> None:
        """Start up the job queue."""
        # Get cache service if available
        # Cache service would be available via service container
        # For now, we'll get it lazily
        self._mark_initialized()
        logger.info("Job queue started")

    async def shutdown(self) -> None:
        """Shut down the job queue."""
        logger.info("Job queue shut down")

    async def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
        delay_seconds: int = 0,
    ) -> Job:
        """Enqueue a job.

        Args:
            job_type: Type of job (e.g., "sync_data", "send_notification")
            payload: Job payload dictionary
            idempotency_key: Optional idempotency key for deduplication
            delay_seconds: Optional delay before job runs

        Returns:
            Created Job instance
        """
        if not self._db_service or not self._db_service.session_factory:
            raise RuntimeError("Database service not available for job queue")

        # Check for duplicate if idempotency_key provided
        if idempotency_key:
            existing = await self._find_by_idempotency_key(idempotency_key)
            if existing and existing.status in ("pending", "running"):
                logger.info(f"Job with idempotency_key '{idempotency_key}' already exists")
                return existing

        async with self._db_service.session_factory() as session:
            next_run_at = datetime.utcnow() + timedelta(seconds=delay_seconds) if delay_seconds > 0 else datetime.utcnow()

            job = Job(
                job_type=job_type,
                status="pending",
                attempts=0,
                max_attempts=3,
                next_run_at=next_run_at,
                idempotency_key=idempotency_key,
                payload=payload,
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)

            logger.info(f"Enqueued job {job.id} of type '{job_type}'")
            return job

    async def _find_by_idempotency_key(self, idempotency_key: str) -> Job | None:
        """Find job by idempotency key.

        Args:
            idempotency_key: Idempotency key

        Returns:
            Job instance or None
        """
        if not self._db_service or not self._db_service.session_factory:
            return None

        async with self._db_service.session_factory() as session:
            stmt = select(Job).where(Job.idempotency_key == idempotency_key)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_pending_jobs(self, limit: int = 10) -> list[Job]:
        """Get pending jobs ready to run.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of Job instances
        """
        if not self._db_service or not self._db_service.session_factory:
            return []

        async with self._db_service.session_factory() as session:
            now = datetime.utcnow()
            stmt = (
                select(Job)
                .where(
                    Job.status == "pending",
                    Job.next_run_at <= now,
                )
                .order_by(Job.next_run_at)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def mark_running(self, job: Job, worker_id: str) -> None:
        """Mark a job as running.

        Args:
            job: Job instance
            worker_id: Worker identifier
        """
        if not self._db_service or not self._db_service.session_factory:
            return

        async with self._db_service.session_factory() as session:
            job.status = "running"
            job.locked_by = worker_id
            job.locked_at = datetime.utcnow()
            session.add(job)
            await session.commit()

    async def mark_completed(self, job: Job) -> None:
        """Mark a job as completed.

        Args:
            job: Job instance
        """
        if not self._db_service or not self._db_service.session_factory:
            return

        async with self._db_service.session_factory() as session:
            job.status = "completed"
            job.locked_by = None
            job.locked_at = None
            session.add(job)
            await session.commit()

    async def mark_failed(self, job: Job, error_message: str) -> None:
        """Mark a job as failed.

        Args:
            job: Job instance
            error_message: Error message
        """
        if not self._db_service or not self._db_service.session_factory:
            return

        async with self._db_service.session_factory() as session:
            job.attempts += 1
            job.error_message = error_message[:1000]  # Truncate if too long

            if job.attempts >= job.max_attempts:
                job.status = "dead_letter"
            else:
                # Schedule retry with exponential backoff
                delay = 2 ** job.attempts  # 2, 4, 8 seconds
                job.status = "pending"
                job.next_run_at = datetime.utcnow() + timedelta(seconds=delay)
                job.locked_by = None
                job.locked_at = None

            session.add(job)
            await session.commit()
