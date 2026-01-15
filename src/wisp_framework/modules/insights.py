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
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info("Running insights rollup...")
            
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
                        
                        # Update metrics if available
                        metrics = ctx.services.get("metrics")
                        if metrics:
                            metrics.increment("insights.rollups")
                            metrics.gauge(f"insights.guild_{guild.id}.rollup_count", current + 1)
                        
                    except Exception as e:
                        logger.error(f"Error in rollup for guild {guild.id}: {e}")
            
            logger.info("Insights rollup completed")

        if scheduler:
            # Register a daily rollup (86400 seconds)
            scheduler.register(periodic_rollup, interval=86400.0, name="insights_rollup")
