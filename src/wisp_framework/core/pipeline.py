"""Execution pipeline for commands and events."""

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from wisp_framework.context import WispContext
from wisp_framework.exceptions import WispError, map_error_to_response

logger = logging.getLogger(__name__)


class Middleware(Protocol):
    """Protocol for pipeline middleware."""

    async def before(self, ctx: WispContext) -> None:
        """Called before command/event execution.

        Args:
            ctx: WispContext for this execution
        """
        ...

    async def after(self, ctx: WispContext, result: Any) -> None:
        """Called after successful command/event execution.

        Args:
            ctx: WispContext for this execution
            result: Result from command/event handler
        """
        ...

    async def on_error(self, ctx: WispContext, exc: Exception) -> Exception | None:
        """Called when an error occurs during execution.

        Args:
            ctx: WispContext for this execution
            exc: Exception that occurred

        Returns:
            Exception to raise (or None to suppress)
        """
        ...


class RequestIdMiddleware:
    """Middleware that ensures request_id is set and logger is bound."""

    async def before(self, ctx: WispContext) -> None:
        """Bind logger with request_id."""
        # Logger is already bound via property access
        ctx.bound_logger.debug(f"Starting {ctx.invocation_type} execution")

    async def after(self, ctx: WispContext, result: Any) -> None:
        """Log successful completion."""
        ctx.bound_logger.debug(f"Completed {ctx.invocation_type} execution")

    async def on_error(self, ctx: WispContext, exc: Exception) -> Exception | None:
        """Log error with request_id."""
        ctx.bound_logger.error(f"Error in {ctx.invocation_type} execution: {exc}", exc_info=True)
        return exc


class FeatureFlagsMiddleware:
    """Middleware that resolves feature flags for the guild."""

    async def before(self, ctx: WispContext) -> None:
        """Resolve feature flags snapshot."""
        # Feature flags are already available via ctx.feature_flags
        # This middleware can be extended to check module enablement
        pass

    async def after(self, ctx: WispContext, result: Any) -> None:
        """No-op after execution."""
        pass

    async def on_error(self, ctx: WispContext, exc: Exception) -> Exception | None:
        """No-op on error."""
        return exc


class PolicyMiddleware:
    """Middleware that checks policy/capabilities."""

    def __init__(self, capability: str | None = None) -> None:
        """Initialize policy middleware.

        Args:
            capability: Optional capability to check (if None, checks from command metadata)
        """
        self._capability = capability

    async def before(self, ctx: WispContext) -> None:
        """Check policy if available."""
        if not ctx.policy:
            return

        # Get capability to check
        capability = self._capability
        if not capability:
            # Try to get from command metadata or context
            # For now, skip if not provided
            return

        # Check policy
        result = await ctx.policy.check(capability, ctx)
        if not result.allowed:
            from wisp_framework.exceptions import PermissionError

            ctx.bound_logger.warning(f"Policy check failed: {result.reason}")
            if ctx.metrics:
                from wisp_framework.observability.metrics import record_command_metric

                record_command_metric(ctx.metrics, ctx.invocation_type, "permission_denied")
            raise PermissionError(
                safe_message="You don't have permission to perform this action.",
                internal_message=result.reason,
            )

    async def after(self, ctx: WispContext, result: Any) -> None:
        """No-op after execution."""
        pass

    async def on_error(self, ctx: WispContext, exc: Exception) -> Exception | None:
        """No-op on error."""
        return exc


class RateLimitMiddleware:
    """Middleware that checks rate limits."""

    def __init__(self, limiter: Any | None = None) -> None:
        """Initialize rate limit middleware.

        Args:
            limiter: Optional RateLimiter instance
        """
        self._limiter = limiter

    async def before(self, ctx: WispContext) -> None:
        """Check rate limits if available."""
        if not self._limiter:
            # Try to get from services
            cache_service = ctx.services.get("cache")
            if cache_service:
                from wisp_framework.ratelimit.limiter import TokenBucketLimiter, get_rate_limit_key

                self._limiter = TokenBucketLimiter(cache_service)

        if self._limiter:
            from wisp_framework.ratelimit.limiter import get_rate_limit_key
            from wisp_framework.exceptions import RateLimitedError

            # Check rate limit for user
            key = get_rate_limit_key(ctx, "user")
            allowed, remaining = await self._limiter.check(key, limit=10, window=60)

            if not allowed:
                ctx.bound_logger.warning(f"Rate limit exceeded for {key}")
                if ctx.metrics:
                    from wisp_framework.observability.metrics import record_command_metric

                    record_command_metric(ctx.metrics, ctx.invocation_type, "rate_limited")
                raise RateLimitedError(
                    safe_message="You're being rate limited. Please try again later.",
                    internal_message=f"Rate limit exceeded for {key}",
                )

    async def after(self, ctx: WispContext, result: Any) -> None:
        """No-op after execution."""
        pass

    async def on_error(self, ctx: WispContext, exc: Exception) -> Exception | None:
        """No-op on error."""
        return exc


class AuditMiddleware:
    """Middleware that logs actions to audit service."""

    async def before(self, ctx: WispContext) -> None:
        """No-op before execution."""
        pass

    async def after(self, ctx: WispContext, result: Any) -> None:
        """Log successful action to audit service."""
        audit_service = ctx.services.get("audit")
        if audit_service:
            audit_service.log_action(
                action=f"{ctx.invocation_type}_completed",
                user_id=ctx.user_id,
                guild_id=ctx.guild_id,
                channel_id=ctx.channel_id,
                metadata={"request_id": ctx.request_id},
            )

    async def on_error(self, ctx: WispContext, exc: Exception) -> Exception | None:
        """Log error to audit service."""
        audit_service = ctx.services.get("audit")
        if audit_service:
            audit_service.log_action(
                action=f"{ctx.invocation_type}_error",
                user_id=ctx.user_id,
                guild_id=ctx.guild_id,
                channel_id=ctx.channel_id,
                metadata={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "request_id": ctx.request_id,
                },
            )
        return exc


class MetricsMiddleware:
    """Middleware that records metrics."""

    def __init__(self, metric_name: str | None = None):
        """Initialize metrics middleware.

        Args:
            metric_name: Optional metric name (defaults to invocation_type)
        """
        self.metric_name = metric_name

    async def before(self, ctx: WispContext) -> None:
        """Record start time."""
        ctx._pipeline_start_time = time.time()

    async def after(self, ctx: WispContext, result: Any) -> None:
        """Record success metrics."""
        if ctx.metrics:
            from wisp_framework.observability.metrics import normalize_metric_name

            duration = time.time() - getattr(ctx, "_pipeline_start_time", 0)
            metric_name = self.metric_name or ctx.invocation_type
            ctx.metrics.timing(normalize_metric_name(metric_name, "duration"), duration)
            ctx.metrics.increment(normalize_metric_name(metric_name, "success"))

    async def on_error(self, ctx: WispContext, exc: Exception) -> Exception | None:
        """Record error metrics."""
        if ctx.metrics:
            from wisp_framework.observability.metrics import normalize_metric_name

            duration = time.time() - getattr(ctx, "_pipeline_start_time", 0)
            metric_name = self.metric_name or ctx.invocation_type
            ctx.metrics.timing(normalize_metric_name(metric_name, "duration"), duration)
            ctx.metrics.increment(normalize_metric_name(metric_name, "error"))
        return exc


class ErrorMappingMiddleware:
    """Middleware that maps errors to user-friendly responses."""

    async def before(self, ctx: WispContext) -> None:
        """No-op before execution."""
        pass

    async def after(self, ctx: WispContext, result: Any) -> None:
        """No-op after execution."""
        pass

    async def on_error(self, ctx: WispContext, exc: Exception) -> Exception | None:
        """Map error to user-friendly exception."""
        if isinstance(exc, WispError):
            # Already a user-friendly error
            return exc

        # Map to user-friendly error
        message, _ = map_error_to_response(exc)
        return WispError(safe_message=message, internal_message=str(exc))


class Pipeline:
    """Execution pipeline that wraps command/event execution with middleware."""

    def __init__(self, *middlewares: Middleware) -> None:
        """Initialize pipeline with middleware.

        Args:
            *middlewares: Middleware instances in execution order
        """
        self.middlewares = list(middlewares)

    def add(self, middleware: Middleware) -> None:
        """Add middleware to the pipeline.

        Args:
            middleware: Middleware instance
        """
        self.middlewares.append(middleware)

    async def execute(
        self,
        ctx: WispContext,
        handler: Callable[[WispContext], Awaitable[Any]],
    ) -> Any:
        """Execute handler through the pipeline.

        Args:
            ctx: WispContext for this execution
            handler: Handler function to execute

        Returns:
            Result from handler

        Raises:
            Exception: Any exception raised by handler or middleware
        """
        # Run before middleware
        for middleware in self.middlewares:
            try:
                await middleware.before(ctx)
            except Exception as e:
                ctx.bound_logger.error(f"Middleware {middleware.__class__.__name__} before() failed: {e}", exc_info=True)
                # Continue with next middleware

        # Execute handler
        result = None
        error: Exception | None = None
        try:
            result = await handler(ctx)
        except Exception as e:
            error = e

        # Run error middleware if error occurred
        if error:
            for middleware in reversed(self.middlewares):
                try:
                    error = await middleware.on_error(ctx, error)
                    if error is None:
                        # Middleware suppressed the error
                        break
                except Exception as e:
                    ctx.bound_logger.error(
                        f"Middleware {middleware.__class__.__name__} on_error() failed: {e}",
                        exc_info=True,
                    )
                    # Continue with original error

            if error:
                raise error

        # Run after middleware
        for middleware in reversed(self.middlewares):
            try:
                await middleware.after(ctx, result)
            except Exception as e:
                ctx.bound_logger.error(f"Middleware {middleware.__class__.__name__} after() failed: {e}", exc_info=True)
                # Continue with next middleware

        return result


def create_default_pipeline(metric_name: str | None = None) -> Pipeline:
    """Create default pipeline with built-in middleware.

    Args:
        metric_name: Optional metric name prefix

    Returns:
        Pipeline instance with default middleware
    """
    return Pipeline(
        RequestIdMiddleware(),
        FeatureFlagsMiddleware(),
        PolicyMiddleware(),  # Will be functional in Phase 4
        RateLimitMiddleware(),  # Will be functional in Phase 6
        AuditMiddleware(),
        MetricsMiddleware(metric_name=metric_name),
        ErrorMappingMiddleware(),
    )
