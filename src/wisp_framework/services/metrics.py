"""Metrics service for collecting and exposing metrics."""

import logging
import time
from collections import defaultdict
from typing import Any, Dict

from wisp_framework.services.base import BaseService

logger = logging.getLogger(__name__)


class MetricsService(BaseService):
    """Service for collecting metrics (counters, timings, etc.)."""

    def __init__(self, config: Any) -> None:
        """Initialize the metrics service."""
        super().__init__(config)
        self._counters: Dict[str, int] = defaultdict(int)
        self._timings: Dict[str, list[float]] = defaultdict(list)
        self._gauges: Dict[str, float] = {}

    async def startup(self) -> None:
        """Start up the metrics service."""
        self._mark_initialized()
        logger.info("Metrics service started")

    async def shutdown(self) -> None:
        """Shut down the metrics service."""
        self._counters.clear()
        self._timings.clear()
        self._gauges.clear()
        logger.info("Metrics service shut down")

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a counter."""
        self._counters[name] += value

    def decrement(self, name: str, value: int = 1) -> None:
        """Decrement a counter."""
        self._counters[name] -= value

    def timing(self, name: str, duration: float) -> None:
        """Record a timing."""
        self._timings[name].append(duration)
        # Keep only last 1000 timings
        if len(self._timings[name]) > 1000:
            self._timings[name] = self._timings[name][-1000:]

    def gauge(self, name: str, value: float) -> None:
        """Set a gauge value."""
        self._gauges[name] = value

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        timing_stats = {}
        for name, timings in self._timings.items():
            if timings:
                timing_stats[name] = {
                    "count": len(timings),
                    "min": min(timings),
                    "max": max(timings),
                    "avg": sum(timings) / len(timings),
                }
            else:
                timing_stats[name] = {"count": 0, "min": 0, "max": 0, "avg": 0}

        return {
            "counters": dict(self._counters),
            "timings": timing_stats,
            "gauges": dict(self._gauges),
        }

    def timeit(self, name: str):
        """Context manager for timing operations."""

        class TimingContext:
            def __init__(self, service: MetricsService, metric_name: str) -> None:
                self.service = service
                self.metric_name = metric_name
                self.start_time: Optional[float] = None

            def __enter__(self) -> "TimingContext":
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
                if self.start_time is not None:
                    duration = time.time() - self.start_time
                    self.service.timing(self.metric_name, duration)

        return TimingContext(self, name)
