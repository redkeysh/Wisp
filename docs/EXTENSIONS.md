# Framework Extensions

This document describes the enhanced utilities and extensions available in the Wisp Framework to make bot development easier.

> **See also:** [[Module-Development]] | [[Examples]] | [[API-Reference]]

## Embed Builders

Create common embed patterns easily:

```python
from wisp_framework.utils.embeds import EmbedBuilder, create_success_embed

# Success embed (green)
embed = EmbedBuilder.success(
    title="Operation Complete",
    description="The task finished successfully",
    fields=[
        {"name": "Status", "value": "✅ Done", "inline": True}
    ]
)

# Error embed (red)
embed = EmbedBuilder.error(
    title="Operation Failed",
    description="Something went wrong"
)

# Info embed (blue)
embed = EmbedBuilder.info(
    title="Information",
    description="Here's some info"
)

# Warning embed (orange)
embed = EmbedBuilder.warning(
    title="Warning",
    description="Be careful!"
)

# List embed with pagination
embed = EmbedBuilder.list_embed(
    title="Items",
    items=["Item 1", "Item 2", "Item 3"],
    page=1,
    items_per_page=10
)

# Table embed
embed = EmbedBuilder.table_embed(
    title="Data Table",
    headers=["Name", "Value"],
    rows=[["Item 1", "100"], ["Item 2", "200"]]
)
```

## Response Helpers

Simplified response sending:

```python
from wisp_framework.utils.responses import (
    respond_success,
    respond_error,
    respond_info,
    respond_embed
)

# Success response
await respond_success(
    interaction,
    "Operation completed!",
    embed=embed,
    ephemeral=True
)

# Error response
await respond_error(
    interaction,
    "Something went wrong",
    ephemeral=True
)

# Info response
await respond_info(
    interaction,
    "Here's some information",
    ephemeral=True
)

# Send embed
await respond_embed(interaction, embed, ephemeral=True)
```

## Pagination

Paginate long lists of items:

```python
from wisp_framework.utils.pagination import paginate_embeds

# Create multiple embeds
embeds = [
    EmbedBuilder.list_embed(title="Page 1", items=items[:10], page=1),
    EmbedBuilder.list_embed(title="Page 2", items=items[10:20], page=2),
]

# Paginate with buttons
await paginate_embeds(interaction, embeds, timeout=300.0, ephemeral=True)
```

## Cooldowns

Add cooldowns to commands:

```python
from wisp_framework.utils.cooldowns import cooldown

@tree.command(name="spam")
@cooldown(seconds=5.0, per_user=True)
async def spam_command(interaction: discord.Interaction):
    await respond_success(interaction, "Command executed!")
```

## Decorators

Useful decorators for commands:

```python
from wisp_framework.utils.decorators import (
    require_guild,
    require_admin,
    require_owner,
    handle_errors
)

@tree.command(name="guild-only")
@require_guild
async def guild_command(interaction: discord.Interaction):
    # Only works in servers
    pass

@tree.command(name="admin-only")
@require_admin
async def admin_command(interaction: discord.Interaction):
    # Requires admin permissions
    pass

@tree.command(name="owner-only")
@require_owner(config)  # Pass config
async def owner_command(interaction: discord.Interaction):
    # Only bot owner
    pass

@tree.command(name="safe")
@handle_errors
async def safe_command(interaction: discord.Interaction):
    # Errors are caught and displayed to user
    raise ValueError("This will be caught!")
```

## Confirmations

Confirmation dialogs for destructive actions:

```python
from wisp_framework.utils.confirmations import confirm_action

async def delete_handler(interaction: discord.Interaction):
    # Handle deletion
    await respond_success(interaction, "Deleted!")

await confirm_action(
    interaction,
    "Are you sure you want to delete this?",
    on_confirm=delete_handler,
    timeout=60.0
)
```

## Command Groups

Organize commands into groups:

```python
from wisp_framework.utils.command_groups import CommandGroup

# Create group
admin_group = CommandGroup("admin", "Admin commands", guild_only=True)
admin_group.create_group(bot.tree)

# Add commands to group
@admin_group.command(name="kick", description="Kick a user")
async def kick_command(interaction: discord.Interaction, user: discord.Member):
    await respond_success(interaction, f"Kicked {user.mention}")
```

## Views and Buttons

Create interactive UI components:

```python
from wisp_framework.utils.views import ButtonView

view = ButtonView(timeout=300.0)

view.add_button(
    label="Click Me",
    style=discord.ButtonStyle.primary,
    callback=lambda i: respond_success(i, "Button clicked!")
)

await interaction.response.send_message("Choose an option:", view=view)
```

## Middleware

Add middleware for cross-cutting concerns:

```python
from wisp_framework.utils.middleware import (
    MiddlewareChain,
    LoggingMiddleware,
    MetricsMiddleware
)

# Create middleware chain
chain = MiddlewareChain(
    LoggingMiddleware(),
    MetricsMiddleware(metrics_service)
)

# Use in command
@tree.command(name="test")
async def test_command(interaction: discord.Interaction):
    await chain.execute(interaction, my_handler)
```

## Testing Utilities

Mock objects for testing:

```python
from wisp_framework.utils.testing import (
    create_mock_interaction,
    create_mock_bot,
    create_mock_context
)

# Create mocks
interaction = create_mock_interaction(user_id=123456)
bot = create_mock_bot()
ctx = create_mock_context()

# Use in tests
await my_module.setup(bot, ctx)
```

## CLI Tools

Generate templates:

```bash
# Create a module template
wisp-framework-cli create-module my_module --output-dir modules/

# Create a bot template
wisp-framework-cli create-bot my_bot --output-dir .
```

## Best Practices

1. **Use embed builders** for consistent styling
2. **Use response helpers** for consistent responses
3. **Add cooldowns** to prevent spam
4. **Use decorators** for common checks
5. **Use pagination** for long lists
6. **Use confirmations** for destructive actions
7. **Use middleware** for logging/metrics
8. **Use command groups** to organize commands

## Example: Complete Enhanced Module

```python
from typing import Any
import discord
from wisp_framework.module import Module
from wisp_framework.utils.decorators import require_guild, handle_errors
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.responses import respond_success
from wisp_framework.utils.cooldowns import cooldown

class MyModule(Module):
    @property
    def name(self) -> str:
        return "my_module"
    
    async def setup(self, bot: Any, ctx: Any) -> None:
        @bot.tree.command(name="example")
        @require_guild
        @handle_errors
        @cooldown(seconds=5.0)
        async def example(interaction: discord.Interaction):
            embed = EmbedBuilder.success(
                title="Success",
                description="Command executed!"
            )
            await respond_success(interaction, "Done!", embed=embed)
```
