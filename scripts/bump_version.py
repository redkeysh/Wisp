#!/usr/bin/env python3
"""Script to bump version, create git tag, commit, and push.

Usage:
    python scripts/bump_version.py [major|minor|patch]
    python scripts/bump_version.py patch  # Default
    python scripts/bump_version.py minor
    python scripts/bump_version.py major
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Ensure stdout can handle Unicode characters on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    NC = '\033[0m'  # No Color


def print_status(msg: str) -> None:
    print(f"{Colors.CYAN}>>>{Colors.NC} {msg}")


def print_success(msg: str) -> None:
    print(f"{Colors.GREEN}✓{Colors.NC} {msg}")


def print_error(msg: str) -> None:
    print(f"{Colors.RED}✗{Colors.NC} {msg}")


def print_warning(msg: str) -> None:
    print(f"{Colors.YELLOW}⚠{Colors.NC} {msg}")


def run_command(cmd: list[str], check: bool = True) -> tuple[int, str]:
    """Run a shell command and return exit code and output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stderr.strip()
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
        sys.exit(1)


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"
    
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        print_error("Could not find version in pyproject.toml")
        sys.exit(1)
    
    return match.group(1)


def increment_version(version: str, bump_type: str) -> str:
    """Increment version based on bump type."""
    parts = version.split('.')
    if len(parts) != 3:
        print_error(f"Invalid version format: {version}")
        sys.exit(1)
    
    major, minor, patch = map(int, parts)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print_error(f"Invalid bump type: {bump_type}")
        sys.exit(1)
    
    return f"{major}.{minor}.{patch}"


def update_version_files(new_version: str) -> None:
    """Update version in pyproject.toml and version.py."""
    project_root = Path(__file__).parent.parent
    
    # Update pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(
        r'^version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    
    with open(pyproject_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Update version.py
    version_path = project_root / "src" / "wisp_framework" / "version.py"
    with open(version_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
        content
    )
    
    with open(version_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success(f"Updated version to {new_version}")


def check_git_status() -> bool:
    """Check if git working directory is clean."""
    code, output = run_command(["git", "status", "--porcelain"], check=False)
    if code != 0:
        print_error("Failed to check git status")
        return False
    
    if output:
        print_warning("Working directory has uncommitted changes:")
        print(output)
        return False
    
    return True


def create_tag_and_push(version: str, push: bool = True) -> None:
    """Create git tag and optionally push."""
    tag_name = f"v{version}"
    
    # Check if tag already exists
    code, _ = run_command(["git", "tag", "-l", tag_name], check=False)
    if code == 0:
        # Check if tag exists remotely
        code, output = run_command(["git", "ls-remote", "--tags", "origin", tag_name], check=False)
        if tag_name in output:
            print_error(f"Tag {tag_name} already exists remotely")
            sys.exit(1)
    
    # Create tag
    print_status(f"Creating tag {tag_name}...")
    code, _ = run_command(["git", "tag", tag_name])
    if code != 0:
        print_error("Failed to create tag")
        sys.exit(1)
    
    print_success(f"Created tag {tag_name}")
    
    if push:
        # Push commit
        print_status("Pushing commit...")
        code, _ = run_command(["git", "push"])
        if code != 0:
            print_warning("Failed to push commit (tag will still be pushed)")
        else:
            print_success("Pushed commit")
        
        # Push tag
        print_status(f"Pushing tag {tag_name}...")
        code, _ = run_command(["git", "push", "origin", tag_name])
        if code != 0:
            print_error("Failed to push tag")
            sys.exit(1)
        
        print_success(f"Pushed tag {tag_name}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bump version, create git tag, commit, and push",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/bump_version.py patch    # 0.5.5 -> 0.5.6
  python scripts/bump_version.py minor    # 0.5.5 -> 0.6.0
  python scripts/bump_version.py major    # 0.5.5 -> 1.0.0
  python scripts/bump_version.py patch --no-push  # Don't push to remote
        """
    )
    parser.add_argument(
        "bump_type",
        nargs="?",
        default="patch",
        choices=["major", "minor", "patch"],
        help="Version bump type (default: patch)"
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push commit and tag to remote"
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip git status check (use with caution)"
    )
    
    args = parser.parse_args()
    
    # Get current version
    current_version = get_current_version()
    print_status(f"Current version: {current_version}")
    
    # Calculate new version
    new_version = increment_version(current_version, args.bump_type)
    print_status(f"New version: {new_version}")
    
    # Confirm
    response = input(f"\nProceed with version bump to {new_version}? [y/N]: ")
    if response.lower() != 'y':
        print_status("Cancelled")
        return 0
    
    # Check git status
    if not args.skip_check:
        print_status("Checking git status...")
        if not check_git_status():
            print_error("Working directory is not clean. Commit or stash changes first.")
            return 1
    
    # Update version files
    print_status("Updating version files...")
    update_version_files(new_version)
    
    # Commit changes
    print_status("Committing version changes...")
    code, _ = run_command([
        "git", "add",
        "pyproject.toml",
        "src/wisp_framework/version.py"
    ])
    if code != 0:
        print_error("Failed to stage version files")
        return 1
    
    code, _ = run_command([
        "git", "commit",
        "-m", f"chore: bump version to {new_version}"
    ])
    if code != 0:
        print_error("Failed to commit version changes")
        return 1
    
    print_success("Committed version changes")
    
    # Create tag and push
    create_tag_and_push(new_version, push=not args.no_push)
    
    print_success(f"\nVersion bump complete: {current_version} -> {new_version}")
    if not args.no_push:
        print_status(f"Tag {new_version} pushed. CI will build and release automatically.")
    else:
        print_warning("Tag created locally but not pushed. Run 'git push --tags' when ready.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
