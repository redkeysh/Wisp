# Examples and Tutorials

Complete examples and tutorials for using the Wisp Framework.

> **See also:** [[Module-Development]] | [[API-Reference]] | [[Framework-Extensions]]

## Table of Contents

- [Basic Bot](#basic-bot)
- [Custom Module](#custom-module)
- [Using Services](#using-services)
- [Database Integration](#database-integration)
- [Event Handling](#event-handling)
- [Advanced Patterns](#advanced-patterns)

## Basic Bot

### Minimal Bot

```python
import asyncio
from wisp_framework import create_app

async def main():
    bot, lifecycle, ctx = create_app()
    await bot.start(bot.config.discord_token)

if __name__ == "__main__":
    asyncio.run(main())
```

### Bot with Custom Modules

```python
import asyncio
from wisp_framework import create_app, ModuleRegistry
from wisp_framework.module import Module
import discord

class MyModule(Module):
    @property
    def name(self) -> str:
        return "my_module"
    
    async def setup(self, bot, ctx):
        @bot.tree.command(name="hello")
        async def hello(interaction: discord.Interaction):
            await interaction.response.send_message("Hello!")

async def main():
    bot, lifecycle, ctx = create_app()
    
    # Register custom module
    bot.module_registry.register(MyModule())
    
    # Load modules
    await bot.module_registry.load_enabled_modules(bot, ctx)
    
    await bot.start(bot.config.discord_token)

if __name__ == "__main__":
    asyncio.run(main())
```

## Custom Module

### Simple Command Module

```python
from typing import Any
import discord
from wisp_framework.module import Module
from wisp_framework.utils.decorators import require_guild, handle_errors
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.responses import respond_success

class GreetingModule(Module):
    @property
    def name(self) -> str:
        return "greeting"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        
        @tree.command(name="greet", description="Greet a user")
        @require_guild
        @handle_errors
        @app_commands.describe(user="User to greet")
        async def greet(interaction: discord.Interaction, user: discord.Member):
            embed = EmbedBuilder.success(
                title="Greeting",
                description=f"Hello, {user.mention}!"
            )
            await respond_success(interaction, f"Greeted {user.name}", embed=embed)
```

### Module with Data Storage

```python
from typing import Any
import discord
from wisp_framework.module import Module

class CounterModule(Module):
    @property
    def name(self) -> str:
        return "counter"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        
        @tree.command(name="count", description="Increment counter")
        @require_guild
        async def count(interaction: discord.Interaction):
            # Get current count
            count = await ctx.guild_data.get(
                guild_id=interaction.guild.id,
                key="count",
                module_name=self.name
            ) or 0
            
            # Increment
            count += 1
            
            # Store
            await ctx.guild_data.set(
                guild_id=interaction.guild.id,
                key="count",
                value=count,
                module_name=self.name
            )
            
            await interaction.response.send_message(f"Count: {count}")
```

## Using Services

### Cache Service

```python
from typing import Any
import discord
from wisp_framework.module import Module

class CacheExampleModule(Module):
    @property
    def name(self) -> str:
        return "cache_example"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        cache = ctx.services.get("cache")
        
        @tree.command(name="cache-test")
        async def cache_test(interaction: discord.Interaction):
            if not cache:
                await interaction.response.send_message("Cache not available")
                return
            
            # Set value
            await cache.set("test_key", "test_value", ttl=60)
            
            # Get value
            value = await cache.get("test_key")
            
            await interaction.response.send_message(f"Cached: {value}")
```

### Scheduler Service

```python
from typing import Any
from wisp_framework.module import Module

class ScheduledModule(Module):
    @property
    def name(self) -> str:
        return "scheduled"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        scheduler = ctx.services.get("scheduler")
        
        async def daily_task():
            # Your periodic task
            print("Running daily task...")
        
        if scheduler:
            scheduler.register(daily_task, interval=86400.0, name="daily")
```

### Metrics Service

```python
from typing import Any
import discord
import time
from wisp_framework.module import Module

class MetricsModule(Module):
    @property
    def name(self) -> str:
        return "metrics"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        metrics = ctx.services.get("metrics")
        
        @tree.command(name="tracked")
        async def tracked(interaction: discord.Interaction):
            if metrics:
                start = time.time()
                # Do work
                duration = time.time() - start
                
                metrics.increment("commands.executed")
                metrics.timing("command.duration", duration)
            
            await interaction.response.send_message("Command executed and tracked")
```

## Database Integration

### Using Database Models

```python
from typing import Any
import discord
from sqlalchemy import select
from wisp_framework.module import Module
from wisp_framework.db.models import GuildConfig
from wisp_framework.services.db import DatabaseService

class DatabaseModule(Module):
    @property
    def name(self) -> str:
        return "database"
    
    @property
    def required_services(self) -> set[str]:
        return {"db"}
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        db = ctx.services.get_typed("db", DatabaseService)
        
        @tree.command(name="set-welcome")
        @app_commands.describe(channel="Welcome channel")
        async def set_welcome(
            interaction: discord.Interaction,
            channel: discord.TextChannel
        ):
            if not db or not db.session_factory:
                await interaction.response.send_message("Database not available")
                return
            
            async with db.session_factory() as session:
                stmt = select(GuildConfig).where(
                    GuildConfig.guild_id == interaction.guild.id
                )
                result = await session.execute(stmt)
                config = result.scalar_one_or_none()
                
                if config:
                    config.welcome_channel_id = channel.id
                else:
                    config = GuildConfig(
                        guild_id=interaction.guild.id,
                        welcome_channel_id=channel.id
                    )
                    session.add(config)
                
                await session.commit()
            
            await interaction.response.send_message(f"Welcome channel set to {channel.mention}")
```

## Event Handling

### Member Join Event

```python
from typing import Any
import discord
from wisp_framework.module import Module
from wisp_framework.utils.embeds import EmbedBuilder

class WelcomeModule(Module):
    @property
    def name(self) -> str:
        return "welcome"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        @bot.event
        async def on_member_join(member: discord.Member):
            if not member.guild:
                return
            
            # Get welcome channel from config
            welcome_channel_id = await ctx.guild_data.get(
                guild_id=member.guild.id,
                key="welcome_channel_id",
                module_name=self.name
            )
            
            if welcome_channel_id:
                channel = member.guild.get_channel(welcome_channel_id)
                if channel:
                    embed = EmbedBuilder.success(
                        title="Welcome!",
                        description=f"Welcome to {member.guild.name}, {member.mention}!",
                        thumbnail=member.display_avatar.url if member.display_avatar else None
                    )
                    await channel.send(embed=embed)
```

## Advanced Patterns

### Module with Dependencies

```python
from typing import Any
from wisp_framework.module import Module

class DependentModule(Module):
    @property
    def name(self) -> str:
        return "dependent"
    
    @property
    def depends_on(self) -> list[str]:
        return ["base_module"]
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        # This module loads after base_module
        base_module = ctx.module_registry.get_module("base_module")
        # Use base_module functionality
        pass
```

### Paginated List

```python
from typing import Any
import discord
from wisp_framework.module import Module
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.pagination import paginate_embeds

class ListModule(Module):
    @property
    def name(self) -> str:
        return "list"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        
        @tree.command(name="list-items")
        async def list_items(interaction: discord.Interaction):
            items = ["Item 1", "Item 2", "Item 3", ...]  # Your items
            
            # Create pages
            embeds = []
            items_per_page = 10
            for i in range(0, len(items), items_per_page):
                page_items = items[i:i+items_per_page]
                embed = EmbedBuilder.list_embed(
                    title="Items",
                    items=page_items,
                    page=(i//items_per_page)+1,
                    items_per_page=items_per_page
                )
                embeds.append(embed)
            
            await paginate_embeds(interaction, embeds)
```

### Confirmation Dialog

```python
from typing import Any
import discord
from wisp_framework.module import Module
from wisp_framework.utils.confirmations import confirm_action
from wisp_framework.utils.responses import respond_success

class DeleteModule(Module):
    @property
    def name(self) -> str:
        return "delete"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        tree = bot.tree
        
        async def delete_handler(interaction: discord.Interaction):
            # Perform deletion
            await respond_success(interaction, "Deleted!")
        
        @tree.command(name="delete")
        async def delete(interaction: discord.Interaction):
            await confirm_action(
                interaction,
                "⚠️ Are you sure you want to delete this?",
                on_confirm=delete_handler
            )
```

## Next Steps

- See [[Module-Development]] for more examples
- Check [[API-Reference]] for API details
- Review [[Framework-Extensions]] for utility examples
