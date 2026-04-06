"""
Project Manager — Create Django projects, virtual environments, install dependencies.
"""

import os
from typing import Optional, Callable

from core.command_executor import CommandExecutor, CommandResult
from utils.file_handler import FileHandler
from templates.deployment_templates import generate_gitignore


class ProjectManager:
    """Handles Django project lifecycle: creation, venv, deps, migrations, server."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.executor = CommandExecutor(log_callback=log_callback)
        self.log = log_callback or print

    def create_project(self, project_name: str, base_dir: str) -> CommandResult:
        """
        Create a new Django project inside `base_dir`.

        Structure created:
            base_dir/
                project_name/
                    manage.py
                    project_name/
                        settings.py ...
        """
        project_path = os.path.join(base_dir, project_name)
        if os.path.exists(project_path):
            self.log(f"⚠ Directory already exists: {project_path}")
            return CommandResult(1, "", "Directory already exists", "create_project")

        FileHandler.ensure_directory(project_path)
        self.log(f"📁 Creating project '{project_name}' in {base_dir}")

        result = self.executor.run(
            f"django-admin startproject {project_name} .",
            cwd=project_path,
        )

        if result.success:
            # Create .gitignore
            gitignore_path = os.path.join(project_path, ".gitignore")
            FileHandler.write(gitignore_path, generate_gitignore(), backup=False)
            self.log(f"✓ Project '{project_name}' created successfully")

        return result

    def create_virtualenv(self, project_path: str, venv_name: str = "venv") -> CommandResult:
        """Create a Python virtual environment inside the project directory."""
        self.log(f"🐍 Creating virtual environment '{venv_name}'...")
        return self.executor.run(f"python -m venv {venv_name}", cwd=project_path)

    def install_dependencies(
        self,
        project_path: str,
        packages: list[str] | None = None,
        venv_name: str = "venv",
    ) -> CommandResult:
        """Install Python packages into the project's virtual environment."""
        pkgs = packages or ["django"]
        pkg_str = " ".join(pkgs)
        self.log(f"📦 Installing: {pkg_str}")
        venv_path = os.path.join(project_path, venv_name)
        return self.executor.run_with_venv(f"pip install {pkg_str}", venv_path, cwd=project_path)

    def run_migrations(self, project_path: str, venv_name: str = "venv") -> CommandResult:
        """Run Django migrations (makemigrations + migrate)."""
        self.log("🔄 Running migrations...")
        venv_path = os.path.join(project_path, venv_name)
        result = self.executor.run_with_venv("python manage.py makemigrations", venv_path, cwd=project_path)
        if result.success:
            result = self.executor.run_with_venv("python manage.py migrate", venv_path, cwd=project_path)
        return result

    def start_server(self, project_path: str, port: int = 8000, venv_name: str = "venv") -> None:
        """Start the Django development server in a background thread."""
        self.log(f"🚀 Starting development server on port {port}...")
        venv_path = os.path.join(project_path, venv_name)
        self.executor.run_with_venv(
            f"python manage.py runserver {port}",
            venv_path,
            cwd=project_path,
        )

    def generate_requirements(self, project_path: str, venv_name: str = "venv") -> CommandResult:
        """Generate requirements.txt using pip freeze."""
        self.log("📋 Generating requirements.txt...")
        venv_path = os.path.join(project_path, venv_name)
        result = self.executor.run_with_venv("pip freeze", venv_path, cwd=project_path)
        if result.success:
            req_path = os.path.join(project_path, "requirements.txt")
            FileHandler.write(req_path, result.stdout, backup=True)
            self.log("✓ requirements.txt generated")
        return result

    def get_project_name(self, project_path: str) -> Optional[str]:
        """
        Detect the Django project name by finding the directory containing settings.py.
        """
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path):
                if os.path.exists(os.path.join(item_path, "settings.py")):
                    return item
        return None