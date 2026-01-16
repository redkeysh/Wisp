"""Plugin migration support."""

import logging
from pathlib import Path
from typing import Any

from alembic.config import Config

logger = logging.getLogger(__name__)


def discover_plugin_migrations(plugin_dir: Path) -> list[Path]:
    """Discover migration directories for plugins.

    Args:
        plugin_dir: Directory containing plugins

    Returns:
        List of migration directory paths
    """
    migrations = []
    if not plugin_dir.exists():
        return migrations

    for plugin_path in plugin_dir.iterdir():
        if not plugin_path.is_dir():
            continue

        migrations_path = plugin_path / "migrations" / "versions"
        if migrations_path.exists() and migrations_path.is_dir():
            migrations.append(migrations_path)

    return migrations


def merge_plugin_migrations_into_alembic(
    alembic_cfg: Config, plugin_migration_dirs: list[Path]
) -> None:
    """Merge plugin migrations into Alembic configuration.

    This modifies the Alembic config to include plugin migrations.

    Args:
        alembic_cfg: Alembic configuration object
        plugin_migration_dirs: List of plugin migration directories
    """
    # This is a placeholder - full implementation would require
    # modifying Alembic's script directory discovery
    # For now, plugins can use Alembic's standard migration system
    # by including their migrations in the main migrations directory
    # with a naming convention like: {plugin_name}_{revision}.py

    logger.info(f"Found {len(plugin_migration_dirs)} plugin migration directories")
    for migration_dir in plugin_migration_dirs:
        logger.debug(f"Plugin migration directory: {migration_dir}")


def apply_plugin_migrations(
    alembic_cfg: Config,
    plugin_migration_dirs: list[Path],
    connection: Any,
    target_metadata: Any,
) -> None:
    """Apply plugin migrations in dependency order.

    Args:
        alembic_cfg: Alembic configuration
        plugin_migration_dirs: List of plugin migration directories
        connection: Database connection
        target_metadata: SQLAlchemy metadata
    """
    # Plugin migrations should be applied after core migrations
    # They should be included in the main Alembic migration chain
    # with proper dependency ordering

    logger.info("Applying plugin migrations...")
    for migration_dir in plugin_migration_dirs:
        logger.debug(f"Processing plugin migrations from: {migration_dir}")
        # In a full implementation, this would:
        # 1. Load migration scripts from the directory
        # 2. Resolve dependencies
        # 3. Apply them in order
        # For now, this is a placeholder
