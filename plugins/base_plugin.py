"""
Base Plugin — abstract contract that every plugin must implement.

All plugins must:
    1. Subclass BasePlugin
    2. Set name, version, description
    3. Implement execute() and get_dependencies()
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional


class BasePlugin(ABC):
    """Abstract base class for all Django Dev Assistant plugins."""

    # ── Metadata (override in subclasses) ─────────────────────────────
    name: str = "base"
    version: str = "0.0.0"
    description: str = "Base plugin — do not use directly."

    @abstractmethod
    def execute(
        self,
        project_path: str,
        log_callback: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> bool:
        """
        Run the plugin's primary action on the given project.

        Args:
            project_path: Root directory of the Django project (contains manage.py).
            log_callback: Function to call with progress/log messages.
            **kwargs: Plugin-specific options.

        Returns:
            True if the action succeeded, False otherwise.
        """
        ...

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """
        Return a list of pip packages this plugin requires.
        Example: ["djangorestframework", "django-filter"]
        """
        ...

    def get_settings_additions(self) -> dict:
        """
        Return a dict of settings.py modifications the plugin wants to apply.
        Keys are setting names, values are the literal Python expressions to assign.

        Example:
            {"REST_FRAMEWORK": "{'DEFAULT_PERMISSION_CLASSES': [...]}"}
        """
        return {}

    def get_installed_apps(self) -> list[str]:
        """Return a list of apps to add to INSTALLED_APPS."""
        return []

    def get_middleware(self) -> list[str]:
        """Return middleware classes to add to MIDDLEWARE."""
        return []

    def __repr__(self) -> str:
        return f"<Plugin: {self.name} v{self.version}>"