# Framework Extensions Guide

This guide covers all the extensions and utilities available to make bot development easier.

## Quick Reference

### Embed Builders
- `EmbedBuilder.success()` - Green success embeds
- `EmbedBuilder.error()` - Red error embeds  
- `EmbedBuilder.info()` - Blue info embeds
- `EmbedBuilder.warning()` - Orange warning embeds
- `EmbedBuilder.list_embed()` - Paginated list embeds
- `EmbedBuilder.table_embed()` - Table-style embeds

### Response Helpers
- `respond_success()` - Send success message
- `respond_error()` - Send error message
- `respond_info()` - Send info message
- `respond_embed()` - Send embed

### Decorators
- `@require_guild` - Require server context
- `@require_admin` - Require admin permissions
- `@require_owner(config)` - Require bot owner
- `@handle_errors` - Auto error handling
- `@cooldown(seconds)` - Add cooldown

### Utilities
- `paginate_embeds()` - Paginate long lists
- `confirm_action()` - Confirmation dialogs
- `CommandGroup` - Organize commands
- `ButtonView` / `SelectMenuView` - UI components
- `MiddlewareChain` - Cross-cutting concerns

## Common Patterns

### Pattern 1: Simple Command with Success Response

```python
@tree.command(name="do-something")
@require_guild
async def do_something(interaction: discord.Interaction):
    # Do work
    embed = EmbedBuilder.success(title="Done", description="Task completed")
    await respond_success(interaction, "Success!", embed=embed)
```

### Pattern 2: Command with Cooldown

```python
@tree.command(name="spam-protected")
@cooldown(seconds=10.0)
async def spam_protected(interaction: discord.Interaction):
    await respond_success(interaction, "Command executed!")
```

### Pattern 3: Paginated List

```python
@tree.command(name="list")
async def list_items(interaction: discord.Interaction):
    items = ["Item 1", "Item 2", ...]  # Your items
    
    # Create pages
    embeds = []
    for i in range(0, len(items), 10):
        embed = EmbedBuilder.list_embed(
            title="Items",
            items=items,
            page=(i//10)+1,
            items_per_page=10
        )
        embeds.append(embed)
    
    await paginate_embeds(interaction, embeds)
```

### Pattern 4: Confirmation Dialog

```python
async def delete_handler(interaction: discord.Interaction):
    # Perform deletion
    await respond_success(interaction, "Deleted!")

@tree.command(name="delete")
@require_admin
async def delete(interaction: discord.Interaction):
    await confirm_action(
        interaction,
        "⚠️ Are you sure you want to delete this?",
        on_confirm=delete_handler
    )
```

### Pattern 5: Command Group

```python
# Create group
mod_group = CommandGroup("mod", "Moderation commands")
mod_group.create_group(bot.tree)

# Add commands
@mod_group.command(name="kick")
async def kick(interaction: discord.Interaction, user: discord.Member):
    await respond_success(interaction, f"Kicked {user.mention}")
```

## Making Multi-Bot Development Easier

### 1. Shared Module Library

Create a shared package with common modules:

```
shared_modules/
├── moderation.py
├── fun.py
├── utility.py
└── __init__.py
```

Then import in each bot:

```python
from shared_modules.moderation import ModerationModule
module_registry.register(ModerationModule())
```

### 2. Configuration Presets

Create preset configurations:

```python
# configs/preset.py
def get_production_config():
    config = AppConfig()
    # Set production defaults
    return config
```

### 3. Base Bot Class

Create a base bot class:

```python
# base_bot.py
class BaseBot:
    def __init__(self, config: AppConfig):
        self.config = config
        self.services = create_services(config)
        # Common setup
    
    def register_common_modules(self, registry: ModuleRegistry):
        # Register modules all bots need
        pass
```

### 4. Template System

Use the CLI to generate templates:

```bash
wisp-framework-cli create-module moderation
wisp-framework-cli create-bot my_bot
```

## Advanced Features

### Custom Middleware

```python
class CustomMiddleware(Middleware):
    async def process(self, interaction, next_handler):
        # Pre-processing
        result = await next_handler(interaction)
        # Post-processing
        return result
```

### Custom Embed Styles

```python
class CustomEmbedBuilder(EmbedBuilder):
    @staticmethod
    def custom(title: str, description: str) -> discord.Embed:
        embed = discord.Embed(title=title, description=description)
        embed.color = discord.Color.purple()
        return embed
```

## Tips for Multi-Bot Development

1. **Shared Utilities**: Put common utilities in a shared package
2. **Module Library**: Create a library of reusable modules
3. **Configuration Management**: Use environment-based configs
4. **Template Generation**: Use CLI tools to scaffold new bots
5. **Testing Utilities**: Use mock objects for testing
6. **Documentation**: Document shared modules well
7. **Version Management**: Version your shared modules
