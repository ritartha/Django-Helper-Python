"""
Git Manager Panel — full Git workflow from the GUI.
"""

import threading
import customtkinter as ctk

from gui.widgets.custom_widgets import SectionHeader, CardFrame, LabeledEntry, ConfirmDialog
from core.git_manager import GitManager


class GitPanel(ctk.CTkScrollableFrame):
    """UI for Git operations — init, add, commit, push, pull, branch, status, log."""

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.gm = GitManager(log_callback=self._log)
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
            title="🌿 Git Manager",
            description="Manage Git operations for your project directly from the GUI.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # ── Info card ─────────────────────────────────────────────────
        info_card = CardFrame(self)
        info_card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(info_card, text="Repository Info", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.info_label = ctk.CTkLabel(
            info_card, text="No project loaded.", anchor="w", justify="left",
        )
        self.info_label.pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkButton(info_card, text="Refresh Info", width=120, command=self._refresh_info).pack(
            anchor="w", padx=15, pady=(0, 15)
        )

        # ── Basic operations card ─────────────────────────────────────
        card = CardFrame(self)
        card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card, text="Basic Operations", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        btn_grid = ctk.CTkFrame(card, fg_color="transparent")
        btn_grid.pack(fill="x", padx=15, pady=(5, 15))

        buttons = [
            ("Git Init", self._git_init),
            ("Git Add .", self._git_add),
            ("Git Status", self._git_status),
            ("Git Log", self._git_log),
            ("Git Push", self._git_push),
            ("Git Pull", self._git_pull),
        ]

        for i, (text, cmd) in enumerate(buttons):
            row = i // 3
            col = i % 3
            ctk.CTkButton(btn_grid, text=text, width=150, command=cmd).grid(
                row=row, column=col, padx=5, pady=5,
            )

        # ── Commit card ───────────────────────────────────────────────
        card2 = CardFrame(self)
        card2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card2, text="Commit", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.commit_msg_entry = LabeledEntry(card2, label="Commit Message:", placeholder="Initial commit")
        self.commit_msg_entry.pack(fill="x", padx=15, pady=5)

        