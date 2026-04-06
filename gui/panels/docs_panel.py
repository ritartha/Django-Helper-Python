"""
Documentation Panel — quick reference for Django commands and project structure.
"""

import webbrowser
import customtkinter as ctk

from gui.widgets.custom_widgets import SectionHeader, CardFrame


class DocsPanel(ctk.CTkScrollableFrame):
    """Quick-reference documentation and helpful links."""

    DOCS_LINKS = [
        ("Django Official Docs", "https://docs.djangoproject.com/"),
        ("Django REST Framework", "https://www.django-rest-framework.org/"),
        ("Celery Docs", "https://docs.celeryq.dev/"),
        ("django-allauth", "https://django-allauth.readthedocs.io/"),
        ("drf-spectacular (OpenAPI)", "https://drf-spectacular.readthedocs.io/"),
        ("Django Deployment Checklist", "https://docs.djangoproject.com/en/stable/howto/deployment/checklist/"),
    ]

    COMMON_COMMANDS = [
        ("Start project", "django-admin startproject myproject ."),
        ("Start app", "python manage.py startapp myapp"),
        ("Make migrations", "python manage.py makemigrations"),
        ("Apply migrations", "python manage.py migrate"),
        ("Create superuser", "python manage.py createsuperuser"),
        ("Run dev server", "python manage.py runserver"),
        ("Collect static", "python manage.py collectstatic"),
        ("Open shell", "python manage.py shell"),
        ("Run tests", "python manage.py test"),
        ("Show URLs", "python manage.py show_urls"),
    ]

    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self._build()

    def _build(self) -> None:
        SectionHeader(
            self,
            title="📚 Documentation",
            description="Quick reference for Django commands and useful links.",
        ).pack(fill="x", padx=15, pady=(15, 10))

        # ── Common Commands card ──────────────────────────────────────
        card = CardFrame(self)
        card.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card, text="Common Django Commands", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        for description, command in self.COMMON_COMMANDS:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=2)

            ctk.CTkLabel(row, text=description, width=200, anchor="w",
                         font=ctk.CTkFont(weight="bold")).pack(side="left")
            ctk.CTkLabel(row, text=command, anchor="w",
                         font=ctk.CTkFont(family="Consolas", size=12),
                         text_color="gray60").pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(card, height=10, fg_color="transparent").pack()  # spacer

        # ── Links card ────────────────────────────────────────────────
        card2 = CardFrame(self)
        card2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(card2, text="Useful Links", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        for title, url in self.DOCS_LINKS:
            ctk.CTkButton(
                card2,
                text=f"🔗  {title}",
                anchor="w",
                fg_color="transparent",
                text_color=("blue", "#5B9BD5"),
                hover_color=("gray85", "gray25"),
                command=lambda u=url: webbrowser.open(u),
            ).pack(fill="x", padx=15, pady=2)

        ctk.CTkFrame(card2, height=10, fg_color="transparent").pack()  # spacer
