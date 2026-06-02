"""
Sidebar — vertical navigation rail with icon‑style buttons and active project info.
"""

import customtkinter as ctk
from typing import Callable, Optional
from core.project_detector import ProjectStatus


# ── Compact badge colours ─────────────────────────────────────────────
_BADGE_COLORS = {
    "green":  {"bg": ("#A5D6A7", "#2E7D32"), "fg": ("#1B5E20", "#C8E6C9")},
    "red":    {"bg": ("#EF9A9A", "#C62828"), "fg": ("#B71C1C", "#FFCDD2")},
    "yellow": {"bg": ("#FFF59D", "#F9A825"), "fg": ("#F57F17", "#FFF9C4")},
    "gray":   {"bg": ("#BDBDBD", "#616161"), "fg": ("#424242", "#9E9E9E")},
}


class _MiniIndicator(ctk.CTkFrame):
    """Tiny circle indicator (8×8 px)."""

    def __init__(self, master, color: str = "gray", **kwargs):
        colors = _BADGE_COLORS.get(color, _BADGE_COLORS["gray"])
        super().__init__(
            master, width=8, height=8,
            corner_radius=4,
            fg_color=colors["bg"],
            **kwargs,
        )

    def set_color(self, color: str) -> None:
        colors = _BADGE_COLORS.get(color, _BADGE_COLORS["gray"])
        self.configure(fg_color=colors["bg"])


class Sidebar(ctk.CTkFrame):
    """Fixed‑width sidebar with navigation buttons for every panel."""

    WIDTH = 210

    # (internal_key, display_label, emoji_icon)
    NAV_ITEMS: list[tuple[str, str, str]] = [
        ("quickstart", "Quick Start", "🚀"),
        ("project", "Project Manager", "📁"),
        ("apps", "App Manager", "📱"),
        ("models", "Model Generator", "🧱"),
        ("urls", "URL Manager", "🔗"),
        ("views", "View Generator", "👁"),
        ("settings", "Settings Mgr", "⚙️"),
        ("git", "Git Manager", "🔀"),
        ("deploy", "Deployment", "☁️"),
        ("docs", "Documentation", "📚"),
    ]

    def __init__(self, master, switch_callback: Callable[[str], None]):
        super().__init__(master, width=self.WIDTH, corner_radius=0)
        self.switch_callback = switch_callback
        self.buttons: dict[str, ctk.CTkButton] = {}
        self._active_key: str = ""

        self._build()

    def _build(self) -> None:
        # ── Header / branding ─────────────────────────────────────────
        header = ctk.CTkLabel(
            self,
            text="🛠️ Django Dev\n   Assistant",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        header.pack(pady=(18, 10), padx=10)

        # ── Active project info section ───────────────────────────────
        self.project_section = ctk.CTkFrame(
            self, fg_color=("gray88", "gray20"),
            corner_radius=10, border_width=1,
            border_color=("gray78", "gray30"),
        )
        self.project_section.pack(fill="x", padx=8, pady=(0, 12))

        self.project_name_label = ctk.CTkLabel(
            self.project_section,
            text="No project loaded",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray45", "gray55"),
            anchor="w",
            wraplength=180,
        )
        self.project_name_label.pack(fill="x", padx=10, pady=(8, 4))

        # Mini indicator row
        self.indicator_row = ctk.CTkFrame(self.project_section, fg_color="transparent")
        self.indicator_row.pack(fill="x", padx=10, pady=(0, 8))

        self._indicators: dict[str, tuple[_MiniIndicator, ctk.CTkLabel]] = {}

        indicator_defs = [
            ("venv", "venv"),
            ("django", "Django"),
            ("git", "Git"),
        ]
        for key, label_text in indicator_defs:
            wrapper = ctk.CTkFrame(self.indicator_row, fg_color="transparent")
            wrapper.pack(side="left", padx=(0, 10))

            dot = _MiniIndicator(wrapper, color="gray")
            dot.pack(side="left", padx=(0, 3))

            lbl = ctk.CTkLabel(
                wrapper, text=label_text,
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray55"),
            )
            lbl.pack(side="left")

            self._indicators[key] = (dot, lbl)

        # ── Separator ─────────────────────────────────────────────────
        sep = ctk.CTkFrame(self, height=1, fg_color=("gray75", "gray30"))
        sep.pack(fill="x", padx=12, pady=(0, 8))

        # ── Navigation buttons ────────────────────────────────────────
        for key, label, icon in self.NAV_ITEMS:
            btn = ctk.CTkButton(
                self,
                text=f" {icon}  {label}",
                anchor="w",
                height=36,
                corner_radius=8,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda k=key: self._on_click(k),
            )
            btn.pack(fill="x", padx=8, pady=1)
            self.buttons[key] = btn

        # ── Spacer ────────────────────────────────────────────────────
        spacer = ctk.CTkLabel(self, text="")
        spacer.pack(expand=True)

        # ── Footer ────────────────────────────────────────────────────
        version_label = ctk.CTkLabel(
            self,
            text="v1.1.0",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
        )
        version_label.pack(pady=(0, 10))

    # ── Project status update ─────────────────────────────────────────
    def update_project_info(self, status: Optional[ProjectStatus] = None, project_name: str = "") -> None:
        """Refresh the sidebar's project info section from a ``ProjectStatus``."""
        if status is None or not status.path:
            self.project_name_label.configure(
                text="No project loaded",
                text_color=("gray45", "gray55"),
            )
            for key in self._indicators:
                dot, lbl = self._indicators[key]
                dot.set_color("gray")
            return

        import os
        display_name = project_name or os.path.basename(status.path)
        self.project_name_label.configure(
            text=f"📂 {display_name}",
            text_color=("gray10", "gray90"),
        )

        # venv
        dot, lbl = self._indicators["venv"]
        dot.set_color("green" if status.has_venv else "red")

        # Django
        dot, lbl = self._indicators["django"]
        if status.is_django_project and status.django_installed:
            dot.set_color("green")
        elif status.is_django_project or status.has_manage_py:
            dot.set_color("yellow")
        else:
            dot.set_color("red")

        # Git
        dot, lbl = self._indicators["git"]
        dot.set_color("green" if status.has_git else "gray")

    def _on_click(self, key: str) -> None:
        """Handle a sidebar button click — highlight active, switch panel."""
        # Reset previous
        if self._active_key and self._active_key in self.buttons:
            self.buttons[self._active_key].configure(fg_color="transparent")

        # Highlight current
        self._active_key = key
        self.buttons[key].configure(fg_color=("gray75", "gray25"))

        self.switch_callback(key)