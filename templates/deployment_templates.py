"""Templates for deployment configuration files."""


def generate_procfile(project_name: str, server: str = "gunicorn") -> str:
    """Generate a Procfile for Heroku / Railway / Render."""
    if server == "uvicorn":
        return f"web: uvicorn {project_name}.asgi:application --host 0.0.0.0 --port $PORT\n"
    return f"web: gunicorn {project_name}.wsgi --bind 0.0.0.0:$PORT\n"


def generate_runtime_txt(python_version: str = "3.11") -> str:
    """Generate runtime.txt specifying the Python version."""
    return f"python-{python_version}\n"


def generate_env_example() -> str:
    """Generate a .env.example file showing required environment variables."""
    return """# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# Static files
STATIC_URL=/static/
STATIC_ROOT=staticfiles

# Media files
MEDIA_URL=/media/
MEDIA_ROOT=media

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Third-party
CORS_ALLOWED_ORIGINS=http://localhost:3000
"""


def generate_gitignore() -> str:
    """Generate a comprehensive .gitignore for Django projects."""
    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/
eggs/
*.egg

# Virtual environments
venv/
env/
.venv/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Coverage
htmlcov/
.coverage
.coverage.*
"""