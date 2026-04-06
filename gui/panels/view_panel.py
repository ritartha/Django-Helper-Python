"""
View Generator Panel — create FBV, CBV, and DRF views from the GUI.
"""

import os
import customtkinter as ctk

from gui.widgets.custom_widgets import (
    SectionHeader, CardFrame, LabeledEntry, LabeledOptionMenu, CodePreview, ConfirmDialog,
)
from templates.view_templates import (
    generate_fbv, generate_cbv, generate_drf_apiview, generate_drf_viewset,
)
from templates.serializer_templates import generate_model_serializer
from utils.file_handler import FileHandler


class ViewPanel(ctk.CTkScrollableFrame):
    """UI for generating Django views (FBV / CBV / DRF)."""

    VIEW_TYPES = ["Function View (FBV)", "Class View (CBV)", "DRF API View", "DRF ViewSet"]
    CBV_TYPES = ["TemplateView", "ListView", "DetailView", "CreateView", "UpdateView", "DeleteView"]

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self._build()

    def _log(self, msg: str) -> None:
        if self.app:
            self.app.log(msg)

    def _build(self) -> None:
        SectionHeader(
            self,
            title="👁️ View Generator",
            description="Generate function‑based, class‑based, or DRF views.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        card = CardFrame(self)
        card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card, text="View Configuration", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.view_type_menu = LabeledOptionMenu(
            card, label="View Type:", values=self.VIEW_TYPES, default=self.VIEW_TYPES[0],
            command=self._on_type_change,
        )
        self.view_type_menu.pack(fill="x", padx=15, pady=5)

        self.view_name_entry = LabeledEntry(card, label="View Name:", placeholder="PostListView")
        self.view_name_entry.pack(fill="x", padx=15, pady=5)

        self.model_name_entry = LabeledEntry(card, label="Model Name:", placeholder="Post")
        self.model_name_entry.pack(fill="x", padx=15, pady=5)

        self.app_name_entry = LabeledEntry(card, label="Target App:", placeholder="blog")
        self.app_name_entry.pack(fill="x", padx=15, pady=5)

        self.cbv_type_menu = LabeledOptionMenu(
            card, label="CBV Type:", values=self.CBV_TYPES, default="ListView",
        )
        self.cbv_type_menu.pack(fill="x", padx=15, pady=5)

        self.template_entry = LabeledEntry(card, label="Template:", placeholder="blog/post_list.html")
        self.template_entry.pack(fill="x", padx=15, pady=(5, 15))

        # ── Preview & generate ────────────────────────────────────────
        ctk.CTkLabel(self, text="Code Preview", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(10, 5)
        )
        self.code_preview = CodePreview(self, height=250)
        self.code_preview.pack(fill="x", padx=15, pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(btn_frame, text="Preview", command=self._preview).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Generate & Write", command=self._generate).pack(side="left")

    def _on_type_change(self, _value: str) -> None:
        """Show/hide CBV‑specific options based on view type selection."""
        pass  # CBV menu always visible for simplicity

    def _get_code(self) -> str:
        vtype = self.view_type_menu.get()
        name = self.view_name_entry.get() or "my_view"
        model = self.model_name_entry.get()
        template = self.template_entry.get()

        if "FBV" in vtype:
            return generate_fbv(name, template)
        elif "CBV" in vtype:
            cbv_type = self.cbv_type_menu.get()
            return generate_cbv(name, model, cbv_type)
        elif "API View" in vtype:
            return generate_drf_apiview(name, model)
        elif "ViewSet" in vtype:
            return generate_drf_viewset(name, model)
        return ""

    def _preview(self) -> None:
        code = self._get_code()
        self.code_preview.set_code(code)

    def _generate(self) -> None:
        if not self.app or not self.app.project_path:
            ConfirmDialog.error("No Project", "Open or create a project first.")
            return
        app_name = self.app_name_entry.get()
        if not app_name:
            ConfirmDialog.error("Missing App", "Please specify a target app.")
            return

        views_path = os.path.join(self.app.project_path, app_name, "views.py")
        code = self._get_code()

        if os.path.exists(views_path):
            existing = FileHandler.read(views_path)
            existing_lines = set(existing.splitlines())
            code_lines = code.split("\n")
            new_lines = []
            for l in code_lines:
                stripped = l.strip()
                if stripped.startswith(("from ", "import ")) and stripped in existing_lines:
                    continue  # Skip duplicate import lines
                new_lines.append(l)
            FileHandler.append(views_path, "\n\n" + "\n".join(new_lines), backup=True)
        else:
            FileHandler.write(views_path, code, backup=False)

        self._log(f"✓ View written to {app_name}/views.py")

        # If DRF, also generate serializer
        vtype = self.view_type_menu.get()
        model = self.model_name_entry.get()
        if ("DRF" in vtype or "API" in vtype) and model:
            ser_path = os.path.join(self.app.project_path, app_name, "serializers.py")
            ser_code = generate_model_serializer(model)
            if os.path.exists(ser_path):
                existing = FileHandler.read(ser_path)
                if model not in existing:
                    FileHandler.append(ser_path, "\n\n" + ser_code, backup=True)
            else:
                FileHandler.write(ser_path, ser_code, backup=False)
            self._log(f"✓ Serializer written to {app_name}/serializers.py")

        ConfirmDialog.info("Done", "View generated successfully!")