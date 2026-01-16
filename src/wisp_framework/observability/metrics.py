"""Metric naming normalization and helpers."""

from typing import Any


def normalize_metric_name(prefix: str, name: str, status: str | None = None) -> str:
    """Normalize metric name with consistent format.

    Args:
        prefix: Metric prefix (e.g., "commands", "events", "jobs")
        name: Metric name (e.g., command name, event name)
        status: Optional status suffix (e.g., "success", "error", "rate_limited")

    Returns:
        Normalized metric name (e.g., "wisp.commands.ping.success")

    Examples:
        >>> normalize_metric_name("commands", "ping", "success")
        'wisp.commands.ping.success'
        >>> normalize_metric_name("events", "message_create")
        'wisp.events.message_create'
        >>> normalize_metric_name("jobs", "sync_data", "failed")
        'wisp.jobs.sync_data.failed'
    """
    parts = ["wisp", prefix, name]
    if status:
        parts.append(status)
    return ".".join(parts)


def record_command_metric(metrics_service: Any, command_name: str, status: str = "executed") -> None:
    """Record a command metric with normalized naming.

    Args:
        metrics_service: Metrics service instance
        command_name: Name of the command
        status: Status of the command (executed, success, error, etc.)
    """
    if metrics_service:
        metric_name = normalize_metric_name("commands", command_name, status)
        metrics_service.increment(metric_name)


def record_event_metric(metrics_service: Any, event_name: str, status: str = "processed") -> None:
    """Record an event metric with normalized naming.

    Args:
        metrics_service: Metrics service instance
        event_name: Name of the event
        status: Status of the event (processed, filtered, error, etc.)
    """
    if metrics_service:
        metric_name = normalize_metric_name("events", event_name, status)
        metrics_service.increment(metric_name)


def record_job_metric(metrics_service: Any, job_type: str, status: str) -> None:
    """Record a job metric with normalized naming.

    Args:
        metrics_service: Metrics service instance
        job_type: Type of the job
        status: Status of the job (enqueued, completed, failed, dead_letter, etc.)
    """
    if metrics_service:
        metric_name = normalize_metric_name("jobs", job_type, status)
        metrics_service.increment(metric_name)
