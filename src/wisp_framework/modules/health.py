"""Health module - provides /health command."""

from typing import Any

import discord

from wisp_framework.module import Module
from wisp_framework.utils.context_helpers import get_wisp_context_from_interaction
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
            # Create WispContext for this command execution
            wisp_ctx = get_wisp_context_from_interaction(bot, interaction, "slash")
            wisp_ctx.bound_logger.debug("Executing health command")

            health_service = wisp_ctx.services.get("health")

            if not health_service:
                await respond_error(interaction, "Health service not available.")
                return

            # Get health status
            health_status = health_service.get_health()

            # Check database health dynamically
            db_service = wisp_ctx.services.get("db")
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

            # Add bot metrics if available (using WispContext)
            if wisp_ctx.metrics:
                metrics = wisp_ctx.metrics.get_metrics()
                if metrics["counters"]:
                    # Use normalized metric names
                    from wisp_framework.observability.metrics import normalize_metric_name

                    total_commands = metrics["counters"].get(
                        normalize_metric_name("commands", "success"), 0
                    )
                    fields.append({
                        "name": "Commands Executed",
                        "value": str(total_commands),
                        "inline": True
                    })

            # Log health check with request_id
            wisp_ctx.bound_logger.info(
                f"Health check completed: {'healthy' if all_healthy else 'unhealthy'}"
            )

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
