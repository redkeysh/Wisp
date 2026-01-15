#!/bin/bash
# Local development script that replicates CI checks
# Usage: ./scripts/dev.sh [lint|test|format|check|ci|all]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Function to print colored output
print_status() {
    echo -e "${GREEN}>>>${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# Check if Python 3.13+ is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 13 ]); then
        print_error "Python 3.13+ is required, found Python $PYTHON_VERSION"
        exit 1
    fi
    
    print_status "Python version: $(python3 --version)"
}

# Install dependencies
install_deps() {
    print_status "Installing dependencies..."
    python3 -m pip install --upgrade pip --quiet
    pip install -e . --quiet
    pip install pytest pytest-asyncio pytest-cov ruff build --quiet
}

# Run linting
run_lint() {
    print_status "Running ruff linter..."
    if ruff check src/; then
        print_status "Linting passed ✓"
        return 0
    else
        print_error "Linting failed"
        return 1
    fi
}

# Run formatting check
run_format_check() {
    print_status "Checking code formatting..."
    if ruff format --check src/; then
        print_status "Formatting check passed ✓"
        return 0
    else
        print_warning "Code formatting issues found. Run 'make format' to fix."
        return 1
    fi
}

# Run tests
run_tests() {
    local test_name="${1:-Tests}"
    
    print_status "Running $test_name..."
    if pytest tests/ -v --cov=src --cov-report=term --cov-report=xml; then
        print_status "$test_name passed ✓"
        return 0
    else
        print_error "$test_name failed"
        return 1
    fi
}

# Run all checks
run_ci() {
    print_status "Running full CI checks..."
    local failed=0
    
    # Linting
    if ! run_lint; then
        failed=1
    fi
    
    # Format check
    if ! run_format_check; then
        failed=1
    fi
    
    # Run tests
    print_status "Installing dependencies..."
    install_deps
    if ! run_tests "Tests"; then
        failed=1
    fi
    
    if [ $failed -eq 0 ]; then
        print_status "All CI checks passed! ✓"
        return 0
    else
        print_error "Some CI checks failed"
        return 1
    fi
}

# Build package
build_package() {
    print_status "Building distribution packages..."
    python3 -m pip install --upgrade pip build --quiet
    if python3 -m build; then
        print_status "Package built successfully ✓"
        print_status "Packages are in dist/"
        return 0
    else
        print_error "Package build failed"
        return 1
    fi
}

# Main
main() {
    check_python
    
    case "${1:-all}" in
        lint)
            install_deps
            run_lint
            ;;
        format)
            install_deps
            print_status "Formatting code..."
            ruff format src/
            print_status "Formatting complete ✓"
            ;;
        format-check)
            install_deps
            run_format_check
            ;;
        check)
            install_deps
            run_lint
            run_format_check
            ;;
        test)
            install_deps
            run_tests "Tests"
            ;;
        build)
            build_package
            ;;
        ci)
            run_ci
            ;;
        all|*)
            run_ci
            ;;
    esac
}

main "$@"
