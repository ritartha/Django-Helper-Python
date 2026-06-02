"""
Main Application Window — the root container that wires sidebar, panels, status bar,
and console together.
"""

import customtkinter as ctk
from gui.sidebar import Sidebar
from gui.console_panel import ConsolePanel
from gui.widgets.status_bar import ProjectStatusBar
from gui.panels.project_panel import ProjectPanel
from gui.panels.app_panel import AppPanel
from gui.panels.model_panel import ModelPanel
from gui.panels.url_panel import URLPanel
from gui.panels.view_panel import ViewPanel
from gui.panels.settings_panel import SettingsPanel
from gui.panels.git_panel import GitPanel
from gui.panels.deployment_panel import DeploymentPanel
from gui.panels.docs_panel import DocsPanel
from gui.panels.quick_start_panel import QuickStartPanel
from core.project_detector import ProjectDetector, ProjectStatus


class DjangoDevAssistant(ctk.CTk):
    """Root application window with sidebar navigation and swappable content panels."""

    APP_TITLE = "Django Dev Assistant"
    APP_GEOMETRY = "1320x820"

    def __init__(self):
        super().__init__()

        # ── Window configuration ──────────────────────────────────────
        self.title(self.APP_TITLE)
        self.geometry(self.APP_GEOMETRY)
        self.minsize(1060, 640)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Shared state across panels
        self.project_path: str = ""
        self.project_name: str = ""
        self.venv_name: str = "venv"
        self._project_status: ProjectStatus | None = None
        self._detector = ProjectDetector(log_callback=self._safe_log)

        # ── Layout: sidebar | (status + content) | console ────────────
        #
        #   Row 0: sidebar (col 0) | content area (col 1)
        #   Row 1: status bar (spans cols 0–1)
        #   Row 2: console   (spans cols 0–1)
        #
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)

        # Console panel (shared log sink)
        self.console = ConsolePanel(self)
        self.console.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 5))

        # Status bar
        self.status_bar = ProjectStatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 3))
        self.status_bar.set_refresh_callback(self._refresh_detection)

        # Build every content panel (lazy‑displayed via grid_forget / grid)
        self.panels: dict[str, ctk.CTkFrame] = {}
        self._build_panels()

        # Sidebar (navigation)
        self.sidebar = Sidebar(self, switch_callback=self.show_panel)
        self.sidebar.grid(row=0, column=0, rowspan=1, sticky="ns", padx=(5, 0), pady=5)

        # Show the default panel
        self.show_panel("quickstart")

    # ── Panel construction ────────────────────────────────────────────
    def _build_panels(self) -> None:
        """Instantiate every panel and store them keyed by name."""
        panel_classes: dict[str, type] = {
            "quickstart": QuickStartPanel,
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

        # Auto-refresh the Project Panel's health card when navigating to it
        if name == "project" and self._project_status and self.project_path:
            project_panel = self.panels.get("project")
            if project_panel and hasattr(project_panel, "_update_health_card"):
                project_panel._update_health_card(self._project_status)

    # ── Helpers available to every panel ──────────────────────────────
    def _safe_log(self, message: str) -> None:
        """Log wrapper safe to call before console is built."""
        if hasattr(self, "console"):
            self.console.log(message)

    def log(self, message: str) -> None:
        """Write a message to the shared console panel."""
        self.console.log(message)

    def set_project(self, path: str, name: str) -> None:
        """Update the active project across all panels and run detection."""
        self.project_path = path
        self.project_name = name
        self.log(f"📂 Active project set to: {name} ({path})")

        # Run detection and update all UI indicators
        self._refresh_detection()

    def _refresh_detection(self) -> None:
        """Re-run project detection and update the status bar + sidebar."""
        if not self.project_path:
            self.status_bar.update_status(None)
            self.sidebar.update_project_info(None)
            return

        status = self._detector.detect(self.project_path)
        self._project_status = status

        # Auto-detect venv name
        if status.has_venv:
            self.venv_name = status.venv_name

        # Update UI components
        self.status_bar.update_status(status)
        self.sidebar.update_project_info(status, self.project_name)

        # Also update the Project Panel's health card if it exists
        project_panel = self.panels.get("project")
        if project_panel and hasattr(project_panel, "_update_health_card"):
            project_panel._update_health_card(status)

        # Log a quick summary
        if status.is_django_project:
            self.log(f"✅ Django project confirmed — {status.app_count} app(s) detected")
        elif status.has_manage_py:
            self.log("⚠️ manage.py found but settings module missing")
        else:
            self.log("ℹ️ Selected folder is not a Django project")

        if status.has_venv:
            installed = "Django installed" if status.django_installed else "Django NOT installed"
            self.log(f"🐍 venv: {status.venv_name}/ — {installed}")