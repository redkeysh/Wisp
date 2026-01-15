"""Command group utilities for organizing commands."""

from typing import Any, Optional

import discord
from discord import app_commands


class CommandGroup:
    """Helper for creating command groups."""

    def __init__(
        self,
        name: str,
        description: str,
        guild_only: bool = False,
        default_permissions: Optional[discord.Permissions] = None,
    ) -> None:
        """Initialize command group.

        Args:
            name: Group name
            description: Group description
            guild_only: Whether group is guild-only
            default_permissions: Default permissions required
        """
        self.name = name
        self.description = description
        self.guild_only = guild_only
        self.default_permissions = default_permissions
        self.group: Optional[app_commands.Group] = None

    def create_group(self, tree: app_commands.CommandTree) -> app_commands.Group:
        """Create the command group on a tree.

        Args:
            tree: Command tree

        Returns:
            Created group
        """
        self.group = app_commands.Group(
            name=self.name,
            description=self.description,
            guild_only=self.guild_only,
            default_permissions=self.default_permissions,
        )
        tree.add_command(self.group)
        return self.group

    def command(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ):
        """Decorator to add a command to this group.

        Args:
            name: Command name
            description: Command description
            **kwargs: Additional command options

        Returns:
            Decorator function
        """
        if not self.group:
            raise RuntimeError("Group must be created before adding commands")

        def decorator(func: Any) -> Any:
            cmd_name = name or func.__name__
            cmd_desc = description or func.__doc__ or "No description"
            return self.group.command(name=cmd_name, description=cmd_desc, **kwargs)(func)

        return decorator
