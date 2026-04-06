"""
Custom reusable widgets used across multiple panels.
"""

import customtkinter as ctk
from typing import Callable, Optional
import tkinter as tk
from tkinter import filedialog, messagebox


class LabeledEntry(ctk.CTkFrame):
    """A horizontal label + entry pair — used everywhere for form fields."""

    def __init__(
        self,
        master,
        label: str,
        placeholder: str = "",
        width: int = 300,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.label = ctk.CTkLabel(self, text=label, width=140, anchor="w")
        self.label.pack(side="left", padx=(0, 10))

        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder, width=width)
        self.entry.pack(side="left", fill="x", expand=True)

    def get(self) -> str:
        return self.entry.get().strip()

    def set(self, value: str) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

    def clear(self) -> None:
        self.entry.delete(0, "end")


class LabeledOptionMenu(ctk.CTkFrame):
    """A horizontal label + option‑menu pair."""

    def __init__(
        self,
        master,
        label: str,
        values: list[str],
        default: str = "",
        command: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.label_widget = ctk.CTkLabel(self, text=label, width=140, anchor="w")
        self.label_widget.pack(side="left", padx=(0, 10))

        self.var = ctk.StringVar(value=default or (values[0] if values else ""))
        self.menu = ctk.CTkOptionMenu(
            self, variable=self.var, values=values, command=command, width=200,
        )
        self.menu.pack(side="left")

    def get(self) -> str:
        return self.var.get()

    def set(self, value: str) -> None:
        self.var.set(value)


class SectionHeader(ctk.CTkFrame):
    """A bold section header with optional description text."""

    def __init__(self, master, title: str, description: str = "", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        ).pack(fill="x")

        if description:
            ctk.CTkLabel(
                self,
                text=description,
                font=ctk.CTkFont(size=12),
                text_color="gray60",
                anchor="w",
            ).pack(fill="x", pady=(2, 0))


class CardFrame(ctk.CTkFrame):
    """A rounded card container with padding — used for grouping related controls."""

    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self.configure(border_width=1, border_color=("gray75", "gray30"))


class ScrollablePanel(ctk.CTkScrollableFrame):
    """A scrollable container that all panels can inherit from."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class DirectoryPicker(ctk.CTkFrame):
    """Label + entry + browse button for selecting a directory."""

    def __init__(self, master, label: str = "Directory:", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        ctk.CTkLabel(self, text=label, width=140, anchor="w").pack(side="left", padx=(0, 10))
        self.entry = ctk.CTkEntry(self, placeholder_text="Select a directory...", width=350)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            self, text="Browse", width=80, command=self._browse,
        ).pack(side="left")

    def _browse(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.entry.delete(0, "end")
            self.entry.insert(0, path)

    def get(self) -> str:
        return self.entry.get().strip()

    def set(self, value: str) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class ConfirmDialog:
    """Static helper to show yes/no confirmation dialogs."""

    @staticmethod
    def ask(title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)

    @staticmethod
    def info(title: str, message: str) -> None:
        messagebox.showinfo(title, message)

    @staticmethod
    def error(title: str, message: str) -> None:
        messagebox.showerror(title, message)


class CodePreview(ctk.CTkFrame):
    """Read‑only code viewer with monospaced font — used for previews."""

    def __init__(self, master, height: int = 200, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=12),
            height=height,
            state="disabled",
            wrap="none",
        )
        self.textbox.pack(fill="both", expand=True)

    def set_code(self, code: str) -> None:
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", code)
        self.textbox.configure(state="disabled")

    def clear(self) -> None:
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")