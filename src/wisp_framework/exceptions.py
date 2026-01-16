"""Custom exception hierarchy for the Wisp Framework."""


class FrameworkError(Exception):
    """Base exception for all framework errors."""

    pass


class WispError(FrameworkError):
    """Base exception for user-facing errors with safe and internal messages.

    This is the base class for all errors that should be shown to users.
    It separates safe user-facing messages from internal error details.
    """

    def __init__(
        self,
        safe_message: str,
        internal_message: str | None = None,
        *args: object,
    ) -> None:
        """Initialize Wisp error.

        Args:
            safe_message: Safe message to show to users
            internal_message: Internal error message for logging (defaults to safe_message)
            *args: Additional arguments passed to Exception
        """
        super().__init__(safe_message, *args)
        self.safe_message = safe_message
        self.internal_message = internal_message or safe_message

    def __str__(self) -> str:
        """Return the internal message for logging."""
        return self.internal_message


class UserError(WispError):
    """Raised when user input is invalid or user action fails.

    This is for errors that are the user's fault (invalid input, etc.).
    """

    pass


class PermissionError(WispError):
    """Raised when user lacks required permissions or capabilities.

    This is for authorization failures.
    """

    pass


class NotFoundError(WispError):
    """Raised when a requested resource is not found.

    This is for 404-like errors (guild not found, user not found, etc.).
    """

    pass


class RateLimitedError(WispError):
    """Raised when rate limit is exceeded.

    This is for rate limiting violations.
    """

    pass


class ExternalServiceError(WispError):
    """Raised when an external service fails.

    This is for errors from external APIs, databases, etc.
    """

    pass


class ConfigError(FrameworkError):
    """Raised when configuration is invalid or missing required values."""

    pass


class ServiceError(FrameworkError):
    """Raised when a service fails to initialize or operate."""

    pass


class ModuleError(FrameworkError):
    """Raised when a module fails to load or operate."""

    pass


class DatabaseError(FrameworkError):
    """Raised when database operations fail."""

    pass


class ValidationError(FrameworkError):
    """Raised when validation fails."""

    pass


def map_error_to_response(error: Exception) -> tuple[str, bool]:
    """Map an exception to a user-friendly Discord response.

    Args:
        error: Exception to map

    Returns:
        Tuple of (message, ephemeral) where message is the user-facing message
        and ephemeral indicates if it should be sent as ephemeral
    """
    if isinstance(error, WispError):
        return (error.safe_message, True)
    elif isinstance(error, PermissionError):
        return ("You don't have permission to perform this action.", True)
    elif isinstance(error, NotFoundError):
        return ("The requested resource was not found.", True)
    elif isinstance(error, RateLimitedError):
        return ("You're being rate limited. Please try again later.", True)
    elif isinstance(error, UserError):
        return (str(error), True)
    elif isinstance(error, ExternalServiceError):
        return ("An external service error occurred. Please try again later.", True)
    else:
        # Generic error message for unexpected errors
        return ("An error occurred while executing the command.", True)
