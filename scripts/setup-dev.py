#!/usr/bin/env python3
"""
Setup script for local development environment.
Cross-platform Python script (works on Windows, Linux, macOS).

Usage:
    python scripts/setup-dev.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Setup development environment."""
    print(">>> Setting up Wisp Framework development environment...")
    print()
    
    # Check Python version
    version_info = sys.version_info
    print(f">>> Found Python {version_info.major}.{version_info.minor}.{version_info.micro}")
    
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 13):
        print(f"ERROR: Python 3.13+ is required, found Python {version_info.major}.{version_info.minor}")
        return 1
    
    # Upgrade pip
    print(">>> Upgrading pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
    
    # Install development dependencies
    print(">>> Installing development dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", ".[all]", "--quiet"],
        check=False,
    )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio", "pytest-cov", "ruff", "build", "--quiet"],
        check=False,
    )
    
    print()
    print(">>> Development environment setup complete!")
    print()
    print("Available commands:")
    print("  python scripts/dev.py lint      - Run linter")
    print("  python scripts/dev.py format     - Format code")
    print("  python scripts/dev.py check      - Run lint + format checks")
    print("  python scripts/dev.py test       - Run tests")
    print("  python scripts/dev.py test-cov   - Run tests with coverage")
    print("  python scripts/dev.py ci         - Run full CI checks")
    print()
    print("Or use Makefile targets (if make is installed):")
    print("  make lint          - Run linter")
    print("  make format        - Format code")
    print("  make check         - Run lint + format checks")
    print("  make test          - Run tests")
    print("  make test-cov      - Run tests with coverage")
    print("  make ci            - Run full CI checks")
    print("  make help          - Show all available targets")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
