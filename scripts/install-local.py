#!/usr/bin/env python3
"""Install Wisp Framework locally in editable mode for development.

Usage:
    python scripts/install-local.py [path/to/bot/directory]
    
If no path is provided, installs in current directory.
"""

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Install Wisp Framework in editable mode."""
    # Get Wisp Framework directory (parent of scripts/)
    wisp_dir = Path(__file__).parent.parent.resolve()
    
    # Get target directory (where to install)
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1]).resolve()
    else:
        target_dir = Path.cwd()
    
    if not target_dir.exists():
        print(f"Error: Target directory does not exist: {target_dir}", file=sys.stderr)
        return 1
    
    if not target_dir.is_dir():
        print(f"Error: Target is not a directory: {target_dir}", file=sys.stderr)
        return 1
    
    print("Installing Wisp Framework in editable mode...")
    print(f"Wisp Framework: {wisp_dir}")
    print(f"Target bot: {target_dir}")
    print()
    
    # Change to target directory
    os.chdir(target_dir)
    
    # Install in editable mode
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(wisp_dir)],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install Wisp Framework: {e}", file=sys.stderr)
        return 1
    
    print()
    print("✅ Wisp Framework installed in editable mode!")
    print()
    print("Changes to Wisp Framework will be immediately available.")
    print("To switch back to PyPI version:")
    print("  pip uninstall wisp-framework")
    print("  pip install wisp-framework")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
