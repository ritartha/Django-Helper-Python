"""
URL Manager — Safely add and manage URL patterns in Django projects.
"""

import os
from typing import Optional, Callable

from utils.code_parser import CodeParser
from utils.file_handler import FileHandler
from templates.url_templates import generate_app_urls, generate_include_line


class URLManager:
    """Manage Django URL configurations with safe AST‑based modifications."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.log = log_callback or print

    def add_url_pattern(
        self,
        urls_file: str,
        path_str: str,
        view_name: str,
        view_type: str = "fbv",
        url_name: str = "",
    ) -> None:
        """
        Add a URL pattern to an existing urls.py file.

        Args:
            urls_file: Path to the urls.py file.
            path_str: The URL path (e.g., 'posts/' or '<int:pk>/').
            view_name: Name of the view function/class.
            view_type: 'fbv' for function‑based, 'cbv' for class‑based.
            url_name: Optional name for the URL pattern.
        """
        name_part = url_name or view_name.lower()

        if view_type == "cbv":
            url_line = f"path('{path_str}', views.{view_name}.as_view(), name='{name_part}'),"
        else:
            url_line = f"path('{path_str}', views.{view_name}, name='{name_part}'),"

        self.log(f"🔗 Adding URL pattern: {url_line}")

        # Ensure the views import exists
        content = FileHandler.read(urls_file)
        if "from . import views" not in content and "from .views import" not in content:
            modified_content = CodeParser.add_import(urls_file, "from . import views")
            FileHandler.write(urls_file, modified_content, backup=True)

        # Add the URL line to urlpatterns
        modified = CodeParser.add_to_urlpatterns(urls_file, url_line)
        FileHandler.write(urls_file, modified, backup=True)
        self.log(f"✓ URL pattern added successfully")

    def include_app_urls(
        self,
        project_path: str,
        app_name: str,
        prefix: str = "",
    ) -> None:
        """
        Add an include() entry for an app into the project‑level urls.py.

        Args:
            project_path: Root of the Django project (contains manage.py).
            app_name: Name of the app whose URLs should be included.
            prefix: URL prefix (defaults to '{app_name}/').
        """
        # Locate the project‑level urls.py
        project_urls = self._find_project_urls(project_path)
        if not project_urls:
            self.log("✗ Could not find project‑level urls.py")
            return

        include_line = generate_include_line(app_name, prefix or f"{app_name}/")

        # Ensure 'include' is imported
        content = FileHandler.read(project_urls)
        if "include" not in content:
            content = content.replace(
                "from django.urls import path",
                "from django.urls import path, include",
            )
            FileHandler.write(project_urls, content, backup=True)

        # Add the include line to urlpatterns
        modified = CodeParser.add_to_urlpatterns(project_urls, include_line)
        FileHandler.write(project_urls, modified, backup=True)
        self.log(f"✓ Included '{app_name}' URLs in project urls.py")

    def create_app_urls(
        self,
        app_path: str,
        app_name: str,
        views: list[dict] | None = None,
    ) -> None:
        """Create a urls.py file inside an app directory."""
        urls_path = os.path.join(app_path, "urls.py")
        content = generate_app_urls(app_name, views)
        FileHandler.write(urls_path, content, backup=True)
        self.log(f"✓ Created {app_name}/urls.py")

    def _find_project_urls(self, project_path: str) -> Optional[str]:
        """Find the project‑level urls.py (inside the config package)."""
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "settings.py")):
                urls_path = os.path.join(item_path, "urls.py")
                if os.path.exists(urls_path):
                    return urls_path
        return None