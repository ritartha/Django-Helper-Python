"""
Project Detector — scans a directory to determine if it contains a Django project,
virtual environment, git repo, and other common artifacts.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Callable


# Common venv directory names to look for
_VENV_CANDIDATES = ("venv", "env", ".venv", ".env")


@dataclass
class ProjectStatus:
    """Structured result of scanning a project directory."""

    path: str = ""

    # ── Virtual environment ───────────────────────────────────────────
    has_venv: bool = False
    venv_path: str = ""
    venv_name: str = ""

    # ── Django project ────────────────────────────────────────────────
    has_manage_py: bool = False
    has_settings_module: bool = False
    settings_module_name: str = ""
    is_django_project: bool = False  # manage.py AND settings module

    # ── Django installed in venv ──────────────────────────────────────
    django_installed: bool = False

    # ── Apps ──────────────────────────────────────────────────────────
    apps: list[str] = field(default_factory=list)
    app_count: int = 0

    # ── Other artifacts ───────────────────────────────────────────────
    has_requirements: bool = False
    has_db_sqlite3: bool = False
    has_git: bool = False
    has_gitignore: bool = False

    # ── Summary helpers ───────────────────────────────────────────────
    @property
    def summary_lines(self) -> list[str]:
        """Human-readable summary lines."""
        lines: list[str] = []
        if self.is_django_project:
            lines.append(f"✅ Django project detected  ({self.settings_module_name})")
        elif self.has_manage_py:
            lines.append("⚠️ manage.py found but no settings module detected")
        else:
            lines.append("❌ Not a Django project (no manage.py)")

        if self.has_venv:
            lines.append(f"✅ Virtual environment found  ({self.venv_name}/)")
        else:
            lines.append("❌ No virtual environment detected")

        if self.django_installed:
            lines.append("✅ Django is installed in the venv")
        elif self.has_venv:
            lines.append("⚠️ Django is NOT installed in the venv")

        if self.app_count:
            names = ", ".join(self.apps[:8])
            extra = f" (+{self.app_count - 8} more)" if self.app_count > 8 else ""
            lines.append(f"📱 {self.app_count} app(s): {names}{extra}")

        if self.has_requirements:
            lines.append("✅ requirements.txt found")
        else:
            lines.append("⚪ No requirements.txt")

        if self.has_git:
            lines.append("✅ Git repository initialized")
        else:
            lines.append("⚪ No Git repository")

        if self.has_db_sqlite3:
            lines.append("✅ SQLite database (db.sqlite3) present")

        return lines


class ProjectDetector:
    """Scans a directory and returns a ``ProjectStatus`` with detection results."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.log = log_callback or (lambda _: None)

    # ── Public API ────────────────────────────────────────────────────
    def detect(self, path: str) -> ProjectStatus:
        """
        Run all detection checks on *path* and return a populated ``ProjectStatus``.

        This is intentionally a fast, synchronous scan (no subprocesses).
        """
        status = ProjectStatus(path=path)

        if not path or not os.path.isdir(path):
            return status

        self.log(f"🔍 Scanning: {path}")

        self._detect_venv(path, status)
        self._detect_django(path, status)
        self._detect_django_installed(status)
        self._detect_apps(path, status)
        self._detect_artifacts(path, status)

        return status

    # ── Internal checks ───────────────────────────────────────────────
    def _detect_venv(self, path: str, status: ProjectStatus) -> None:
        """Look for a virtual environment directory."""
        # Check well-known names first
        for name in _VENV_CANDIDATES:
            candidate = os.path.join(path, name)
            if os.path.isdir(candidate) and self._is_venv(candidate):
                status.has_venv = True
                status.venv_path = candidate
                status.venv_name = name
                return

        # Fallback: scan top-level dirs for pyvenv.cfg
        try:
            for entry in os.scandir(path):
                if entry.is_dir() and self._is_venv(entry.path):
                    status.has_venv = True
                    status.venv_path = entry.path
                    status.venv_name = entry.name
                    return
        except PermissionError:
            pass

    @staticmethod
    def _is_venv(directory: str) -> bool:
        """Return True if *directory* looks like a Python virtual environment."""
        return os.path.isfile(os.path.join(directory, "pyvenv.cfg"))

    def _detect_django(self, path: str, status: ProjectStatus) -> None:
        """Check for manage.py and a settings module."""
        status.has_manage_py = os.path.isfile(os.path.join(path, "manage.py"))

        # Look for a subdirectory containing settings.py
        try:
            for entry in os.scandir(path):
                if entry.is_dir():
                    settings_file = os.path.join(entry.path, "settings.py")
                    init_file = os.path.join(entry.path, "__init__.py")
                    if os.path.isfile(settings_file) and os.path.isfile(init_file):
                        status.has_settings_module = True
                        status.settings_module_name = entry.name
                        break
        except PermissionError:
            pass

        status.is_django_project = status.has_manage_py and status.has_settings_module

    def _detect_django_installed(self, status: ProjectStatus) -> None:
        """Check if Django is installed inside the detected venv (file-system check, no subprocess)."""
        if not status.has_venv:
            return

        # Windows: venv/Lib/site-packages/django
        # Unix:    venv/lib/python3.x/site-packages/django
        site_packages_candidates = []

        lib_dir = os.path.join(status.venv_path, "Lib", "site-packages")
        if os.path.isdir(lib_dir):
            site_packages_candidates.append(lib_dir)

        lib_lower = os.path.join(status.venv_path, "lib")
        if os.path.isdir(lib_lower):
            try:
                for entry in os.scandir(lib_lower):
                    if entry.is_dir() and entry.name.startswith("python"):
                        sp = os.path.join(entry.path, "site-packages")
                        if os.path.isdir(sp):
                            site_packages_candidates.append(sp)
            except PermissionError:
                pass

        for sp in site_packages_candidates:
            django_dir = os.path.join(sp, "django")
            if os.path.isdir(django_dir):
                status.django_installed = True
                return

    def _detect_apps(self, path: str, status: ProjectStatus) -> None:
        """List Django apps (dirs with models.py, excluding the settings module dir)."""
        try:
            for entry in os.scandir(path):
                if not entry.is_dir():
                    continue
                # Skip common non-app directories
                if entry.name.startswith(".") or entry.name in _VENV_CANDIDATES:
                    continue
                if entry.name == status.settings_module_name:
                    continue
                if entry.name in ("__pycache__", "static", "media", "templates", "staticfiles"):
                    continue

                models_py = os.path.join(entry.path, "models.py")
                if os.path.isfile(models_py):
                    status.apps.append(entry.name)
        except PermissionError:
            pass

        status.apps.sort()
        status.app_count = len(status.apps)

    def _detect_artifacts(self, path: str, status: ProjectStatus) -> None:
        """Check for requirements.txt, db.sqlite3, .git, .gitignore."""
        status.has_requirements = os.path.isfile(os.path.join(path, "requirements.txt"))
        status.has_db_sqlite3 = os.path.isfile(os.path.join(path, "db.sqlite3"))
        status.has_git = os.path.isdir(os.path.join(path, ".git"))
        status.has_gitignore = os.path.isfile(os.path.join(path, ".gitignore"))
