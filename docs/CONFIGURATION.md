# Configuration Reference

Complete reference for all configuration options in the Wisp Framework.

> **See also:** [[Deployment-Guide]] | [[Troubleshooting]] | [[Architecture-Overview]]

## Table of Contents

- [Environment Variables](#environment-variables)
- [Configuration Loading](#configuration-loading)
- [Discord Intents](#discord-intents)
- [Database Configuration](#database-configuration)
- [Redis Configuration](#redis-configuration)
- [Logging Configuration](#logging-configuration)
- [Service Configuration](#service-configuration)

## Environment Variables

Configuration is loaded from environment variables and optional `.env` files.

### Required Variables

#### `DISCORD_TOKEN`

Discord bot token. **Required.**

```bash
DISCORD_TOKEN=your_bot_token_here
```

### Optional Variables

#### `ENV`

Environment name. Determines which `.env.{ENV}` file to load. Default: `local`

```bash
ENV=production
```

#### `DATABASE_URL`

PostgreSQL database connection URL. Optional (requires `[db]` extra).

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/discord_bot
```

> **⚠️ SECURITY WARNING**: Change default passwords from `docker-compose.yml` before production!

#### `REDIS_URL`

Redis connection URL. Optional (requires `[redis]` extra).

```bash
REDIS_URL=redis://localhost:6379/0
```

#### `LOG_LEVEL`

Logging level. Default: `INFO`

Valid values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

```bash
LOG_LEVEL=DEBUG
```

#### `SYNC_ON_STARTUP`

Whether to sync slash commands on startup. Default: `true`

```bash
SYNC_ON_STARTUP=false
```

#### `OWNER_ID`

Discord user ID of the bot owner. Used for owner-only commands.

```bash
OWNER_ID=123456789012345678
```

#### `WELCOME_CHANNEL_ID`

Default welcome channel ID for guilds.

```bash
WELCOME_CHANNEL_ID=987654321098765432
```

### Discord Intent Configuration

Configure Discord gateway intents via environment variables. All default to `true` if not specified.

#### `INTENTS_GUILDS`

Guilds intent. Default: `true`

```bash
INTENTS_GUILDS=true
```

#### `INTENTS_MEMBERS`

Members intent. Default: `true`

```bash
INTENTS_MEMBERS=true
```

#### `INTENTS_MESSAGES`

Messages intent. Default: `true`

```bash
INTENTS_MESSAGES=true
```

#### `INTENTS_MESSAGE_CONTENT`

Message content intent. Default: `true`

```bash
INTENTS_MESSAGE_CONTENT=true
```

#### `INTENTS_REACTIONS`

Reactions intent. Default: `true`

```bash
INTENTS_REACTIONS=true
```

#### `INTENTS_VOICE_STATES`

Voice states intent. Default: `true`

```bash
INTENTS_VOICE_STATES=true
```

#### `INTENTS_GUILD_MESSAGES`

Guild messages intent. Default: `true`

```bash
INTENTS_GUILD_MESSAGES=true
```

#### `INTENTS_DM_MESSAGES`

DM messages intent. Default: `true`

```bash
INTENTS_DM_MESSAGES=true
```

### Database Configuration

#### `DB_POOL_SIZE`

Database connection pool size. Default: `10`

```bash
DB_POOL_SIZE=20
```

#### `DB_MAX_OVERFLOW`

Maximum overflow connections. Default: `20`

```bash
DB_MAX_OVERFLOW=30
```

#### `DB_POOL_TIMEOUT`

Connection pool timeout in seconds. Default: `30`

```bash
DB_POOL_TIMEOUT=60
```

### Docker Compose Variables

When using Docker Compose, these variables configure the database:

#### `POSTGRES_USER`

PostgreSQL username. Default (dev): `discord_bot`

```bash
POSTGRES_USER=myuser
```

#### `POSTGRES_PASSWORD`

PostgreSQL password. **MUST be changed in production!**

```bash
POSTGRES_PASSWORD=strong_password_here
```

#### `POSTGRES_DB`

PostgreSQL database name. Default (dev): `discord_bot`

```bash
POSTGRES_DB=mydb
```

## Configuration Loading

### Environment File Loading

The framework loads environment variables from `.env.{ENV}` files:

1. Check `ENV` environment variable (default: `local`)
2. Load `.env.{ENV}` file if it exists
3. Environment variables override file values

### Example `.env.local`

```bash
# Discord Configuration
DISCORD_TOKEN=your_token_here
OWNER_ID=123456789012345678

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/discord_bot

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO

# Intents
INTENTS_GUILDS=true
INTENTS_MEMBERS=true
INTENTS_MESSAGES=true
INTENTS_MESSAGE_CONTENT=true
```

### Example `.env.prod`

```bash
# Discord Configuration
DISCORD_TOKEN=${DISCORD_TOKEN}
OWNER_ID=${OWNER_ID}

# Database Configuration (use environment variables, never defaults!)
DATABASE_URL=${DATABASE_URL}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}

# Logging
LOG_LEVEL=WARNING

# Intents (only enable what you need)
INTENTS_GUILDS=true
INTENTS_MEMBERS=true
INTENTS_MESSAGES=false
INTENTS_MESSAGE_CONTENT=false
```

## Discord Intents

### Required Intents

Depending on your bot's functionality, you may need specific intents:

- **Guilds**: Required for most bots
- **Members**: Required for member join/leave events
- **Messages**: Required for message events
- **Message Content**: Required to read message content
- **Reactions**: Required for reaction events
- **Voice States**: Required for voice channel events

### Enabling Intents in Discord Developer Portal

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to "Bot" section
4. Scroll to "Privileged Gateway Intents"
5. Enable required intents
6. Save changes

## Database Configuration

### Connection URL Format

```
postgresql+asyncpg://[user[:password]@][host][:port][/database]
```

### Examples

```bash
# Local database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/discord_bot

# Remote database
DATABASE_URL=postgresql+asyncpg://user:password@db.example.com:5432/discord_bot

# With SSL
DATABASE_URL=postgresql+asyncpg://user:password@db.example.com:5432/discord_bot?ssl=require
```

### Connection Pooling

The framework uses SQLAlchemy's connection pooling:

- **Pool Size**: Number of connections to maintain
- **Max Overflow**: Additional connections allowed beyond pool size
- **Pool Timeout**: Time to wait for a connection before timing out

## Redis Configuration

### Connection URL Format

```
redis://[password@]host[:port][/database]
```

### Examples

```bash
# Local Redis
REDIS_URL=redis://localhost:6379/0

# Remote Redis with password
REDIS_URL=redis://password@redis.example.com:6379/0

# Redis Cluster
REDIS_URL=redis://node1:6379,node2:6379,node3:6379
```

## Logging Configuration

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Structured Logging

The framework uses structured logging with correlation IDs:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Message", extra={"key": "value"})
```

## Service Configuration

### Health Service

No configuration required. Automatically checks all services.

### Cache Service

Automatically uses Redis if `REDIS_URL` is set, otherwise uses in-memory cache.

### Metrics Service

No configuration required. Metrics are stored in memory.

### Scheduler Service

No configuration required. Tasks are scheduled in memory.

### Audit Service

Logs to Python's logging system. Configure via `LOG_LEVEL`.

### Webhook Logger Service

Configure webhook URL via environment variable (if implemented).

### Database Service

Configured via `DATABASE_URL` and database-specific environment variables.

## Configuration Validation

The framework validates configuration on startup:

- **Required Variables**: `DISCORD_TOKEN` must be present
- **Format Validation**: URLs and IDs are validated
- **Service Availability**: Services check for required dependencies

### Error Handling

If configuration is invalid:

```python
from wisp_framework.config import ConfigError

try:
    config = AppConfig()
except ConfigError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

1. **Use Environment Variables**: Never hardcode sensitive values
2. **Separate Environments**: Use different `.env` files for dev/prod
3. **Change Defaults**: Always change default passwords
4. **Minimal Intents**: Only enable intents you need
5. **Secure Storage**: Store production secrets securely
6. **Validate Early**: Check configuration before deployment
7. **Document Custom Config**: Document any custom configuration

## Next Steps

- See [[Deployment-Guide]] for production configuration
- Check [[Troubleshooting]] for configuration issues
- Review [[Architecture-Overview]] for configuration context
