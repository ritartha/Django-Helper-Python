"""
Console Output Panel — real‑time log viewer at the bottom of the main window.
"""

import customtkinter as ctk
from datetime import datetime


class ConsolePanel(ctk.CTkFrame):
    """Scrollable console that displays timestamped log messages."""

    MAX_LINES = 500

    def __init__(self, master, **kwargs):
        super().__init__(master, height=180, **kwargs)

        self._line_count = 0

        # ── Header bar ────────────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=(5, 0))

        ctk.CTkLabel(
            header_frame,
            text="📟 Console Output",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header_frame,
            text="Clear",
            width=60,
            height=26,
            font=ctk.CTkFont(size=11),
            command=self.clear,
        ).pack(side="right")

        # ── Text area ─────────────────────────────────────────────────
        self.textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=12),
            state="disabled",
            wrap="word",
            height=140,
        )
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, message: str) -> None:
        """Append a timestamped message to the console (thread‑safe via after())."""
        self.after(0, self._append, message)

    def _append(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"

        self.textbox.configure(state="normal")
        self.textbox.insert("end", line)
        self._line_count += 1

        # Trim old lines when the buffer is full
        if self._line_count > self.MAX_LINES:
            self.textbox.delete("1.0", "2.0")
            self._line_count -= 1

        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear(self) -> None:
        """Clear all console output."""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
        self._line_count = 0