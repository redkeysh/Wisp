# Wisp Framework Issues Found During Echo Bot Development

This document lists workarounds implemented in Echo bot that should be fixed in Wisp Framework itself. Once these are fixed upstream, Echo can remove these workarounds.

## 1. Database Table Migrations

### Issue
Wisp Framework requires `module_states` and `guild_data` tables but doesn't provide migrations for them. Downstream bots must create these migrations manually.

### Workaround in Echo
- Created `alembic/versions/001_add_wisp_module_states.py`
- Created `alembic/versions/002_add_wisp_guild_data.py`

### Expected Fix in Wisp Framework
- Provide Alembic migrations for all Wisp Framework tables
- Or provide a way to auto-create tables on first use
- Or document the exact table schemas so bots can create migrations

### Files to Remove After Fix
- `alembic/versions/001_add_wisp_module_states.py`
- `alembic/versions/002_add_wisp_guild_data.py`

---

## 2. NULL Values for NOT NULL Columns

### Issue
Wisp Framework's `GuildDataService` explicitly passes `NULL` for `updated_at` column in INSERT statements, violating NOT NULL constraint.

**Error:**
```
null value in column "updated_at" of relation "guild_data" violates not-null constraint
[SQL: INSERT INTO guild_data (..., updated_at) VALUES (..., NULL)]
```

### Workaround in Echo
- Added database trigger in migration `002_add_wisp_guild_data.py` to handle NULL values:
  ```sql
  CREATE TRIGGER update_guild_data_updated_at 
  BEFORE INSERT OR UPDATE ON guild_data
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
  ```

### Expected Fix in Wisp Framework
- **Option 1 (Preferred):** Don't include `updated_at` in INSERT statements, let database default handle it
- **Option 2:** Always pass a proper timestamp value for `updated_at`
- **Option 3:** Make `updated_at` nullable (not recommended)

### Code Location
- `wisp_framework/db/guild_data.py` - `GuildDataService.set()` method

### Files to Remove After Fix
- Trigger code in `alembic/versions/002_add_wisp_guild_data.py` (lines 41-66)

---

## 3. Missing `!sync` Prefix Command

### Issue
Wisp Framework documentation suggests a `!sync` prefix command should be available for syncing slash commands, but it's not registered.

**Error:**
```
discord.ext.commands.errors.CommandNotFound: Command "sync" is not found
```

### Workaround in Echo
- None - command simply doesn't work
- Added note in README.md about this issue

### Expected Fix in Wisp Framework
- Register the `!sync` prefix command automatically
- Or provide a module that bots can enable to get sync command
- Or document that it needs to be enabled/configured

### Code Location
- Should be in Wisp Framework's command sync module (if it exists)

---

## 4. Command Sync Timing Issue

### Issue
Wisp Framework's bot doesn't have `application_id` set immediately after `lifecycle.startup()`, causing command sync to fail if called too early.

**Error:**
```
Client does not have an application_id set. Either the function was called before on_ready was called or application_id was not passed to the Client constructor.
```

### Workaround in Echo
- Moved command sync to `on_ready` event handler in `src/echo/main.py` (lines 235-268)
- Added custom `on_ready` handler to sync commands after bot is ready

### Expected Fix in Wisp Framework
- Handle command syncing internally in Wisp Framework's `on_ready` handler
- Or provide a method that waits for bot to be ready before syncing
- Or document that command sync should happen in `on_ready`

### Code Location
- `src/echo/main.py` lines 235-268 (custom `on_ready` handler)

### Files to Remove After Fix
- Custom `on_ready` handler in `src/echo/main.py` (can use Wisp Framework's built-in sync)

---

## 5. Discord Intents Configuration

### Issue
Wisp Framework doesn't configure Discord intents properly, causing warnings about missing intents (GUILDS, MESSAGE_CONTENT).

**Warnings:**
```
Guilds intent seems to be disabled. This may cause state related issues.
Privileged message content intent is missing, commands may not work as expected.
```

### Workaround in Echo
- Added intent checking and warnings in `src/echo/main.py` (lines 232-238)
- Added documentation in README.md about required intents

### Expected Fix in Wisp Framework
- Configure intents properly when creating the bot
- Allow intent configuration via `AppConfig` or environment variables
- Or document required intents and how to configure them

### Code Location
- `wisp_framework/bot.py` or `wisp_framework/config.py` - Bot creation with intents

### Files to Remove After Fix
- Intent checking code in `src/echo/main.py` (lines 232-238)

---

## 6. Logging Formatter Override

### Issue
Wisp Framework's `setup_logging()` overrides the logging formatter, making it difficult for downstream bots to customize logging format or add prefixes.

### Workaround in Echo
- Created `EchoLogFormatter` class to brand Echo logs
- Re-applies formatter after Wisp Framework configures logging
- Added complex logic to detect Echo loggers and add "Echo:" prefix

### Expected Fix in Wisp Framework
- Allow custom formatters to be passed to `setup_logging()`
- Or provide a way to add log prefixes/filters without overriding the formatter
- Or use a logging filter system instead of formatter override

### Code Location
- `src/echo/logging.py` - `EchoLogFormatter` class
- `src/echo/main.py` lines 157-205 (formatter re-application)

### Files to Simplify After Fix
- `src/echo/logging.py` - Can use simpler formatter or remove custom formatter
- `src/echo/main.py` - Remove formatter re-application code

---

## 7. Database Metadata Not Included in Alembic

### Issue
Wisp Framework's database models aren't automatically included in Alembic migrations, requiring manual table creation.

### Workaround in Echo
- Added code in `alembic/env.py` to try importing Wisp models and merge metadata (lines 24-37)
- This doesn't work reliably, so manual migrations were created instead

### Expected Fix in Wisp Framework
- Provide a way to include Wisp Framework models in Alembic migrations
- Or provide standalone migrations that bots can include
- Or document how to properly integrate Wisp models with Alembic

### Code Location
- `alembic/env.py` lines 24-37 (attempted Wisp model import)

### Files to Remove After Fix
- Wisp model import code in `alembic/env.py` (if Wisp provides proper migrations)

---

## Summary of Priority Fixes

### High Priority (Breaks Functionality)
1. **NULL values for NOT NULL columns** - Causes database errors
2. **Missing `!sync` command** - Expected feature doesn't work
3. **Command sync timing** - Commands fail to sync if called too early

### Medium Priority (Requires Workarounds)
4. **Database table migrations** - Bots must manually create migrations
5. **Discord intents configuration** - Causes warnings and potential issues

### Low Priority (Nice to Have)
6. **Logging formatter override** - Makes custom logging harder
7. **Database metadata in Alembic** - Would simplify migration setup

---

## Testing Recommendations

When fixing these issues in Wisp Framework, test with:
- Echo bot's current implementation
- Check that all workarounds can be removed
- Verify database operations work without triggers
- Ensure command syncing works automatically
- Confirm logging can be customized properly
