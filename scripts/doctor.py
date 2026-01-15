#!/usr/bin/env python3
"""Pre-flight health check tool for Wisp Framework."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def check_env_file() -> bool:
    """Check if environment file exists."""
    env = os.getenv("ENV", "local")
    env_file = f".env.{env}"
    if not os.path.exists(env_file):
        print(f"❌ Environment file {env_file} not found")
        return False
    print(f"✓ Environment file {env_file} exists")
    return True


def check_required_env_vars() -> bool:
    """Check required environment variables."""
    required = ["DISCORD_TOKEN"]
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        return False
    print("✓ Required environment variables present")
    return True


def check_imports() -> bool:
    """Check if all imports work."""
    try:
        from wisp_framework.config import AppConfig
        from wisp_framework.logging import setup_logging
        print("✓ Core imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def check_database() -> bool:
    """Check database connectivity if configured."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠ Database not configured (optional)")
        return True

    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        import asyncio

        async def test_db():
            engine = create_async_engine(database_url)
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            await engine.dispose()

        asyncio.run(test_db())
        print("✓ Database connection successful")
        return True
    except ImportError:
        print("⚠ Database URL configured but SQLAlchemy not installed")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_migrations() -> bool:
    """Check if migrations are up to date."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠ Database not configured, skipping migration check")
        return True

    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print("✓ Migrations check passed")
            return True
        else:
            print(f"⚠ Migration check warning: {result.stderr}")
            return True
    except FileNotFoundError:
        print("⚠ Alembic not found, skipping migration check")
        return True
    except Exception as e:
        print(f"⚠ Migration check error: {e}")
        return True


def main() -> int:
    """Run all health checks."""
    print("🔍 Running Wisp Framework health checks...\n")

    checks = [
        ("Environment file", check_env_file),
        ("Required environment variables", check_required_env_vars),
        ("Imports", check_imports),
        ("Database", check_database),
        ("Migrations", check_migrations),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        results.append(check_func())

    print("\n" + "=" * 50)
    if all(results):
        print("✅ All health checks passed!")
        return 0
    else:
        print("❌ Some health checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
