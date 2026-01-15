# Wisp Framework Wiki

Welcome to the Wisp Framework documentation wiki! This wiki contains comprehensive guides, references, and examples for building Discord bots with the Wisp Framework.

## 📚 Documentation Index

### Getting Started
- [[Installation-Guide]] - Installation instructions and setup
- [[Usage-Guide]] - Quick start and basic usage examples
- [[Examples]] - Complete code examples and tutorials

### Core Concepts
- [[Architecture-Overview]] - Framework architecture and design principles
- [[Module-Development]] - Creating and developing modules
- [[Configuration-Reference]] - Complete configuration options
- [[Services-Documentation]] - Available services and their usage

### Reference
- [[API-Reference]] - Complete API documentation for all classes and functions
- [[Framework-Extensions]] - Enhanced utilities and helpers
- [[Framework-Extensions-Summary]] - Quick reference for extensions

### Operations
- [[Deployment-Guide]] - Production deployment instructions
- [[Troubleshooting]] - Common issues and solutions

### Contributing
- [[Contributing-Guide]] - How to contribute to the framework

## 🚀 Quick Start

1. **Install the framework:**
   ```bash
   pip install git+https://github.com/redkeysh/wisp.git
   ```

2. **Create your first bot:**
   See [[Usage-Guide]] for a complete example

3. **Build modules:**
   Follow the [[Module-Development]] guide

## 📖 Framework Overview

Wisp Framework is a production-grade, modular Discord bot framework built with Python 3.13+ and discord.py. It provides:

- **Modular Architecture**: Easy-to-create modules with per-guild enable/disable support
- **Optional Database**: SQLAlchemy 2.x async support with graceful degradation
- **Service Container**: Built-in services (cache, metrics, scheduler, audit, webhook logger)
- **Per-Guild Data Storage**: Automatic support for storing stats/data per guild
- **Production Ready**: Docker support, health checks, graceful shutdown, connection pooling
- **Type Hints**: Full type hints throughout for better IDE support
- **Extensible**: Clean interfaces for extending without forking

## 🎯 Common Tasks

### Creating a Module
See [[Module-Development]] for step-by-step instructions.

### Configuring the Bot
See [[Configuration-Reference]] for all configuration options.

### Deploying to Production
See [[Deployment-Guide]] for production deployment instructions.

### Troubleshooting
See [[Troubleshooting]] for common issues and solutions.

## 🔗 External Resources

- **GitHub Repository**: [redkeysh/wisp](https://github.com/redkeysh/wisp)
- **Issues**: [Report bugs or request features](https://github.com/redkeysh/wisp/issues)
- **Releases**: [View releases](https://github.com/redkeysh/wisp/releases)

## 📝 Version Information

Current version: **0.2.0**

## 📄 License

MIT License - see LICENSE file for details.

---

**Need help?** Check the [[Troubleshooting]] guide or open an issue on GitHub.
