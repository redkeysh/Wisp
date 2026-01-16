"""CLI utilities for framework operations."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from wisp_framework.config import AppConfig
from wisp_framework.lifecycle import create_services
from wisp_framework.services.db import DatabaseService


def create_module_template(module_name: str, output_dir: Path) -> None:
    """Create a module template file.

    Args:
        module_name: Name of the module
        output_dir: Output directory
    """
    template = f'''"""{module_name.title()} module."""

from typing import Any

import discord
from discord import app_commands

from wisp_framework.module import Module
from wisp_framework.utils.decorators import require_guild
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.responses import respond_success


class {module_name.title()}Module(Module):
    """{module_name.title()} module."""

    @property
    def name(self) -> str:
        """Module name."""
        return "{module_name}"

    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the {module_name} module."""
        tree = bot.tree

        @tree.command(name="{module_name}", description="{module_name.title()} command")
        @require_guild
        async def {module_name}_command(interaction: discord.Interaction) -> None:
            """{module_name.title()} command handler."""
            embed = EmbedBuilder.success(
                title="Success",
                description="This is a template command."
            )
            await respond_success(
                interaction,
                "Command executed!",
                embed=embed,
                ephemeral=True
            )
'''
    output_file = output_dir / f"{module_name}.py"
    output_file.write_text(template)
    print(f"Created module template: {output_file}")


def create_bot_template(bot_name: str, output_dir: Path) -> None:
    """Create a bot template file.

    Args:
        bot_name: Name of the bot
        output_dir: Output directory
    """
    template = f'''"""{bot_name.title()} bot."""

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    try:
        # Load configuration
        config = AppConfig()
        setup_logging(config)

        logger.info("Starting {bot_name} bot...")

        # Create services
        services = create_services(config)

        # Create feature flags
        feature_flags = create_feature_flags(services)

        # Create module registry
        module_registry = ModuleRegistry(feature_flags)

        # Register your modules here
        # from modules.my_module import MyModule
        # module_registry.register(MyModule())

        # Create bot context
        ctx = create_bot_context(config, services)

        # Create lifecycle manager
        lifecycle = LifecycleManager()

        # Start bot
        async def run():
            bot = await lifecycle.startup(config, services, module_registry, ctx)
            await bot.start(config.discord_token)

        asyncio.run(run())

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Failed to start bot: {{e}}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
'''
    output_file = output_dir / f"{bot_name}_bot.py"
    output_file.write_text(template)
    print(f"Created bot template: {output_file}")


async def doctor_command(config: AppConfig) -> int:
    """Run doctor command to validate system health.

    Args:
        config: Application configuration

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("Running Wisp Framework doctor...")
    issues = []

    # Check config
    try:
        if not config.discord_token:
            issues.append("WARNING: DISCORD_TOKEN not set (required for bot, optional for CLI)")
    except Exception as e:
        issues.append(f"ERROR: Config validation failed: {e}")

    # Check database
    services = create_services(config)
    await services.startup_all()

    db_service = services.get_typed("db", DatabaseService)
    if db_service:
        try:
            if db_service.engine:
                from sqlalchemy import text as sa_text
                async with db_service.engine.begin() as conn:
                    await conn.execute(sa_text("SELECT 1"))
                print("✓ Database connectivity: OK")
            else:
                issues.append("WARNING: Database service not initialized")
        except Exception as e:
            issues.append(f"ERROR: Database connectivity failed: {e}")
    else:
        issues.append("WARNING: Database service not available")

    # Check Redis
    cache_service = services.get("cache")
    if cache_service:
        try:
            if hasattr(cache_service, "_redis_client") and cache_service._redis_client:
                await cache_service._redis_client.ping()
                print("✓ Redis connectivity: OK")
            else:
                print("ℹ Redis: Using in-memory cache")
        except Exception as e:
            issues.append(f"WARNING: Redis connectivity failed: {e}")

    # Check plugin registry
    from wisp_framework.feature_flags import FeatureFlags
    from wisp_framework.plugins.registry import PluginRegistry

    feature_flags = FeatureFlags(db_service)
    plugin_registry = PluginRegistry(feature_flags, db_service)
    plugins = plugin_registry.list_plugins()
    print(f"✓ Plugin registry: {len(plugins)} plugins registered")

    # Check job queue
    job_queue = services.get("job_queue")
    if job_queue:
        print("✓ Job queue: Available")
    else:
        issues.append("WARNING: Job queue not available")

    await services.shutdown_all()

    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("\n✓ All checks passed!")
        return 0


async def migrate_command(config: AppConfig) -> int:
    """Run migrations.

    Args:
        config: Application configuration

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("Running migrations...")
    try:
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")
        if config.database_url:
            alembic_cfg.set_main_option("sqlalchemy.url", config.database_url)

        command.upgrade(alembic_cfg, "head")
        print("✓ Migrations completed successfully")
        return 0
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        return 1


async def plugins_list_command(config: AppConfig) -> int:
    """List all plugins.

    Args:
        config: Application configuration

    Returns:
        Exit code
    """
    services = create_services(config)
    await services.startup_all()

    from wisp_framework.feature_flags import FeatureFlags
    from wisp_framework.plugins.registry import PluginRegistry

    db_service = services.get_typed("db", DatabaseService)
    feature_flags = FeatureFlags(db_service)
    plugin_registry = PluginRegistry(feature_flags, db_service)

    plugins = plugin_registry.list_plugins()
    print(f"Registered plugins ({len(plugins)}):")
    for plugin_name in plugins:
        plugin = plugin_registry.get_plugin(plugin_name)
        if plugin:
            print(f"  - {plugin_name} v{plugin.version}")

    await services.shutdown_all()
    return 0


async def plugins_enable_command(config: AppConfig, plugin_name: str, guild_id: int | None = None) -> int:
    """Enable a plugin.

    Args:
        config: Application configuration
        plugin_name: Plugin name
        guild_id: Optional guild ID

    Returns:
        Exit code
    """
    services = create_services(config)
    await services.startup_all()

    from wisp_framework.feature_flags import FeatureFlags
    from wisp_framework.plugins.registry import PluginRegistry

    db_service = services.get_typed("db", DatabaseService)
    feature_flags = FeatureFlags(db_service)
    plugin_registry = PluginRegistry(feature_flags, db_service)

    try:
        await plugin_registry.enable_plugin(plugin_name, guild_id)
        scope = f"guild {guild_id}" if guild_id else "globally"
        print(f"✓ Enabled plugin '{plugin_name}' {scope}")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to enable plugin: {e}")
        return 1
    finally:
        await services.shutdown_all()


async def plugins_disable_command(config: AppConfig, plugin_name: str, guild_id: int | None = None) -> int:
    """Disable a plugin.

    Args:
        config: Application configuration
        plugin_name: Plugin name
        guild_id: Optional guild ID

    Returns:
        Exit code
    """
    services = create_services(config)
    await services.startup_all()

    from wisp_framework.feature_flags import FeatureFlags
    from wisp_framework.plugins.registry import PluginRegistry

    db_service = services.get_typed("db", DatabaseService)
    feature_flags = FeatureFlags(db_service)
    plugin_registry = PluginRegistry(feature_flags, db_service)

    try:
        await plugin_registry.disable_plugin(plugin_name, guild_id)
        scope = f"guild {guild_id}" if guild_id else "globally"
        print(f"✓ Disabled plugin '{plugin_name}' {scope}")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to disable plugin: {e}")
        return 1
    finally:
        await services.shutdown_all()


async def export_command(config: AppConfig, output_file: Path) -> int:
    """Export configuration and state.

    Args:
        config: Application configuration
        output_file: Output file path

    Returns:
        Exit code
    """
    print(f"Exporting to {output_file}...")
    services = create_services(config)
    await services.startup_all()

    export_data = {
        "version": "1.0",
        "plugins": [],
        "policy_rules": [],
    }

    # Export plugin states

    db_service = services.get_typed("db", DatabaseService)
    if db_service:
        from sqlalchemy import select

        from wisp_framework.db.models import PluginState, PolicyRule

        async with db_service.session_factory() as session:
            # Export plugin states
            stmt = select(PluginState)
            result = await session.execute(stmt)
            for row in result.scalars().all():
                export_data["plugins"].append({
                    "name": row.plugin_name,
                    "version": row.version,
                    "guild_id": row.guild_id,
                    "enabled": row.enabled,
                    "degraded": row.degraded,
                })

            # Export policy rules
            stmt = select(PolicyRule)
            result = await session.execute(stmt)
            for row in result.scalars().all():
                export_data["policy_rules"].append({
                    "scope_type": row.scope_type,
                    "scope_id": row.scope_id,
                    "capability": row.capability,
                    "action": row.action,
                    "priority": row.priority,
                })

    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2)

    print(f"✓ Exported {len(export_data['plugins'])} plugins and {len(export_data['policy_rules'])} policy rules")
    await services.shutdown_all()
    return 0


async def import_command(config: AppConfig, input_file: Path, dry_run: bool = False) -> int:
    """Import configuration and state.

    Args:
        config: Application configuration
        input_file: Input file path
        dry_run: If True, don't actually import

    Returns:
        Exit code
    """
    print(f"Importing from {input_file}...")
    if dry_run:
        print("DRY RUN MODE - no changes will be made")

    with open(input_file) as f:
        import_data = json.load(f)

    services = create_services(config)
    await services.startup_all()

    db_service = services.get_typed("db", DatabaseService)
    if not db_service:
        print("ERROR: Database service not available")
        return 1

    try:
        from wisp_framework.db.models import PluginState, PolicyRule

        async with db_service.session_factory() as session:
            if not dry_run:
                from sqlalchemy import select

                # Import plugin states
                for plugin_data in import_data.get("plugins", []):
                    stmt = select(PluginState).where(
                        PluginState.plugin_name == plugin_data["name"],
                        PluginState.guild_id == plugin_data.get("guild_id"),
                    )
                    result = await session.execute(stmt)
                    row = result.scalar_one_or_none()
                    if row:
                        row.enabled = plugin_data["enabled"]
                        row.degraded = plugin_data.get("degraded", False)
                    else:
                        row = PluginState(**plugin_data)
                        session.add(row)

                # Import policy rules
                for rule_data in import_data.get("policy_rules", []):
                    stmt = select(PolicyRule).where(
                        PolicyRule.scope_type == rule_data["scope_type"],
                        PolicyRule.scope_id == rule_data.get("scope_id"),
                        PolicyRule.capability == rule_data["capability"],
                    )
                    result = await session.execute(stmt)
                    row = result.scalar_one_or_none()
                    if row:
                        row.action = rule_data["action"]
                        row.priority = rule_data["priority"]
                    else:
                        row = PolicyRule(**rule_data)
                        session.add(row)

                await session.commit()
                print(f"✓ Imported {len(import_data.get('plugins', []))} plugins and {len(import_data.get('policy_rules', []))} policy rules")
            else:
                print(f"Would import {len(import_data.get('plugins', []))} plugins and {len(import_data.get('policy_rules', []))} policy rules")

        return 0
    except Exception as e:
        print(f"ERROR: Import failed: {e}")
        return 1
    finally:
        await services.shutdown_all()


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Wisp Framework CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create module command
    module_parser = subparsers.add_parser("create-module", help="Create a module template")
    module_parser.add_argument("name", help="Module name")
    module_parser.add_argument(
        "--output-dir", type=Path, default=Path("modules"), help="Output directory"
    )

    # Create bot command
    bot_parser = subparsers.add_parser("create-bot", help="Create a bot template")
    bot_parser.add_argument("name", help="Bot name")
    bot_parser.add_argument(
        "--output-dir", type=Path, default=Path("."), help="Output directory"
    )

    # Doctor command
    subparsers.add_parser("doctor", help="Validate system health")

    # Migrate command
    subparsers.add_parser("migrate", help="Run database migrations")

    # Plugins commands
    plugins_parser = subparsers.add_parser("plugins", help="Manage plugins")
    plugins_subparsers = plugins_parser.add_subparsers(dest="plugins_command", help="Plugin command")
    plugins_subparsers.add_parser("list", help="List plugins")
    plugins_enable_parser = plugins_subparsers.add_parser("enable", help="Enable plugin")
    plugins_enable_parser.add_argument("name", help="Plugin name")
    plugins_enable_parser.add_argument("--guild", type=int, help="Guild ID")
    plugins_disable_parser = plugins_subparsers.add_parser("disable", help="Disable plugin")
    plugins_disable_parser.add_argument("name", help="Plugin name")
    plugins_disable_parser.add_argument("--guild", type=int, help="Guild ID")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export configuration")
    export_parser.add_argument("output", type=Path, help="Output file path")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import configuration")
    import_parser.add_argument("input", type=Path, help="Input file path")
    import_parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    args = parser.parse_args()
    config = AppConfig()

    if args.command == "create-module":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        create_module_template(args.name, args.output_dir)
    elif args.command == "create-bot":
        create_bot_template(args.name, args.output_dir)
    elif args.command == "doctor":
        sys.exit(asyncio.run(doctor_command(config)))
    elif args.command == "migrate":
        sys.exit(asyncio.run(migrate_command(config)))
    elif args.command == "plugins":
        if args.plugins_command == "list":
            sys.exit(asyncio.run(plugins_list_command(config)))
        elif args.plugins_command == "enable":
            sys.exit(asyncio.run(plugins_enable_command(config, args.name, getattr(args, "guild", None))))
        elif args.plugins_command == "disable":
            sys.exit(asyncio.run(plugins_disable_command(config, args.name, getattr(args, "guild", None))))
        else:
            plugins_parser.print_help()
            sys.exit(1)
    elif args.command == "export":
        sys.exit(asyncio.run(export_command(config, args.output)))
    elif args.command == "import":
        sys.exit(asyncio.run(import_command(config, args.input, args.dry_run)))
    else:
        parser.print_help()
        sys.exit(1)
