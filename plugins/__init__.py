"""
Plugin system for Django Dev Assistant.
Plugins extend the application with additional functionality (DRF, Auth, Celery, etc.)
without modifying the core codebase.
"""

import os
import importlib
from typing import Optional

from plugins.base_plugin import BasePlugin


class PluginRegistry:
    """
    Discovers, loads, and manages plugins.

    Usage:
        registry = PluginRegistry()
        registry.discover()          # scan plugins/ directory
        registry.activate("drf")     # activate by name
        registry.get("drf").execute(project_path, log)
    """

    def __init__(self):
        self._plugins: dict[str, BasePlugin] = {}
        self._active: set[str] = set()

    def discover(self) -> list[str]:
        """
        Scan the plugins/ directory for Python modules that export a subclass
        of BasePlugin. Returns a list of discovered plugin names.
        """
        plugins_dir = os.path.dirname(os.path.abspath(__file__))
        discovered: list[str] = []

        for filename in os.listdir(plugins_dir):
            if filename.endswith("_plugin.py") and filename != "base_plugin.py":
                module_name = f"plugins.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    # Look for a class that subclasses BasePlugin
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BasePlugin)
                            and attr is not BasePlugin
                        ):
                            instance = attr()
                            self._plugins[instance.name] = instance
                            discovered.append(instance.name)
                except Exception as e:
                    print(f"[PluginRegistry] Failed to load {module_name}: {e}")

        return discovered

    def list_plugins(self) -> list[dict]:
        """Return metadata for all discovered plugins."""
        return [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "active": p.name in self._active,
            }
            for p in self._plugins.values()
        ]

    def get(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin instance by name."""
        return self._plugins.get(name)

    def activate(self, name: str) -> bool:
        """Mark a plugin as active."""
        if name in self._plugins:
            self._active.add(name)
            return True
        return False

    def deactivate(self, name: str) -> bool:
        """Mark a plugin as inactive."""
        if name in self._active:
            self._active.discard(name)
            return True
        return False

    def is_active(self, name: str) -> bool:
        return name in self._active

    @property
    def active_plugins(self) -> list[BasePlugin]:
        """Return all currently active plugin instances."""
        return [self._plugins[n] for n in self._active if n in self._plugins]