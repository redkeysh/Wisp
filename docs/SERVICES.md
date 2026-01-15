# Services Documentation

Complete documentation for all framework services.

> **See also:** [[API-Reference]] | [[Module-Development]] | [[Architecture-Overview]]

## Table of Contents

- [Service Overview](#service-overview)
- [Core Services](#core-services)
- [Optional Services](#optional-services)
- [Using Services](#using-services)
- [Creating Custom Services](#creating-custom-services)

## Service Overview

Services are managed through the `ServiceContainer` and provide reusable functionality across modules. All services follow a common lifecycle pattern:

1. **Registration**: Service is registered with the container
2. **Startup**: `startup()` method is called during bot initialization
3. **Execution**: Service provides functionality during bot runtime
4. **Shutdown**: `shutdown()` method is called during bot shutdown

## Core Services

### HealthService

Provides health checks for all services.

```python
health = ctx.services.get("health")

# Check service health
status = await health.check_service("db")

# Get all service statuses
all_statuses = await health.get_all_statuses()
```

**Methods:**
- `async check_service(name: str) -> bool`: Check if a service is healthy
- `async get_all_statuses() -> Dict[str, bool]`: Get health status of all services

### CacheService

In-memory caching service.

```python
cache = ctx.services.get("cache")

# Set value with TTL
await cache.set("key", "value", ttl=3600)

# Get value
value = await cache.get("key")

# Delete value
await cache.delete("key")

# Clear all cache
await cache.clear()
```

**Methods:**
- `async set(key: str, value: Any, ttl: Optional[float] = None) -> None`
- `async get(key: str) -> Optional[Any]`
- `async delete(key: str) -> None`
- `async clear() -> None`

### MetricsService

Counter and timing metrics.

```python
metrics = ctx.services.get("metrics")

# Increment counter
metrics.increment("commands.executed")

# Decrement counter
metrics.decrement("commands.executed")

# Record timing
import time
start = time.time()
# ... do work ...
metrics.timing("command.duration", time.time() - start)

# Set gauge
metrics.gauge("active_users", 42)
```

**Methods:**
- `increment(name: str, value: float = 1.0) -> None`
- `decrement(name: str, value: float = 1.0) -> None`
- `timing(name: str, value: float) -> None`
- `gauge(name: str, value: float) -> None`

### SchedulerService

Periodic task scheduling.

```python
scheduler = ctx.services.get("scheduler")

async def my_task():
    # Task logic
    pass

# Register periodic task (runs every hour)
scheduler.register(my_task, interval=3600.0, name="hourly_task")

# Register one-time task (runs after delay)
scheduler.register_once(my_task, delay=60.0, name="delayed_task")

# Unregister task
scheduler.unregister("hourly_task")
```

**Methods:**
- `register(task: Callable, interval: float, name: str) -> None`
- `register_once(task: Callable, delay: float, name: str) -> None`
- `unregister(name: str) -> None`

### AuditService

Audit logging with Discord object serialization.

```python
audit = ctx.services.get("audit")

audit.log_action(
    action="command_executed",
    user_id=interaction.user.id,
    guild_id=interaction.guild_id,
    channel_id=interaction.channel_id,
    metadata={
        "command": "example",
        "args": ["arg1", "arg2"]
    }
)
```

**Methods:**
- `log_action(action: str, user_id: Optional[int] = None, guild_id: Optional[int] = None, channel_id: Optional[int] = None, metadata: Optional[Dict] = None) -> None`

### WebhookLoggerService

Rate-limited webhook logging with retry logic.

```python
webhook_logger = ctx.services.get("webhook_logger")

await webhook_logger.log(
    content="Important event occurred",
    embed=embed,
    level="info"
)
```

**Methods:**
- `async log(content: str, embed: Optional[discord.Embed] = None, level: str = "info") -> None`

## Optional Services

### DatabaseService

SQLAlchemy async database service (requires `[db]` extra).

```python
from wisp_framework.services.db import DatabaseService

db = ctx.services.get_typed("db", DatabaseService)

if db and db.session_factory:
    async with db.session_factory() as session:
        # Use SQLAlchemy session
        result = await session.execute(select(Model))
        data = result.scalar_one_or_none()
```

**Properties:**
- `engine`: SQLAlchemy async engine
- `session_factory`: Async session factory

**Methods:**
- `get_session() -> AsyncSession`: Get a new database session

### RedisCacheService

Redis-backed caching (requires `[redis]` extra).

If Redis is available, `CacheService` automatically uses Redis instead of in-memory cache.

## Using Services

### Getting Services

```python
# Get service by name (returns Optional[BaseService])
cache = ctx.services.get("cache")

# Get typed service (returns Optional[ServiceType])
from wisp_framework.services.db import DatabaseService
db = ctx.services.get_typed("db", DatabaseService)
```

### Checking Service Availability

```python
cache = ctx.services.get("cache")
if cache:
    await cache.set("key", "value")
else:
    # Fallback behavior
    logger.warning("Cache service not available")
```

### Service Lifecycle

Services are automatically started and stopped by the framework. You don't need to manually manage service lifecycle unless creating custom services.

## Creating Custom Services

### Basic Service Structure

```python
from wisp_framework.services.base import BaseService

class MyService(BaseService):
    async def startup(self) -> None:
        """Initialize the service."""
        # Setup code here
        self._mark_initialized()
    
    async def shutdown(self) -> None:
        """Clean up the service."""
        # Cleanup code here
```

### Registering Custom Services

```python
from wisp_framework.lifecycle import create_services

# Custom service creation
def create_custom_services(config):
    services = ServiceContainer(config)
    
    # Register custom service
    my_service = MyService(config)
    services.register("my_service", my_service)
    
    # Register standard services
    # ...
    
    return services
```

### Service Dependencies

Services can depend on other services:

```python
class DependentService(BaseService):
    async def startup(self) -> None:
        # Access other services through config
        # (services are passed via config in create_services)
        pass
```

## Service Best Practices

1. **Check Availability**: Always check if a service is available before using it
2. **Handle Gracefully**: Provide fallback behavior if services are unavailable
3. **Use Type Hints**: Use `get_typed()` for type-safe service access
4. **Clean Up**: Implement `shutdown()` to clean up resources
5. **Log Operations**: Log important service operations for debugging

## Service Configuration

Services are configured via `AppConfig` and environment variables. See [Configuration Reference](CONFIGURATION.md) for details.

## Next Steps

- See [[API-Reference]] for detailed API documentation
- Check [[Architecture-Overview]] for service architecture
- Review [[Module-Development]] for using services in modules
