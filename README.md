# Wisp Framework

[![GitHub release](https://img.shields.io/github/v/release/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/releases)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/network)
[![GitHub issues](https://img.shields.io/github/issues/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/commits/main)

A production-grade, modular Discord bot framework built with Python 3.13+ and discord.py. This framework provides a clean architecture for building Discord bots with optional database support, per-guild module management, and a comprehensive service system.

## Features

- **Modular Architecture**: Easy-to-create modules with per-guild enable/disable support
- **Optional Database**: SQLAlchemy 2.x async support with graceful degradation
- **Service Container**: Built-in services (cache, metrics, scheduler, audit, webhook logger)
- **Per-Guild Data Storage**: Automatic support for storing stats/data per guild
- **Production Ready**: Docker support, health checks, graceful shutdown, connection pooling
- **Type Hints**: Full type hints throughout for better IDE support
- **Extensible**: Clean interfaces for extending without forking

## Quickstart

### Installation

#### From GitHub (Recommended)

Install directly from GitHub:

```bash
# Basic installation
pip install git+https://github.com/redkeysh/wisp.git

# With database support
pip install git+https://github.com/redkeysh/wisp.git[db]

# With all extras
pip install git+https://github.com/redkeysh/wisp.git[all]

# Pin to specific version
pip install git+https://github.com/redkeysh/wisp.git@v1.0.0
```

#### From PyPI (If Published)

```bash
# Basic installation
pip install wisp-framework

# With database support
pip install wisp-framework[db]

# With all extras
pip install wisp-framework[all]
```

#### Local Development

```bash
# Clone and install in editable mode
git clone https://github.com/redkeysh/wisp.git
cd wisp
pip install -e ".[db,redis,all]"
```

See [Installation Guide](docs/INSTALLATION.md) and [GitHub Setup Guide](docs/GITHUB_SETUP.md) for more details.

### Basic Usage

1. **Set up environment variables:**

```bash
cp .env.local.example .env.local
# Edit .env.local and set DISCORD_TOKEN
```

2. **Run the bot:**

```bash
wisp-framework-runner
```

Or use the development script:

```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

### Docker Quickstart

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## Configuration

### Environment Variables

The framework uses environment variables for configuration. Create `.env.local` for development or `.env.prod` for production.

**Required:**
- `DISCORD_TOKEN`: Your Discord bot token

**Optional:**
- `DATABASE_URL`: PostgreSQL connection URL (requires `[db]` extra)
- `REDIS_URL`: Redis connection URL (requires `[redis]` extra)
- `LOG_LEVEL`: Logging level (default: INFO)
- `SYNC_ON_STARTUP`: Whether to sync commands on startup (default: true)
- `OWNER_ID`: Bot owner Discord user ID
- `WELCOME_CHANNEL_ID`: Default welcome channel ID

See `.env.local.example` for all available options.

### Intent Configuration

Configure Discord intents via environment variables:

```bash
INTENTS_GUILDS=true
INTENTS_MEMBERS=true
INTENTS_MESSAGES=true
INTENTS_MESSAGE_CONTENT=true
# ... etc
```

Defaults to all intents enabled if not specified.

## Module System

### Creating a Module

Create a new module by extending the `Module` base class:

```python
from wisp_framework.module import Module
from discord import app_commands
import discord

class MyModule(Module):
    @property
    def name(self) -> str:
        return "my_module"
    
    @property
    def default_enabled(self) -> bool:
        return True
    
    async def setup(self, bot, ctx):
        tree = bot.tree
        
        @tree.command(name="hello", description="Say hello")
        async def hello(interaction: discord.Interaction):
            await interaction.response.send_message("Hello!")
```

### Registering Modules

In your runner bot:

```python
from wisp_framework.registry import ModuleRegistry

module_registry = ModuleRegistry(feature_flags)
module_registry.register(MyModule())

# Or auto-discover modules
module_registry.discover_modules("my_package.modules")
```

### Enabling/Disabling Modules

Modules can be enabled or disabled per guild:

- Use `/modules list` to see all modules
- Use `/modules enable <module>` to enable a module
- Use `/modules disable <module>` to disable a module

Requires admin permissions or bot owner.

## Per-Guild Data Storage

The framework automatically provides per-guild data storage:

```python
# In your module setup
async def setup(self, bot, ctx):
    # Store data
    await ctx.guild_data.set(
        guild_id=interaction.guild_id,
        key="command_count",
        value=42,
        module_name="my_module"  # Optional namespace
    )
    
    # Retrieve data
    count = await ctx.guild_data.get(
        guild_id=interaction.guild_id,
        key="command_count",
        module_name="my_module"
    )
```

Data is automatically persisted to the database if available, otherwise stored in memory.

## Database Support

### Setup

1. Install with database extra:
```bash
pip install wisp-framework[db]
```

2. Set `DATABASE_URL` in your environment:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/discord_bot
```

> **⚠️ SECURITY WARNING**: The default passwords in `docker-compose.yml` are for development only. **You MUST change all database passwords** before deploying to production. Never use default passwords in production environments!

3. Run migrations:
```bash
alembic upgrade head
```

### Models

The framework provides three base models:

- `GuildConfig`: Per-guild configuration
- `ModuleState`: Module enable/disable state per guild
- `GuildData`: Generic key-value storage for per-guild data

### Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
alembic upgrade head
```

## Services

### Available Services

- **HealthService**: Health checks for all services
- **CacheService**: In-memory or Redis-backed caching
- **MetricsService**: Counter and timing metrics
- **SchedulerService**: Periodic task scheduling
- **AuditService**: Audit logging with Discord object serialization
- **WebhookLoggerService**: Rate-limited webhook logging
- **DatabaseService**: Async SQLAlchemy engine and sessions

### Using Services

```python
async def setup(self, bot, ctx):
    # Get a service
    cache = ctx.services.get("cache")
    await cache.set("key", "value", ttl=3600)
    
    # Get typed service
    from wisp_framework.services.db import DatabaseService
    db = ctx.services.get_typed("db", DatabaseService)
    if db:
        session = db.get_session()
```

## Deployment

### Docker Deployment

> **⚠️ SECURITY WARNING**: The default database passwords in `docker-compose.yml` are for development only. **You MUST change all database passwords** before deploying to production. Set strong, unique passwords via environment variables in `.env.prod` and never commit passwords to version control!

**Development:**
```bash
docker-compose up -d
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

The production compose file includes:
- Security hardening (non-root user, read-only filesystem)
- Resource limits
- Health checks
- Migration service that runs before the bot

### Manual Deployment

1. Install dependencies:
```bash
pip install wisp-framework[all]
```

2. Set up environment:
```bash
cp .env.prod.example .env.prod
# Edit .env.prod and set strong, unique database passwords
# ⚠️ Never use default passwords from docker-compose.yml in production!
```

3. Run migrations (if using database):
```bash
alembic upgrade head
```

4. Run the bot:
```bash
wisp-framework-runner
```

Or use the production script:
```bash
./scripts/prod.sh
```

## Discord Setup

### Required Intents

Depending on your bot's functionality, you may need to enable specific intents in the Discord Developer Portal:

- **Guilds**: Required for most bots
- **Members**: Required for member join events
- **Messages**: Required for message events
- **Message Content**: Required to read message content
- **Reactions**: Required for reaction events
- **Voice States**: Required for voice channel events

### Bot Permissions

Ensure your bot has the necessary permissions:
- Send Messages
- Embed Links
- Use Slash Commands
- Read Message History

### Command Sync

Commands are synced automatically on startup by default. To disable:

```bash
SYNC_ON_STARTUP=false
```

Manually sync commands using `/sync` (owner only).

## Common Pitfalls

### Commands Not Appearing

1. **Check intents**: Ensure required intents are enabled in Discord Developer Portal
2. **Check permissions**: Bot needs "Use Slash Commands" permission
3. **Wait for sync**: Commands can take up to an hour to appear globally
4. **Use `/sync`**: Manually sync commands if needed (owner only)

### Database Connection Issues

1. **Check DATABASE_URL**: Ensure it's correctly formatted
2. **Check migrations**: Run `alembic upgrade head`
3. **Check pool settings**: Adjust `DB_POOL_SIZE` if needed
4. **Check network**: Ensure database is accessible

### Module Not Loading

1. **Check dependencies**: Ensure required services are available
2. **Check feature flags**: Module may be disabled for the guild
3. **Check logs**: Look for error messages in the logs
4. **Check registration**: Ensure module is registered in the registry

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Linting

```bash
ruff check src/
```

### Pre-flight Checks

Run the doctor tool before deployment:

```bash
python scripts/doctor.py
```

## Project Structure

```
.
├── src/
│   ├── wisp_framework/     # Core framework
│   │   ├── modules/           # Prebuilt modules
│   │   ├── services/          # Service implementations
│   │   ├── db/                # Database models and migrations
│   │   └── utils/             # Utility functions
│   └── runner_bot/            # Runner bot application
├── scripts/                   # Utility scripts
├── docker-compose.yml         # Development Docker setup
├── docker-compose.prod.yml    # Production Docker setup
└── alembic.ini                # Alembic configuration
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please ensure:
- Code follows the existing style
- Tests are added for new features
- Documentation is updated
- Type hints are included

## Documentation

Complete developer documentation is available in the `docs/` directory:

- **[Documentation Index](docs/INDEX.md)** - Start here for complete documentation
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Architecture Overview](docs/ARCHITECTURE.md)** - Framework architecture and design
- **[Module Development Guide](docs/MODULE_DEVELOPMENT.md)** - Creating and developing modules
- **[Services Documentation](docs/SERVICES.md)** - Available services and usage
- **[Configuration Reference](docs/CONFIGURATION.md)** - Complete configuration options
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Examples](docs/EXAMPLES.md)** - Code examples and tutorials
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute

## Usage Examples

See the [Usage Guide](docs/USAGE_GUIDE.md) for detailed examples and [Extensions Guide](docs/EXTENSIONS.md) for enhanced utilities.

### Quick Example with Extensions

```python
from wisp_framework.module import Module
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.responses import respond_success
from wisp_framework.utils.decorators import require_guild, handle_errors
import discord

class MyModule(Module):
    @property
    def name(self) -> str:
        return "my_module"
    
    async def setup(self, bot, ctx):
        @bot.tree.command(name="hello")
        @require_guild
        @handle_errors
        async def hello(interaction: discord.Interaction):
            embed = EmbedBuilder.success(title="Hello!", description="Welcome!")
            await respond_success(interaction, "Greetings!", embed=embed)
```

### Framework Extensions

The framework includes powerful extensions to make development easier:

- **Embed Builders**: Success, error, info, warning embeds
- **Response Helpers**: Simplified response sending
- **Pagination**: Paginated lists with buttons
- **Cooldowns**: Per-user command cooldowns
- **Decorators**: `@require_guild`, `@require_admin`, `@handle_errors`
- **Confirmations**: Confirmation dialogs for destructive actions
- **Command Groups**: Organize commands into groups
- **Views**: Button and select menu helpers
- **Middleware**: Cross-cutting concerns (logging, metrics)
- **Testing**: Mock objects for testing
- **CLI Tools**: Generate module and bot templates

See [Extensions Guide](docs/EXTENSIONS.md) for full documentation.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the [Usage Guide](docs/USAGE_GUIDE.md)
- Review common pitfalls section
