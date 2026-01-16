"""Ping module - simple ping command."""

from typing import Any

import discord
from discord.ext import commands

from wisp_framework.module import Module
from wisp_framework.utils.context_helpers import (
    get_wisp_context_from_command_context,
    get_wisp_context_from_interaction,
)
from wisp_framework.utils.decorators import handle_errors
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.responses import respond_success


class PingModule(Module):
    """Simple ping command module."""

    @property
    def name(self) -> str:
        """Module name."""
        return "ping"

    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the ping module."""
        tree = bot.tree

        @tree.command(name="ping", description="Check bot latency")
        @handle_errors
        async def ping_command(interaction: discord.Interaction) -> None:
            """Ping command handler."""
            # Create WispContext for this command execution
            wisp_ctx = get_wisp_context_from_interaction(bot, interaction, "slash")
            wisp_ctx.bound_logger.debug("Executing ping command")

            latency = round(bot.latency * 1000)

            # Determine status color based on latency
            if latency < 100:
                status = "Excellent"
                color_type = "success"
            elif latency < 200:
                status = "Good"
                color_type = "info"
            elif latency < 500:
                status = "Fair"
                color_type = "warning"
            else:
                status = "Poor"
                color_type = "error"

            # Create appropriate embed
            if color_type == "success":
                embed = EmbedBuilder.success(
                    title="Pong! 🏓",
                    description=f"Latency: **{latency}ms**\nStatus: {status}",
                    fields=[{"name": "Response Time", "value": f"{latency}ms", "inline": True}]
                )
            elif color_type == "info":
                embed = EmbedBuilder.info(
                    title="Pong! 🏓",
                    description=f"Latency: **{latency}ms**\nStatus: {status}",
                    fields=[{"name": "Response Time", "value": f"{latency}ms", "inline": True}]
                )
            elif color_type == "warning":
                embed = EmbedBuilder.warning(
                    title="Pong! 🏓",
                    description=f"Latency: **{latency}ms**\nStatus: {status}",
                    fields=[{"name": "Response Time", "value": f"{latency}ms", "inline": True}]
                )
            else:
                embed = EmbedBuilder.error(
                    title="Pong! 🏓",
                    description=f"Latency: **{latency}ms**\nStatus: {status}",
                    fields=[{"name": "Response Time", "value": f"{latency}ms", "inline": True}]
                )

            # Record metrics using WispContext
            if wisp_ctx.metrics:
                from wisp_framework.observability.metrics import record_command_metric

                record_command_metric(wisp_ctx.metrics, "ping", "success")

            await respond_success(interaction, f"Pong! Latency: {latency}ms", embed=embed)

        # Prefixed ping command
        async def ping_prefixed_command(ctx: commands.Context) -> None:
            """Ping command handler (prefixed)."""
            # Create WispContext for this command execution
            wisp_ctx = get_wisp_context_from_command_context(bot, ctx)
            wisp_ctx.bound_logger.debug("Executing ping command (prefix)")

            latency = round(bot.latency * 1000)

            # Determine status color based on latency
            if latency < 100:
                status = "Excellent"
                color_type = "success"
            elif latency < 200:
                status = "Good"
                color_type = "info"
            elif latency < 500:
                status = "Fair"
                color_type = "warning"
            else:
                status = "Poor"
                color_type = "error"

            # Create appropriate embed
            if color_type == "success":
                embed = EmbedBuilder.success(
                    title="Pong! 🏓",
                    description=f"Latency: **{latency}ms**\nStatus: {status}",
                    fields=[{"name": "Response Time", "value": f"{latency}ms", "inline": True}]
                )
            elif color_type == "info":
                embed = EmbedBuilder.info(
                    title="Pong! 🏓",
                    description=f"Latency: **{latency}ms**\nStatus: {status}",
                    fields=[{"name": "Response Time", "value": f"{latency}ms", "inline": True}]
                )
            elif color_type == "warning":
                embed = EmbedBuilder.warning(
                    title="Pong! 🏓",
                    description=f"Latency: **{latency}ms**\nStatus: {status}",
                    fields=[{"name": "Response Time", "value": f"{latency}ms", "inline": True}]
                )
            else:
                embed = EmbedBuilder.error(
                    title="Pong! 🏓",
                    description=f"Latency: **{latency}ms**\nStatus: {status}",
                    fields=[{"name": "Response Time", "value": f"{latency}ms", "inline": True}]
                )

            # Record metrics using WispContext
            if wisp_ctx.metrics:
                from wisp_framework.observability.metrics import record_command_metric

                record_command_metric(wisp_ctx.metrics, "ping", "success")

            await ctx.send(embed=embed)

        # Register prefixed command
        ping_cmd = commands.Command(ping_prefixed_command, name="ping")
        bot.add_command(ping_cmd)
