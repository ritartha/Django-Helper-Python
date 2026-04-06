"""
Model Generator Panel — visual model builder with field management and code preview.
"""

import os
import threading
import customtkinter as ctk

from gui.widgets.custom_widgets import (
    SectionHeader, CardFrame, LabeledEntry, LabeledOptionMenu, CodePreview, ConfirmDialog,
)
from core.model_generator import ModelGenerator
from templates.model_templates import COMMON_FIELD_TYPES


class ModelPanel(ctk.CTkScrollableFrame):
    """Interactive model builder: add fields, preview code, generate."""

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.mg = ModelGenerator(log_callback=self._log)
        self.fields: list[dict] = []
        self._build()

    def _log(self, msg: str) -> None:
        if self.app:
            self.app.log(msg)

    def _build(self) -> None:
        SectionHeader(
            self,
            title="🧱 Model Generator",
            description="Design Django models visually and generate code with admin registration.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # ── Model info card ───────────────────────────────────────────
        card = CardFrame(self)
        card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card, text="Model Definition", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.model_name_entry = LabeledEntry(card, label="Model Name:", placeholder="BlogPost")
        self.model_name_entry.pack(fill="x", padx=15, pady=5)

        self.app_name_entry = LabeledEntry(card, label="Target App:", placeholder="blog")
        self.app_name_entry.pack(fill="x", padx=15, pady=(5, 15))

        # ── Add field card ────────────────────────────────────────────
        card2 = CardFrame(self)
        card2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card2, text="Add Field", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.field_name_entry = LabeledEntry(card2, label="Field Name:", placeholder="title")
        self.field_name_entry.pack(fill="x", padx=15, pady=5)

        self.field_type_menu = LabeledOptionMenu(
            card2, label="Field Type:", values=COMMON_FIELD_TYPES, default="CharField",
        )
        self.field_type_menu.pack(fill="x", padx=15, pady=5)

        btn_frame = ctk.CTkFrame(card2, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkButton(btn_frame, text="Add Field", command=self._add_field).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Clear Fields", command=self._clear_fields, fg_color="gray40").pack(side="left")

        # ── Fields list ───────────────────────────────────────────────
        card3 = CardFrame(self)
        card3.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card3, text="Current Fields", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        self.fields_label = ctk.CTkLabel(card3, text="No fields added yet.", anchor="w", justify="left")
        self.fields_label.pack(fill="x", padx=15, pady=(0, 15))

        # ── Code preview ──────────────────────────────────────────────
        ctk.CTkLabel(self, text="Code Preview", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(10, 5)
        )
        self.code_preview = CodePreview(self, height=200)
        self.code_preview.pack(fill="x", padx=15, pady=5)

        # ── Action buttons ────────────────────────────────────────────
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(action_frame, text="Preview Code", command=self._preview).pack(side="left", padx=(0, 10))
        ctk.CTkButton(action_frame, text="Generate Model", command=self._generate).pack(side="left", padx=(0, 10))

        self.admin_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(action_frame, text="Register in admin.py", variable=self.admin_var).pack(side="left")

    # ── Field management ──────────────────────────────────────────────
    def _add_field(self) -> None:
        name = self.field_name_entry.get()
        ftype = self.field_type_menu.get()
        if not name:
            ConfirmDialog.error("Missing Name", "Please enter a field name.")
            return
        self.fields.append({"name": name, "type": ftype, "options": {}})
        self._refresh_fields_display()
        self.field_name_entry.clear()
        self._log(f"  + Added field: {name} ({ftype})")

    def _clear_fields(self) -> None:
        self.fields.clear()
        self._refresh_fields_display()
        self.code_preview.clear()

    def _refresh_fields_display(self) -> None:
        if self.fields:
            lines = [f"  •  {f['name']} : {f['type']}" for f in self.fields]
            self.fields_label.configure(text="\n".join(lines))
        else:
            self.fields_label.configure(text="No fields added yet.")

    # ── Preview / generate ────────────────────────────────────────────
    def _preview(self) -> None:
        model_name = self.model_name_entry.get() or "MyModel"
        code = self.mg.preview(model_name, self.fields)
        self.code_preview.set_code(code)

    def _generate(self) -> None:
        model_name = self.model_name_entry.get()
        app_name = self.app_name_entry.get()
        if not model_name or not app_name:
            ConfirmDialog.error("Missing Info", "Please enter both a model name and target app.")
            return
        if not self.app or not self.app.project_path:
            ConfirmDialog.error("No Project", "Open or create a project first.")
            return
        if not self.fields:
            ConfirmDialog.error("No Fields", "Add at least one field to the model.")
            return

        app_path = os.path.join(self.app.project_path, app_name)
        if not os.path.isdir(app_path):
            ConfirmDialog.error("App Not Found", f"The app '{app_name}' does not exist in the project.")
            return

        def _do_generate():
            self.mg.generate(
                model_name=model_name,
                fields=self.fields.copy(),
                app_path=app_path,
                register_admin=self.admin_var.get(),
                run_migrations=False,
                project_path=self.app.project_path,
                venv_name=self.app.venv_name,
            )
            self.after(0, lambda: ConfirmDialog.info("Success", f"Model '{model_name}' generated in {app_name}/models.py"))

        threading.Thread(target=_do_generate, daemon=True).start()