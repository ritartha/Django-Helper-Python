"""
Sidebar — vertical navigation rail with icon‑style buttons.
"""

import customtkinter as ctk
from typing import Callable


class Sidebar(ctk.CTkFrame):
    """Fixed‑width sidebar with navigation buttons for every panel."""

    WIDTH = 200

    # (internal_key, display_label, emoji_icon)
    NAV_ITEMS: list[tuple[str, str, str]] = [
        ("project", "Project Manager", "🏗️"),
        ("apps", "App Manager", "📱"),
        ("models", "Model Generator", "🧱"),
        ("urls", "URL Manager", "🔗"),
        ("views", "View Generator", "👁️"),
        ("settings", "Settings Mgr", "⚙️"),
        ("git", "Git Manager", "🌿"),
        ("deploy", "Deployment", "🚀"),
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
        header.pack(pady=(20, 30), padx=10)

        # ── Navigation buttons ────────────────────────────────────────
        for key, label, icon in self.NAV_ITEMS:
            btn = ctk.CTkButton(
                self,
                text=f" {icon}  {label}",
                anchor="w",
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda k=key: self._on_click(k),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.buttons[key] = btn

        # ── Spacer ────────────────────────────────────────────────────
        spacer = ctk.CTkLabel(self, text="")
        spacer.pack(expand=True)

        # ── Footer ────────────────────────────────────────────────────
        version_label = ctk.CTkLabel(
            self,
            text="v1.0.0",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
        )
        version_label.pack(pady=(0, 10))

    def _on_click(self, key: str) -> None:
        """Handle a sidebar button click — highlight active, switch panel."""
        # Reset previous
        if self._active_key and self._active_key in self.buttons:
            self.buttons[self._active_key].configure(fg_color="transparent")

        # Highlight current
        self._active_key = key
        self.buttons[key].configure(fg_color=("gray75", "gray25"))

        self.switch_callback(key)