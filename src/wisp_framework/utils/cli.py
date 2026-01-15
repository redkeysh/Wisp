"""CLI utilities for framework operations."""

import argparse
import sys
from pathlib import Path


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

    args = parser.parse_args()

    if args.command == "create-module":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        create_module_template(args.name, args.output_dir)
    elif args.command == "create-bot":
        create_bot_template(args.name, args.output_dir)
    else:
        parser.print_help()
        sys.exit(1)
