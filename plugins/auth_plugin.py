"""
Auth Plugin — one‑click Django authentication scaffolding.

Sets up django.contrib.auth views, creates login/register/logout templates,
adds URL patterns, and optionally installs django‑allauth.
"""

import os
from typing import Callable, Optional

from plugins.base_plugin import BasePlugin
from core.command_executor import CommandExecutor
from utils.file_handler import FileHandler
from utils.code_parser import CodeParser


class AuthPlugin(BasePlugin):
    """Scaffold a complete Django authentication system."""

    name = "auth"
    version = "1.0.0"
    description = "One‑click authentication setup — login, register, logout templates, URL routing, and optional django‑allauth support."

    # ── Contract implementation ───────────────────────────────────────

    def execute(
        self,
        project_path: str,
        log_callback: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> bool:
        log = log_callback or print
        use_allauth = kwargs.get("use_allauth", False)
        venv_name = kwargs.get("venv_name", "venv")
        venv_path = os.path.join(project_path, venv_name)

        # 1. Optionally install django‑allauth
        if use_allauth:
            log("📦 [Auth Plugin] Installing django-allauth...")
            executor = CommandExecutor(log_callback=log)
            result = executor.run_with_venv("pip install django-allauth", venv_path, cwd=project_path)
            if not result.success:
                log("✗ [Auth Plugin] Failed to install django-allauth")
                return False
            self._configure_allauth(project_path, log)

        # 2. Add login/logout redirect settings
        settings_path = FileHandler.find_file(project_path, "settings.py")
        if settings_path:
            self._add_auth_settings(settings_path, log)

        # 3. Create accounts app if it doesn't exist
        accounts_path = os.path.join(project_path, "accounts")
        if not os.path.isdir(accounts_path):
            executor = CommandExecutor(log_callback=log)
            executor.run_with_venv(
                "python manage.py startapp accounts", venv_path, cwd=project_path
            )
            if settings_path:
                content = CodeParser.add_to_installed_apps(settings_path, "accounts")
                FileHandler.write(settings_path, content, backup=True)
            log("✓ [Auth Plugin] Created 'accounts' app")

        # 4. Write views.py for accounts
        self._create_auth_views(accounts_path, log)

        # 5. Write urls.py for accounts
        self._create_auth_urls(accounts_path, log)

        # 6. Create auth templates
        self._create_auth_templates(project_path, log)

        # 7. Include accounts URLs in project urls.py
        self._include_in_project_urls(project_path, log)

        log("✓ [Auth Plugin] Authentication setup complete!")
        return True

    def get_dependencies(self) -> list[str]:
        return []  # django-allauth is optional

    def get_installed_apps(self) -> list[str]:
        return ["accounts"]

    def get_settings_additions(self) -> dict:
        return {
            "LOGIN_REDIRECT_URL": "'/'",
            "LOGOUT_REDIRECT_URL": "'/'",
            "LOGIN_URL": "'/accounts/login/'",
        }

    def get_middleware(self) -> list[str]:
        return []

    # ── Internal helpers ──────────────────────────────────────────────

    def _add_auth_settings(self, settings_path: str, log: Callable) -> None:
        """Append auth redirect settings."""
        content = FileHandler.read(settings_path)
        additions = self.get_settings_additions()
        changed = False
        for key, value in additions.items():
            if key not in content:
                content += f"\n{key} = {value}\n"
                changed = True
        if changed:
            FileHandler.write(settings_path, content, backup=True)
            log("📝 [Auth Plugin] Auth settings added to settings.py")

    def _configure_allauth(self, project_path: str, log: Callable) -> None:
        """Add allauth apps and settings."""
        settings_path = FileHandler.find_file(project_path, "settings.py")
        if not settings_path:
            return

        allauth_apps = [
            "django.contrib.sites",
            "allauth",
            "allauth.account",
            "allauth.socialaccount",
        ]
        for app_entry in allauth_apps:
            content = CodeParser.add_to_installed_apps(settings_path, app_entry)
            FileHandler.write(settings_path, content, backup=True)

        content = FileHandler.read(settings_path)
        if "SITE_ID" not in content:
            content += "\nSITE_ID = 1\n"
        if "AUTHENTICATION_BACKENDS" not in content:
            content += (
                "\nAUTHENTICATION_BACKENDS = [\n"
                "    'django.contrib.auth.backends.ModelBackend',\n"
                "    'allauth.account.auth_backends.AuthenticationBackend',\n"
                "]\n"
            )
            FileHandler.write(settings_path, content, backup=True)
        log("✓ [Auth Plugin] django-allauth configured")

    def _create_auth_views(self, accounts_path: str, log: Callable) -> None:
        """Write a views.py with register, profile views."""
        views_code = '''from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


def register_view(request):
    """Handle user registration."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    """Display user profile."""
    return render(request, "accounts/profile.html")
'''
        views_path = os.path.join(accounts_path, "views.py")
        FileHandler.write(views_path, views_code, backup=True)
        log("✓ [Auth Plugin] Created accounts/views.py")

    def _create_auth_urls(self, accounts_path: str, log: Callable) -> None:
        """Write urls.py for the accounts app including built‑in auth views."""
        urls_code = '''from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path(
        'password-change/',
        auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'),
        name='password_change',
    ),
    path(
        'password-change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
        name='password_change_done',
    ),
]
'''
        urls_path = os.path.join(accounts_path, "urls.py")
        FileHandler.write(urls_path, urls_code, backup=True)
        log("✓ [Auth Plugin] Created accounts/urls.py")

    def _create_auth_templates(self, project_path: str, log: Callable) -> None:
        """Create HTML templates for login, register, profile, password change."""
        templates_dir = os.path.join(project_path, "templates", "accounts")
        FileHandler.ensure_directory(templates_dir)

        templates = {
            "login.html": '''{% extends 'base.html' %}

{% block title %}Login{% endblock %}

{% block content %}
<div style="max-width: 400px; margin: 40px auto;">
    <h2>Login</h2>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" style="width:100%; padding:10px; margin-top:10px;">Login</button>
    </form>
    <p style="margin-top:15px;">Don't have an account? <a href="{% url 'accounts:register' %}">Register</a></p>
</div>
{% endblock %}
''',
            "register.html": '''{% extends 'base.html' %}

{% block title %}Register{% endblock %}

{% block content %}
<div style="max-width: 400px; margin: 40px auto;">
    <h2>Register</h2>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" style="width:100%; padding:10px; margin-top:10px;">Register</button>
    </form>
    <p style="margin-top:15px;">Already have an account? <a href="{% url 'accounts:login' %}">Login</a></p>
</div>
{% endblock %}
''',
            "profile.html": '''{% extends 'base.html' %}

{% block title %}Profile{% endblock %}

{% block content %}
<div style="max-width: 600px; margin: 40px auto;">
    <h2>Profile</h2>
    <p><strong>Username:</strong> {{ user.username }}</p>
    <p><strong>Email:</strong> {{ user.email }}</p>
    <p><strong>Date Joined:</strong> {{ user.date_joined }}</p>
    <a href="{% url 'accounts:password_change' %}">Change Password</a> |
    <a href="{% url 'accounts:logout' %}">Logout</a>
</div>
{% endblock %}
''',
            "password_change.html": '''{% extends 'base.html' %}

{% block title %}Change Password{% endblock %}

{% block content %}
<div style="max-width: 400px; margin: 40px auto;">
    <h2>Change Password</h2>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" style="width:100%; padding:10px; margin-top:10px;">Change Password</button>
    </form>
</div>
{% endblock %}
''',
            "password_change_done.html": '''{% extends 'base.html' %}

{% block title %}Password Changed{% endblock %}

{% block content %}
<div style="max-width: 400px; margin: 40px auto;">
    <h2>Password Changed Successfully</h2>
    <p>Your password has been updated.</p>
    <a href="{% url 'accounts:profile' %}">Back to Profile</a>
</div>
{% endblock %}
''',
        }

        for filename, content in templates.items():
            filepath = os.path.join(templates_dir, filename)
            FileHandler.write(filepath, content, backup=False)

        log(f"✓ [Auth Plugin] Created {len(templates)} auth templates")

    def _include_in_project_urls(self, project_path: str, log: Callable) -> None:
        """Add include('accounts.urls') to the project‑level urls.py."""
        # Find the project-level urls.py (inside the project config package)
        for item in os.listdir(project_path):
            item_path = os.path.join(project_path, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "settings.py")):
                urls_path = os.path.join(item_path, "urls.py")
                if os.path.exists(urls_path):
                    content = FileHandler.read(urls_path)
                    if "accounts.urls" not in content:
                        # Add the include import if missing
                        if "include" not in content:
                            content = content.replace(
                                "from django.urls import path",
                                "from django.urls import path, include",
                            )
                        url_line = "path('accounts/', include('accounts.urls')),"
                        content = CodeParser.add_to_urlpatterns(urls_path, url_line)
                        FileHandler.write(urls_path, content, backup=True)
                        log("✓ [Auth Plugin] Added accounts URLs to project urls.py")
                break