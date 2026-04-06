"""
Project Manager Panel — create projects, venvs, install deps, run migrations.
"""

import os
import threading
import customtkinter as ctk

from gui.widgets.custom_widgets import (
    SectionHeader, CardFrame, LabeledEntry, DirectoryPicker, ConfirmDialog,
)
from core.project_manager import ProjectManager


class ProjectPanel(ctk.CTkScrollableFrame):
    """UI for creating and managing Django projects."""

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app  # reference to the root DjangoDevAssistant
        self.pm = ProjectManager(log_callback=self._log)

        self._build()

    def _log(self, msg: str) -> None:
        if self.app:
            self.app.log(msg)

    # ── Build UI ──────────────────────────────────────────────────────
    def _build(self) -> None:
        SectionHeader(
            self,
            title="🏗️ Project Manager",
            description="Create Django projects, virtual environments, and manage dependencies.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # ── New project card ──────────────────────────────────────────
        card = CardFrame(self)
        card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card, text="Create New Project", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.project_name_entry = LabeledEntry(card, label="Project Name:", placeholder="my_django_project")
        self.project_name_entry.pack(fill="x", padx=15, pady=5)

        self.dir_picker = DirectoryPicker(card, label="Parent Directory:")
        self.dir_picker.pack(fill="x", padx=15, pady=5)

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(10, 15))

        ctk.CTkButton(btn_frame, text="Create Project", command=self._create_project).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Create Venv", command=self._create_venv).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Install Django", command=self._install_django).pack(side="left", padx=(0, 10))

        # ── Open existing project card ────────────────────────────────
        card2 = CardFrame(self)
        card2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card2, text="Open Existing Project", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.open_dir_picker = DirectoryPicker(card2, label="Project Directory:")
        self.open_dir_picker.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(card2, text="Open Project", command=self._open_project).pack(
            anchor="w", padx=15, pady=(5, 15)
        )

        # ── Server & migrations card ─────────────────────────────────
        card3 = CardFrame(self)
        card3.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card3, text="Server & Migrations", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        btn_frame2 = ctk.CTkFrame(card3, fg_color="transparent")
        btn_frame2.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkButton(btn_frame2, text="Run Migrations", command=self._run_migrations).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame2, text="Start Server", command=self._start_server).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame2, text="Generate requirements.txt", command=self._gen_requirements).pack(side="left")

    # ── Actions ───────────────────────────────────────────────────────
    def _require_project(self) -> bool:
        if not self.app or not self.app.project_path:
            ConfirmDialog.error("No Project", "Please create or open a project first.")
            return False
        return True

    def _create_project(self) -> None:
        name = self.project_name_entry.get()
        base = self.dir_picker.get()
        if not name or not base:
            ConfirmDialog.error("Missing Info", "Please enter a project name and select a directory.")
            return
        threading.Thread(target=self._do_create_project, args=(name, base), daemon=True).start()

    def _do_create_project(self, name: str, base: str) -> None:
        result = self.pm.create_project(name, base)
        if result.success:
            project_path = os.path.join(base, name)
            self.app.set_project(project_path, name)

    def _create_venv(self) -> None:
        if not self._require_project():
            return
        threading.Thread(
            target=self.pm.create_virtualenv, args=(self.app.project_path,), daemon=True
        ).start()

    def _install_django(self) -> None:
        if not self._require_project():
            return
        threading.Thread(
            target=self.pm.install_dependencies, args=(self.app.project_path, ["django"]), daemon=True
        ).start()

    def _run_migrations(self) -> None:
        if not self._require_project():
            return
        threading.Thread(
            target=self.pm.run_migrations, args=(self.app.project_path,), daemon=True
        ).start()

    def _start_server(self) -> None:
        if not self._require_project():
            return
        threading.Thread(
            target=self.pm.start_server, args=(self.app.project_path,), daemon=True
        ).start()

    def _gen_requirements(self) -> None:
        if not self._require_project():
            return
        threading.Thread(
            target=self.pm.generate_requirements, args=(self.app.project_path,), daemon=True
        ).start()

    def _open_project(self) -> None:
        path = self.open_dir_picker.get()
        if not path or not os.path.isdir(path):
            ConfirmDialog.error("Invalid Path", "Please select a valid project directory.")
            return
        name = self.pm.get_project_name(path) or os.path.basename(path)
        self.app.set_project(path, name)