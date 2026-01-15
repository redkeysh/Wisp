"""Wisp Framework - A production-grade framework for building Discord bots."""

from wisp_framework.app import create_app
from wisp_framework.bot import WispBot
from wisp_framework.config import AppConfig
from wisp_framework.context import BotContext
from wisp_framework.lifecycle import LifecycleManager
from wisp_framework.module import Module
from wisp_framework.registry import ModuleRegistry
from wisp_framework.version import __version__

__all__ = [
    "__version__",
    "create_app",
    "WispBot",
    "AppConfig",
    "BotContext",
    "LifecycleManager",
    "Module",
    "ModuleRegistry",
]
