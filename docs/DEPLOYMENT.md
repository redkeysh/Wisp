# Deployment Guide

Complete guide for deploying Wisp Framework bots to production.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Docker Deployment](#docker-deployment)
- [Manual Deployment](#manual-deployment)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Security Considerations](#security-considerations)
- [Monitoring](#monitoring)
- [Scaling](#scaling)

## Pre-Deployment Checklist

- [ ] Change all default passwords
- [ ] Set strong, unique database passwords
- [ ] Configure production environment variables
- [ ] Enable only required Discord intents
- [ ] Set up database migrations
- [ ] Configure logging level appropriately
- [ ] Set up monitoring and health checks
- [ ] Test in staging environment
- [ ] Review security settings
- [ ] Document deployment process

## Docker Deployment

### Production Docker Compose

The framework includes `docker-compose.prod.yml` with production-ready settings:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Production Features

- Security hardening (non-root user, read-only filesystem)
- Resource limits
- Health checks
- Migration service that runs before the bot
- Proper restart policies

### Environment Variables

Create `.env.prod` with production values:

```bash
# Copy example
cp .env.prod.example .env.prod

# Edit with production values
# ⚠️ Never use default passwords!
```

### Running Migrations

Migrations run automatically before the bot starts:

```bash
docker-compose -f docker-compose.prod.yml --profile migrate up migrate
```

### Health Checks

The bot includes health checks:

```bash
docker-compose -f docker-compose.prod.yml ps
```

## Manual Deployment

### 1. Install Dependencies

```bash
pip install wisp-framework[all]
```

### 2. Set Up Environment

```bash
# Create production environment file
cp .env.prod.example .env.prod

# Edit .env.prod with production values
# ⚠️ Set strong, unique passwords!
```

### 3. Run Migrations

```bash
# Set DATABASE_URL in environment
export DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db

# Run migrations
alembic upgrade head
```

### 4. Run the Bot

```bash
# Using the runner
wisp-framework-runner

# Or using Python
python -m runner_bot.main
```

### 5. Process Management

Use a process manager like systemd or supervisor:

#### systemd Service

```ini
[Unit]
Description=Wisp Framework Bot
After=network.target postgresql.service

[Service]
Type=simple
User=discord-bot
WorkingDirectory=/opt/wisp-bot
Environment="ENV=production"
ExecStart=/usr/bin/python3 -m runner_bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Environment Setup

### Production Environment Variables

```bash
# Required
DISCORD_TOKEN=your_production_token

# Database (change passwords!)
DATABASE_URL=postgresql+asyncpg://user:strong_password@host:5432/db
POSTGRES_USER=production_user
POSTGRES_PASSWORD=strong_unique_password
POSTGRES_DB=production_db

# Redis (if used)
REDIS_URL=redis://strong_password@host:6379/0

# Logging
LOG_LEVEL=WARNING

# Intents (only enable what you need)
INTENTS_GUILDS=true
INTENTS_MEMBERS=true
INTENTS_MESSAGES=false
INTENTS_MESSAGE_CONTENT=false

# Owner
OWNER_ID=your_discord_user_id
```

### Security Best Practices

1. **Never commit `.env.prod`** to version control
2. **Use secret management** (AWS Secrets Manager, HashiCorp Vault, etc.)
3. **Rotate passwords** regularly
4. **Use strong passwords** (minimum 32 characters)
5. **Limit database access** to necessary IPs
6. **Enable SSL/TLS** for database connections
7. **Use read-only database users** when possible

## Database Setup

### Initial Setup

```bash
# Create database
createdb discord_bot

# Run migrations
alembic upgrade head
```

### Migration Management

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Review migration file
# Edit if needed

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Backup Strategy

```bash
# Backup database
pg_dump -h host -U user -d database > backup.sql

# Restore database
psql -h host -U user -d database < backup.sql
```

### Connection Pooling

Configure connection pool size based on load:

```bash
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=60
```

## Security Considerations

### Docker Security

The production Docker setup includes:

- Non-root user execution
- Read-only filesystem
- Dropped capabilities
- Resource limits
- Security options

### Network Security

- Use private networks for database/Redis
- Enable firewall rules
- Use VPN or SSH tunnels for database access
- Limit exposed ports

### Application Security

- Validate all user input
- Use parameterized queries
- Implement rate limiting
- Log security events
- Monitor for anomalies

### Secrets Management

Never store secrets in code or configuration files:

- Use environment variables
- Use secret management services
- Rotate secrets regularly
- Audit secret access

## Monitoring

### Health Checks

The framework provides health check endpoints:

```python
# Check bot health
/health command

# Check service health
health_service.check_service("db")
```

### Logging

Configure logging for production:

```bash
LOG_LEVEL=WARNING
```

Log to files or centralized logging:

```python
import logging

# File handler
file_handler = logging.FileHandler("bot.log")
logger.addHandler(file_handler)
```

### Metrics

Use the metrics service for monitoring:

```python
metrics = ctx.services.get("metrics")
metrics.increment("commands.executed")
metrics.timing("command.duration", duration)
```

### Alerting

Set up alerts for:

- Bot downtime
- High error rates
- Database connection failures
- Resource usage

## Scaling

### Horizontal Scaling

Discord bots typically don't need horizontal scaling, but if needed:

- Use shared database
- Use Redis for shared state
- Implement stateless modules
- Use load balancer for webhooks

### Vertical Scaling

Increase resources:

- More CPU for command processing
- More memory for caching
- Larger database connection pool
- More Redis connections

### Performance Optimization

- Use caching for frequently accessed data
- Optimize database queries
- Use connection pooling
- Implement rate limiting
- Monitor performance metrics

## Troubleshooting

See [Troubleshooting Guide](TROUBLESHOOTING.md) for common deployment issues.

## Next Steps

- Review [Configuration Reference](CONFIGURATION.md) for configuration details
- Check [Architecture Overview](ARCHITECTURE.md) for deployment context
- See [API Reference](API_REFERENCE.md) for deployment-related APIs
