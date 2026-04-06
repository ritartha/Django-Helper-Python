"""
Main Application Window — the root container that wires sidebar, panels, and console together.
"""

import customtkinter as ctk
from gui.sidebar import Sidebar
from gui.console_panel import ConsolePanel
from gui.panels.project_panel import ProjectPanel
from gui.panels.app_panel import AppPanel
from gui.panels.model_panel import ModelPanel
from gui.panels.url_panel import URLPanel
from gui.panels.view_panel import ViewPanel
from gui.panels.settings_panel import SettingsPanel
from gui.panels.git_panel import GitPanel
from gui.panels.deployment_panel import DeploymentPanel
from gui.panels.docs_panel import DocsPanel


class DjangoDevAssistant(ctk.CTk):
    """Root application window with sidebar navigation and swappable content panels."""

    APP_TITLE = "Django Dev Assistant"
    APP_GEOMETRY = "1280x780"

    def __init__(self):
        super().__init__()

        # ── Window configuration ──────────────────────────────────────
        self.title(self.APP_TITLE)
        self.geometry(self.APP_GEOMETRY)
        self.minsize(1024, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Shared state across panels
        self.project_path: str = ""
        self.project_name: str = ""
        self.venv_name: str = "venv"

        # ── Layout: sidebar | content | console ──────────────────────
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Console panel (shared log sink)
        self.console = ConsolePanel(self)
        self.console.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 5))
        self.grid_rowconfigure(1, weight=0)

        # Build every content panel (lazy‑displayed via pack_forget / pack)
        self.panels: dict[str, ctk.CTkFrame] = {}
        self._build_panels()

        # Sidebar (navigation)
        self.sidebar = Sidebar(self, switch_callback=self.show_panel)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(5, 0), pady=5)

        # Show the default panel
        self.show_panel("project")

    # ── Panel construction ────────────────────────────────────────────
    def _build_panels(self) -> None:
        """Instantiate every panel and store them keyed by name."""
        panel_classes: dict[str, type] = {
            "project": ProjectPanel,
            "apps": AppPanel,
            "models": ModelPanel,
            "urls": URLPanel,
            "views": ViewPanel,
            "settings": SettingsPanel,
            "git": GitPanel,
            "deploy": DeploymentPanel,
            "docs": DocsPanel,
        }
        for key, cls in panel_classes.items():
            panel = cls(self, app=self)
            self.panels[key] = panel

    # ── Navigation ────────────────────────────────────────────────────
    def show_panel(self, name: str) -> None:
        """Hide all panels, then display the selected one."""
        for panel in self.panels.values():
            panel.grid_forget()

        target = self.panels.get(name)
        if target:
            target.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    # ── Helpers available to every panel ──────────────────────────────
    def log(self, message: str) -> None:
        """Write a message to the shared console panel."""
        self.console.log(message)

    def set_project(self, path: str, name: str) -> None:
        """Update the active project across all panels."""
        self.project_path = path
        self.project_name = name
        self.log(f"📂 Active project set to: {name} ({path})")