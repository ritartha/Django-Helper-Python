"""
Deployment Manager Panel — generate Procfile, runtime.txt, requirements.txt, and export ZIP.
"""

import threading
import customtkinter as ctk

from gui.widgets.custom_widgets import SectionHeader, CardFrame, LabeledEntry, LabeledOptionMenu, ConfirmDialog
from core.deployment_manager import DeploymentManager


class DeploymentPanel(ctk.CTkScrollableFrame):
    """UI for generating deployment configuration files."""

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.dm = DeploymentManager(log_callback=self._log)
        self._build()

    def _log(self, msg: str) -> None:
        if self.app:
            self.app.log(msg)

    def _require_project(self) -> bool:
        if not self.app or not self.app.project_path:
            ConfirmDialog.error("No Project", "Open or create a project first.")
            return False
        return True

    def _build(self) -> None:
        SectionHeader(
            self,
            title="🚀 Deployment",
            description="Generate deployment configuration files for Heroku, Railway, Render, and more.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # ── Procfile card ─────────────────────────────────────────────
        card = CardFrame(self)
        card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card, text="Procfile", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.project_name_entry = LabeledEntry(card, label="Project Name:", placeholder="myproject")
        self.project_name_entry.pack(fill="x", padx=15, pady=5)

        self.server_menu = LabeledOptionMenu(
            card, label="Server:", values=["gunicorn", "uvicorn"], default="gunicorn",
        )
        self.server_menu.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(card, text="Create Procfile", command=self._create_procfile).pack(
            anchor="w", padx=15, pady=(5, 15)
        )

        # ── Runtime + env card ────────────────────────────────────────
        card2 = CardFrame(self)
        card2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card2, text="Runtime & Environment", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.python_version_entry = LabeledEntry(card2, label="Python Version:", placeholder="3.11")
        self.python_version_entry.pack(fill="x", padx=15, pady=5)

        btn_frame = ctk.CTkFrame(card2, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkButton(btn_frame, text="Create runtime.txt", command=self._create_runtime).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Create .env.example", command=self._create_env_example).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Generate requirements.txt", command=self._gen_requirements).pack(side="left")

        # ── Export card ───────────────────────────────────────────────
        card3 = CardFrame(self)
        card3.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card3, text="Export Project", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        ctk.CTkLabel(
            card3,
            text="Export the project as a ZIP archive (excludes venv, __pycache__, .git).",
            text_color="gray60",
            wraplength=600,
            anchor="w",
        ).pack(fill="x", padx=15)

        ctk.CTkButton(card3, text="Export ZIP", command=self._export_zip).pack(
            anchor="w", padx=15, pady=(10, 15)
        )

    # ── Actions ───────────────────────────────────────────────────────

    def _create_procfile(self) -> None:
        if not self._require_project():
            return
        name = self.project_name_entry.get()
        if not name:
            name = self.app.project_name or "myproject"
        server = self.server_menu.get()
        threading.Thread(
            target=self.dm.create_procfile,
            args=(self.app.project_path, name, server),
            daemon=True,
        ).start()

    def _create_runtime(self) -> None:
        if not self._require_project():
            return
        version = self.python_version_entry.get() or "3.11"
        threading.Thread(
            target=self.dm.create_runtime_txt,
            args=(self.app.project_path, version),
            daemon=True,
        ).start()

    def _create_env_example(self) -> None:
        if not self._require_project():
            return
        threading.Thread(
            target=self.dm.create_env_example,
            args=(self.app.project_path,),
            daemon=True,
        ).start()

    def _gen_requirements(self) -> None:
        if not self._require_project():
            return
        threading.Thread(
            target=self.dm.generate_requirements,
            args=(self.app.project_path, self.app.venv_name),
            daemon=True,
        ).start()

    def _export_zip(self) -> None:
        if not self._require_project():
            return

        def _do_export():
            zip_path = self.dm.export_project_zip(self.app.project_path)
            self.after(0, lambda: ConfirmDialog.info("Exported", f"Project exported to:\n{zip_path}"))

        threading.Thread(target=_do_export, daemon=True).start()
