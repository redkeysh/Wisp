#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test compatibility with updated dependency versions."""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_imports():
    """Test that all framework imports work."""
    print("=" * 80)
    print("TESTING IMPORTS")
    print("=" * 80)
    print()
    
    imports_to_test = [
        ("discord", "discord.py"),
        ("discord.ext.commands", "discord.py commands"),
        ("discord.app_commands", "discord.py app_commands"),
        ("sqlalchemy", "SQLAlchemy"),
        ("sqlalchemy.ext.asyncio", "SQLAlchemy async"),
        ("asyncpg", "asyncpg"),
        ("alembic", "Alembic"),
        ("redis", "Redis"),
        ("prometheus_client", "Prometheus client"),
        ("sentry_sdk", "Sentry SDK"),
    ]
    
    results = []
    
    for module_name, display_name in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {display_name:<30} - Import successful")
            results.append((display_name, True, None))
        except ImportError as e:
            print(f"❌ {display_name:<30} - Import failed: {e}")
            results.append((display_name, False, str(e)))
        except Exception as e:
            print(f"⚠️  {display_name:<30} - Unexpected error: {e}")
            results.append((display_name, False, str(e)))
    
    print()
    return results


def test_framework_imports():
    """Test framework imports."""
    print("=" * 80)
    print("TESTING FRAMEWORK IMPORTS")
    print("=" * 80)
    print()
    
    # Add src to path
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    framework_imports = [
        "wisp_framework",
        "wisp_framework.bot",
        "wisp_framework.config",
        "wisp_framework.module",
        "wisp_framework.registry",
        "wisp_framework.context",
        "wisp_framework.services.base",
        "wisp_framework.db.base",
    ]
    
    results = []
    
    for module_name in framework_imports:
        try:
            module = __import__(module_name, fromlist=[''])
            print(f"✅ {module_name:<40} - Import successful")
            results.append((module_name, True, None))
        except ImportError as e:
            print(f"❌ {module_name:<40} - Import failed: {e}")
            results.append((module_name, False, str(e)))
        except Exception as e:
            print(f"⚠️  {module_name:<40} - Unexpected error: {e}")
            results.append((module_name, False, str(e)))
    
    print()
    return results


def test_version_compatibility():
    """Test version compatibility."""
    print("=" * 80)
    print("TESTING VERSION COMPATIBILITY")
    print("=" * 80)
    print()
    
    version_checks = []
    
    # Check discord.py version
    try:
        import discord
        version = discord.__version__
        print(f"✅ discord.py version: {version}")
        version_checks.append(("discord.py", version, True))
    except Exception as e:
        print(f"❌ discord.py version check failed: {e}")
        version_checks.append(("discord.py", None, False))
    
    # Check SQLAlchemy version
    try:
        import sqlalchemy
        version = sqlalchemy.__version__
        print(f"✅ SQLAlchemy version: {version}")
        version_checks.append(("SQLAlchemy", version, True))
    except ImportError:
        print("⚠️  SQLAlchemy not installed (optional dependency)")
        version_checks.append(("SQLAlchemy", None, None))
    except Exception as e:
        print(f"❌ SQLAlchemy version check failed: {e}")
        version_checks.append(("SQLAlchemy", None, False))
    
    # Check asyncpg version
    try:
        import asyncpg
        version = asyncpg.__version__
        print(f"✅ asyncpg version: {version}")
        version_checks.append(("asyncpg", version, True))
    except ImportError:
        print("⚠️  asyncpg not installed (optional dependency)")
        version_checks.append(("asyncpg", None, None))
    except Exception as e:
        print(f"❌ asyncpg version check failed: {e}")
        version_checks.append(("asyncpg", None, False))
    
    # Check Redis version
    try:
        import redis
        version = redis.__version__
        print(f"✅ Redis version: {version}")
        version_checks.append(("Redis", version, True))
    except ImportError:
        print("⚠️  Redis not installed (optional dependency)")
        version_checks.append(("Redis", None, None))
    except Exception as e:
        print(f"❌ Redis version check failed: {e}")
        version_checks.append(("Redis", None, False))
    
    print()
    return version_checks


def test_basic_functionality():
    """Test basic framework functionality."""
    print("=" * 80)
    print("TESTING BASIC FUNCTIONALITY")
    print("=" * 80)
    print()
    
    # Add src to path
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    tests = []
    
    # Test AppConfig creation
    try:
        from wisp_framework.config import AppConfig
        # Don't actually create it (needs DISCORD_TOKEN)
        print("✅ AppConfig class import successful")
        tests.append(("AppConfig import", True))
    except Exception as e:
        print(f"❌ AppConfig import failed: {e}")
        tests.append(("AppConfig import", False))
    
    # Test Module base class
    try:
        from wisp_framework.module import Module
        print("✅ Module base class import successful")
        tests.append(("Module import", True))
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        tests.append(("Module import", False))
    
    # Test FrameworkBot class
    try:
        from wisp_framework.bot import FrameworkBot
        print("✅ FrameworkBot class import successful")
        tests.append(("FrameworkBot import", True))
    except Exception as e:
        print(f"❌ FrameworkBot import failed: {e}")
        tests.append(("FrameworkBot import", False))
    
    # Test ServiceContainer
    try:
        from wisp_framework.services.base import ServiceContainer
        print("✅ ServiceContainer class import successful")
        tests.append(("ServiceContainer import", True))
    except Exception as e:
        print(f"❌ ServiceContainer import failed: {e}")
        tests.append(("ServiceContainer import", False))
    
    # Test discord.py Intents
    try:
        import discord
        intents = discord.Intents.default()
        intents.message_content = True
        print("✅ Discord Intents creation successful")
        tests.append(("Discord Intents", True))
    except Exception as e:
        print(f"❌ Discord Intents test failed: {e}")
        tests.append(("Discord Intents", False))
    
    # Test SQLAlchemy async (if available)
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        print("✅ SQLAlchemy async imports successful")
        tests.append(("SQLAlchemy async", True))
    except ImportError:
        print("⚠️  SQLAlchemy async not available (optional)")
        tests.append(("SQLAlchemy async", None))
    except Exception as e:
        print(f"❌ SQLAlchemy async test failed: {e}")
        tests.append(("SQLAlchemy async", False))
    
    print()
    return tests


def main():
    """Run all compatibility tests."""
    print()
    print("=" * 80)
    print("WISP FRAMEWORK COMPATIBILITY TEST")
    print("=" * 80)
    print()
    
    # Run tests
    import_results = test_imports()
    framework_results = test_framework_imports()
    version_results = test_version_compatibility()
    functionality_results = test_basic_functionality()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    total_imports = len(import_results)
    successful_imports = sum(1 for _, success, _ in import_results if success)
    failed_imports = sum(1 for _, success, _ in import_results if not success)
    
    total_framework = len(framework_results)
    successful_framework = sum(1 for _, success, _ in framework_results if success)
    failed_framework = sum(1 for _, success, _ in framework_results if not success)
    
    total_functionality = len(functionality_results)
    successful_functionality = sum(1 for _, success in functionality_results if success)
    failed_functionality = sum(1 for _, success in functionality_results if success is False)
    
    print(f"External Dependencies:")
    print(f"  ✅ Successful: {successful_imports}/{total_imports}")
    print(f"  ❌ Failed: {failed_imports}/{total_imports}")
    print()
    
    print(f"Framework Imports:")
    print(f"  ✅ Successful: {successful_framework}/{total_framework}")
    print(f"  ❌ Failed: {failed_framework}/{total_framework}")
    print()
    
    print(f"Functionality Tests:")
    print(f"  ✅ Successful: {successful_functionality}/{total_functionality}")
    print(f"  ❌ Failed: {failed_functionality}/{total_functionality}")
    print()
    
    # Overall status
    all_passed = (
        failed_imports == 0 and
        failed_framework == 0 and
        failed_functionality == 0
    )
    
    if all_passed:
        print("✅ All compatibility tests passed!")
        return 0
    else:
        print("⚠️  Some compatibility tests failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
