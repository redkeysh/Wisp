"""Insights module - stub module demonstrating scheduler usage."""

from typing import Any

from wisp_framework.module import Module


class InsightsModule(Module):
    """Insights module demonstrating scheduler and per-guild data storage."""

    @property
    def name(self) -> str:
        """Module name."""
        return "insights"

    @property
    def required_services(self) -> set[str]:
        """Required services."""
        return {"scheduler"}

    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the insights module."""
        scheduler = ctx.services.get("scheduler")

        async def periodic_rollup() -> None:
            """Periodic task for insights aggregation."""
            # Create WispContext for job execution
            from wisp_framework.context import WispContext

            wisp_ctx = WispContext.from_job(
                config=bot.config,
                services=bot.services,
                job_id="insights_rollup",
            )
            wisp_ctx.bound_logger.info("Running insights rollup...")

            if ctx.guild_data:
                # Aggregate stats per guild
                for guild in bot.guilds:
                    try:
                        # Get current rollup count
                        current = await ctx.guild_data.get(
                            guild.id, "rollup_count", module_name="insights"
                        ) or 0

                        # Increment and store
                        await ctx.guild_data.set(
                            guild.id,
                            "rollup_count",
                            current + 1,
                            module_name="insights",
                        )

                        # Update metrics using WispContext
                        if wisp_ctx.metrics:
                            from wisp_framework.observability.metrics import normalize_metric_name

                            wisp_ctx.metrics.increment(normalize_metric_name("insights", "rollups"))
                            wisp_ctx.metrics.gauge(
                                normalize_metric_name("insights", f"guild_{guild.id}_rollup_count"),
                                current + 1,
                            )

                    except Exception as e:
                        wisp_ctx.bound_logger.error(f"Error in rollup for guild {guild.id}: {e}", exc_info=True)

            wisp_ctx.bound_logger.info("Insights rollup completed")

        if scheduler:
            # Register a daily rollup (86400 seconds)
            scheduler.register(periodic_rollup, interval=86400.0, name="insights_rollup")
