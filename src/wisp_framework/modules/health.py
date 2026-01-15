"""Health module - provides /health command."""

from typing import Any

import discord
from discord import app_commands

from wisp_framework.module import Module
from wisp_framework.utils.decorators import handle_errors
from wisp_framework.utils.embeds import EmbedBuilder
from wisp_framework.utils.responses import respond_error, respond_success


class HealthModule(Module):
    """Health check module."""

    @property
    def name(self) -> str:
        """Module name."""
        return "health"

    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the health module."""
        tree = bot.tree

        @tree.command(name="health", description="Check bot health status")
        @handle_errors
        async def health_command(interaction: discord.Interaction) -> None:
            """Health check command."""
            health_service = ctx.services.get("health")
            
            if not health_service:
                await respond_error(interaction, "Health service not available.")
                return

            # Get health status
            health_status = health_service.get_health()
            
            # Check database health dynamically
            db_service = ctx.services.get("db")
            if db_service:
                db_healthy = db_service.engine is not None and db_service.initialized
                health_status["services"]["db"] = {"healthy": db_healthy}
            
            # Recalculate overall health
            all_healthy = all(
                status.get("healthy", False) for status in health_status["services"].values()
            )
            health_status["healthy"] = all_healthy
            
            # Build fields for embed
            fields = []
            
            # Add service statuses
            if health_status["services"]:
                service_text = []
                for service_name, status in health_status["services"].items():
                    status_icon = "✅" if status.get("healthy", False) else "❌"
                    service_text.append(f"{status_icon} {service_name}")
                fields.append({
                    "name": "Services",
                    "value": "\n".join(service_text) or "No services registered",
                    "inline": False
                })
            
            # Add bot metrics if available
            metrics_service = ctx.services.get("metrics")
            if metrics_service:
                metrics = metrics_service.get_metrics()
                if metrics["counters"]:
                    total_commands = metrics["counters"].get("commands.executed", 0)
                    fields.append({
                        "name": "Commands Executed",
                        "value": str(total_commands),
                        "inline": True
                    })
            
            # Create appropriate embed based on health
            if health_status["healthy"]:
                embed = EmbedBuilder.success(
                    title="Bot Health Status",
                    description="All systems operational",
                    fields=fields
                )
            else:
                embed = EmbedBuilder.error(
                    title="Bot Health Status",
                    description="Some services are unhealthy",
                    fields=fields
                )
            
            await respond_success(interaction, "Health check complete", embed=embed)
