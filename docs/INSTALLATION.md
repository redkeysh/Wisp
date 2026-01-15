# Installation Guide

## Installing from GitHub

You can install the Wisp Framework directly from GitHub using pip.

### Basic Installation

```bash
pip install git+https://github.com/redkeysh/wisp.git
```

### Install from Specific Branch

```bash
# Install from a specific branch
pip install git+https://github.com/redkeysh/wisp.git@branch-name

# Example: Install from develop branch
pip install git+https://github.com/redkeysh/wisp.git@develop
```

### Install from Specific Tag/Release

```bash
# Install from a specific tag
pip install git+https://github.com/redkeysh/wisp.git@v1.0.0

# Install from a specific commit
pip install git+https://github.com/redkeysh/wisp.git@abc123def
```

### Install with Extras

```bash
# Install with database support
pip install git+https://github.com/redkeysh/wisp.git[db]

# Install with Redis support
pip install git+https://github.com/redkeysh/wisp.git[redis]

# Install with all extras
pip install git+https://github.com/redkeysh/wisp.git[all]
```

### Install for Development

If you want to make changes to the framework:

```bash
# Clone the repository
git clone https://github.com/redkeysh/wisp.git
cd wisp

# Install in editable mode
pip install -e .

# Or with extras
pip install -e ".[db,redis,all]"
```

## Using in Your Bot Project

### Option 1: Direct Import

Once installed, you can import and use the framework:

```python
from wisp_framework import FrameworkBot, Module
from wisp_framework.config import AppConfig
from wisp_framework.lifecycle import LifecycleManager

# Use the framework
```

### Option 2: requirements.txt

Add to your `requirements.txt`:

```txt
# Install from GitHub
git+https://github.com/redkeysh/wisp.git

# Or with extras
git+https://github.com/redkeysh/wisp.git[db,redis]

# Or pin to a specific version
git+https://github.com/redkeysh/wisp.git@v1.0.0
```

### Option 3: pyproject.toml (Modern Python Projects)

Add to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "git+https://github.com/redkeysh/wisp.git",
]

[project.optional-dependencies]
all = [
    "git+https://github.com/redkeysh/wisp.git[db,redis,all]",
]
```

### Option 4: Poetry

If using Poetry:

```bash
poetry add git+https://github.com/redkeysh/wisp.git

# With extras
poetry add "git+https://github.com/redkeysh/wisp.git[db,redis]"
```

Or add to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
wisp-framework = {git = "https://github.com/redkeysh/wisp.git", extras = ["db", "redis"]}
```

## Private Repositories

### Using SSH

```bash
pip install git+ssh://git@github.com/redkeysh/wisp.git
```

### Using HTTPS with Token

```bash
# Set token as environment variable
export GIT_TOKEN=your_github_token

# Use in URL
pip install git+https://${GIT_TOKEN}@github.com/redkeysh/wisp.git
```

### Using requirements.txt with Token

```txt
git+https://${GIT_TOKEN}@github.com/redkeysh/wisp.git
```

Then set the token before installing:
```bash
export GIT_TOKEN=your_token
pip install -r requirements.txt
```

## Version Pinning

### Recommended: Use Tags/Releases

1. Create a release on GitHub (e.g., `v1.0.0`)
2. Pin to that version:

```bash
pip install git+https://github.com/redkeysh/wisp.git@v1.0.0
```

### Using requirements.txt

```txt
# Pin to specific tag
git+https://github.com/redkeysh/wisp.git@v1.0.0

# Pin to specific commit (most stable)
git+https://github.com/redkeysh/wisp.git@abc123def456789
```

## Updating the Framework

### Update to Latest

```bash
pip install --upgrade git+https://github.com/redkeysh/wisp.git
```

### Update to Specific Version

```bash
pip install --upgrade git+https://github.com/redkeysh/wisp.git@v1.1.0
```

## Example Bot Setup

### 1. Create Your Bot Project

```bash
mkdir my-discord-bot
cd my-discord-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Create requirements.txt

```txt
git+https://github.com/redkeysh/wisp.git[db,redis]
discord.py>=2.3.0
python-dotenv>=1.0.0
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Your Bot

```python
# bot.py
from wisp_framework.config import AppConfig
from wisp_framework.lifecycle import (
    LifecycleManager,
    create_bot_context,
    create_feature_flags,
    create_services,
)
from wisp_framework.logging import setup_logging
from wisp_framework.registry import ModuleRegistry

def main():
    config = AppConfig()
    setup_logging(config)
    
    services = create_services(config)
    feature_flags = create_feature_flags(services)
    module_registry = ModuleRegistry(feature_flags)
    ctx = create_bot_context(config, services)
    
    lifecycle = LifecycleManager()
    
    import asyncio
    async def run():
        bot = await lifecycle.startup(config, services, module_registry, ctx)
        await bot.start(config.discord_token)
    
    asyncio.run(run())

if __name__ == "__main__":
    main()
```

### 5. Run Your Bot

```bash
python bot.py
```

## Troubleshooting

### Issue: "Could not find a version that satisfies"

**Solution**: Make sure you're using the correct URL format:
- ✅ `git+https://github.com/user/repo.git`
- ❌ `https://github.com/user/repo.git` (missing `git+`)

### Issue: Authentication Required

**Solution**: Use SSH or provide a token:
```bash
pip install git+ssh://git@github.com/redkeysh/wisp.git
```

### Issue: Import Errors After Installation

**Solution**: Make sure you installed with the correct package name:
```bash
# The package name is 'wisp-framework' but imports as 'wisp_framework'
from wisp_framework import ...
```

### Issue: Extras Not Working

**Solution**: Make sure extras are in brackets:
```bash
# Correct
pip install git+https://github.com/user/repo.git[db]

# Incorrect
pip install git+https://github.com/user/repo.git db
```

## Best Practices

1. **Pin Versions**: Always pin to a specific tag or commit in production
2. **Use Tags**: Create GitHub releases/tags for stable versions
3. **Document Versions**: Keep track of which version your bot uses
4. **Test Updates**: Test framework updates in a development environment first
5. **Use Requirements Files**: Always use `requirements.txt` or `pyproject.toml`

## Publishing to PyPI (Optional)

If you want to publish to PyPI instead of GitHub:

1. Build the package:
```bash
pip install build
python -m build
```

2. Upload to PyPI:
```bash
pip install twine
twine upload dist/*
```

Then users can install with:
```bash
pip install wisp-framework
```
