"""Embed builders and helpers for common Discord message patterns."""

from typing import Any

import discord


class EmbedBuilder:
    """Builder for creating Discord embeds with common patterns."""

    @staticmethod
    def success(
        title: str,
        description: str | None = None,
        fields: list[dict[str, Any]] | None = None,
        footer: str | None = None,
    ) -> discord.Embed:
        """Create a success embed (green).

        Args:
            title: Embed title
            description: Embed description
            fields: List of field dicts with 'name', 'value', 'inline' keys
            footer: Footer text

        Returns:
            Discord embed
        """
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
        )
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False),
                )
        if footer:
            embed.set_footer(text=footer)
        return embed

    @staticmethod
    def error(
        title: str,
        description: str | None = None,
        fields: list[dict[str, Any]] | None = None,
        footer: str | None = None,
    ) -> discord.Embed:
        """Create an error embed (red).

        Args:
            title: Embed title
            description: Embed description
            fields: List of field dicts
            footer: Footer text

        Returns:
            Discord embed
        """
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red(),
        )
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False),
                )
        if footer:
            embed.set_footer(text=footer)
        return embed

    @staticmethod
    def info(
        title: str,
        description: str | None = None,
        fields: list[dict[str, Any]] | None = None,
        footer: str | None = None,
    ) -> discord.Embed:
        """Create an info embed (blue).

        Args:
            title: Embed title
            description: Embed description
            fields: List of field dicts
            footer: Footer text

        Returns:
            Discord embed
        """
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=discord.Color.blue(),
        )
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False),
                )
        if footer:
            embed.set_footer(text=footer)
        return embed

    @staticmethod
    def warning(
        title: str,
        description: str | None = None,
        fields: list[dict[str, Any]] | None = None,
        footer: str | None = None,
    ) -> discord.Embed:
        """Create a warning embed (orange).

        Args:
            title: Embed title
            description: Embed description
            fields: List of field dicts
            footer: Footer text

        Returns:
            Discord embed
        """
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=discord.Color.orange(),
        )
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", False),
                )
        if footer:
            embed.set_footer(text=footer)
        return embed

    @staticmethod
    def list_embed(
        title: str,
        items: list[str],
        description: str | None = None,
        items_per_page: int = 10,
        page: int = 1,
        footer: str | None = None,
    ) -> discord.Embed:
        """Create a paginated list embed.

        Args:
            title: Embed title
            items: List of items to display
            description: Embed description
            items_per_page: Number of items per page
            page: Current page (1-indexed)
            footer: Footer text (page info will be appended)

        Returns:
            Discord embed
        """
        total_pages = (len(items) + items_per_page - 1) // items_per_page
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = items[start_idx:end_idx]

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue(),
        )

        if page_items:
            embed.description = (
                (description + "\n\n" if description else "")
                + "\n".join(f"{i+start_idx+1}. {item}" for i, item in enumerate(page_items))
            )
        else:
            embed.description = (description or "") + "\n\n*No items to display.*"

        page_footer = f"Page {page}/{total_pages}"
        if footer:
            embed.set_footer(text=f"{footer} • {page_footer}")
        else:
            embed.set_footer(text=page_footer)

        return embed

    @staticmethod
    def table_embed(
        title: str,
        headers: list[str],
        rows: list[list[str]],
        description: str | None = None,
    ) -> discord.Embed:
        """Create a table-style embed.

        Args:
            title: Embed title
            headers: Column headers
            rows: List of rows (each row is a list of cell values)
            description: Embed description

        Returns:
            Discord embed
        """
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue(),
        )

        if not rows:
            embed.add_field(name="No Data", value="*No data to display*", inline=False)
            return embed

        # Format as a simple table
        max_col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(max_col_widths):
                    max_col_widths[i] = max(max_col_widths[i], len(str(cell)))

        # Build table string
        header_row = " | ".join(h.ljust(max_col_widths[i]) for i, h in enumerate(headers))
        separator = "-" * len(header_row)
        table_lines = [header_row, separator]

        for row in rows:
            row_str = " | ".join(
                str(cell).ljust(max_col_widths[i]) if i < len(max_col_widths) else str(cell)
                for i, cell in enumerate(row)
            )
            table_lines.append(row_str)

        table_text = "```\n" + "\n".join(table_lines) + "\n```"
        embed.add_field(name="\u200b", value=table_text, inline=False)

        return embed


def create_success_embed(
    title: str, description: str | None = None, **kwargs: Any
) -> discord.Embed:
    """Convenience function for success embeds."""
    return EmbedBuilder.success(title, description, **kwargs)


def create_error_embed(
    title: str, description: str | None = None, **kwargs: Any
) -> discord.Embed:
    """Convenience function for error embeds."""
    return EmbedBuilder.error(title, description, **kwargs)


def create_info_embed(
    title: str, description: str | None = None, **kwargs: Any
) -> discord.Embed:
    """Convenience function for info embeds."""
    return EmbedBuilder.info(title, description, **kwargs)


def create_warning_embed(
    title: str, description: str | None = None, **kwargs: Any
) -> discord.Embed:
    """Convenience function for warning embeds."""
    return EmbedBuilder.warning(title, description, **kwargs)
