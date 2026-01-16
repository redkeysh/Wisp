#!/bin/bash
# Quick script to install Wisp Framework locally in editable mode
# Usage: ./scripts/install-local.sh /path/to/echo/bot

set -e

WISP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${1:-.}"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Target directory does not exist: $TARGET_DIR"
    echo "Usage: $0 [path/to/bot/directory]"
    exit 1
fi

echo "Installing Wisp Framework in editable mode..."
echo "Wisp Framework: $WISP_DIR"
echo "Target bot: $TARGET_DIR"
echo ""

cd "$TARGET_DIR"

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "Error: pip not found. Please install pip first."
    exit 1
fi

# Install in editable mode
pip install -e "$WISP_DIR"

echo ""
echo "✅ Wisp Framework installed in editable mode!"
echo ""
echo "Changes to Wisp Framework will be immediately available."
echo "To switch back to PyPI version: pip uninstall wisp-framework && pip install wisp-framework"
