"""Configuration management with environment variable loading and validation."""

import os

import discord


class ConfigError(Exception):
    """Raised when configuration is invalid or missing required values."""

    pass


class AppConfig:
    """Application configuration loaded from environment variables and optional YAML files."""

    def __init__(self) -> None:
        """Initialize configuration by loading environment variables."""
        self._load_env_file()
        self._validate_required()
        self._load_intents()

    def _load_env_file(self) -> None:
        """Load environment variables from .env file based on ENV variable."""
        env = os.getenv("ENV", "local")
        env_file = f".env.{env}"

        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value

    def _validate_required(self) -> None:
        """Validate that all required environment variables are present."""
        required = ["DISCORD_TOKEN"]
        missing = [var for var in required if not os.getenv(var)]

        if missing:
            raise ConfigError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

    def _load_intents(self) -> None:
        """Load Discord intents configuration from environment."""
        # Default to all intents if not specified
        intents_dict = {
            "guilds": self._get_bool("INTENTS_GUILDS", True),
            "members": self._get_bool("INTENTS_MEMBERS", True),
            "messages": self._get_bool("INTENTS_MESSAGES", True),
            "message_content": self._get_bool("INTENTS_MESSAGE_CONTENT", True),
            "reactions": self._get_bool("INTENTS_REACTIONS", True),
            "voice_states": self._get_bool("INTENTS_VOICE_STATES", True),
            "guild_messages": self._get_bool("INTENTS_GUILD_MESSAGES", True),
            "dm_messages": self._get_bool("INTENTS_DM_MESSAGES", True),
        }

        self.intents = discord.Intents(**intents_dict)

    def _get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, "").lower()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off", ""):
            return False
        return default

    def _get_int(self, key: str, default: int | None = None) -> int | None:
        """Get integer value from environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    @property
    def discord_token(self) -> str:
        """Discord bot token."""
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ConfigError("DISCORD_TOKEN is required")
        return token

    @discord_token.setter
    def discord_token(self, value: str) -> None:
        """Set Discord bot token."""
        if not value:
            raise ConfigError("DISCORD_TOKEN cannot be empty")
        os.environ["DISCORD_TOKEN"] = value

    @property
    def database_url(self) -> str | None:
        """Database connection URL (optional)."""
        return os.getenv("DATABASE_URL")

    @property
    def redis_url(self) -> str | None:
        """Redis connection URL (optional)."""
        return os.getenv("REDIS_URL")

    @property
    def log_level(self) -> str:
        """Logging level."""
        return os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def sync_on_startup(self) -> bool:
        """Whether to sync commands on startup."""
        return self._get_bool("SYNC_ON_STARTUP", True)

    @property
    def owner_id(self) -> int | None:
        """Bot owner Discord user ID (optional)."""
        return self._get_int("OWNER_ID")

    @property
    def welcome_channel_id(self) -> int | None:
        """Default welcome channel ID (optional)."""
        return self._get_int("WELCOME_CHANNEL_ID")

    @property
    def sentry_dsn(self) -> str | None:
        """Sentry DSN for error tracking (optional)."""
        return os.getenv("SENTRY_DSN")

    @property
    def webhook_logger_url(self) -> str | None:
        """Webhook URL for logging (optional)."""
        return os.getenv("WEBHOOK_LOGGER_URL")

    # Database pool settings
    @property
    def db_pool_size(self) -> int:
        """Database connection pool size."""
        return self._get_int("DB_POOL_SIZE", 10) or 10

    @property
    def db_max_overflow(self) -> int:
        """Database connection pool max overflow."""
        return self._get_int("DB_MAX_OVERFLOW", 20) or 20

    @property
    def db_pool_timeout(self) -> int:
        """Database connection pool timeout in seconds."""
        return self._get_int("DB_POOL_TIMEOUT", 30) or 30

    @property
    def db_pool_recycle(self) -> int:
        """Database connection pool recycle time in seconds."""
        return self._get_int("DB_POOL_RECYCLE", 3600) or 3600
