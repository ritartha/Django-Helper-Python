"""
App Manager — Create Django apps and auto-register them in settings.py.
"""

import os
from typing import Optional, Callable

from core.command_executor import CommandExecutor, CommandResult
from utils.code_parser import CodeParser
from utils.file_handler import FileHandler


class AppManager:
    """Create Django apps and auto-register them in INSTALLED_APPS."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.executor = CommandExecutor(log_callback=log_callback)
        self.log = log_callback or print

    def create_app(
        self,
        app_name: str,
        project_path: str,
        venv_name: str = "venv",
        auto_register: bool = True,
    ) -> CommandResult:
        """
        Create a Django app and optionally register it in settings.py.

        Args:
            app_name: Name for the new app.
            project_path: Root of the Django project (contains manage.py).
            venv_name: Name of the virtual environment directory.
            auto_register: Whether to add the app to INSTALLED_APPS.
        """
        self.log(f"📱 Creating app '{app_name}'...")
        venv_path = os.path.join(project_path, venv_name)
        result = self.executor.run_with_venv(
            f"python manage.py startapp {app_name}",
            venv_path,
            cwd=project_path,
        )

        if result.success and auto_register:
            self._register_app(app_name, project_path)

        # Create a urls.py for the app
        if result.success:
            self._create_app_urls(app_name, project_path)

        return result

    def _register_app(self, app_name: str, project_path: str) -> None:
        """Register the app in the project's settings.py INSTALLED_APPS."""
        settings_path = self._find_settings(project_path)
        if not settings_path:
            self.log("⚠ Could not find settings.py — app not registered")
            return

        self.log(f"📝 Registering '{app_name}' in INSTALLED_APPS...")
        modified = CodeParser.add_to_installed_apps(settings_path, app_name)
        FileHandler.write(settings_path, modified, backup=True)
        self.log(f"✓ '{app_name}' added to INSTALLED_APPS")

    def _create_app_urls(self, app_name: str, project_path: str) -> None:
        """Create a boilerplate urls.py inside the new app."""
        urls_path = os.path.join(project_path, app_name, "urls.py")
        if not os.path.exists(urls_path):
            content = (
                "from django.urls import path\n"
                "from . import views\n\n"
                f"app_name = '{app_name}'\n\n"
                "urlpatterns = [\n"
                "    # Add your URL patterns here\n"
                "]\n"
            )
            FileHandler.write(urls_path, content, backup=False)
            self.log(f"✓ Created {app_name}/urls.py")

    def _find_settings(self, project_path: str) -> Optional[str]:
        """Locate settings.py within the project."""
        return FileHandler.find_file(project_path, "settings.py")

    def list_apps(self, project_path: str) -> list[str]:
        """List all Django apps in the project (directories with models.py)."""
        apps = []
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "models.py")):
                # Exclude the project config directory (which also has settings.py)
                if not os.path.exists(os.path.join(item_path, "settings.py")):
                    apps.append(item)
        return sorted(apps)