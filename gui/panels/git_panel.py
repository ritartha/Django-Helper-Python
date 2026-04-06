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

        ctk.CTkButton(card2, text="Git Commit", command=self._git_commit).pack(
            anchor="w", padx=15, pady=(5, 15)
        )

        # ── Branch card ───────────────────────────────────────────────
        card3 = CardFrame(self)
        card3.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card3, text="Branches", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.branch_entry = LabeledEntry(card3, label="Branch Name:", placeholder="feature/my-feature")
        self.branch_entry.pack(fill="x", padx=15, pady=5)

        branch_btn_frame = ctk.CTkFrame(card3, fg_color="transparent")
        branch_btn_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkButton(branch_btn_frame, text="New Branch", command=self._git_new_branch).pack(side="left", padx=(0, 10))
        ctk.CTkButton(branch_btn_frame, text="Checkout Branch", command=self._git_checkout).pack(side="left")

        # ── Remote card ───────────────────────────────────────────────
        card4 = CardFrame(self)
        card4.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card4, text="Remote", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.remote_name_entry = LabeledEntry(card4, label="Remote Name:", placeholder="origin")
        self.remote_name_entry.pack(fill="x", padx=15, pady=5)

        self.remote_url_entry = LabeledEntry(card4, label="Remote URL:", placeholder="https://github.com/user/repo.git")
        self.remote_url_entry.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(card4, text="Add Remote", command=self._git_add_remote).pack(
            anchor="w", padx=15, pady=(5, 15)
        )

    # ── Actions ───────────────────────────────────────────────────────

    def _refresh_info(self) -> None:
        if not self._require_project():
            return
        info = self.gm.get_info(self.app.project_path)
        text = (
            f"Branch:     {info.get('branch', 'unknown')}\n"
            f"Remote:     {info.get('remote', 'not set')}\n"
            f"User:       {info.get('user_name', 'not set')}\n"
            f"Email:      {info.get('user_email', 'not set')}"
        )
        self.info_label.configure(text=text)

    def _git_init(self) -> None:
        if not self._require_project():
            return
        threading.Thread(target=self.gm.init, args=(self.app.project_path,), daemon=True).start()

    def _git_add(self) -> None:
        if not self._require_project():
            return
        threading.Thread(target=self.gm.add_all, args=(self.app.project_path,), daemon=True).start()

    def _git_commit(self) -> None:
        if not self._require_project():
            return
        msg = self.commit_msg_entry.get()
        if not msg:
            ConfirmDialog.error("Missing Message", "Please enter a commit message.")
            return
        threading.Thread(target=self.gm.commit, args=(self.app.project_path, msg), daemon=True).start()

    def _git_status(self) -> None:
        if not self._require_project():
            return
        threading.Thread(target=self.gm.status, args=(self.app.project_path,), daemon=True).start()

    def _git_log(self) -> None:
        if not self._require_project():
            return
        threading.Thread(target=self.gm.log_history, args=(self.app.project_path,), daemon=True).start()

    def _git_push(self) -> None:
        if not self._require_project():
            return
        threading.Thread(target=self.gm.push, args=(self.app.project_path,), daemon=True).start()

    def _git_pull(self) -> None:
        if not self._require_project():
            return
        threading.Thread(target=self.gm.pull, args=(self.app.project_path,), daemon=True).start()

    def _git_new_branch(self) -> None:
        if not self._require_project():
            return
        branch = self.branch_entry.get()
        if not branch:
            ConfirmDialog.error("Missing Name", "Please enter a branch name.")
            return
        threading.Thread(target=self.gm.checkout_new, args=(self.app.project_path, branch), daemon=True).start()

    def _git_checkout(self) -> None:
        if not self._require_project():
            return
        branch = self.branch_entry.get()
        if not branch:
            ConfirmDialog.error("Missing Name", "Please enter a branch name.")
            return
        threading.Thread(target=self.gm.checkout, args=(self.app.project_path, branch), daemon=True).start()

    def _git_add_remote(self) -> None:
        if not self._require_project():
            return
        name = self.remote_name_entry.get() or "origin"
        url = self.remote_url_entry.get()
        if not url:
            ConfirmDialog.error("Missing URL", "Please enter a remote URL.")
            return
        threading.Thread(target=self.gm.add_remote, args=(self.app.project_path, name, url), daemon=True).start()
        