"""Configuration management with environment variable loading and validation."""

import os

import discord


class ConfigError(Exception):
    """Raised when configuration is invalid or missing required values."""

    pass


class AppConfig:
    """Application configuration loaded from environment variables.

    This class handles core Wisp Framework configuration. Bots can subclass
    this to add their own configuration properties.

    Environment file loading:
    - Checks for .env.local, .env.{APP_ENV}, or .env files
    - Only sets variables that aren't already in os.environ
    - Supports quoted values and comments
    """

    def __init__(self, env_file: str | None = None, strict: bool | None = None) -> None:
        """Initialize configuration by loading environment variables.

        Args:
            env_file: Optional path to env file (defaults to .env.local or .env.{APP_ENV})
            strict: Whether to fail fast on missing required configs (defaults to STRICT_CONFIG env var)
        """
        self._load_env_file(env_file)
        self._strict = strict if strict is not None else self._get_bool("STRICT_CONFIG", False)
        self._validate_required()
        self._load_intents()

    def _load_env_file(self, env_file: str | None = None) -> None:
        """Load environment variables from .env file.

        Priority order:
        1. Explicit env_file parameter
        2. .env.local (if exists)
        3. .env.{APP_ENV} (if APP_ENV is set)
        4. .env (fallback)
        """
        if env_file:
            files_to_try = [env_file]
        else:
            app_env = os.getenv("APP_ENV") or os.getenv("ENV", "local")
            files_to_try = [".env.local", f".env.{app_env}", ".env"]

        for env_file_path in files_to_try:
            if os.path.exists(env_file_path):
                with open(env_file_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if not line or line.startswith("#"):
                            continue
                        # Parse key=value pairs
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            # Only set if not already in environment
                            if key not in os.environ:
                                os.environ[key] = value
                break

    def _validate_required(self) -> None:
        """Validate that all required environment variables are present."""
        required = ["DISCORD_TOKEN"]
        missing = [var for var in required if not os.getenv(var)]

        if missing:
            error_msg = f"Missing required environment variables: {', '.join(missing)}"
            if self._strict:
                raise ConfigError(error_msg)
            else:
                # In non-strict mode, only DISCORD_TOKEN is fatal
                if "DISCORD_TOKEN" in missing:
                    raise ConfigError(error_msg)

    def _load_intents(self) -> None:
        """Load Discord intents configuration from environment.

        Supports both old format (INTENTS_GUILDS) and new format (DISCORD_INTENTS_GUILDS).
        GUILDS intent is always enabled as it's required for basic bot functionality.
        """
        # Try new format first (DISCORD_INTENTS_*), fallback to old format (INTENTS_*)
        intents_dict = {
            "guilds": self._get_bool("DISCORD_INTENTS_GUILDS") or self._get_bool("INTENTS_GUILDS", True),
            "members": self._get_bool("DISCORD_INTENTS_MEMBERS") or self._get_bool("INTENTS_MEMBERS", False),
            "messages": self._get_bool("DISCORD_INTENTS_MESSAGES") or self._get_bool("INTENTS_MESSAGES", True),
            "message_content": self._get_bool("DISCORD_INTENTS_MESSAGE_CONTENT") or self._get_bool("INTENTS_MESSAGE_CONTENT", False),
            "reactions": self._get_bool("DISCORD_INTENTS_REACTIONS") or self._get_bool("INTENTS_REACTIONS", True),
            "voice_states": self._get_bool("DISCORD_INTENTS_VOICE_STATES") or self._get_bool("INTENTS_VOICE_STATES", False),
            "guild_messages": self._get_bool("DISCORD_INTENTS_GUILD_MESSAGES") or self._get_bool("INTENTS_GUILD_MESSAGES", True),
            "dm_messages": self._get_bool("DISCORD_INTENTS_DM_MESSAGES") or self._get_bool("INTENTS_DM_MESSAGES", True),
            "presences": self._get_bool("DISCORD_INTENTS_PRESENCES") or self._get_bool("INTENTS_PRESENCES", False),
        }

        # Ensure GUILDS intent is always enabled (required for basic functionality)
        intents_dict["guilds"] = True

        self.intents = discord.Intents(**intents_dict)

    def _get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable.

        If the environment variable is not set, returns the default.
        If set to empty string, treats as False (explicitly disabled).
        """
        value = os.getenv(key)
        if value is None:
            # Environment variable not set - use default
            return default
        value = value.lower().strip()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off", ""):
            return False
        # Unknown value - use default
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

    def _get_float(self, key: str, default: float | None = None) -> float | None:
        """Get float value from environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def _get_list(self, key: str, default: list[str] | None = None, separator: str = ",") -> list[str]:
        """Get list value from environment variable (comma-separated by default)."""
        value = os.getenv(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(separator) if item.strip()]

    def _get_int_list(self, key: str, default: list[int] | None = None) -> list[int]:
        """Get list of integers from environment variable (comma-separated)."""
        str_list = self._get_list(key)
        if not str_list:
            return default or []
        result = []
        for item in str_list:
            try:
                result.append(int(item))
            except ValueError:
                continue
        return result

    @property
    def discord_token(self) -> str:
        """Discord bot token (read-only, must be set via DISCORD_TOKEN environment variable)."""
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ConfigError("DISCORD_TOKEN is required")
        return token

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
        # Support both DISCORD_OWNER_IDS (comma-separated) and OWNER_ID (single)
        owner_ids = self._get_int_list("DISCORD_OWNER_IDS")
        if owner_ids:
            return owner_ids[0]  # Return first owner ID for backward compatibility
        return self._get_int("OWNER_ID")

    @property
    def owner_ids(self) -> list[int]:
        """Bot owner Discord user IDs (optional, comma-separated)."""
        # Support both DISCORD_OWNER_IDS (comma-separated) and OWNER_ID (single)
        owner_ids = self._get_int_list("DISCORD_OWNER_IDS")
        if owner_ids:
            return owner_ids
        owner_id = self._get_int("OWNER_ID")
        return [owner_id] if owner_id else []

    @property
    def application_id(self) -> int | None:
        """Discord application ID (optional but useful for OAuth/command sync)."""
        return self._get_int("DISCORD_APPLICATION_ID")

    @property
    def guild_ids(self) -> list[int]:
        """Guild IDs for dev-only command sync (optional, comma-separated)."""
        return self._get_int_list("DISCORD_GUILD_IDS")

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
        return self._get_int("DB_POOL_RECYCLE") or self._get_int("DB_POOL_RECYCLE_SECONDS", 3600) or 3600

    @property
    def db_echo_sql(self) -> bool:
        """Whether to echo SQL queries (useful for debugging)."""
        return self._get_bool("DB_ECHO_SQL", False)

    # Redis/Cache settings
    @property
    def redis_enabled(self) -> bool:
        """Whether Redis is enabled."""
        return self._get_bool("REDIS_ENABLED", True) if self.redis_url else False

    @property
    def cache_default_ttl(self) -> int:
        """Default cache TTL in seconds."""
        return self._get_int("CACHE_DEFAULT_TTL_SECONDS", 300) or 300

    # Observability settings
    @property
    def sentry_traces_sample_rate(self) -> float:
        """Sentry traces sample rate (0.0-1.0)."""
        return self._get_float("SENTRY_TRACES_SAMPLE_RATE", 0.0) or 0.0

    @property
    def otel_enabled(self) -> bool:
        """Whether OpenTelemetry is enabled."""
        return self._get_bool("OTEL_ENABLED", False)

    @property
    def otel_service_name(self) -> str:
        """OpenTelemetry service name."""
        return os.getenv("OTEL_SERVICE_NAME", "wisp-bot")

    @property
    def otel_endpoint(self) -> str | None:
        """OpenTelemetry OTLP endpoint."""
        return os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    # App metadata (for bot-level use, but provided here for convenience)
    @property
    def app_name(self) -> str:
        """Application name."""
        return os.getenv("APP_NAME", "wisp-bot")

    @property
    def app_env(self) -> str:
        """Application environment (development/staging/production)."""
        return os.getenv("APP_ENV") or os.getenv("ENV", "development")

    @property
    def timezone(self) -> str:
        """Timezone for the application."""
        return os.getenv("TZ", "UTC")
