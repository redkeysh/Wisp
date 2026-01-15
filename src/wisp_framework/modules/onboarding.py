"""Onboarding module - welcome messages for new members."""

from typing import Any

import discord

from wisp_framework.module import Module


class OnboardingModule(Module):
    """Onboarding module for welcoming new members."""

    @property
    def name(self) -> str:
        """Module name."""
        return "onboarding"

    async def setup(self, bot: Any, ctx: Any) -> None:
        """Set up the onboarding module."""

        @bot.event
        async def on_member_join(member: discord.Member) -> None:
            """Handle member join event."""
            if not member.guild:
                return

            # Get welcome channel
            welcome_channel_id = ctx.config.welcome_channel_id

            # Try to get from database if available
            db_service = ctx.services.get("db")
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
                    ctx.services.get("logger").warning(
                        f"Failed to get guild config: {e}"
                    )

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