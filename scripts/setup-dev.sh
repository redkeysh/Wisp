#!/bin/bash
# Setup script for local development environment
# Usage: ./scripts/setup-dev.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo ">>> Setting up Wisp Framework development environment..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo ">>> Found $PYTHON_VERSION"

# Upgrade pip
echo ">>> Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# Install development dependencies
echo ">>> Installing development dependencies..."
pip install -e ".[all]" --quiet
pip install pytest pytest-asyncio pytest-cov ruff build --quiet

echo ""
echo ">>> Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  make lint          - Run linter"
echo "  make format        - Format code"
echo "  make check         - Run lint + format checks"
echo "  make test          - Run tests"
echo "  make test-cov      - Run tests with coverage"
echo "  make ci            - Run full CI checks"
echo "  ./scripts/dev.sh   - Run dev script (same as make ci)"
echo ""
echo "Or use: make help for all available targets"
