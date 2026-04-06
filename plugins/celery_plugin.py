"""
Celery Plugin — one‑click Celery + Redis task queue setup.

Installs Celery, creates the celery.py configuration module,
updates __init__.py, adds a sample task, and creates a basic
Procfile worker entry.
"""

import os
from typing import Callable, Optional

from plugins.base_plugin import BasePlugin
from core.command_executor import CommandExecutor
from utils.file_handler import FileHandler
from utils.code_parser import CodeParser


class CeleryPlugin(BasePlugin):
    """Automate Celery integration with a Django project."""

    name = "celery"
    version = "1.0.0"
    description = "One‑click Celery + Redis setup — installs packages, creates celery.py, sample tasks, and a Procfile worker entry."

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

        # Detect project config package name
        project_name = self._detect_project_name(project_path)
        if not project_name:
            log("✗ [Celery Plugin] Could not detect Django project name")
            return False

        # 1. Install dependencies
        log("📦 [Celery Plugin] Installing celery and redis...")
        deps = " ".join(self.get_dependencies())
        result = executor.run_with_venv(f"pip install {deps}", venv_path, cwd=project_path)
        if not result.success:
            log("✗ [Celery Plugin] Dependency installation failed")
            return False

        # 2. Add 'django_celery_results' to INSTALLED_APPS
        settings_path = FileHandler.find_file(project_path, "settings.py")
        if settings_path:
            for app_entry in self.get_installed_apps():
                content = CodeParser.add_to_installed_apps(settings_path, app_entry)
                FileHandler.write(settings_path, content, backup=True)

            # Add Celery settings
            self._add_celery_settings(settings_path, log)

        # 3. Create celery.py in the project config package
        self._create_celery_module(project_path, project_name, log)

        # 4. Update project __init__.py to import Celery
        self._update_init_py(project_path, project_name, log)

        # 5. Create a sample tasks.py
        target_app = kwargs.get("target_app")
        if target_app:
            self._create_sample_tasks(project_path, target_app, log)

        # 6. Add worker to Procfile
        self._update_procfile(project_path, project_name, log)

        log("✓ [Celery Plugin] Setup complete!")
        return True

    def get_dependencies(self) -> list[str]:
        return ["celery", "redis", "django-celery-results"]

    def get_installed_apps(self) -> list[str]:
        return ["django_celery_results"]

    def get_settings_additions(self) -> dict:
        return {
            "CELERY_BROKER_URL": "'redis://localhost:6379/0'",
            "CELERY_RESULT_BACKEND": "'django-db'",
            "CELERY_ACCEPT_CONTENT": "['json']",
            "CELERY_TASK_SERIALIZER": "'json'",
            "CELERY_RESULT_SERIALIZER": "'json'",
            "CELERY_TIMEZONE": "'UTC'",
        }

    # ── Internal helpers ──────────────────────────────────────────────

    def _detect_project_name(self, project_path: str) -> Optional[str]:
        """Find the Django config package (directory containing settings.py)."""
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "settings.py")):
                return item
        return None

    def _add_celery_settings(self, settings_path: str, log: Callable) -> None:
        content = FileHandler.read(settings_path)
        additions = self.get_settings_additions()
        changed = False
        for key, value in additions.items():
            if key not in content:
                content += f"\n{key} = {value}\n"
                changed = True
        if changed:
            FileHandler.write(settings_path, content, backup=True)
            log("📝 [Celery Plugin] Celery settings added")

    def _create_celery_module(self, project_path: str, project_name: str, log: Callable) -> None:
        """Create the celery.py configuration file."""
        celery_code = f'''"""
Celery configuration for {project_name}.
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')

app = Celery('{project_name}')

# Read config from Django settings, the CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """A simple debug task to verify Celery is working."""
    print(f'Request: {{self.request!r}}')
'''
        celery_path = os.path.join(project_path, project_name, "celery.py")
        FileHandler.write(celery_path, celery_code, backup=True)
        log(f"✓ [Celery Plugin] Created {project_name}/celery.py")

    def _update_init_py(self, project_path: str, project_name: str, log: Callable) -> None:
        """Ensure __init__.py imports the Celery app."""
        init_path = os.path.join(project_path, project_name, "__init__.py")
        marker = "celery_app"

        if os.path.exists(init_path):
            content = FileHandler.read(init_path)
            if marker in content:
                return
        else:
            content = ""

        init_code = (
            "\n# Celery app — imported so shared_task uses this app.\n"
            "from .celery import app as celery_app\n\n"
            "__all__ = ('celery_app',)\n"
        )
        content += init_code
        FileHandler.write(init_path, content, backup=True)
        log(f"✓ [Celery Plugin] Updated {project_name}/__init__.py")

    def _create_sample_tasks(self, project_path: str, app_name: str, log: Callable) -> None:
        """Create a sample tasks.py in the given app."""
        tasks_code = '''"""
Sample Celery tasks for the app.
"""

from celery import shared_task


@shared_task
def add(x: int, y: int) -> int:
    """A simple addition task — useful for testing Celery."""
    return x + y


@shared_task
def send_notification(user_id: int, message: str) -> str:
    """
    Example async notification task.
    Replace with real notification logic (email, push, etc.).
    """
    # Simulate work
    import time
    time.sleep(2)
    return f"Notification sent to user {user_id}: {message}"
'''
        tasks_path = os.path.join(project_path, app_name, "tasks.py")
        FileHandler.write(tasks_path, tasks_code, backup=True)
        log(f"✓ [Celery Plugin] Created {app_name}/tasks.py")

    def _update_procfile(self, project_path: str, project_name: str, log: Callable) -> None:
        """Append a Celery worker entry to the Procfile."""
        procfile_path = os.path.join(project_path, "Procfile")
        worker_line = f"worker: celery -A {project_name} worker --loglevel=info\n"

        if os.path.exists(procfile_path):
            content = FileHandler.read(procfile_path)
            if "celery" not in content.lower():
                FileHandler.append(procfile_path, worker_line, backup=True)
                log("✓ [Celery Plugin] Worker entry added to Procfile")
        else:
            FileHandler.write(procfile_path, worker_line, backup=False)
            log("✓ [Celery Plugin] Procfile created with worker entry")