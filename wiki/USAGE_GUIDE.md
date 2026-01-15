# Usage Guide

This guide shows you how to use the Wisp Framework to build your own bots.

> **See also:** [[Installation-Guide]] | [[Module-Development]] | [[Examples]] | [[API-Reference]]

## Installation

```bash
# Basic installation
pip install wisp-framework

# With database support
pip install wisp-framework[db]

# With all extras
pip install wisp-framework[all]
```

## Quick Start: Creating Your Own Bot

### Importing the Framework

The Wisp Framework provides several ways to create a bot:

**Option 1: Using `create_app()` (Recommended)**
```python
from wisp_framework import create_app

bot, lifecycle, ctx = create_app()
```

**Option 2: Using `WispBot` directly**
```python
from wisp_framework import WispBot
from wisp_framework.config import AppConfig
# ... other imports
```

**Important:** There is no `Wisp` class. Use `WispBot` (the main bot class) or `create_app()` (convenience function) instead.

### 1. Create a Simple Bot

Create a file `my_bot.py`:

```python
import asyncio
import logging
from wisp_framework.config import AppConfig
from wisp_framework.context import BotContext
from wisp_framework.feature_flags import FeatureFlags
from wisp_framework.lifecycle import (
    LifecycleManager,
    create_bot_context,
    create_feature_flags,
    create_services,
)
from wisp_framework.logging import setup_logging
from wisp_framework.registry import ModuleRegistry

# Set up logging
logging.basicConfig(level=logging.INFO)

def main():
    # Load configuration
    config = AppConfig()
    setup_logging(config)
    
    # Create services
    services = create_services(config)
    
    # Create feature flags
    feature_flags = create_feature_flags(services)
    
    # Create module registry
    module_registry = ModuleRegistry(feature_flags)
    
    # Register your modules here
    # module_registry.register(MyCustomModule())
    
    # Create bot context
    ctx = create_bot_context(config, services)
    
    # Create lifecycle manager
    lifecycle = LifecycleManager()
    
    # Start bot
    async def run():
        bot = await lifecycle.startup(config, services, module_registry, ctx)
        await bot.start(config.discord_token)
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        asyncio.run(lifecycle.shutdown())

if __name__ == "__main__":
    main()
```

### 2. Create a Custom Module

Create `my_module.py`:

```python
from typing import Any
import discord
from discord import app_commands
from wisp_framework.module import Module

class MyCustomModule(Module):
    @property
    def name(self) -> str:
        return "my_custom_module"
    
    @property
    def default_enabled(self) -> bool:
        return True
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        
        @tree.command(name="hello", description="Say hello")
        async def hello(interaction: discord.Interaction):
            await interaction.response.send_message("Hello from my custom module!")
        
        @tree.command(name="echo", description="Echo a message")
        @app_commands.describe(message="The message to echo")
        async def echo(interaction: discord.Interaction, message: str):
            await interaction.response.send_message(f"You said: {message}")
    
    async def teardown(self, bot: Any, ctx: Any) -> None:
        # Cleanup code here if needed
        pass
```

Then register it in your bot:

```python
from my_module import MyCustomModule

module_registry.register(MyCustomModule())
```

## Using Framework Services

### Accessing Services in Modules

```python
from typing import Any
import discord
from wisp_framework.module import Module

class ServiceExampleModule(Module):
    @property
    def name(self) -> str:
        return "service_example"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        
        @tree.command(name="cache-test", description="Test cache service")
        async def cache_test(interaction: discord.Interaction):
            # Get cache service
            cache = ctx.services.get("cache")
            
            # Store a value
            await cache.set("test_key", "test_value", ttl=60)
            
            # Retrieve it
            value = await cache.get("test_key")
            
            await interaction.response.send_message(f"Cached value: {value}")
        
        @tree.command(name="metrics-test", description="Test metrics service")
        async def metrics_test(interaction: discord.Interaction):
            # Get metrics service
            metrics = ctx.services.get("metrics")
            
            # Increment a counter
            metrics.increment("commands.test")
            
            # Record a timing
            import time
            start = time.time()
            # ... do some work ...
            duration = time.time() - start
            metrics.timing("commands.test.duration", duration)
            
            await interaction.response.send_message("Metrics recorded!")
```

### Using Per-Guild Data Storage

```python
from typing import Any
import discord
from wisp_framework.module import Module

class DataStorageModule(Module):
    @property
    def name(self) -> str:
        return "data_storage"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        
        @tree.command(name="set-data", description="Set guild data")
        @app_commands.describe(key="Data key", value="Data value")
        async def set_data(
            interaction: discord.Interaction,
            key: str,
            value: str
        ):
            if not interaction.guild:
                await interaction.response.send_message(
                    "This command only works in servers.", ephemeral=True
                )
                return
            
            # Store data per guild
            await ctx.guild_data.set(
                guild_id=interaction.guild.id,
                key=key,
                value=value,
                module_name="data_storage"  # Optional namespace
            )
            
            await interaction.response.send_message(
                f"Set {key} = {value} for this server", ephemeral=True
            )
        
        @tree.command(name="get-data", description="Get guild data")
        @app_commands.describe(key="Data key")
        async def get_data(interaction: discord.Interaction, key: str):
            if not interaction.guild:
                await interaction.response.send_message(
                    "This command only works in servers.", ephemeral=True
                )
                return
            
            # Retrieve data
            value = await ctx.guild_data.get(
                guild_id=interaction.guild.id,
                key=key,
                module_name="data_storage"
            )
            
            if value is None:
                await interaction.response.send_message(
                    f"No data found for key: {key}", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"{key} = {value}", ephemeral=True
                )
```

### Using the Database

> **⚠️ SECURITY WARNING**: Before using the database, ensure you have changed all default passwords from the repository's `docker-compose.yml` files. Never use default passwords in production!

```python
from typing import Any
import discord
from sqlalchemy import select
from wisp_framework.module import Module
from wisp_framework.db.models import GuildConfig

class DatabaseModule(Module):
    @property
    def name(self) -> str:
        return "database_example"
    
    @property
    def required_services(self) -> set[str]:
        return {"db"}
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        
        @tree.command(name="set-welcome", description="Set welcome channel")
        @app_commands.describe(channel="Welcome channel")
        async def set_welcome(
            interaction: discord.Interaction,
            channel: discord.TextChannel
        ):
            if not interaction.guild:
                await interaction.response.send_message(
                    "This command only works in servers.", ephemeral=True
                )
                return
            
            # Get database service
            db_service = ctx.services.get("db")
            if not db_service or not db_service.session_factory:
                await interaction.response.send_message(
                    "Database not available.", ephemeral=True
                )
                return
            
            # Update guild config
            async with db_service.session_factory() as session:
                stmt = select(GuildConfig).where(
                    GuildConfig.guild_id == interaction.guild.id
                )
                result = await session.execute(stmt)
                guild_config = result.scalar_one_or_none()
                
                if guild_config:
                    guild_config.welcome_channel_id = channel.id
                else:
                    guild_config = GuildConfig(
                        guild_id=interaction.guild.id,
                        welcome_channel_id=channel.id
                    )
                    session.add(guild_config)
                
                await session.commit()
            
            await interaction.response.send_message(
                f"Welcome channel set to {channel.mention}", ephemeral=True
            )
```

### Using the Scheduler

```python
from typing import Any
from wisp_framework.module import Module

class ScheduledTaskModule(Module):
    @property
    def name(self) -> str:
        return "scheduled_tasks"
    
    @property
    def required_services(self) -> set[str]:
        return {"scheduler"}
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        scheduler = ctx.services.get("scheduler")
        
        async def daily_task():
            """Run every 24 hours"""
            # Your periodic task logic here
            print("Running daily task...")
            # Example: update stats, send reports, etc.
        
        # Register periodic task (runs every 86400 seconds = 24 hours)
        if scheduler:
            scheduler.register(daily_task, interval=86400.0, name="daily_task")
```

## Advanced Patterns

### Module Dependencies

```python
class DependentModule(Module):
    @property
    def name(self) -> str:
        return "dependent_module"
    
    @property
    def depends_on(self) -> list[str]:
        return ["base_module"]  # Requires base_module to be loaded first
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        # This module will be loaded after base_module
        pass
```

### Event Listeners

```python
class EventModule(Module):
    @property
    def name(self) -> str:
        return "events"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        @bot.event
        async def on_member_join(member: discord.Member):
            # Handle member join
            if member.guild:
                channel = member.guild.system_channel
                if channel:
                    await channel.send(f"Welcome {member.mention}!")
        
        @bot.event
        async def on_message(message: discord.Message):
            # Handle messages
            if message.author.bot:
                return
            # Your logic here
```

### Using Audit Service

```python
class AuditModule(Module):
    @property
    def name(self) -> str:
        return "audit_example"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        audit = ctx.services.get("audit")
        
        @tree.command(name="admin-action", description="Admin action")
        async def admin_action(interaction: discord.Interaction):
            # Log the action
            if audit:
                audit.log_action(
                    action="admin_action_executed",
                    user_id=interaction.user.id,
                    guild_id=interaction.guild_id,
                    channel_id=interaction.channel_id if interaction.channel else None,
                    metadata={"command": "admin_action"}
                )
            
            await interaction.response.send_message("Action logged!")
```

## Project Structure

A typical bot project structure:

```
my_bot/
├── my_bot.py              # Main entry point
├── modules/               # Your custom modules
│   ├── __init__.py
│   ├── my_module.py
│   └── another_module.py
├── .env.local            # Environment variables
└── requirements.txt      # Dependencies
```

## Complete Example

Here's a complete example of a custom bot:

```python
# my_bot.py
import asyncio
import logging
from wisp_framework.config import AppConfig
from wisp_framework.lifecycle import (
    LifecycleManager,
    create_bot_context,
    create_feature_flags,
    create_services,
)
from wisp_framework.logging import setup_logging
from wisp_framework.registry import ModuleRegistry

# Import your modules
from modules.my_module import MyCustomModule
from modules.data_storage import DataStorageModule

logging.basicConfig(level=logging.INFO)

def main():
    config = AppConfig()
    setup_logging(config)
    
    services = create_services(config)
    feature_flags = create_feature_flags(services)
    module_registry = ModuleRegistry(feature_flags)
    
    # Register your modules
    module_registry.register(MyCustomModule())
    module_registry.register(DataStorageModule())
    
    ctx = create_bot_context(config, services)
    lifecycle = LifecycleManager()
    
    async def run():
        bot = await lifecycle.startup(config, services, module_registry, ctx)
        await bot.start(config.discord_token)
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        asyncio.run(lifecycle.shutdown())

if __name__ == "__main__":
    main()
```

## Tips

1. **Use type hints**: The framework is fully typed, use type hints in your modules
2. **Handle errors**: Always handle potential errors in your modules
3. **Use ephemeral responses**: For admin commands, use `ephemeral=True`
4. **Check permissions**: Use `is_owner()` and `is_admin()` helpers
5. **Namespace your data**: Use `module_name` parameter in `guild_data` calls
6. **Clean up resources**: Implement `teardown()` if your module needs cleanup

## Next Steps

- Read the [[Module-Development]] guide for best practices
- Check the [[Deployment-Guide]] for production deployment
- Review the framework source code for more examples
