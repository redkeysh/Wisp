# Troubleshooting Guide

Common issues and solutions for the Wisp Framework.

> **See also:** [[Configuration-Reference]] | [[Deployment-Guide]] | [[API-Reference]]

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Database Issues](#database-issues)
- [Module Issues](#module-issues)
- [Command Issues](#command-issues)
- [Performance Issues](#performance-issues)
- [Deployment Issues](#deployment-issues)

## Installation Issues

### "Could not find a version that satisfies"

**Problem:** Package not found during installation.

**Solutions:**
- Check URL format: `git+https://github.com/redkeysh/wisp.git`
- Ensure repository is accessible
- Check Python version (requires 3.13+)
- Try upgrading pip: `pip install --upgrade pip`

### Import Errors

**Problem:** `ModuleNotFoundError` when importing.

**Solutions:**
- Verify installation: `pip show wisp-framework`
- Check Python environment
- Reinstall: `pip install --force-reinstall git+https://github.com/redkeysh/wisp.git`
- Check import path: `from wisp_framework import WispBot, create_app, Module, ...`
- **Common error:** `cannot import name 'Wisp'` - There is no `Wisp` class. Use `WispBot` (the main bot class) or `create_app()` (convenience function) instead.

## Configuration Issues

### Missing DISCORD_TOKEN

**Problem:** `ConfigError: Missing required environment variables: DISCORD_TOKEN`

**Solutions:**
- Set `DISCORD_TOKEN` environment variable
- Create `.env.local` file with `DISCORD_TOKEN=your_token`
- Check token is valid in Discord Developer Portal

### Environment File Not Loading

**Problem:** Environment variables from `.env` file not loading.

**Solutions:**
- Check `ENV` variable (defaults to `local`)
- Ensure file is named `.env.{ENV}`
- Verify file format (no spaces around `=`)
- Check file permissions

### Intent Configuration

**Problem:** Bot not receiving events.

**Solutions:**
- Enable intents in Discord Developer Portal
- Set intent environment variables: `INTENTS_MEMBERS=true`
- Check bot has necessary permissions
- Verify intent configuration in code

## Database Issues

### Connection Errors

**Problem:** Database connection fails.

**Solutions:**
- Check `DATABASE_URL` format
- Verify database is running
- Check network connectivity
- Verify credentials
- Check firewall rules

### Migration Errors

**Problem:** Alembic migrations fail.

**Solutions:**
- Check database connection
- Verify Alembic configuration
- Review migration files
- Try: `alembic upgrade head --sql` (dry run)
- Check database permissions

### Pool Exhaustion

**Problem:** "QueuePool limit of size X overflow Y reached"

**Solutions:**
- Increase pool size: `DB_POOL_SIZE=20`
- Increase max overflow: `DB_MAX_OVERFLOW=30`
- Check for connection leaks
- Review connection usage

### Default Passwords

**Problem:** Using default passwords in production.

**Solutions:**
- **MUST change all default passwords**
- Set strong passwords via environment variables
- Never commit passwords to version control
- Use secret management services

## Module Issues

### Module Not Loading

**Problem:** Module doesn't appear or load.

**Solutions:**
- Check module is registered: `module_registry.register(MyModule())`
- Verify module name is unique
- Check module is enabled for guild
- Review module logs for errors
- Check required services are available

### Module Dependencies

**Problem:** Module fails due to missing dependency.

**Solutions:**
- Declare dependencies: `depends_on = ["other_module"]`
- Ensure dependency is registered first
- Check dependency is enabled
- Review dependency loading order

### Service Not Available

**Problem:** Required service not found.

**Solutions:**
- Check service is registered
- Verify service started successfully
- Check service name spelling
- Review service logs
- Provide fallback behavior

## Command Issues

### Commands Not Appearing

**Problem:** Slash commands don't show in Discord.

**Solutions:**
- Wait for sync (can take up to 1 hour globally)
- Use `/sync` command (owner only)
- Check `SYNC_ON_STARTUP` is enabled
- Verify bot has "Use Slash Commands" permission
- Check intents are enabled
- Review command registration code

### Command Errors

**Problem:** Commands fail with errors.

**Solutions:**
- Check error logs
- Use `@handle_errors` decorator
- Validate user input
- Check permissions
- Review command implementation

### Permission Errors

**Problem:** Commands fail permission checks.

**Solutions:**
- Use `@require_guild` for guild-only commands
- Use `@require_admin` for admin commands
- Use `@require_owner` for owner commands
- Check bot permissions in guild
- Verify user has required permissions

## Performance Issues

### High Memory Usage

**Problem:** Bot uses too much memory.

**Solutions:**
- Review cache usage
- Check for memory leaks
- Limit cached data size
- Use Redis instead of in-memory cache
- Review module resource usage

### Slow Commands

**Problem:** Commands are slow to respond.

**Solutions:**
- Optimize database queries
- Use caching for frequent data
- Review async/await usage
- Check network latency
- Profile command execution

### Database Performance

**Problem:** Database queries are slow.

**Solutions:**
- Add database indexes
- Optimize queries
- Use connection pooling
- Review query patterns
- Consider caching

## Deployment Issues

### Docker Issues

**Problem:** Docker container fails to start.

**Solutions:**
- Check logs: `docker-compose logs bot`
- Verify environment variables
- Check Docker resources
- Review health checks
- Check container permissions

### Migration Issues

**Problem:** Migrations fail in production.

**Solutions:**
- Test migrations in staging first
- Review migration files
- Check database permissions
- Verify database version compatibility
- Have rollback plan

### Environment Variables

**Problem:** Environment variables not set in production.

**Solutions:**
- Verify `.env.prod` file exists
- Check variable names match
- Review deployment process
- Use secret management
- Test configuration before deployment

## Getting Help

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG
```

### Check Logs

```bash
# Docker
docker-compose logs -f bot

# Manual
# Check console output or log files
```

### Common Commands

```bash
# Check configuration
python -c "from wisp_framework.config import AppConfig; print(AppConfig())"

# Test database connection
python -c "from wisp_framework.services.db import DatabaseService; ..."

# List registered modules
# Use /modules list command in Discord
```

### Reporting Issues

When reporting issues, include:

- Python version
- Framework version
- Error messages
- Relevant logs
- Steps to reproduce
- Configuration (sanitized)

## Next Steps

- Review [[Configuration-Reference]] for configuration details
- Check [[Deployment-Guide]] for deployment issues
- See [[API-Reference]] for API details
