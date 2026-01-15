# Wisp Framework Logging - What's Already Logged

This document lists what Wisp Framework logs automatically, so downstream bots (like Echo) can avoid duplicate logging.

## ✅ Already Logged by Wisp Framework

### **Startup Sequence**
- `"Starting bot lifecycle..."`
- `"Starting up all services..."`
- `"Service '{name}' started successfully"` (for each service)
- `"Health service started"`
- `"Cache service started with Redis backend"` or `"Cache service started with in-memory backend"`
- `"Metrics service started"`
- `"Scheduler service started"`
- `"Audit service started"`
- `"Webhook logger service started"` or `"Webhook logger service started (no webhook URL configured)"`
- `"Database service started successfully"` (if DATABASE_URL configured)
- `"Bot lifecycle startup complete"`
- `"Bot setup hook called"`
- `"Synced {N} command(s)"` (if sync_on_startup is True)
- `"Bot ready: {user} (ID: {id})"`
- `"Connected to {N} guild(s)"`
- `"Registered module: {name}"` (for each registered module)
- `"Loading module: {module_name}"` (when modules load per guild)

### **Runtime**
- `"Command error: {error}"` (all command errors with full traceback)
- Command completion logged to audit service (structured JSON, not console)
- `"Registered scheduled task '{task_name}' with interval {interval}s"`
- `"Running insights rollup..."` (if InsightsModule is enabled)
- `"Insights rollup completed"`

### **Shutdown Sequence**
- `"Received shutdown signal"`
- `"Shutting down bot lifecycle..."`
- `"Shutting down all services..."`
- `"Service '{name}' shut down successfully"` (for each service)
- `"Closing bot..."`
- `"Bot lifecycle shutdown complete"`

### **Error/Warning Messages**
- `"Failed to sync commands: {e}"`
- `"Failed to start service '{name}': {e}"`
- `"Error tearing down module '{module_name}': {e}"`
- `"Failed to load module '{module_name}': {e}"`
- `"No DATABASE_URL configured, database service will not be available"`
- `"Database get failed: {e}, using memory cache"` (warnings)
- `"Redis get failed: {e}, falling back to memory"` (warnings)

## ❌ What Echo Bot Should NOT Log

**Avoid logging these in Echo bot:**
- ✅ Bot startup/shutdown messages
- ✅ Service initialization status
- ✅ Bot ready/connected status
- ✅ Command sync status
- ✅ Module registration/loading
- ✅ Generic command errors (WF already logs these)
- ✅ Service health checks

## ✅ What Echo Bot SHOULD Log

**Echo-specific logging:**
- ✅ Echo module-specific events (e.g., "Echo command executed")
- ✅ Echo-specific errors (beyond what WF logs)
- ✅ Echo business logic events (e.g., "Message echoed to channel X")
- ✅ Echo configuration changes
- ✅ Echo-specific warnings (not framework warnings)

## Example: Clean Echo Logging

```python
# ❌ DON'T log this (WF already does):
logger.info("Bot starting...")
logger.info("Bot ready!")
logger.info("Connected to guilds")

# ✅ DO log Echo-specific things:
logger.info("Echo module initialized")
logger.info(f"Echo command used by {user} in {guild}")
logger.warning("Echo rate limit approaching")
```

## Log Format

Wisp Framework uses this format:
```
%(asctime)s [%(levelname)8s] [%(name)s] [%(correlation_id)s] %(message)s
```

Example output:
```
2026-01-15 21:30:00 [    INFO] [wisp_framework.bot] [None] Bot ready: EchoBot#1234 (ID: 123456789)
```

Your Echo bot logs will appear with `[echo]` or `[your_module_name]` in the name field, making them easy to distinguish.

## Configuring Log Levels

### Global Log Level

Set the root log level via `LOG_LEVEL` environment variable:

```bash
# In .env.local or environment
LOG_LEVEL=INFO    # Show INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=WARNING # Show only WARNING, ERROR, CRITICAL
LOG_LEVEL=ERROR   # Show only ERROR, CRITICAL
LOG_LEVEL=DEBUG   # Show everything (very verbose)
```

### Suppress Wisp Framework Logs

To suppress Wisp Framework logs while keeping your bot's logs at INFO:

```bash
# Set your bot's log level
LOG_LEVEL=INFO

# Suppress Wisp Framework logs to WARNING or ERROR
LOG_LEVEL_WISP_FRAMEWORK=WARNING
```

This allows you to:
- See your Echo bot's INFO logs
- Hide Wisp Framework's INFO/DEBUG logs
- Still see Wisp Framework warnings/errors

### Example Configuration

**`.env.local` for production:**
```bash
LOG_LEVEL=INFO
LOG_LEVEL_WISP_FRAMEWORK=WARNING
```

**`.env.local` for development:**
```bash
LOG_LEVEL=DEBUG
LOG_LEVEL_WISP_FRAMEWORK=INFO
```

### Available Log Levels

- `DEBUG` - Most verbose (all logs)
- `INFO` - Default (informational messages)
- `WARNING` - Warnings and above
- `ERROR` - Errors and critical issues only
- `CRITICAL` - Only critical failures
