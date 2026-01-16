"""Example of extending AppConfig for bot-specific configuration."""

import os

from wisp_framework.config import AppConfig


class EchoBotConfig(AppConfig):
    """Echo bot specific configuration extending Wisp Framework's AppConfig.

    This demonstrates how to add bot-specific configuration properties
    while leveraging Wisp Framework's core configuration handling.
    """

    def __init__(self) -> None:
        """Initialize Echo bot configuration."""
        super().__init__()
        self._validate_bot_required()

    def _validate_bot_required(self) -> None:
        """Validate bot-specific required configuration."""
        # Add bot-specific validation here
        pass

    # Feature flags
    @property
    def feature_welcome_messages(self) -> bool:
        """Whether welcome messages are enabled."""
        return self._get_bool("FEATURE_WELCOME_MESSAGES", True)

    @property
    def feature_automod(self) -> bool:
        """Whether automod is enabled."""
        return self._get_bool("FEATURE_AUTOMOD", False)

    @property
    def feature_tickets(self) -> bool:
        """Whether ticket system is enabled."""
        return self._get_bool("FEATURE_TICKETS", False)

    # External integrations
    @property
    def openai_api_key(self) -> str | None:
        """OpenAI API key (optional)."""
        return os.getenv("OPENAI_API_KEY")

    @property
    def giphy_api_key(self) -> str | None:
        """Giphy API key (optional)."""
        return os.getenv("GIPHY_API_KEY")

    @property
    def youtube_api_key(self) -> str | None:
        """YouTube API key (optional)."""
        return os.getenv("YOUTUBE_API_KEY")

    # Webhooks
    @property
    def alerts_webhook_url(self) -> str | None:
        """Alerts webhook URL (optional)."""
        return os.getenv("ALERTS_WEBHOOK_URL")

    @property
    def audit_webhook_url(self) -> str | None:
        """Audit webhook URL (optional)."""
        return os.getenv("AUDIT_WEBHOOK_URL")

    # Storage
    @property
    def data_dir(self) -> str:
        """Data directory path."""
        return os.getenv("DATA_DIR", "./data")

    @property
    def uploads_dir(self) -> str:
        """Uploads directory path."""
        return os.getenv("UPLOADS_DIR", "./data/uploads")

    # S3 storage (optional)
    @property
    def s3_enabled(self) -> bool:
        """Whether S3 storage is enabled."""
        return self._get_bool("S3_ENABLED", False)

    @property
    def s3_endpoint_url(self) -> str | None:
        """S3 endpoint URL."""
        return os.getenv("S3_ENDPOINT_URL")

    @property
    def s3_region(self) -> str:
        """S3 region."""
        return os.getenv("S3_REGION", "us-west-2")

    @property
    def s3_bucket(self) -> str | None:
        """S3 bucket name."""
        return os.getenv("S3_BUCKET")

    @property
    def s3_access_key_id(self) -> str | None:
        """S3 access key ID."""
        return os.getenv("S3_ACCESS_KEY_ID")

    @property
    def s3_secret_access_key(self) -> str | None:
        """S3 secret access key."""
        return os.getenv("S3_SECRET_ACCESS_KEY")

    # Security
    @property
    def app_secret_key(self) -> str | None:
        """Application secret key for signing/encryption."""
        return os.getenv("APP_SECRET_KEY")

    @property
    def signing_secret(self) -> str | None:
        """Signing secret for webhook verification."""
        return os.getenv("SIGNING_SECRET")
