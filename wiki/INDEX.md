# Wisp Framework Documentation

Welcome to the official Wisp Framework developer documentation. This documentation provides comprehensive guides, references, and examples for building Discord bots with the Wisp Framework.

## Documentation Structure

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

## Quick Navigation

### For New Users
1. Start with [[Installation-Guide]]
2. Follow the [[Usage-Guide]] for your first bot
3. Review [[Examples]] for common patterns

### For Module Developers
1. Read [[Architecture-Overview]] for context
2. Follow [[Module-Development]]
3. Reference [[API-Reference]] for details

### For Contributors
1. Review [[Contributing-Guide]]
2. Understand [[Architecture-Overview]]
3. Check [[API-Reference]] for implementation details

## Framework Overview

Wisp Framework is a production-grade, modular Discord bot framework built with Python 3.13+ and discord.py. It provides:

- **Modular Architecture**: Easy-to-create modules with per-guild enable/disable support
- **Optional Database**: SQLAlchemy 2.x async support with graceful degradation
- **Service Container**: Built-in services (cache, metrics, scheduler, audit, webhook logger)
- **Per-Guild Data Storage**: Automatic support for storing stats/data per guild
- **Production Ready**: Docker support, health checks, graceful shutdown, connection pooling
- **Type Hints**: Full type hints throughout for better IDE support
- **Extensible**: Clean interfaces for extending without forking

## Version Information

Current version: **0.2.0**

See [[API-Reference#version-information]] for version details.

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/redkeysh/wisp/issues)
- **Documentation**: This documentation set
- **Examples**: See [[Examples]] for code samples

## License

MIT License - see LICENSE file for details.
