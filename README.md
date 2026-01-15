# Wisp Framework

[![GitHub release](https://img.shields.io/github/v/release/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/releases)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/network)
[![GitHub issues](https://img.shields.io/github/issues/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/redkeysh/wisp?style=flat-square)](https://github.com/redkeysh/wisp/commits/main)

Welcome to **Wisp Framework** — a production-grade, modular Discord bot framework built with Python 3.13+ and discord.py.

## What is Wisp Framework?

Wisp Framework provides a clean, extensible architecture for building Discord bots with:

- 🧩 **Modular Design** - Create reusable modules with per-guild enable/disable support
- 🗄️ **Optional Database** - SQLAlchemy 2.x async support with graceful degradation
- 🔧 **Service Container** - Built-in services (cache, metrics, scheduler, audit, webhook logger)
- 📊 **Per-Guild Data** - Automatic support for storing stats/data per guild
- 🚀 **Production Ready** - Docker support, health checks, graceful shutdown, connection pooling
- 💡 **Type Hints** - Full type hints throughout for better IDE support
- 🔌 **Extensible** - Clean interfaces for extending without forking

## Quick Start

```bash
# Install from GitHub
pip install git+https://github.com/redkeysh/wisp.git

# With database support
pip install git+https://github.com/redkeysh/wisp.git[db]

# With all extras
pip install git+https://github.com/redkeysh/wisp.git[all]
```

## Development

For local development, set up your environment and run checks:

```bash
# Setup development environment
./scripts/setup-dev.sh

# Or manually:
make install-dev
make install-test

# Run checks locally (replicates CI)
make ci              # Run lint + format + tests
make lint            # Run linter only
make format          # Format code
make test-cov        # Run tests with coverage
./scripts/dev.sh     # Alternative: use dev script

# See all available targets
make help
```

## Documentation

📚 **Complete documentation is available in the [Wiki](https://github.com/redkeysh/wisp/wiki)**.

For quick reference:
- **[Installation Guide](https://github.com/redkeysh/wisp/wiki/Installation-Guide)** - Get started quickly
- **[Usage Guide](https://github.com/redkeysh/wisp/wiki/Usage-Guide)** - Build your first bot
- **[Module Development](https://github.com/redkeysh/wisp/wiki/Module-Development)** - Create custom modules
- **[API Reference](https://github.com/redkeysh/wisp/wiki/API-Reference)** - Complete API documentation

## Features at a Glance

### Modular Architecture
Create modules that can be enabled or disabled per guild, making it easy to customize bot functionality for different servers.

### Production Ready
Built-in support for Docker, health checks, graceful shutdown, connection pooling, and more — everything you need for production deployments.

### Developer Friendly
Full type hints, comprehensive documentation, and a clean API make development a breeze.

### Extensible
Add your own services, modules, and utilities without modifying the core framework.

## Getting Help

- 📖 **[Wiki Documentation](https://github.com/redkeysh/wisp/wiki)** - Comprehensive guides and references
- 🐛 **[GitHub Issues](https://github.com/redkeysh/wisp/issues)** - Report bugs or request features
- 💬 **[Discussions](https://github.com/redkeysh/wisp/discussions)** - Ask questions and share ideas

## Contributing

Contributions are welcome! See the [Contributing Guide](https://github.com/redkeysh/wisp/wiki/Contributing-Guide) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Ready to build?** Check out the [Installation Guide](https://github.com/redkeysh/wisp/wiki/Installation-Guide) to get started!
