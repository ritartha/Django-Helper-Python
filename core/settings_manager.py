"""
Settings Manager — automate settings.py modifications for dev/prod modes
and apply recommendations.
"""

import os
from typing import Optional, Callable

from utils.file_handler import FileHandler
from utils.code_parser import CodeParser


class SettingsManager:
    """Automate Django settings.py — mode switching and recommendations."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.log = log_callback or print

    # ── Mode switching ────────────────────────────────────────────────

    def set_development_mode(self, settings_path: str) -> None:
        """Apply development‑friendly settings."""
        self.log("🔧 Switching to Development mode...")
        content = FileHandler.read(settings_path)

        content = CodeParser.modify_setting(settings_path, "DEBUG", "True")
        FileHandler.write(settings_path, content, backup=True)

        content = FileHandler.read(settings_path)
        content = CodeParser.modify_setting(settings_path, "ALLOWED_HOSTS", "['*']")
        FileHandler.write(settings_path, content, backup=True)

        self.log("✓ Development mode activated (DEBUG=True)")

    def set_production_mode(self, settings_path: str) -> None:
        """Apply production‑hardened settings."""
        self.log("🚀 Switching to Production mode...")

        modifications = {
            "DEBUG": "False",
            "ALLOWED_HOSTS": "['*']  # TODO: replace with your domain(s)",
            "CSRF_COOKIE_SECURE": "True",
            "SESSION_COOKIE_SECURE": "True",
            "SECURE_BROWSER_XSS_FILTER": "True",
            "SECURE_CONTENT_TYPE_NOSNIFF": "True",
            "X_FRAME_OPTIONS": "'DENY'",
            "SECURE_SSL_REDIRECT": "False  # Set True when SSL is configured",
            "SECURE_HSTS_SECONDS": "31536000",
            "SECURE_HSTS_INCLUDE_SUBDOMAINS": "True",
            "SECURE_HSTS_PRELOAD": "True",
        }

        for setting, value in modifications.items():
            content = CodeParser.modify_setting(settings_path, setting, value)
            FileHandler.write(settings_path, content, backup=True)

        # Add STATIC_ROOT if missing
        content = FileHandler.read(settings_path)
        if "STATIC_ROOT" not in content:
            content += "\nSTATIC_ROOT = BASE_DIR / 'staticfiles'\n"
            FileHandler.write(settings_path, content, backup=True)

        self.log("✓ Production mode activated (DEBUG=False, security hardened)")

    # ── Recommendations ───────────────────────────────────────────────

    def apply_recommendation(self, settings_path: str, recommendation: str) -> None:
        """Apply a named recommendation to settings.py."""
        handlers = {
            "static_files": self._apply_static_files,
            "media_files": self._apply_media_files,
            "template_dirs": self._apply_template_dirs,
            "csrf_settings": self._apply_csrf,
            "cors_settings": self._apply_cors,
            "postgres_db": self._apply_postgres,
            "logging_setup": self._apply_logging,
            "security_middleware": self._apply_security_middleware,
        }
        handler = handlers.get(recommendation)
        if handler:
            handler(settings_path)
        else:
            self.log(f"⚠ Unknown recommendation: {recommendation}")

    def _apply_static_files(self, path: str) -> None:
        content = FileHandler.read(path)
        additions = """
# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
"""
        if "STATICFILES_DIRS" not in content:
            content += additions
            FileHandler.write(path, content, backup=True)
            self.log("✓ Static files configured")

    def _apply_media_files(self, path: str) -> None:
        content = FileHandler.read(path)
        additions = """
# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
"""
        if "MEDIA_ROOT" not in content:
            content += additions
            FileHandler.write(path, content, backup=True)
            self.log("✓ Media files configured")

    def _apply_template_dirs(self, path: str) -> None:
        content = FileHandler.read(path)
        if "BASE_DIR / 'templates'" not in content and "'DIRS': []" in content:
            content = content.replace("'DIRS': []", "'DIRS': [BASE_DIR / 'templates']")
            FileHandler.write(path, content, backup=True)
            self.log("✓ Template DIRS configured")

    def _apply_csrf(self, path: str) -> None:
        content = FileHandler.read(path)
        if "CSRF_TRUSTED_ORIGINS" not in content:
            content += "\nCSRF_TRUSTED_ORIGINS = [\n    'http://localhost:8000',\n    'http://127.0.0.1:8000',\n]\n"
            FileHandler.write(path, content, backup=True)
            self.log("✓ CSRF settings configured")

    def _apply_cors(self, path: str) -> None:
        content = FileHandler.read(path)
        content = CodeParser.add_to_installed_apps(path, "corsheaders")
        FileHandler.write(path, content, backup=True)

        content = FileHandler.read(path)
        if "CORS_ALLOWED_ORIGINS" not in content:
            content += """
# CORS configuration (django-cors-headers)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True
"""
            FileHandler.write(path, content, backup=True)

        # Add CorsMiddleware
        if "corsheaders.middleware.CorsMiddleware" not in content:
            content = content.replace(
                "'django.middleware.common.CommonMiddleware',",
                "'corsheaders.middleware.CorsMiddleware',\n    'django.middleware.common.CommonMiddleware',",
            )
            FileHandler.write(path, content, backup=True)

        self.log("✓ CORS headers configured (remember to pip install django-cors-headers)")

    def _apply_postgres(self, path: str) -> None:
        content = FileHandler.read(path)
        pg_config = """
# PostgreSQL Database
# Make sure to: pip install psycopg2-binary
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
"""
        # Comment out the existing SQLite block and add PostgreSQL
        if "postgresql" not in content:
            content = content.replace(
                "DATABASES = {",
                "# --- Original SQLite (commented out) ---\n# DATABASES = {",
            )
            # Find the end of the old DATABASES block (heuristic)
            content += pg_config
            FileHandler.write(path, content, backup=True)
            self.log("✓ PostgreSQL database configured (update credentials!)")

    def _apply_logging(self, path: str) -> None:
        content = FileHandler.read(path)
        if "LOGGING" not in content:
            logging_config = """
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
"""
            content += logging_config
            FileHandler.write(path, content, backup=True)
            self.log("✓ Logging configuration added")

    def _apply_security_middleware(self, path: str) -> None:
        content = FileHandler.read(path)
        if "django.middleware.security.SecurityMiddleware" not in content:
            content = content.replace(
                "MIDDLEWARE = [",
                "MIDDLEWARE = [\n    'django.middleware.security.SecurityMiddleware',",
            )
            FileHandler.write(path, content, backup=True)
            self.log("✓ Security middleware added")