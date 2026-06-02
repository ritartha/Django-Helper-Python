"""
Status Bar Widget — a horizontal bar of color-coded indicator badges
that show the health/state of the currently loaded project.
"""

import customtkinter as ctk
from typing import Optional

# Avoid circular import — we only need the dataclass at runtime
from core.project_detector import ProjectStatus


# ── Badge colour palette ──────────────────────────────────────────────
_COLORS = {
    "green":  {"fg": "#1B5E20", "bg": "#A5D6A7", "dark_fg": "#C8E6C9", "dark_bg": "#2E7D32"},
    "red":    {"fg": "#B71C1C", "bg": "#EF9A9A", "dark_fg": "#FFCDD2", "dark_bg": "#C62828"},
    "yellow": {"fg": "#F57F17", "bg": "#FFF59D", "dark_fg": "#FFF9C4", "dark_bg": "#F9A825"},
    "blue":   {"fg": "#0D47A1", "bg": "#90CAF9", "dark_fg": "#BBDEFB", "dark_bg": "#1565C0"},
    "gray":   {"fg": "#424242", "bg": "#BDBDBD", "dark_fg": "#9E9E9E", "dark_bg": "#616161"},
}


class _Badge(ctk.CTkFrame):
    """A single pill-shaped indicator badge."""

    def __init__(self, master, text: str, color_key: str = "gray", **kwargs):
        colors = _COLORS.get(color_key, _COLORS["gray"])
        super().__init__(
            master,
            corner_radius=12,
            fg_color=(colors["bg"], colors["dark_bg"]),
            height=28,
            **kwargs,
        )

        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=(colors["fg"], colors["dark_fg"]),
            padx=6,
            pady=2,
        )
        self.label.pack(padx=8, pady=2)

    def update_badge(self, text: str, color_key: str) -> None:
        """Change the badge text and color."""
        colors = _COLORS.get(color_key, _COLORS["gray"])
        self.configure(fg_color=(colors["bg"], colors["dark_bg"]))
        self.label.configure(
            text=text,
            text_color=(colors["fg"], colors["dark_fg"]),
        )


class ProjectStatusBar(ctk.CTkFrame):
    """Horizontal bar that shows colour-coded badges for a project's health."""

    def __init__(self, master, **kwargs):
        super().__init__(master, height=44, corner_radius=10, **kwargs)
        self.configure(
            fg_color=("gray92", "gray17"),
            border_width=1,
            border_color=("gray80", "gray30"),
        )

        # ── Left side: project name ───────────────────────────────────
        self.project_label = ctk.CTkLabel(
            self,
            text="  No project selected",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray40", "gray60"),
            anchor="w",
        )
        self.project_label.pack(side="left", padx=(12, 20))

        # ── Badge container ───────────────────────────────────────────
        self.badge_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.badge_frame.pack(side="left", fill="x", expand=True, padx=5)

        self.badges: dict[str, _Badge] = {}
        self._create_initial_badges()

        # ── Right side: refresh button ────────────────────────────────
        self.refresh_btn = ctk.CTkButton(
            self,
            text="⟳",
            width=32,
            height=28,
            corner_radius=14,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            text_color=("gray40", "gray60"),
            command=self._on_refresh,
        )
        self.refresh_btn.pack(side="right", padx=(5, 10))

        self._refresh_callback: Optional[callable] = None

    # ── Initialization ────────────────────────────────────────────────
    def _create_initial_badges(self) -> None:
        """Create all badges in their default (empty) state."""
        badge_defs = [
            ("venv", "● venv", "gray"),
            ("django", "● Django", "gray"),
            ("git", "● Git", "gray"),
            ("apps", "● 0 apps", "gray"),
            ("reqs", "● requirements", "gray"),
        ]
        for key, text, color in badge_defs:
            badge = _Badge(self.badge_frame, text=text, color_key=color)
            badge.pack(side="left", padx=3, pady=6)
            self.badges[key] = badge

    # ── Public API ────────────────────────────────────────────────────
    def set_refresh_callback(self, callback: callable) -> None:
        """Register a callback invoked when the user clicks the refresh button."""
        self._refresh_callback = callback

    def update_status(self, status: Optional[ProjectStatus]) -> None:
        """Refresh all badges from a ``ProjectStatus`` instance."""
        if status is None or not status.path:
            self.project_label.configure(
                text="  No project selected",
                text_color=("gray40", "gray60"),
            )
            for badge in self.badges.values():
                badge.update_badge("● —", "gray")
            return

        # Project name
        import os
        name = os.path.basename(status.path)
        self.project_label.configure(
            text=f"  📂 {name}",
            text_color=("gray10", "gray90"),
        )

        # venv
        if status.has_venv:
            self.badges["venv"].update_badge(f"✔ venv ({status.venv_name})", "green")
        else:
            self.badges["venv"].update_badge("✘ No venv", "red")

        # Django
        if status.is_django_project:
            color = "green" if status.django_installed else "yellow"
            extra = "" if status.django_installed else " (not installed)"
            self.badges["django"].update_badge(f"✔ Django{extra}", color)
        elif status.has_manage_py:
            self.badges["django"].update_badge("⚠ manage.py only", "yellow")
        else:
            self.badges["django"].update_badge("✘ No Django", "red")

        # Git
        if status.has_git:
            self.badges["git"].update_badge("✔ Git", "green")
        else:
            self.badges["git"].update_badge("— No Git", "gray")

        # Apps
        if status.app_count > 0:
            self.badges["apps"].update_badge(f"📱 {status.app_count} app(s)", "blue")
        else:
            self.badges["apps"].update_badge("— 0 apps", "gray")

        # Requirements
        if status.has_requirements:
            self.badges["reqs"].update_badge("✔ requirements.txt", "green")
        else:
            self.badges["reqs"].update_badge("— No requirements", "gray")

    # ── Internal ──────────────────────────────────────────────────────
    def _on_refresh(self) -> None:
        if self._refresh_callback:
            self._refresh_callback()
