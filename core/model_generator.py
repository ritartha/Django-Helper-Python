"""
Model Generator — Generate Django models from GUI input and handle admin registration.
"""

import os
from typing import Optional, Callable

from core.command_executor import CommandExecutor
from templates.model_templates import generate_model_code, generate_admin_registration
from utils.file_handler import FileHandler


class ModelGenerator:
    """Generate Django model code, write it to models.py, and register in admin."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.executor = CommandExecutor(log_callback=log_callback)
        self.log = log_callback or print

    def generate(
        self,
        model_name: str,
        fields: list[dict],
        app_path: str,
        register_admin: bool = True,
        run_migrations: bool = False,
        project_path: str = "",
        venv_name: str = "venv",
    ) -> str:
        """
        Generate a model, write to models.py, register in admin, optionally migrate.

        Args:
            model_name: PascalCase model name (e.g. 'BlogPost').
            fields: List of dicts with 'name', 'type', 'options' keys.
            app_path: Full path to the Django app directory.
            register_admin: Whether to add admin registration.
            run_migrations: Whether to run makemigrations+migrate.
            project_path: Root project path (needed for migrations).
            venv_name: Name of the venv directory.

        Returns:
            The generated model code as a string.
        """
        # Generate model code
        model_code = generate_model_code(model_name, fields)
        self.log(f"🏗️ Generating model '{model_name}'...")

        # Append to models.py
        models_path = os.path.join(app_path, "models.py")
        if os.path.exists(models_path):
            existing = FileHandler.read(models_path)
            if f"class {model_name}" in existing:
                self.log(f"⚠ Model '{model_name}' already exists in models.py")
                return model_code
            # Append without the duplicate import line
            code_to_append = model_code.replace("from django.db import models\n", "")
            FileHandler.append(models_path, f"\n\n{code_to_append}", backup=True)
        else:
            FileHandler.write(models_path, model_code, backup=False)

        self.log(f"✓ Model '{model_name}' written to models.py")

        # Register in admin.py
        if register_admin:
            self._register_admin(model_name, fields, app_path)

        # Run migrations
        if run_migrations and project_path:
            self._run_migrations(project_path, venv_name)

        return model_code

    def _register_admin(self, model_name: str, fields: list[dict], app_path: str) -> None:
        """Add admin registration for the model."""
        admin_path = os.path.join(app_path, "admin.py")
        admin_code = generate_admin_registration(model_name, fields)

        if os.path.exists(admin_path):
            existing = FileHandler.read(admin_path)
            if model_name in existing:
                self.log(f"⚠ {model_name} already registered in admin.py")
                return
            # Append the registration (skip duplicate imports)
            registration_lines = admin_code.split("\n")
            # Keep only from the @admin.register line onward, plus the model import
            import_line = f"from .models import {model_name}"
            body_start = next(
                (i for i, l in enumerate(registration_lines) if l.startswith("@admin")),
                0,
            )
            body = "\n".join(registration_lines[body_start:])
            FileHandler.append(admin_path, f"\n{import_line}\n\n{body}", backup=True)
        else:
            FileHandler.write(admin_path, admin_code, backup=False)

        self.log(f"✓ {model_name} registered in admin.py")

    def _run_migrations(self, project_path: str, venv_name: str) -> None:
        """Run makemigrations and migrate."""
        venv_path = os.path.join(project_path, venv_name)
        self.log("🔄 Running makemigrations...")
        self.executor.run_with_venv("python manage.py makemigrations", venv_path, cwd=project_path)
        self.log("🔄 Running migrate...")
        self.executor.run_with_venv("python manage.py migrate", venv_path, cwd=project_path)

    def preview(self, model_name: str, fields: list[dict]) -> str:
        """Return the generated model code without writing anything."""
        return generate_model_code(model_name, fields)