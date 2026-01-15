#!/usr/bin/env python3
"""
Local development script that replicates CI checks.
Cross-platform Python script (works on Windows, Linux, macOS).

Usage:
    python scripts/dev.py [lint|test|format|check|ci|all]
    python scripts/dev.py --help
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color

    @staticmethod
    def disable():
        """Disable colors on Windows if needed."""
        Colors.RED = ""
        Colors.GREEN = ""
        Colors.YELLOW = ""
        Colors.BLUE = ""
        Colors.NC = ""


def print_status(msg: str) -> None:
    """Print a status message."""
    # Replace checkmark with [OK] for Windows compatibility
    msg = msg.replace("✓", "[OK]")
    print(f"{Colors.GREEN}>>>{Colors.NC} {msg}")


def print_error(msg: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}ERROR:{Colors.NC} {msg}")


def print_warning(msg: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}WARNING:{Colors.NC} {msg}")


def run_command(cmd: list[str], check: bool = True, capture: bool = False) -> tuple[int, str]:
    """Run a command and return exit code and output."""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture,
            text=True,
        )
        output = result.stdout if capture else ""
        return result.returncode, output
    except subprocess.CalledProcessError as e:
        if capture:
            return e.returncode, e.stdout + e.stderr
        return e.returncode, ""
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
        print_error(f"Please install: {cmd[0]}")
        return 1, ""


def check_python() -> bool:
    """Check if Python 3.13+ is available."""
    print_status("Checking Python version...")
    result = subprocess.run(
        [sys.executable, "--version"],
        capture_output=True,
        text=True,
    )
    version_str = result.stdout.strip()
    print_status(f"Found {version_str}")
    
    # Check version
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 13):
        print_error(f"Python 3.13+ is required, found Python {version_info.major}.{version_info.minor}")
        return False
    return True


def install_deps() -> bool:
    """Install dependencies."""
    print_status("Installing dependencies...")
    
    # Upgrade pip
    code, _ = run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
    if code != 0:
        print_warning("Failed to upgrade pip, continuing anyway...")
    
    # Install package
    install_cmd = [sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"]
    code, _ = run_command(install_cmd, check=False)
    if code != 0:
        print_error("Failed to install package")
        return False
    
    # Install test dependencies
    test_deps = ["pytest", "pytest-asyncio", "pytest-cov", "ruff", "build"]
    code, _ = run_command(
        [sys.executable, "-m", "pip", "install"] + test_deps + ["--quiet"],
        check=False,
    )
    if code != 0:
        print_warning("Some test dependencies may not be installed")
    
    return True


def run_lint() -> bool:
    """Run linting."""
    print_status("Running ruff linter...")
    code, _ = run_command([sys.executable, "-m", "ruff", "check", "src/"], check=False)
    if code == 0:
        print_status("Linting passed ✓")
        return True
    else:
        print_error("Linting failed")
        return False


def run_format_check() -> bool:
    """Check code formatting."""
    print_status("Checking code formatting...")
    code, _ = run_command(
        [sys.executable, "-m", "ruff", "format", "--check", "src/"],
        check=False,
    )
    if code == 0:
        print_status("Formatting check passed ✓")
        return True
    else:
        print_warning("Code formatting issues found. Run 'python scripts/dev.py format' to fix.")
        return False


def run_format() -> bool:
    """Format code."""
    print_status("Formatting code...")
    code, _ = run_command([sys.executable, "-m", "ruff", "format", "src/"], check=False)
    if code == 0:
        print_status("Formatting complete ✓")
        return True
    else:
        print_error("Formatting failed")
        return False


def run_tests(test_name: str = "Tests") -> bool:
    """Run tests."""
    print_status(f"Running {test_name}...")
    code, _ = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--cov=src",
            "--cov-report=term",
            "--cov-report=xml",
        ],
        check=False,
    )
    if code == 0:
        print_status(f"{test_name} passed ✓")
        return True
    else:
        print_error(f"{test_name} failed")
        return False


def build_package() -> bool:
    """Build distribution packages."""
    print_status("Building distribution packages...")
    code, _ = run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "build", "--quiet"],
        check=False,
    )
    code, _ = run_command([sys.executable, "-m", "build"], check=False)
    if code == 0:
        print_status("Package built successfully ✓")
        print_status("Packages are in dist/")
        return True
    else:
        print_error("Package build failed")
        return False


def run_ci() -> bool:
    """Run full CI checks."""
    print_status("Running full CI checks...")
    failed = False
    
    # Linting
    if not run_lint():
        failed = True
    
    # Format check
    if not run_format_check():
        failed = True
    
    # Run tests
    print_status("Installing dependencies...")
    if not install_deps():
        failed = True
    elif not run_tests("Tests"):
        failed = True
    
    if not failed:
        print_status("All CI checks passed! ✓")
        return True
    else:
        print_error("Some CI checks failed")
        return False


def main() -> int:
    """Main entry point."""
    # Disable colors on Windows if terminal doesn't support them
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Try to enable ANSI colors on Windows 10+
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            Colors.disable()
    
    parser = argparse.ArgumentParser(
        description="Local development script that replicates CI checks"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="ci",
        choices=["lint", "format", "format-check", "check", "test", "build", "ci", "all"],
        help="Command to run (default: ci)",
    )
    
    args = parser.parse_args()
    
    if not check_python():
        return 1
    
    command = args.command
    
    if command == "lint":
        if not install_deps():
            return 1
        return 0 if run_lint() else 1
    
    elif command == "format":
        if not install_deps():
            return 1
        return 0 if run_format() else 1
    
    elif command == "format-check":
        if not install_deps():
            return 1
        return 0 if run_format_check() else 1
    
    elif command == "check":
        if not install_deps():
            return 1
        lint_ok = run_lint()
        format_ok = run_format_check()
        return 0 if (lint_ok and format_ok) else 1
    
    elif command == "test":
        if not install_deps():
            return 1
        return 0 if run_tests("Tests") else 1
    
    elif command == "build":
        return 0 if build_package() else 1
    
    elif command in ("ci", "all"):
        return 0 if run_ci() else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
