"""Onboarding module - welcome messages for new members."""

from typing import Any

import discord

from wisp_framework.context import WispContext
from wisp_framework.module import Module
from wisp_framework.utils.context_helpers import get_wisp_context_from_event
from wisp_framework.utils.event_helpers import register_event_handler


class OnboardingModule(Module):
    """Onboarding module for welcoming new members."""

    @property
    def name(self) -> str:
        """Module name."""
        return "onboarding"

    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the onboarding module."""
        # Register event handler with EventRouter for pipeline benefits
        # This provides: request_id tracking, rate limiting, metrics, error handling

        async def handle_member_join(wisp_ctx: WispContext, member: discord.Member) -> None:
            """Handle member join event with full pipeline support.

            This handler receives WispContext automatically from the EventRouter,
            which includes request_id, bound_logger, metrics, etc.
            """
            if not member.guild:
                return

            wisp_ctx.bound_logger.info(f"Member joined: {member.name} (ID: {member.id})")

            # Get welcome channel
            welcome_channel_id = wisp_ctx.config.welcome_channel_id

            # Try to get from database if available
            db_service = wisp_ctx.services.get("db")
            if db_service and db_service.session_factory:
                try:
                    from sqlalchemy import select

                    from wisp_framework.db.models import GuildConfig

                    async with db_service.session_factory() as session:
                        stmt = select(GuildConfig).where(
                            GuildConfig.guild_id == member.guild.id
                        )
                        result = await session.execute(stmt)
                        guild_config = result.scalar_one_or_none()
                        if guild_config and guild_config.welcome_channel_id:
                            welcome_channel_id = guild_config.welcome_channel_id
                except Exception as e:
                    wisp_ctx.bound_logger.warning(f"Failed to get guild config: {e}")

            if welcome_channel_id:
                channel = member.guild.get_channel(welcome_channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    # Use embed builder for nicer welcome message
                    from wisp_framework.utils.embeds import EmbedBuilder

                    embed = EmbedBuilder.success(
                        title=f"Welcome to {member.guild.name}! 🎉",
                        description=f"{member.mention} has joined the server.",
                        fields=[
                            {"name": "Member", "value": f"{member.mention}\n{member.name}", "inline": True},
                            {"name": "Account Created", "value": f"<t:{int(member.created_at.timestamp())}:R>", "inline": True},
                        ]
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)

                    await channel.send(embed=embed)

                    # Metrics are automatically recorded by pipeline!
                    # But we can also record custom metrics if needed
                    wisp_ctx.bound_logger.info(f"Sent welcome message for {member.name}")

        # Register with EventRouter using helper function
        # Falls back to @bot.event if EventRouter not available
        if not register_event_handler(
            bot,
            "on_member_join",
            handle_member_join,
            priority=10,  # Higher priority = runs first
            module_name=self.name,
        ):
            # Fallback to @bot.event for backward compatibility
            @bot.event
            async def on_member_join(member: discord.Member) -> None:
                """Handle member join event (fallback mode)."""
                # Create WispContext manually (no pipeline benefits)
                wisp_ctx = get_wisp_context_from_event(bot, member)
                await handle_member_join(wisp_ctx, member)
