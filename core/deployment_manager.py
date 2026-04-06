"""
Deployment Manager — generate Procfile, runtime.txt, requirements.txt, and more.
"""

import os
from typing import Optional, Callable

from utils.file_handler import FileHandler
from templates.deployment_templates import (
    generate_procfile,
    generate_runtime_txt,
    generate_env_example,
)
from core.command_executor import CommandExecutor


class DeploymentManager:
    """Generate deployment configuration files."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.executor = CommandExecutor(log_callback=log_callback)
        self.log = log_callback or print

    def create_procfile(
        self,
        project_path: str,
        project_name: str,
        server: str = "gunicorn",
    ) -> None:
        """Create a Procfile for the project."""
        content = generate_procfile(project_name, server)
        path = os.path.join(project_path, "Procfile")
        FileHandler.write(path, content, backup=True)
        self.log(f"✓ Procfile created ({server})")

    def create_runtime_txt(
        self,
        project_path: str,
        python_version: str = "3.11",
    ) -> None:
        """Create a runtime.txt specifying the Python version."""
        content = generate_runtime_txt(python_version)
        path = os.path.join(project_path, "runtime.txt")
        FileHandler.write(path, content, backup=True)
        self.log(f"✓ runtime.txt created (python-{python_version})")

    def create_env_example(self, project_path: str) -> None:
        """Create a .env.example file."""
        content = generate_env_example()
        path = os.path.join(project_path, ".env.example")
        FileHandler.write(path, content, backup=True)
        self.log("✓ .env.example created")

    def generate_requirements(
        self,
        project_path: str,
        venv_name: str = "venv",
    ) -> None:
        """Generate requirements.txt via pip freeze."""
        self.log("📋 Generating requirements.txt...")
        venv_path = os.path.join(project_path, venv_name)
        result = self.executor.run_with_venv("pip freeze", venv_path, cwd=project_path)
        if result.success:
            req_path = os.path.join(project_path, "requirements.txt")
            FileHandler.write(req_path, result.stdout, backup=True)
            self.log("✓ requirements.txt generated")

    def export_project_zip(self, project_path: str, output_path: str = "") -> str:
        """
        Export the project directory as a ZIP archive (excluding venv, __pycache__, .git).
        Returns the path to the created ZIP file.
        """
        import shutil
        import tempfile

        project_name = os.path.basename(project_path)
        if not output_path:
            output_path = os.path.join(
                tempfile.gettempdir(), f"{project_name}_export"
            )

        self.log(f"📦 Exporting project to {output_path}.zip ...")

        def _ignore(directory: str, contents: list[str]) -> list[str]:
            """Ignore venv, caches, and .git when copying."""
            ignored = set()
            for item in contents:
                if item in ("venv", ".venv", "env", "__pycache__", ".git", "node_modules"):
                    ignored.add(item)
                elif item.endswith(".pyc"):
                    ignored.add(item)
            return ignored

        # Create a temp copy without ignored dirs, then zip it
        temp_dir = os.path.join(tempfile.gettempdir(), f"_export_{project_name}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        shutil.copytree(project_path, temp_dir, ignore=_ignore)

        zip_path = shutil.make_archive(output_path, "zip", temp_dir)

        # Cleanup the temporary copy
        shutil.rmtree(temp_dir, ignore_errors=True)

        self.log(f"✓ Project exported to {zip_path}")
        return zip_path