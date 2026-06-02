"""
Project Manager Panel — create projects, venvs, install deps, run migrations.
Enhanced with auto-detection when opening/creating projects.
"""

import os
import threading
import customtkinter as ctk

from gui.widgets.custom_widgets import (
    SectionHeader, CardFrame, LabeledEntry, DirectoryPicker, ConfirmDialog,
)
from core.project_manager import ProjectManager
from core.project_detector import ProjectDetector, ProjectStatus


# ── Detection card colours ────────────────────────────────────────────
_HEALTH_COLORS = {
    "ok":   {"bg": ("#E8F5E9", "#1B3A1D"), "border": ("#66BB6A", "#388E3C")},
    "warn": {"bg": ("#FFF8E1", "#3A3018"), "border": ("#FFB74D", "#F57F17")},
    "bad":  {"bg": ("#FFEBEE", "#3A1B1B"), "border": ("#EF5350", "#C62828")},
}


class ProjectPanel(ctk.CTkScrollableFrame):
    """UI for creating and managing Django projects."""

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app  # reference to the root DjangoDevAssistant
        self.pm = ProjectManager(log_callback=self._log)
        self.detector = ProjectDetector(log_callback=self._log)

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

        # ══════════════════════════════════════════════════════════════
        #  PROJECT HEALTH CARD (detection results)
        # ══════════════════════════════════════════════════════════════
        self.health_card = CardFrame(self)
        self.health_card.pack(fill="x", padx=15, pady=5)

        health_header = ctk.CTkFrame(self.health_card, fg_color="transparent")
        health_header.pack(fill="x", padx=15, pady=(12, 5))

        ctk.CTkLabel(
            health_header, text="📊 Project Health",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            health_header, text="⟳ Rescan", width=80, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", hover_color=("gray80", "gray30"),
            text_color=("gray40", "gray60"),
            command=self._rescan_project,
        ).pack(side="right")

        # Status lines
        self.health_text = ctk.CTkLabel(
            self.health_card,
            text="Open or create a project to see its health status.",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray55"),
            anchor="w", justify="left",
            wraplength=650,
        )
        self.health_text.pack(fill="x", padx=15, pady=(0, 5))

        # Action buttons (hidden initially)
        self.health_actions = ctk.CTkFrame(self.health_card, fg_color="transparent")
        self.health_actions.pack(fill="x", padx=15, pady=(0, 12))

        self.action_venv_btn = ctk.CTkButton(
            self.health_actions,
            text="🐍 Create Virtual Env",
            width=170, height=32,
            fg_color=("#EF5350", "#C62828"),
            hover_color=("#E53935", "#B71C1C"),
            command=self._create_venv,
        )

        self.action_django_btn = ctk.CTkButton(
            self.health_actions,
            text="📦 Install Django",
            width=150, height=32,
            fg_color=("#FFB74D", "#F57F17"),
            hover_color=("#FFA726", "#E65100"),
            command=self._install_django,
        )

        self.action_git_btn = ctk.CTkButton(
            self.health_actions,
            text="🔀 Init Git",
            width=120, height=32,
            fg_color="gray40",
            hover_color="gray50",
            command=self._init_git,
        )

        # ══════════════════════════════════════════════════════════════
        #  NEW PROJECT CARD
        # ══════════════════════════════════════════════════════════════
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

        # ══════════════════════════════════════════════════════════════
        #  OPEN EXISTING PROJECT CARD
        # ══════════════════════════════════════════════════════════════
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

        # ══════════════════════════════════════════════════════════════
        #  SERVER & MIGRATIONS CARD
        # ══════════════════════════════════════════════════════════════
        card3 = CardFrame(self)
        card3.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card3, text="Server & Migrations", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        btn_frame2 = ctk.CTkFrame(card3, fg_color="transparent")
        btn_frame2.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkButton(btn_frame2, text="Run Migrations", command=self._run_migrations).pack(side="left", padx=(0, 10))
        self.start_server_btn = ctk.CTkButton(btn_frame2, text="Start Server", command=self._start_server)
        self.start_server_btn.pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame2, text="Generate requirements.txt", command=self._gen_requirements).pack(side="left")

    # ══════════════════════════════════════════════════════════════════
    #  HEALTH CARD MANAGEMENT
    # ══════════════════════════════════════════════════════════════════
    def _update_health_card(self, status: ProjectStatus) -> None:
        """Populate the health card from a ProjectStatus."""
        lines = status.summary_lines
        self.health_text.configure(
            text="\n".join(lines),
            text_color=("gray15", "gray85"),
        )

        # Show/hide action buttons depending on what's missing
        # First, clear all action buttons
        for child in self.health_actions.winfo_children():
            child.pack_forget()

        if not status.has_venv:
            self.action_venv_btn.pack(side="left", padx=(0, 8))
        if status.has_venv and not status.django_installed and not status.is_django_project:
            self.action_django_btn.pack(side="left", padx=(0, 8))
        if not status.has_git:
            self.action_git_btn.pack(side="left", padx=(0, 8))

        # Update Start Server button text based on venv presence
        if status.has_venv:
            self.start_server_btn.configure(text="Enable Env & Start Server")
        else:
            self.start_server_btn.configure(text="Start Server")

        # Update app-level status
        if hasattr(self.app, '_project_status'):
            self.app._project_status = status
        if hasattr(self.app, 'status_bar'):
            self.app.status_bar.update_status(status)
        if hasattr(self.app, 'sidebar') and hasattr(self.app.sidebar, 'update_project_info'):
            self.app.sidebar.update_project_info(status, self.app.project_name)

    def _rescan_project(self) -> None:
        """Re-run detection on the currently loaded project."""
        if not self.app or not self.app.project_path:
            return
        status = self.detector.detect(self.app.project_path)
        self._update_health_card(status)

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
            # Auto-detect after creation
            self.after(500, self._rescan_project)

    def _create_venv(self) -> None:
        if not self._require_project():
            return

        def _worker():
            self.pm.create_virtualenv(self.app.project_path)
            # Rescan after venv creation
            self.after(500, self._rescan_project)

        threading.Thread(target=_worker, daemon=True).start()

    def _install_django(self) -> None:
        if not self._require_project():
            return

        def _worker():
            self.pm.install_dependencies(self.app.project_path, ["django"])
            self.after(500, self._rescan_project)

        threading.Thread(target=_worker, daemon=True).start()

    def _init_git(self) -> None:
        """Initialize a git repository in the project."""
        if not self._require_project():
            return

        def _worker():
            from core.command_executor import CommandExecutor
            executor = CommandExecutor(log_callback=self._log)
            result = executor.run("git init", cwd=self.app.project_path)
            if result.success:
                self._log("✅ Git repository initialized")
            self.after(500, self._rescan_project)

        threading.Thread(target=_worker, daemon=True).start()

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
        # set_project triggers _refresh_detection which updates
        # status bar, sidebar, AND this panel's health card automatically
        self.app.set_project(path, name)