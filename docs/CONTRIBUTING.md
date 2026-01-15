# Contributing Guide

Thank you for your interest in contributing to the Wisp Framework! This guide will help you get started.

> **See also:** [[Architecture-Overview]] | [[API-Reference]] | [[Module-Development]]

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

### Prerequisites

- Python 3.13+
- Git
- Basic understanding of Discord bots and Python

### Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/wisp.git
cd wisp

# Add upstream remote
git remote add upstream https://github.com/redkeysh/wisp.git
```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install in editable mode with all extras
pip install -e ".[db,redis,all]"

# Install development dependencies
pip install pytest pytest-asyncio ruff mypy
```

### 3. Set Up Environment

```bash
# Copy example environment file
cp .env.local.example .env.local

# Edit .env.local with your Discord token
# DISCORD_TOKEN=your_token_here
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/wisp_framework

# Run specific test
pytest tests/test_module.py
```

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring

### Example Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ...

# Commit changes
git add .
git commit -m "feat: add my feature"

# Push to your fork
git push origin feature/my-feature

# Create pull request on GitHub
```

## Code Style

### Type Hints

Always use type hints:

```python
from typing import Optional, List

def my_function(param: str) -> Optional[int]:
    return None
```

### Formatting

We use `ruff` for formatting:

```bash
# Format code
ruff format src/

# Check code
ruff check src/
```

### Line Length

Maximum line length: 100 characters

### Imports

Organize imports:

```python
# Standard library
import os
from typing import Optional

# Third-party
import discord

# Local
from wisp_framework.module import Module
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(param: str) -> int:
    """Brief description.
    
    Longer description if needed.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
        
    Raises:
        ValueError: When param is invalid
    """
    pass
```

## Testing

### Writing Tests

```python
import pytest
from wisp_framework.module import Module

def test_module_creation():
    class TestModule(Module):
        @property
        def name(self) -> str:
            return "test"
        
        async def setup(self, bot, ctx):
            pass
    
    module = TestModule()
    assert module.name == "test"
```

### Test Structure

- Tests go in `tests/` directory
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_module.py

# Specific test
pytest tests/test_module.py::test_module_creation

# With coverage
pytest --cov=src/wisp_framework --cov-report=html
```

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Document parameters and return values
- Include examples for complex functions

### Documentation Updates

When adding features:

1. Update relevant documentation files
2. Add examples if applicable
3. Update API reference if needed
4. Update changelog

### Documentation Files

- `docs/API_REFERENCE.md` - API documentation
- `docs/ARCHITECTURE.md` - Architecture overview
- `docs/MODULE_DEVELOPMENT.md` - Module development guide
- `README.md` - Main readme

## Submitting Changes

### Pull Request Process

1. **Update your fork**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make changes**
   - Write code
   - Add tests
   - Update documentation
   - Format code

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add my feature"
   ```

5. **Push to fork**
   ```bash
   git push origin feature/my-feature
   ```

6. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill out PR template
   - Submit

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

Examples:

```
feat: add pagination support
fix: resolve database connection issue
docs: update API reference
```

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Type hints added
- [ ] No breaking changes (or documented)
- [ ] Commit messages follow conventions

## Review Process

1. **Automated Checks**
   - Tests must pass
   - Code must be formatted
   - Type checks must pass

2. **Code Review**
   - Maintainers review code
   - Address feedback
   - Make requested changes

3. **Merge**
   - Approved PRs are merged
   - Changes are included in next release

## Questions?

- Open an issue for questions
- Check existing documentation
- Ask in discussions

## Thank You!

Your contributions make the Wisp Framework better for everyone. Thank you for contributing!
