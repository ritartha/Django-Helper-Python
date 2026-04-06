"""
Settings Manager Panel — one‑click dev/production mode, settings recommendations.
"""

import os
import customtkinter as ctk

from gui.widgets.custom_widgets import SectionHeader, CardFrame, ConfirmDialog
from core.settings_manager import SettingsManager


class SettingsPanel(ctk.CTkScrollableFrame):
    """Settings intelligence system with toggle recommendations."""

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.sm = SettingsManager(log_callback=self._log)
        self._build()

    def _log(self, msg: str) -> None:
        if self.app:
            self.app.log(msg)

    def _build(self) -> None:
        SectionHeader(
            self,
            title="⚙️ Settings Manager",
            description="One‑click mode switching and settings recommendations.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # ── Mode switch card ──────────────────────────────────────────
        card = CardFrame(self)
        card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card, text="Environment Mode", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        ctk.CTkLabel(
            card,
            text="Switch your project between Development and Production settings instantly.",
            text_color="gray60",
            wraplength=600,
        ).pack(anchor="w", padx=15, pady=(0, 10))

        mode_btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        mode_btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            mode_btn_frame, text="🔧 Development Mode", width=200,
            command=self._set_dev_mode,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            mode_btn_frame, text="🚀 Production Mode", width=200,
            fg_color="#c0392b", hover_color="#e74c3c",
            command=self._set_prod_mode,
        ).pack(side="left")

        # ── Recommendations card ──────────────────────────────────────
        card2 = CardFrame(self)
        card2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card2, text="Settings Recommendations", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.toggles: dict[str, ctk.BooleanVar] = {}
        recommendations = [
            ("static_files", "Static Files Config", "Configure STATIC_URL, STATICFILES_DIRS, STATIC_ROOT"),
            ("media_files", "Media Files Config", "Configure MEDIA_URL and MEDIA_ROOT"),
            ("template_dirs", "Template DIRS Config", "Set TEMPLATES DIRS to include a 'templates' folder"),
            ("csrf_settings", "CSRF Settings", "Configure CSRF_TRUSTED_ORIGINS"),
            ("cors_settings", "CORS Headers", "Install and configure django‑cors‑headers"),
            ("postgres_db", "PostgreSQL Database", "Switch from SQLite to PostgreSQL"),
            ("logging_setup", "Logging Setup", "Add a production‑ready logging configuration"),
            ("security_middleware", "Security Middleware", "Add SecurityMiddleware and secure headers"),
        ]

        for key, title, description in recommendations:
            row = ctk.CTkFrame(card2, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)

            var = ctk.BooleanVar(value=False)
            self.toggles[key] = var

            ctk.CTkSwitch(
                row, text="", variable=var, width=40,
                command=lambda k=key: self._on_toggle(k),
            ).pack(side="left", padx=(0, 10))

            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(text_frame, text=title, font=ctk.CTkFont(weight="bold"), anchor="w").pack(
                fill="x"
            )
            ctk.CTkLabel(text_frame, text=description, text_color="gray60", anchor="w", wraplength=500).pack(
                fill="x"
            )

        ctk.CTkButton(card2, text="Apply Selected", command=self._apply_selected).pack(
            anchor="w", padx=15, pady=(10, 15)
        )

    # ── Actions ───────────────────────────────────────────────────────
    def _find_settings(self) -> str | None:
        if not self.app or not self.app.project_path:
            ConfirmDialog.error("No Project", "Open or create a project first.")
            return None
        from utils.file_handler import FileHandler
        path = FileHandler.find_file(self.app.project_path, "settings.py")
        if not path:
            ConfirmDialog.error("Not Found", "settings.py not found in the project.")
        return path

    def _set_dev_mode(self) -> None:
        path = self._find_settings()
        if path:
            self.sm.set_development_mode(path)
            ConfirmDialog.info("Done", "Switched to Development mode.")

    def _set_prod_mode(self) -> None:
        path = self._find_settings()
        if path:
            self.sm.set_production_mode(path)
            ConfirmDialog.info("Done", "Switched to Production mode.")

    def _on_toggle(self, key: str) -> None:
        state = "ON" if self.toggles[key].get() else "OFF"
        self._log(f"⚙️ {key} toggled {state}")

    def _apply_selected(self) -> None:
        path = self._find_settings()
        if not path:
            return

        applied = []
        for key, var in self.toggles.items():
            if var.get():
                self.sm.apply_recommendation(path, key)
                applied.append(key)

        if applied:
            ConfirmDialog.info("Applied", f"Applied: {', '.join(applied)}")
        else:
            ConfirmDialog.info("Nothing Selected", "Toggle at least one recommendation.")