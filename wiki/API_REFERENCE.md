# API Reference

Complete API documentation for the Wisp Framework.

> **See also:** [[Architecture-Overview]] | [[Module-Development]] | [[Services-Documentation]]

## Quick Import Reference

The main classes and functions you'll use:

```python
from wisp_framework import WispBot, create_app, Module, ModuleRegistry
from wisp_framework.config import AppConfig
from wisp_framework.context import BotContext
from wisp_framework.lifecycle import LifecycleManager
```

**Important:** There is no `Wisp` class. Use `WispBot` (the main bot class) or `create_app()` (convenience function) instead.

## Table of Contents

- [Core Classes](#core-classes)
- [Configuration](#configuration)
- [Services](#services)
- [Database](#database)
- [Utilities](#utilities)
- [Exceptions](#exceptions)

> **See also:** [[Architecture-Overview]] | [[Module-Development]] | [[Services-Documentation]]

## Core Classes

### `WispBot`

Main bot class for Wisp Framework, extending `discord.ext.commands.Bot`.

```python
from wisp_framework import WispBot
```

#### Constructor

```python
WispBot(
    config: AppConfig,
    services: ServiceContainer,
    module_registry: ModuleRegistry,
    ctx: BotContext
)
```

**Parameters:**
- `config` (AppConfig): Application configuration
- `services` (ServiceContainer): Service container instance
- `module_registry` (ModuleRegistry): Module registry instance
- `ctx` (BotContext): Bot context with services and config

**Attributes:**
- `config` (AppConfig): Application configuration
- `services` (ServiceContainer): Service container
- `module_registry` (ModuleRegistry): Module registry
- `ctx` (BotContext): Bot context
- `started_at` (Optional[datetime]): Bot startup timestamp

#### Methods

##### `async setup_hook() -> None`

Called when the bot is starting up. Syncs commands if configured.

##### `async on_ready() -> None`

Called when the bot is ready. Loads modules for all guilds.

##### `async on_app_command_completion(interaction, command) -> None`

Called when an app command completes successfully. Logs to audit service.

##### `async on_guild_join(guild) -> None`

Called when the bot joins a new guild. Loads enabled modules for the guild.

##### `async on_app_command_error(interaction, error) -> None`

Global error handler for app commands. Provides user-friendly error messages.

---

### `Module`

Abstract base class for framework modules.

```python
from wisp_framework import Module
```

#### Properties

##### `name: str` (abstract)

Module name. Must be unique.

##### `default_enabled: bool`

Whether the module is enabled by default. Default: `True`

##### `required_services: Set[str]`

Set of required service names. Default: `set()`

##### `depends_on: list[str]`

List of module names this module depends on. Default: `[]`

#### Methods

##### `async setup(bot, ctx) -> None` (abstract)

Set up the module. Called when the module is loaded.

**Parameters:**
- `bot`: The Discord bot instance
- `ctx`: Bot context with services and config

##### `async teardown(bot, ctx) -> None`

Tear down the module. Called when the module is unloaded. Default implementation does nothing.

---

### `ModuleRegistry`

Registry for managing framework modules.

```python
from wisp_framework import ModuleRegistry
```

#### Constructor

```python
ModuleRegistry(feature_flags: FeatureFlags)
```

#### Methods

##### `register(module: Module) -> None`

Register a module.

**Raises:**
- `ValueError`: If module name is already registered

##### `discover_modules(package_path: str) -> None`

Automatically discover and register modules from a package.

**Parameters:**
- `package_path`: Python package path (e.g., 'wisp_framework.modules')

##### `list_modules() -> List[str]`

List all registered module names.

##### `get_module(name: str) -> Optional[Module]`

Get a module by name.

##### `async load_enabled_modules(bot, ctx, guild_id: Optional[int] = None) -> None`

Load all enabled modules for a guild.

**Parameters:**
- `bot`: The Discord bot instance
- `ctx`: Bot context with services and config
- `guild_id`: Guild ID (None for global modules)

---

### `BotContext`

Context object passed to modules with services and configuration.

```python
from wisp_framework import BotContext
```

#### Attributes

- `config` (AppConfig): Application configuration
- `services` (ServiceContainer): Service container
- `guild_data` (GuildDataService): Per-guild data storage service

---

### `LifecycleManager`

Manages bot startup and shutdown lifecycle.

```python
from wisp_framework.lifecycle import LifecycleManager
```

#### Methods

##### `async startup(config, services, module_registry, ctx) -> FrameworkBot`

Start up the bot and all services.

**Returns:** Configured FrameworkBot instance

##### `async shutdown() -> None`

Shut down the bot and all services gracefully.

---

### `AppConfig`

Application configuration loaded from environment variables.

```python
from wisp_framework import AppConfig
```

#### Properties

- `discord_token: str` - Discord bot token (required)
- `database_url: Optional[str]` - Database connection URL
- `redis_url: Optional[str]` - Redis connection URL
- `log_level: str` - Logging level (default: "INFO")
- `sync_on_startup: bool` - Whether to sync commands on startup (default: True)
- `owner_id: Optional[int]` - Bot owner Discord user ID
- `welcome_channel_id: Optional[int]` - Default welcome channel ID
- `intents: discord.Intents` - Discord gateway intents

#### Methods

##### `_load_env_file() -> None`

Load environment variables from `.env.{ENV}` file.

##### `_validate_required() -> None`

Validate that all required environment variables are present.

**Raises:**
- `ConfigError`: If required variables are missing

---

## Configuration

### Environment Variables

See [[Configuration-Reference]] for complete list.

---

## Services

### `ServiceContainer`

Container for managing framework services.

```python
from wisp_framework.services.base import ServiceContainer
```

#### Methods

##### `register(name: str, service: BaseService) -> None`

Register a service with the container.

**Raises:**
- `ServiceError`: If service name is already registered

##### `get(name: str) -> Optional[BaseService]`

Get a service by name.

##### `get_typed(name: str, service_type: Type[T]) -> Optional[T]`

Get a service by name with type checking.

**Raises:**
- `ServiceError`: If service is not of the expected type

##### `async startup_all() -> None`

Start up all registered services.

##### `async shutdown_all() -> None`

Shut down all registered services.

##### `list_services() -> list[str]`

List all registered service names.

### Available Services

See [[Services-Documentation]] for detailed service documentation.

---

## Database

### `GuildDataService`

Service for per-guild key-value data storage.

```python
from wisp_framework.db.guild_data import GuildDataService
```

#### Methods

##### `async set(guild_id: int, key: str, value: Any, module_name: Optional[str] = None) -> None`

Store a value for a guild.

##### `async get(guild_id: int, key: str, module_name: Optional[str] = None) -> Optional[Any]`

Retrieve a value for a guild.

##### `async delete(guild_id: int, key: str, module_name: Optional[str] = None) -> None`

Delete a value for a guild.

##### `async get_all(guild_id: int, module_name: Optional[str] = None) -> Dict[str, Any]`

Get all data for a guild (optionally filtered by module).

### Database Models

See [Database Models](ARCHITECTURE.md#database-models) for model documentation.

---

## Utilities

### Embed Builders

```python
from wisp_framework.utils.embeds import EmbedBuilder
```

See [Framework Extensions](EXTENSIONS.md#embed-builders) for details.

### Response Helpers

```python
from wisp_framework.utils.responses import (
    respond_success,
    respond_error,
    respond_info,
    respond_embed
)
```

See [Framework Extensions](EXTENSIONS.md#response-helpers) for details.

### Decorators

```python
from wisp_framework.utils.decorators import (
    require_guild,
    require_admin,
    require_owner,
    handle_errors
)
```

See [Framework Extensions](EXTENSIONS.md#decorators) for details.

### Pagination

```python
from wisp_framework.utils.pagination import paginate_embeds
```

See [Framework Extensions](EXTENSIONS.md#pagination) for details.

### Cooldowns

```python
from wisp_framework.utils.cooldowns import cooldown
```

See [Framework Extensions](EXTENSIONS.md#cooldowns) for details.

---

## Exceptions

### `FrameworkError`

Base exception for framework errors.

### `ConfigError`

Raised when configuration is invalid or missing required values.

### `ServiceError`

Raised when a service operation fails.

---

## Version Information

### `__version__`

Current framework version.

```python
from wisp_framework import __version__
```

Current version: **0.2.0**

## Related Documentation

- [[Module-Development]] - Using these APIs in modules
- [[Services-Documentation]] - Detailed service documentation
- [[Configuration-Reference]] - Configuration options
- [[Architecture-Overview]] - Understanding the architecture

---

## Convenience Functions

### `create_app()`

Create and configure a Discord bot application.

```python
from wisp_framework import create_app

bot, lifecycle, ctx = create_app(
    config=None,
    auto_discover_modules=False,
    module_package="wisp_framework.modules"
)
```

**Parameters:**
- `config` (Optional[AppConfig]): Optional AppConfig instance
- `auto_discover_modules` (bool): Whether to auto-discover modules
- `module_package` (str): Package path for module discovery

**Returns:** Tuple of (bot, lifecycle_manager, context)
