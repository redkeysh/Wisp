# Module Development Guide

Complete guide to creating, developing, and maintaining modules for the Wisp Framework.

## Table of Contents

- [Module Basics](#module-basics)
- [Creating Your First Module](#creating-your-first-module)
- [Module Properties](#module-properties)
- [Module Lifecycle](#module-lifecycle)
- [Working with Commands](#working-with-commands)
- [Working with Events](#working-with-events)
- [Using Services](#using-services)
- [Per-Guild Data Storage](#per-guild-data-storage)
- [Module Dependencies](#module-dependencies)
- [Best Practices](#best-practices)
- [Testing Modules](#testing-modules)

## Module Basics

A module is a self-contained unit of functionality that extends the `Module` base class. Modules can:

- Register slash commands
- Handle Discord events
- Store per-guild data
- Use framework services
- Depend on other modules

## Creating Your First Module

### Basic Module Structure

```python
from typing import Any
import discord
from wisp_framework.module import Module

class MyModule(Module):
    @property
    def name(self) -> str:
        return "my_module"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        # Module setup code here
        pass
    
    async def teardown(self, bot: Any, ctx: Any) -> None:
        # Cleanup code here (optional)
        pass
```

### Registering a Module

```python
from wisp_framework.registry import ModuleRegistry

module_registry = ModuleRegistry(feature_flags)
module_registry.register(MyModule())
```

## Module Properties

### Required Properties

#### `name: str`

Unique identifier for the module. Used for:
- Module registration
- Feature flag lookups
- Dependency resolution
- Module commands (`/modules enable my_module`)

**Example:**
```python
@property
def name(self) -> str:
    return "my_module"
```

### Optional Properties

#### `default_enabled: bool`

Whether the module is enabled by default for new guilds. Default: `True`

```python
@property
def default_enabled(self) -> bool:
    return False  # Disabled by default
```

#### `required_services: Set[str]`

Set of service names this module requires. If a service is unavailable, the module won't load.

```python
@property
def required_services(self) -> Set[str]:
    return {"db", "cache"}
```

#### `depends_on: list[str]`

List of module names this module depends on. Dependencies are loaded first.

```python
@property
def depends_on(self) -> list[str]:
    return ["base_module", "auth_module"]
```

## Module Lifecycle

### Setup Phase

The `setup()` method is called when the module is loaded:

```python
async def setup(self, bot: Any, ctx: Any) -> None:
    # Register commands
    # Set up event handlers
    # Initialize module-specific resources
    pass
```

### Execution Phase

During execution, the module handles:
- Slash commands
- Discord events
- Scheduled tasks
- User interactions

### Teardown Phase

The `teardown()` method is called when the module is unloaded:

```python
async def teardown(self, bot: Any, ctx: Any) -> None:
    # Clean up resources
    # Cancel scheduled tasks
    # Close connections
    pass
```

## Working with Commands

### Slash Commands

```python
async def setup(self, bot: Any, ctx: Any) -> None:
    tree = bot.tree
    
    @tree.command(name="hello", description="Say hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message("Hello!")
```

### Command Parameters

```python
@tree.command(name="greet", description="Greet a user")
@app_commands.describe(user="The user to greet")
async def greet(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"Hello, {user.mention}!")
```

### Using Decorators

```python
from wisp_framework.utils.decorators import require_guild, handle_errors

@tree.command(name="guild-only")
@require_guild
@handle_errors
async def guild_command(interaction: discord.Interaction):
    await interaction.response.send_message("This only works in servers!")
```

### Command Groups

```python
from wisp_framework.utils.command_groups import CommandGroup

async def setup(self, bot: Any, ctx: Any) -> None:
    admin_group = CommandGroup("admin", "Admin commands", guild_only=True)
    admin_group.create_group(bot.tree)
    
    @admin_group.command(name="kick", description="Kick a user")
    async def kick(interaction: discord.Interaction, user: discord.Member):
        await interaction.response.send_message(f"Kicked {user.mention}")
```

## Working with Events

### Discord Events

```python
async def setup(self, bot: Any, ctx: Any) -> None:
    @bot.event
    async def on_member_join(member: discord.Member):
        if member.guild:
            channel = member.guild.system_channel
            if channel:
                await channel.send(f"Welcome {member.mention}!")
    
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return
        # Handle message
```

### Custom Events

You can emit and listen to custom events using the bot's event system.

## Using Services

### Accessing Services

```python
async def setup(self, bot: Any, ctx: Any) -> None:
    # Get service by name
    cache = ctx.services.get("cache")
    
    # Get typed service
    from wisp_framework.services.db import DatabaseService
    db = ctx.services.get_typed("db", DatabaseService)
    
    # Check if service is available
    if cache:
        await cache.set("key", "value", ttl=3600)
```

### Cache Service

```python
cache = ctx.services.get("cache")

# Set value
await cache.set("key", "value", ttl=3600)

# Get value
value = await cache.get("key")

# Delete value
await cache.delete("key")
```

### Database Service

```python
db = ctx.services.get_typed("db", DatabaseService)
if db and db.session_factory:
    async with db.session_factory() as session:
        # Use session
        result = await session.execute(select(Model))
        data = result.scalar_one_or_none()
```

### Scheduler Service

```python
scheduler = ctx.services.get("scheduler")

async def periodic_task():
    # Your periodic task logic
    pass

if scheduler:
    scheduler.register(periodic_task, interval=3600.0, name="my_task")
```

### Metrics Service

```python
metrics = ctx.services.get("metrics")

# Increment counter
metrics.increment("commands.executed")

# Record timing
import time
start = time.time()
# ... do work ...
metrics.timing("command.duration", time.time() - start)
```

### Audit Service

```python
audit = ctx.services.get("audit")

if audit:
    audit.log_action(
        action="user_action",
        user_id=interaction.user.id,
        guild_id=interaction.guild_id,
        metadata={"key": "value"}
    )
```

## Per-Guild Data Storage

### Storing Data

```python
await ctx.guild_data.set(
    guild_id=interaction.guild.id,
    key="command_count",
    value=42,
    module_name="my_module"  # Optional namespace
)
```

### Retrieving Data

```python
count = await ctx.guild_data.get(
    guild_id=interaction.guild.id,
    key="command_count",
    module_name="my_module"
)
```

### Deleting Data

```python
await ctx.guild_data.delete(
    guild_id=interaction.guild.id,
    key="command_count",
    module_name="my_module"
)
```

### Getting All Data

```python
all_data = await ctx.guild_data.get_all(
    guild_id=interaction.guild.id,
    module_name="my_module"
)
```

## Module Dependencies

### Declaring Dependencies

```python
@property
def depends_on(self) -> list[str]:
    return ["base_module", "auth_module"]
```

Dependencies are loaded in order before the module itself.

### Checking Dependencies

The framework automatically resolves dependencies. If a dependency is missing, the module won't load.

## Best Practices

### 1. Use Type Hints

```python
from typing import Any
import discord

async def setup(self, bot: Any, ctx: Any) -> None:
    pass
```

### 2. Handle Errors Gracefully

```python
from wisp_framework.utils.decorators import handle_errors

@tree.command(name="safe")
@handle_errors
async def safe_command(interaction: discord.Interaction):
    # Errors are automatically caught and displayed
    raise ValueError("This will be caught!")
```

### 3. Check Service Availability

```python
cache = ctx.services.get("cache")
if cache:
    await cache.set("key", "value")
else:
    # Fallback behavior
    pass
```

### 4. Use Module Namespacing

Always use `module_name` parameter in `guild_data` calls to avoid key conflicts:

```python
await ctx.guild_data.set(
    guild_id=guild_id,
    key="data",
    value=value,
    module_name=self.name  # Use module name
)
```

### 5. Implement Teardown

If your module creates resources that need cleanup:

```python
async def teardown(self, bot: Any, ctx: Any) -> None:
    # Cancel scheduled tasks
    # Close connections
    # Clean up resources
    pass
```

### 6. Use Framework Utilities

Leverage framework utilities for common tasks:

```python
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.responses import respond_success
from wisp_framework.utils.pagination import paginate_embeds
```

### 7. Log Appropriately

```python
import logging

logger = logging.getLogger(__name__)

async def setup(self, bot: Any, ctx: Any) -> None:
    logger.info(f"Setting up {self.name}")
    # ...
```

### 8. Document Your Module

Add docstrings and comments:

```python
class MyModule(Module):
    """Module description here."""
    
    @property
    def name(self) -> str:
        """Module name."""
        return "my_module"
```

## Testing Modules

### Unit Testing

```python
from wisp_framework.utils.testing import (
    create_mock_interaction,
    create_mock_bot,
    create_mock_context
)

def test_my_module():
    interaction = create_mock_interaction(user_id=123456)
    bot = create_mock_bot()
    ctx = create_mock_context()
    
    module = MyModule()
    # Test module
```

### Integration Testing

Test modules with actual Discord interactions using discord.py's testing utilities.

## Example: Complete Module

```python
from typing import Any
import discord
from wisp_framework.module import Module
from wisp_framework.utils.decorators import require_guild, handle_errors
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.responses import respond_success
from wisp_framework.utils.cooldowns import cooldown

class ExampleModule(Module):
    """Example module demonstrating best practices."""
    
    @property
    def name(self) -> str:
        return "example"
    
    @property
    def default_enabled(self) -> bool:
        return True
    
    @property
    def required_services(self) -> Set[str]:
        return {"cache"}  # Requires cache service
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        
        @tree.command(name="example")
        @require_guild
        @handle_errors
        @cooldown(seconds=5.0)
        async def example(interaction: discord.Interaction):
            # Get cache
            cache = ctx.services.get("cache")
            if cache:
                count = await cache.get("example_count") or 0
                await cache.set("example_count", count + 1)
            
            # Store guild data
            await ctx.guild_data.set(
                guild_id=interaction.guild.id,
                key="last_used",
                value=interaction.created_at.isoformat(),
                module_name=self.name
            )
            
            # Respond
            embed = EmbedBuilder.success(
                title="Example Command",
                description="This is an example!"
            )
            await respond_success(interaction, "Success!", embed=embed)
    
    async def teardown(self, bot: Any, ctx: Any) -> None:
        # Cleanup if needed
        pass
```

## Next Steps

- Review [API Reference](API_REFERENCE.md) for detailed API documentation
- Check [Examples](EXAMPLES.md) for more code samples
- See [Services Documentation](SERVICES.md) for service details
- Read [Architecture Overview](ARCHITECTURE.md) for design context
