"""
App Manager Panel — create Django apps with auto‑registration.
"""

import threading
import customtkinter as ctk

from gui.widgets.custom_widgets import SectionHeader, CardFrame, LabeledEntry, ConfirmDialog
from core.app_manager import AppManager


class AppPanel(ctk.CTkScrollableFrame):
    """UI for creating and listing Django apps inside the active project."""

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.am = AppManager(log_callback=self._log)
        self._build()

    def _log(self, msg: str) -> None:
        if self.app:
            self.app.log(msg)

    def _build(self) -> None:
        SectionHeader(
            self,
            title="📱 App Manager",
            description="Create Django apps and auto‑register them in INSTALLED_APPS.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # ── Create app card ───────────────────────────────────────────
        card = CardFrame(self)
        card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card, text="Create New App", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.app_name_entry = LabeledEntry(card, label="App Name:", placeholder="blog")
        self.app_name_entry.pack(fill="x", padx=15, pady=5)

        self.auto_register_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            card, text="Auto‑register in INSTALLED_APPS", variable=self.auto_register_var,
        ).pack(anchor="w", padx=15, pady=5)

        ctk.CTkButton(card, text="Create App", command=self._create_app).pack(
            anchor="w", padx=15, pady=(5, 15)
        )

        # ── Existing apps card ────────────────────────────────────────
        card2 = CardFrame(self)
        card2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card2, text="Existing Apps", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.apps_list_label = ctk.CTkLabel(card2, text="No project loaded.", anchor="w")
        self.apps_list_label.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(card2, text="Refresh", width=100, command=self._refresh_apps).pack(
            anchor="w", padx=15, pady=(0, 15)
        )

    # ── Actions ───────────────────────────────────────────────────────
    def _create_app(self) -> None:
        if not self.app or not self.app.project_path:
            ConfirmDialog.error("No Project", "Open or create a project first.")
            return
        name = self.app_name_entry.get()
        if not name:
            ConfirmDialog.error("Missing Name", "Please enter an app name.")
            return

        auto_reg = self.auto_register_var.get()
        threading.Thread(
            target=self.am.create_app,
            args=(name, self.app.project_path, self.app.venv_name, auto_reg),
            daemon=True,
        ).start()

    def _refresh_apps(self) -> None:
        if not self.app or not self.app.project_path:
            return
        apps = self.am.list_apps(self.app.project_path)
        if apps:
            self.apps_list_label.configure(text="\n".join(f"  •  {a}" for a in apps))
        else:
            self.apps_list_label.configure(text="No apps found.")