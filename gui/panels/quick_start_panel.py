"""
Quick Start Wizard Panel — guided step-by-step project creation.
Creates a fully working Django project in a single flow:
    Step 1  →  Project info & template
    Step 2  →  Virtual environment & dependencies
    Step 3  →  Django scaffold & apps
    Step 4  →  Initial migrations & optional superuser
    Step 5  →  Done! Summary & next actions
"""

import os
import json
import threading
import subprocess
import customtkinter as ctk
from typing import Optional

from gui.widgets.custom_widgets import (
    SectionHeader, CardFrame, LabeledEntry, LabeledOptionMenu, DirectoryPicker, ConfirmDialog,
)
from core.project_manager import ProjectManager
from core.app_manager import AppManager
from core.project_detector import ProjectDetector


# ── Load presets from config ──────────────────────────────────────────
_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")


def _load_presets() -> dict:
    path = os.path.join(_CONFIG_DIR, "presets.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ── Step indicator colours ────────────────────────────────────────────
_STEP_ACTIVE   = ("#2563EB", "#3B82F6")   # bright blue
_STEP_DONE     = ("#16A34A", "#22C55E")   # green
_STEP_PENDING  = ("gray65", "gray45")     # muted
_STEP_TEXT_ACT  = ("white", "white")
_STEP_TEXT_DONE = ("white", "white")
_STEP_TEXT_PEN  = ("gray40", "gray60")


class _StepIndicator(ctk.CTkFrame):
    """Horizontal numbered step tracker: ① ─ ② ─ ③ ─ ④ ─ ⑤"""

    LABELS = ["Setup", "Env", "Scaffold", "Config", "Done"]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.circles: list[ctk.CTkButton] = []
        self.lines: list[ctk.CTkFrame] = []
        self._build()

    def _build(self) -> None:
        for i, label in enumerate(self.LABELS):
            if i > 0:
                line = ctk.CTkFrame(self, height=3, width=40, fg_color=_STEP_PENDING, corner_radius=2)
                line.pack(side="left", padx=0, pady=0)
                self.lines.append(line)

            circle = ctk.CTkButton(
                self,
                text=f"{i + 1}",
                width=34,
                height=34,
                corner_radius=17,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=_STEP_PENDING,
                text_color=_STEP_TEXT_PEN,
                hover=False,
                state="disabled",
            )
            circle.pack(side="left", padx=2)
            self.circles.append(circle)

            lbl = ctk.CTkLabel(
                self, text=label,
                font=ctk.CTkFont(size=10),
                text_color=_STEP_TEXT_PEN,
            )
            lbl.pack(side="left", padx=(0, 6))

    def set_step(self, step: int) -> None:
        """Highlight steps up to *step* (0-indexed)."""
        for i, circle in enumerate(self.circles):
            if i < step:
                circle.configure(fg_color=_STEP_DONE, text_color=_STEP_TEXT_DONE)
            elif i == step:
                circle.configure(fg_color=_STEP_ACTIVE, text_color=_STEP_TEXT_ACT)
            else:
                circle.configure(fg_color=_STEP_PENDING, text_color=_STEP_TEXT_PEN)

        for i, line in enumerate(self.lines):
            if i < step:
                line.configure(fg_color=_STEP_DONE)
            else:
                line.configure(fg_color=_STEP_PENDING)


class QuickStartPanel(ctk.CTkScrollableFrame):
    """Guided wizard to create a complete Django project in one flow."""

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.pm = ProjectManager(log_callback=self._log)
        self.am = AppManager(log_callback=self._log)
        self.detector = ProjectDetector(log_callback=self._log)
        self.presets = _load_presets()

        self._current_step = 0
        self._created_path: str = ""
        self._selected_preset_key: str = "blank"

        self._build()
        self._show_step(0)

    def _log(self, msg: str) -> None:
        if self.app:
            self.app.log(msg)

    # ══════════════════════════════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════════════════════════════
    def _build(self) -> None:
        SectionHeader(
            self,
            title="🚀 Quick Start Wizard",
            description="Create a fully configured Django project in seconds — no command line needed.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # Step indicator
        self.step_indicator = _StepIndicator(self)
        self.step_indicator.pack(pady=(5, 15))

        # ── Container for swappable step frames ───────────────────────
        self.step_container = ctk.CTkFrame(self, fg_color="transparent")
        self.step_container.pack(fill="both", expand=True, padx=15)

        self.step_frames: list[ctk.CTkFrame] = []
        self._build_step_0()  # Setup
        self._build_step_1()  # Env
        self._build_step_2()  # Scaffold
        self._build_step_3()  # Config
        self._build_step_4()  # Done

        # ── Navigation buttons ────────────────────────────────────────
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=15, pady=(15, 10))

        self.back_btn = ctk.CTkButton(
            nav, text="← Back", width=120, fg_color="gray40", hover_color="gray50",
            command=self._go_back,
        )
        self.back_btn.pack(side="left")

        self.next_btn = ctk.CTkButton(
            nav, text="Next →", width=120,
            command=self._go_next,
        )
        self.next_btn.pack(side="right")

        # ── Progress / status label ───────────────────────────────────
        self.progress_label = ctk.CTkLabel(
            self, text="", text_color="gray60",
            font=ctk.CTkFont(size=12),
        )
        self.progress_label.pack(fill="x", padx=15, pady=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(self, height=6, corner_radius=3)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 15))
        self.progress_bar.set(0)

    # ── Step 0: Project Setup ─────────────────────────────────────────
    def _build_step_0(self) -> None:
        frame = CardFrame(self.step_container)
        self.step_frames.append(frame)

        ctk.CTkLabel(frame, text="Step 1 — Project Setup",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(frame, text="Choose a name, location, and project template.",
                      text_color="gray60", wraplength=600).pack(
            anchor="w", padx=15, pady=(0, 10))

        self.qs_name = LabeledEntry(frame, label="Project Name:", placeholder="my_django_project")
        self.qs_name.pack(fill="x", padx=15, pady=5)

        self.qs_dir = DirectoryPicker(frame, label="Parent Directory:")
        self.qs_dir.pack(fill="x", padx=15, pady=5)

        # Template selector
        preset_names = [v.get("name", k) for k, v in self.presets.items()]
        preset_keys = list(self.presets.keys())
        self._preset_keys = preset_keys

        self.qs_template = LabeledOptionMenu(
            frame, label="Template:", values=preset_names or ["Blank Project"],
            default=preset_names[0] if preset_names else "Blank Project",
            command=self._on_template_change,
        )
        self.qs_template.pack(fill="x", padx=15, pady=5)

        # Template description
        first_desc = ""
        if self.presets:
            first_key = preset_keys[0]
            first_desc = self.presets[first_key].get("description", "")
        self.template_desc = ctk.CTkLabel(
            frame, text=first_desc, text_color="gray60",
            wraplength=550, justify="left",
        )
        self.template_desc.pack(anchor="w", padx=15, pady=(0, 15))

    def _on_template_change(self, chosen_name: str) -> None:
        """Update description when the user selects a different template."""
        for key, preset in self.presets.items():
            if preset.get("name") == chosen_name:
                self._selected_preset_key = key
                self.template_desc.configure(text=preset.get("description", ""))
                return

    # ── Step 1: Environment ───────────────────────────────────────────
    def _build_step_1(self) -> None:
        frame = CardFrame(self.step_container)
        self.step_frames.append(frame)

        ctk.CTkLabel(frame, text="Step 2 — Virtual Environment & Dependencies",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(frame, text="A virtual environment will be created and dependencies installed automatically.",
                      text_color="gray60", wraplength=600).pack(
            anchor="w", padx=15, pady=(0, 10))

        self.env_status_label = ctk.CTkLabel(
            frame, text="⏳ Waiting to start...",
            font=ctk.CTkFont(size=13), anchor="w", justify="left",
        )
        self.env_status_label.pack(fill="x", padx=15, pady=(5, 15))

    # ── Step 2: Scaffold ──────────────────────────────────────────────
    def _build_step_2(self) -> None:
        frame = CardFrame(self.step_container)
        self.step_frames.append(frame)

        ctk.CTkLabel(frame, text="Step 3 — Django Scaffold",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(frame, text="Creating the Django project and apps from your selected template.",
                      text_color="gray60", wraplength=600).pack(
            anchor="w", padx=15, pady=(0, 10))

        self.scaffold_status_label = ctk.CTkLabel(
            frame, text="⏳ Waiting to start...",
            font=ctk.CTkFont(size=13), anchor="w", justify="left",
        )
        self.scaffold_status_label.pack(fill="x", padx=15, pady=(5, 15))

    # ── Step 3: Initial Config ────────────────────────────────────────
    def _build_step_3(self) -> None:
        frame = CardFrame(self.step_container)
        self.step_frames.append(frame)

        ctk.CTkLabel(frame, text="Step 4 — Initial Setup",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(frame, text="Running initial migrations and optional configuration.",
                      text_color="gray60", wraplength=600).pack(
            anchor="w", padx=15, pady=(0, 10))

        self.migrate_status_label = ctk.CTkLabel(
            frame, text="⏳ Waiting to start...",
            font=ctk.CTkFont(size=13), anchor="w", justify="left",
        )
        self.migrate_status_label.pack(fill="x", padx=15, pady=(5, 5))

        # Optional superuser
        self.create_superuser_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            frame, text="Create a superuser account",
            variable=self.create_superuser_var,
        ).pack(anchor="w", padx=15, pady=(5, 5))

        su_frame = ctk.CTkFrame(frame, fg_color="transparent")
        su_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.su_username = LabeledEntry(su_frame, label="Username:", placeholder="admin")
        self.su_username.pack(fill="x", pady=2)
        self.su_email = LabeledEntry(su_frame, label="Email:", placeholder="admin@example.com")
        self.su_email.pack(fill="x", pady=2)
        self.su_password = LabeledEntry(su_frame, label="Password:", placeholder="strongpassword123")
        self.su_password.pack(fill="x", pady=2)

    # ── Step 4: Done ──────────────────────────────────────────────────
    def _build_step_4(self) -> None:
        frame = CardFrame(self.step_container)
        self.step_frames.append(frame)

        ctk.CTkLabel(frame, text="🎉 Project Created Successfully!",
                      font=ctk.CTkFont(size=18, weight="bold"),
                      text_color=("#16A34A", "#22C55E")).pack(
            anchor="w", padx=15, pady=(15, 5))

        self.done_summary = ctk.CTkLabel(
            frame, text="",
            font=ctk.CTkFont(size=12), anchor="w", justify="left",
            wraplength=600,
        )
        self.done_summary.pack(fill="x", padx=15, pady=(5, 10))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkButton(
            btn_frame, text="📂 Open Folder",
            width=150, command=self._open_folder,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="🚀 Start Server",
            width=150, command=self._start_server,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="🔄 Start New",
            width=150, fg_color="gray40", hover_color="gray50",
            command=self._reset_wizard,
        ).pack(side="left")

    # ══════════════════════════════════════════════════════════════════
    #  NAVIGATION
    # ══════════════════════════════════════════════════════════════════
    def _show_step(self, step: int) -> None:
        for f in self.step_frames:
            f.pack_forget()
        self.step_frames[step].pack(fill="x", padx=0, pady=5)
        self.step_indicator.set_step(step)
        self._current_step = step

        # Button visibility
        self.back_btn.configure(state="normal" if step > 0 and step < 4 else "disabled")
        if step == 4:
            self.next_btn.configure(text="✓ Finish", state="disabled")
        elif step == 3:
            self.next_btn.configure(text="Finish Setup →", state="normal")
        else:
            self.next_btn.configure(text="Next →", state="normal")

    def _go_back(self) -> None:
        if self._current_step > 0:
            self._show_step(self._current_step - 1)

    def _go_next(self) -> None:
        step = self._current_step
        if step == 0:
            if self._validate_step_0():
                self._show_step(1)
                self._run_step_1()
        elif step == 1:
            # Step 1 auto-advances; allow manual advance if already done
            self._show_step(2)
            self._run_step_2()
        elif step == 2:
            self._show_step(3)
        elif step == 3:
            self._run_step_3()

    # ══════════════════════════════════════════════════════════════════
    #  STEP LOGIC
    # ══════════════════════════════════════════════════════════════════

    # ── Step 0: validation ────────────────────────────────────────────
    def _validate_step_0(self) -> bool:
        name = self.qs_name.get()
        base = self.qs_dir.get()
        if not name:
            ConfirmDialog.error("Missing Name", "Please enter a project name.")
            return False
        if not base or not os.path.isdir(base):
            ConfirmDialog.error("Invalid Directory", "Please select a valid parent directory.")
            return False
        # Check if directory already exists
        target = os.path.join(base, name)
        if os.path.exists(target):
            ConfirmDialog.error("Already Exists", f"The directory '{target}' already exists.")
            return False
        self._created_path = target
        return True

    # ── Step 1: venv + deps ───────────────────────────────────────────
    def _run_step_1(self) -> None:
        self.next_btn.configure(state="disabled")
        self.progress_bar.set(0.1)
        self.progress_label.configure(text="Creating virtual environment...")
        self.env_status_label.configure(text="⏳ Creating virtual environment...")

        def _worker():
            name = self.qs_name.get()
            base = self.qs_dir.get()
            project_path = os.path.join(base, name)

            # Ensure directory exists
            os.makedirs(project_path, exist_ok=True)
            self._created_path = project_path

            # Create venv
            result = self.pm.create_virtualenv(project_path)
            if not result.success:
                self.after(0, lambda: self._step_error("Failed to create virtual environment."))
                return

            self.after(0, lambda: self.progress_bar.set(0.3))
            self.after(0, lambda: self.progress_label.configure(text="Installing dependencies..."))
            self.after(0, lambda: self.env_status_label.configure(text="✅ venv created\n⏳ Installing dependencies..."))

            # Get deps from preset
            preset = self.presets.get(self._selected_preset_key, {})
            deps = preset.get("dependencies", ["django"])
            if "django" not in deps:
                deps.insert(0, "django")

            result = self.pm.install_dependencies(project_path, deps)
            if not result.success:
                self.after(0, lambda: self._step_error("Failed to install dependencies."))
                return

            dep_list = ", ".join(deps)
            self.after(0, lambda: self.env_status_label.configure(
                text=f"✅ venv created\n✅ Dependencies installed: {dep_list}"
            ))
            self.after(0, lambda: self.progress_bar.set(0.4))
            self.after(0, lambda: self.progress_label.configure(text="Environment ready!"))
            self.after(0, lambda: self.next_btn.configure(state="normal"))

        threading.Thread(target=_worker, daemon=True).start()

    # ── Step 2: scaffold ──────────────────────────────────────────────
    def _run_step_2(self) -> None:
        self.next_btn.configure(state="disabled")
        self.progress_bar.set(0.5)
        self.progress_label.configure(text="Creating Django project...")
        self.scaffold_status_label.configure(text="⏳ Running django-admin startproject...")

        def _worker():
            name = self.qs_name.get()

            # startproject
            result = self.pm.create_project(name, os.path.dirname(self._created_path))
            # It may fail if dir already exists (we pre-created it for venv).
            # In that case the venv is already inside, so django-admin might still work
            # because create_project uses "django-admin startproject <name> ." inside the dir.
            # Let's try running it directly.

            # Actually, create_project checks if dir exists and returns error.
            # We already created it for venv, so we need to run the command directly.
            from core.command_executor import CommandExecutor
            executor = CommandExecutor(log_callback=self._log)
            venv_path = os.path.join(self._created_path, "venv")
            result = executor.run_with_venv(
                f"django-admin startproject {name} .",
                venv_path, cwd=self._created_path,
            )

            if not result.success:
                self.after(0, lambda: self._step_error("Failed to create Django project."))
                return

            self.after(0, lambda: self.progress_bar.set(0.6))

            # Create .gitignore
            from templates.deployment_templates import generate_gitignore
            from utils.file_handler import FileHandler
            gitignore_path = os.path.join(self._created_path, ".gitignore")
            FileHandler.write(gitignore_path, generate_gitignore(), backup=False)

            # Create apps from preset
            preset = self.presets.get(self._selected_preset_key, {})
            apps = preset.get("apps", [])
            status_lines = ["✅ Django project created"]

            for i, app_name in enumerate(apps):
                self.after(0, lambda a=app_name: self.scaffold_status_label.configure(
                    text="\n".join(status_lines) + f"\n⏳ Creating app '{a}'..."
                ))
                self.am.create_app(app_name, self._created_path, "venv", auto_register=True)
                status_lines.append(f"✅ App '{app_name}' created & registered")
                pct = 0.6 + (0.15 * (i + 1) / max(len(apps), 1))
                self.after(0, lambda p=pct: self.progress_bar.set(p))

            if not apps:
                status_lines.append("ℹ️ No apps in this template (add them later)")

            status_lines.append("✅ .gitignore created")
            final_text = "\n".join(status_lines)
            self.after(0, lambda: self.scaffold_status_label.configure(text=final_text))
            self.after(0, lambda: self.progress_bar.set(0.75))
            self.after(0, lambda: self.progress_label.configure(text="Scaffold complete!"))
            self.after(0, lambda: self.next_btn.configure(state="normal"))

        threading.Thread(target=_worker, daemon=True).start()

    # ── Step 3: migrations + superuser ────────────────────────────────
    def _run_step_3(self) -> None:
        self.next_btn.configure(state="disabled")
        self.progress_bar.set(0.8)
        self.progress_label.configure(text="Running migrations...")
        self.migrate_status_label.configure(text="⏳ Running makemigrations + migrate...")

        def _worker():
            result = self.pm.run_migrations(self._created_path)
            status_lines = []

            if result.success:
                status_lines.append("✅ Migrations applied successfully")
            else:
                status_lines.append("⚠️ Migration had issues (check console)")

            self.after(0, lambda: self.progress_bar.set(0.9))

            # Superuser
            if self.create_superuser_var.get():
                username = self.su_username.get() or "admin"
                email = self.su_email.get() or "admin@example.com"
                password = self.su_password.get() or "admin123"

                self.after(0, lambda: self.migrate_status_label.configure(
                    text="\n".join(status_lines) + "\n⏳ Creating superuser..."
                ))

                venv_path = os.path.join(self._created_path, "venv")
                from core.command_executor import CommandExecutor
                executor = CommandExecutor(log_callback=self._log)

                # Use environment variable approach for non-interactive superuser creation
                if os.name == "nt":
                    activate = os.path.join(venv_path, "Scripts", "activate.bat")
                    cmd = f'"{activate}" && python manage.py createsuperuser --noinput'
                else:
                    activate = os.path.join(venv_path, "bin", "activate")
                    cmd = f'. "{activate}" && python manage.py createsuperuser --noinput'

                env = {
                    "DJANGO_SUPERUSER_USERNAME": username,
                    "DJANGO_SUPERUSER_EMAIL": email,
                    "DJANGO_SUPERUSER_PASSWORD": password,
                }
                result = executor.run(cmd, cwd=self._created_path, env=env)
                if result.success:
                    status_lines.append(f"✅ Superuser '{username}' created")
                else:
                    status_lines.append("⚠️ Superuser creation had issues (check console)")

            # Set project in app
            name = self.qs_name.get()
            self.after(0, lambda: self.app.set_project(self._created_path, name))

            # Detect final state
            status = self.detector.detect(self._created_path)
            if hasattr(self.app, '_project_status'):
                self.app._project_status = status
            if hasattr(self.app, 'status_bar'):
                self.after(0, lambda: self.app.status_bar.update_status(status))

            final_text = "\n".join(status_lines)
            self.after(0, lambda: self.migrate_status_label.configure(text=final_text))
            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.progress_label.configure(text="All done! 🎉"))

            # Build done summary
            summary_parts = [
                f"📂 Project: {self._created_path}",
                f"🐍 Virtual environment: venv/",
                f"📦 Template: {self.presets.get(self._selected_preset_key, {}).get('name', 'Blank')}",
            ]
            if status.app_count:
                summary_parts.append(f"📱 Apps: {', '.join(status.apps)}")
            summary_parts.append(f"✅ Migrations applied")
            if self.create_superuser_var.get():
                summary_parts.append(f"👤 Superuser: {self.su_username.get() or 'admin'}")

            summary = "\n".join(summary_parts)
            self.after(0, lambda: self.done_summary.configure(text=summary))
            self.after(0, lambda: self._show_step(4))

        threading.Thread(target=_worker, daemon=True).start()

    # ── Helpers ───────────────────────────────────────────────────────
    def _step_error(self, message: str) -> None:
        self.progress_label.configure(text=f"❌ {message}")
        self.next_btn.configure(state="normal")
        ConfirmDialog.error("Error", message)

    def _open_folder(self) -> None:
        if self._created_path and os.path.isdir(self._created_path):
            # Try VS Code first, fall back to file explorer
            try:
                subprocess.Popen(["code", self._created_path], shell=True)
                self._log("📂 Opened in VS Code")
            except Exception:
                os.startfile(self._created_path)
                self._log("📂 Opened in file explorer")

    def _start_server(self) -> None:
        if self._created_path:
            self.pm.start_server(self._created_path)

    def _reset_wizard(self) -> None:
        """Reset the wizard to Step 0 for a new project."""
        self._current_step = 0
        self._created_path = ""
        self._selected_preset_key = "blank"

        self.qs_name.clear()
        self.env_status_label.configure(text="⏳ Waiting to start...")
        self.scaffold_status_label.configure(text="⏳ Waiting to start...")
        self.migrate_status_label.configure(text="⏳ Waiting to start...")
        self.done_summary.configure(text="")
        self.progress_bar.set(0)
        self.progress_label.configure(text="")
        self.create_superuser_var.set(False)

        self._show_step(0)
