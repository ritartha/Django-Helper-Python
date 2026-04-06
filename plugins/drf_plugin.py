"""
DRF Plugin — one‑click Django REST Framework setup.

Installs DRF, registers it in INSTALLED_APPS, adds default settings,
and generates a sample serializer + viewset + router configuration.
"""

import os
from typing import Callable, Optional

from plugins.base_plugin import BasePlugin
from core.command_executor import CommandExecutor
from utils.code_parser import CodeParser
from utils.file_handler import FileHandler


class DRFPlugin(BasePlugin):
    """Automate Django REST Framework setup in a Django project."""

    name = "drf"
    version = "1.0.0"
    description = "One‑click Django REST Framework integration — installs the package, registers apps, adds REST_FRAMEWORK settings, and scaffolds an example API."

    # ── Contract implementation ───────────────────────────────────────

    def execute(
        self,
        project_path: str,
        log_callback: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> bool:
        log = log_callback or print
        executor = CommandExecutor(log_callback=log)
        venv_name = kwargs.get("venv_name", "venv")
        venv_path = os.path.join(project_path, venv_name)

        # 1. Install packages
        log("📦 [DRF Plugin] Installing djangorestframework & django-filter...")
        deps = " ".join(self.get_dependencies())
        result = executor.run_with_venv(f"pip install {deps}", venv_path, cwd=project_path)
        if not result.success:
            log("✗ [DRF Plugin] Failed to install dependencies")
            return False

        # 2. Register in INSTALLED_APPS
        settings_path = FileHandler.find_file(project_path, "settings.py")
        if not settings_path:
            log("✗ [DRF Plugin] settings.py not found")
            return False

        for app_entry in self.get_installed_apps():
            log(f"📝 [DRF Plugin] Adding '{app_entry}' to INSTALLED_APPS...")
            content = CodeParser.add_to_installed_apps(settings_path, app_entry)
            FileHandler.write(settings_path, content, backup=True)

        # 3. Add REST_FRAMEWORK settings block
        log("📝 [DRF Plugin] Adding REST_FRAMEWORK configuration...")
        self._add_rest_framework_settings(settings_path)

        # 4. Scaffold example API (optional)
        target_app = kwargs.get("target_app")
        if target_app:
            self._scaffold_api(project_path, target_app, log)

        log("✓ [DRF Plugin] Setup complete!")
        return True

    def get_dependencies(self) -> list[str]:
        return [
            "djangorestframework",
            "django-filter",
            "drf-spectacular",
        ]

    def get_installed_apps(self) -> list[str]:
        return [
            "rest_framework",
            "django_filters",
            "drf_spectacular",
        ]

    def get_settings_additions(self) -> dict:
        return {
            "REST_FRAMEWORK": """{
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}""",
        }

    def get_middleware(self) -> list[str]:
        return []

    # ── Internal helpers ──────────────────────────────────────────────

    def _add_rest_framework_settings(self, settings_path: str) -> None:
        """Append the REST_FRAMEWORK dict to settings.py if not present."""
        content = FileHandler.read(settings_path)
        if "REST_FRAMEWORK" in content:
            return
        additions = self.get_settings_additions()
        for key, value in additions.items():
            content += f"\n\n{key} = {value}\n"
        FileHandler.write(settings_path, content, backup=True)

    def _scaffold_api(self, project_path: str, app_name: str, log: Callable) -> None:
        """Create a sample serializers.py and update views.py with a ViewSet."""
        app_path = os.path.join(project_path, app_name)
        if not os.path.isdir(app_path):
            log(f"⚠ [DRF Plugin] App '{app_name}' not found — skipping scaffold")
            return

        # --- serializers.py ---
        serializer_path = os.path.join(app_path, "serializers.py")
        if not os.path.exists(serializer_path):
            serializer_code = (
                "from rest_framework import serializers\n\n"
                "# Example serializer — replace 'YourModel' with an actual model\n"
                "# from .models import YourModel\n\n\n"
                "# class YourModelSerializer(serializers.ModelSerializer):\n"
                "#     class Meta:\n"
                "#         model = YourModel\n"
                "#         fields = '__all__'\n"
            )
            FileHandler.write(serializer_path, serializer_code, backup=False)
            log(f"✓ [DRF Plugin] Created {app_name}/serializers.py")

        # --- urls.py (router‑based) ---
        urls_path = os.path.join(app_path, "urls.py")
        router_code = (
            "from django.urls import path, include\n"
            "from rest_framework.routers import DefaultRouter\n"
            "# from .views import YourModelViewSet\n\n"
            "router = DefaultRouter()\n"
            "# router.register(r'yourmodel', YourModelViewSet)\n\n"
            f"app_name = '{app_name}'\n\n"
            "urlpatterns = [\n"
            "    path('', include(router.urls)),\n"
            "]\n"
        )
        FileHandler.write(urls_path, router_code, backup=True)
        log(f"✓ [DRF Plugin] Created DRF router in {app_name}/urls.py")