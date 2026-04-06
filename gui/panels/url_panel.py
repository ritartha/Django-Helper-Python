"""
URL Manager Panel — add URL patterns to app‑level and project‑level urls.py.
"""

import os
import customtkinter as ctk

from gui.widgets.custom_widgets import (
    SectionHeader, CardFrame, LabeledEntry, LabeledOptionMenu, ConfirmDialog,
)
from core.url_manager import URLManager


class URLPanel(ctk.CTkScrollableFrame):
    """UI for safely adding URL routes."""

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.um = URLManager(log_callback=self._log)
        self._build()

    def _log(self, msg: str) -> None:
        if self.app:
            self.app.log(msg)

    def _build(self) -> None:
        SectionHeader(
            self,
            title="🔗 URL Manager",
            description="Add URL routes safely to your Django URL configurations.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # ── App URL card ──────────────────────────────────────────────
        card = CardFrame(self)
        card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card, text="Add App URL Pattern", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.app_name_entry = LabeledEntry(card, label="App Name:", placeholder="blog")
        self.app_name_entry.pack(fill="x", padx=15, pady=5)

        self.url_path_entry = LabeledEntry(card, label="URL Path:", placeholder="posts/")
        self.url_path_entry.pack(fill="x", padx=15, pady=5)

        self.view_name_entry = LabeledEntry(card, label="View Name:", placeholder="post_list")
        self.view_name_entry.pack(fill="x", padx=15, pady=5)

        self.view_type_menu = LabeledOptionMenu(
            card, label="View Type:", values=["fbv", "cbv"], default="fbv",
        )
        self.view_type_menu.pack(fill="x", padx=15, pady=5)

        self.url_name_entry = LabeledEntry(card, label="URL Name:", placeholder="post-list")
        self.url_name_entry.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(card, text="Add URL Pattern", command=self._add_app_url).pack(
            anchor="w", padx=15, pady=(10, 15)
        )

        # ── Include in project card ───────────────────────────────────
        card2 = CardFrame(self)
        card2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card2, text="Include App in Project URLs", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.include_app_entry = LabeledEntry(card2, label="App Name:", placeholder="blog")
        self.include_app_entry.pack(fill="x", padx=15, pady=5)

        self.include_prefix_entry = LabeledEntry(card2, label="URL Prefix:", placeholder="blog/")
        self.include_prefix_entry.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(card2, text="Add Include", command=self._add_include).pack(
            anchor="w", padx=15, pady=(10, 15)
        )

    # ── Actions ───────────────────────────────────────────────────────
    def _add_app_url(self) -> None:
        if not self.app or not self.app.project_path:
            ConfirmDialog.error("No Project", "Open or create a project first.")
            return

        app_name = self.app_name_entry.get()
        url_path = self.url_path_entry.get()
        view_name = self.view_name_entry.get()
        view_type = self.view_type_menu.get()
        url_name = self.url_name_entry.get()

        if not app_name or not view_name:
            ConfirmDialog.error("Missing Info", "App name and view name are required.")
            return

        urls_file = os.path.join(self.app.project_path, app_name, "urls.py")
        if not os.path.exists(urls_file):
            ConfirmDialog.error("Not Found", f"urls.py not found for app '{app_name}'.")
            return

        self.um.add_url_pattern(urls_file, url_path, view_name, view_type, url_name)
        ConfirmDialog.info("Done", f"URL pattern for '{view_name}' added to {app_name}/urls.py")

    def _add_include(self) -> None:
        if not self.app or not self.app.project_path:
            ConfirmDialog.error("No Project", "Open or create a project first.")
            return

        app_name = self.include_app_entry.get()
        prefix = self.include_prefix_entry.get()
        if not app_name:
            ConfirmDialog.error("Missing Info", "App name is required.")
            return

        self.um.include_app_urls(self.app.project_path, app_name, prefix or f"{app_name}/")
        ConfirmDialog.info("Done", f"'{app_name}' URLs included in project urls.py")