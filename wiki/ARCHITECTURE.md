# Architecture Overview

This document provides an overview of the Wisp Framework architecture, design principles, and component relationships.

> **See also:** [[API-Reference]] | [[Module-Development]] | [[Services-Documentation]]

## Table of Contents

- [Design Principles](#design-principles)
- [Component Overview](#component-overview)
- [Data Flow](#data-flow)
- [Module System](#module-system)
- [Service System](#service-system)
- [Database Architecture](#database-architecture)
- [Lifecycle Management](#lifecycle-management)

## Design Principles

### 1. Modularity

The framework is built around a modular architecture where functionality is organized into independent, reusable modules. Each module can be enabled or disabled per guild, allowing for flexible bot configurations.

### 2. Graceful Degradation

Optional dependencies (like database or Redis) are handled gracefully. The framework functions even if these services are unavailable, with appropriate fallbacks and warnings.

### 3. Dependency Injection

Services are managed through a service container, providing dependency injection and making components testable and loosely coupled.

### 4. Type Safety

Full type hints throughout the codebase enable better IDE support, static analysis, and self-documenting code.

### 5. Production Ready

Built-in support for production concerns:
- Health checks
- Graceful shutdown
- Connection pooling
- Error handling
- Audit logging

## Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                    │
│  (User's Bot Code, Custom Modules, Runner Bot)         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  WispBot                               │
│  - Command handling                                     │
│  - Event processing                                     │
│  - Module lifecycle                                     │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌─────────▼──────────┐
│ ModuleRegistry │      │  ServiceContainer  │
│  - Registration│      │  - Service mgmt    │
│  - Discovery   │      │  - DI              │
│  - Loading     │      │  - Lifecycle       │
└────────────────┘      └─────────┬──────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
            ┌───────▼───┐  ┌──────▼────┐  ┌─────▼─────┐
            │ Database  │  │   Cache   │  │ Scheduler │
            │  Service  │  │  Service  │  │  Service  │
            └───────────┘  └───────────┘  └───────────┘
```

## Data Flow

### Command Execution Flow

```
User Command
    │
    ▼
WispBot.on_app_command_completion()
    │
    ▼
Module Command Handler
    │
    ▼
BotContext (services, config, guild_data)
    │
    ▼
Service Layer (if needed)
    │
    ▼
Response to User
```

### Module Loading Flow

```
Bot Startup
    │
    ▼
LifecycleManager.startup()
    │
    ▼
ServiceContainer.startup_all()
    │
    ▼
ModuleRegistry.load_enabled_modules()
    │
    ▼
Module.setup() for each enabled module
    │
    ▼
Bot Ready
```

## Module System

### Module Structure

Each module is a Python class that extends `Module`:

```python
class MyModule(Module):
    @property
    def name(self) -> str:
        return "my_module"
    
    async def setup(self, bot, ctx):
        # Register commands, event handlers, etc.
        pass
```

### Module Lifecycle

1. **Registration**: Module is registered with `ModuleRegistry`
2. **Discovery**: Modules can be auto-discovered from packages
3. **Dependency Resolution**: Dependencies are resolved before loading
4. **Loading**: `setup()` is called for enabled modules
5. **Execution**: Module handles commands/events
6. **Unloading**: `teardown()` is called when module is disabled

### Per-Guild Module State

Modules can be enabled or disabled per guild using feature flags:

- Stored in database (if available) or memory
- Checked before module loading
- Can be toggled via `/modules enable/disable` commands

## Service System

### Service Architecture

Services are managed through a `ServiceContainer` that provides:

- **Registration**: Services register themselves with a name
- **Retrieval**: Services can be retrieved by name or type
- **Lifecycle**: Services have `startup()` and `shutdown()` methods
- **Dependency Management**: Services can depend on other services

### Service Types

#### Core Services (Always Available)

- **HealthService**: Health checks for all services
- **CacheService**: In-memory caching
- **MetricsService**: Counter and timing metrics
- **SchedulerService**: Periodic task scheduling
- **AuditService**: Audit logging
- **WebhookLoggerService**: Rate-limited webhook logging

#### Optional Services

- **DatabaseService**: SQLAlchemy async database (requires `[db]` extra)
- **RedisCacheService**: Redis-backed caching (requires `[redis]` extra)

### Service Lifecycle

```python
class MyService(BaseService):
    async def startup(self):
        # Initialize service
        self._mark_initialized()
    
    async def shutdown(self):
        # Cleanup resources
        pass
```

## Database Architecture

### Models

The framework provides three base models:

#### `GuildConfig`

Stores per-guild configuration:
- `guild_id`: Discord guild ID (primary key)
- `welcome_channel_id`: Welcome channel ID
- Custom configuration fields

#### `ModuleState`

Tracks module enable/disable state per guild:
- `guild_id`: Discord guild ID
- `module_name`: Module name
- `enabled`: Whether module is enabled

#### `GuildData`

Generic key-value storage for per-guild data:
- `guild_id`: Discord guild ID
- `key`: Data key
- `value`: JSON-serialized value
- `module_name`: Optional module namespace

### Database Service

The `DatabaseService` provides:

- Async SQLAlchemy engine and sessions
- Connection pooling
- Migration support via Alembic
- Graceful degradation (stub if unavailable)

### Guild Data Service

`GuildDataService` provides a high-level interface for per-guild data:

- Automatic serialization/deserialization
- Module namespacing
- Database-backed with in-memory fallback

## Lifecycle Management

### Startup Sequence

1. Load configuration from environment
2. Set up logging
3. Create service container
4. Register and start services
5. Create feature flags
6. Create module registry
7. Register/discover modules
8. Create bot context
9. Initialize bot
10. Load modules for each guild
11. Start bot

### Shutdown Sequence

1. Stop accepting new commands
2. Unload modules (call `teardown()`)
3. Shutdown services (in reverse order)
4. Close database connections
5. Clean up resources

### Error Handling

- Services that fail to start prevent bot startup
- Module loading errors are logged but don't stop bot
- Command errors are caught and displayed to users
- Global error handlers provide user-friendly messages

## Extension Points

### Creating Custom Services

```python
from wisp_framework.services.base import BaseService

class MyService(BaseService):
    async def startup(self):
        # Initialize
        pass
    
    async def shutdown(self):
        # Cleanup
        pass
```

### Creating Custom Modules

See [[Module-Development]].

### Extending Bot Functionality

- Override `WispBot` methods
- Add custom event handlers
- Extend `BotContext` with custom services
- Create utility functions in `utils/`

## Best Practices

1. **Use Type Hints**: Always type hint function parameters and return values
2. **Handle Errors**: Use try/except blocks and provide meaningful error messages
3. **Log Appropriately**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
4. **Test Services**: Check if services are available before using them
5. **Namespace Data**: Use `module_name` parameter in `guild_data` calls
6. **Clean Up**: Implement `teardown()` if your module needs cleanup
7. **Document Code**: Add docstrings to classes and functions
8. **Follow Patterns**: Use existing modules as examples

## Performance Considerations

- **Connection Pooling**: Database connections are pooled
- **Lazy Loading**: Modules are loaded only when needed
- **Caching**: Use cache service for frequently accessed data
- **Async Operations**: All I/O operations are async
- **Resource Limits**: Docker deployments include resource limits

## Security Considerations

- **Environment Variables**: Sensitive data in environment variables
- **Input Validation**: Validate user input in commands
- **Permission Checks**: Use decorators for permission checks
- **Audit Logging**: All actions are logged via audit service
- **Database Passwords**: Must be changed from defaults in production
