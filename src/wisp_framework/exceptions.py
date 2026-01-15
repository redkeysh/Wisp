"""Custom exception hierarchy for the Wisp Framework."""


class FrameworkError(Exception):
    """Base exception for all framework errors."""

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
