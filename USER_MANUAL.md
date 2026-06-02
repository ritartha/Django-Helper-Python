# 📖 Django Dev Assistant — User Manual

> **Version:** 1.1.0  
> **Last Updated:** June 2026  
> A complete guide to using the Django Dev Assistant desktop application.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation & Setup](#2-installation--setup)
3. [Launching the Application](#3-launching-the-application)
4. [Application Layout](#4-application-layout)
5. [Quick Start Wizard](#5-quick-start-wizard)
6. [Project Manager](#6-project-manager)
7. [App Manager](#7-app-manager)
8. [Model Generator](#8-model-generator)
9. [URL Manager](#9-url-manager)
10. [View Generator](#10-view-generator)
11. [Settings Manager](#11-settings-manager)
12. [Git Manager](#12-git-manager)
13. [Deployment](#13-deployment)
14. [Documentation Panel](#14-documentation-panel)
15. [Console Output](#15-console-output)
16. [Project Health & Status Indicators](#16-project-health--status-indicators)
17. [Project Templates](#17-project-templates)
18. [Typical Workflows](#18-typical-workflows)
19. [Troubleshooting & FAQ](#19-troubleshooting--faq)

---

## 1. Introduction

**Django Dev Assistant** is a GUI-based desktop application that automates repetitive Django development tasks. Instead of memorizing terminal commands, you can create projects, manage apps, generate models, configure URLs, switch settings modes, manage Git, and prepare deployments — all from a single visual interface.

### Who is this for?

- **Beginners** learning Django who want a guided project setup experience.
- **Intermediate developers** who want to speed up repetitive scaffolding tasks.
- **Instructors** who need a visual teaching aid for Django concepts.

### What can it do?

| Feature             | Description                                              |
|---------------------|----------------------------------------------------------|
| Quick Start Wizard  | Create a complete Django project in a step-by-step flow  |
| Project Manager     | Create/open projects, manage venvs, run servers          |
| App Manager         | Create Django apps with auto-registration                |
| Model Generator     | Visually design models and generate code                 |
| URL Manager         | Add URL routes safely using AST-based insertion          |
| View Generator      | Generate FBV, CBV, and DRF views with live preview       |
| Settings Manager    | One-click dev/production mode switching                  |
| Git Manager         | Full Git workflow (init, commit, push, branch, etc.)     |
| Deployment          | Generate Procfile, runtime.txt, export ZIP               |
| Documentation       | Built-in Django command reference and useful links       |

---

## 2. Installation & Setup

### Prerequisites

- **Python 3.11** or higher
- **Git** (optional, required for Git Manager features)
- **pip** (comes with Python)

### Step-by-Step Installation

1. **Download or clone** the Django Dev Assistant project to your computer.

2. **Open a terminal** (Command Prompt, PowerShell, or any terminal) and navigate to the project folder:
   ```bash
   cd path/to/Django-Dev-Assistant/project
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   This installs:
   - `customtkinter` — The modern GUI framework
   - `Pillow` — Image processing library
   - `django` — Django framework (also installed per-project)

4. **Verify the installation:**
   ```bash
   python main.py
   ```
   The application window should open.

---

## 3. Launching the Application

To start the application, run:

```bash
python main.py
```

The application opens in **dark mode** by default with a window size of **1320×820 pixels** (minimum 1060×640).

---

## 4. Application Layout

The application window is divided into four main areas:

```
┌──────────────┬────────────────────────────────────────┐
│              │                                        │
│   SIDEBAR    │           CONTENT PANEL                │
│  (Navigation)│    (Changes based on selected tab)     │
│              │                                        │
│  🚀 Quick    │                                        │
│  📁 Project  │                                        │
│  📱 Apps     │                                        │
│  🧱 Models   │                                        │
│  🔗 URLs     │                                        │
│  👁 Views    │                                        │
│  ⚙️ Settings │                                        │
│  🔀 Git      │                                        │
│  ☁️ Deploy   │                                        │
│  📚 Docs     │                                        │
│              │                                        │
├──────────────┴────────────────────────────────────────┤
│  STATUS BAR  (project name + health badges)           │
├───────────────────────────────────────────────────────┤
│  📟 CONSOLE OUTPUT  (timestamped logs)                │
└───────────────────────────────────────────────────────┘
```

### Sidebar (Left)
- Shows the application title and version number.
- Displays the **active project info** with color-coded indicators for venv, Django, and Git status.
- Contains navigation buttons for all 10 panels.
- Click any button to switch the content panel.

### Content Panel (Center)
- Displays the currently selected panel.
- Scrollable to accommodate all content.

### Status Bar (Bottom)
- Shows the active project name.
- Displays color-coded **health badges**: venv, Django, Git, Apps count, and requirements.txt.
- Has a **⟳ Refresh** button to re-scan the project.

### Console Output (Bottom)
- Shows real-time, timestamped log messages from all operations.
- Has a **Clear** button to reset the console.
- Auto-scrolls to the latest message.
- Keeps the last 500 lines of output.

---

## 5. Quick Start Wizard

> **Sidebar:** 🚀 Quick Start

The Quick Start Wizard is the **recommended way** to create a new Django project. It guides you through a 5-step process:

### Step 1 — Project Setup
1. Enter a **Project Name** (e.g., `my_blog`).
2. Choose a **Parent Directory** where the project folder will be created.
3. Select a **Template** from the dropdown:
   - **Blank Project** — Minimal Django setup
   - **Blog Starter** — Blog with posts, categories, auth
   - **E-Commerce Starter** — Products, cart, orders, payments
   - **REST API Project** — DRF with CORS, filtering, OpenAPI
4. Click **Next →** to proceed.

### Step 2 — Virtual Environment & Dependencies
- The wizard **automatically**:
  - Creates the project directory
  - Creates a Python virtual environment (`venv/`)
  - Installs all dependencies from the selected template
- Wait for the green checkmarks to appear, then click **Next →**.

### Step 3 — Django Scaffold
- The wizard **automatically**:
  - Runs `django-admin startproject`
  - Creates all apps defined in the template
  - Registers apps in `INSTALLED_APPS`
  - Creates a `.gitignore` file
- Wait for completion, then click **Next →**.

### Step 4 — Initial Setup
- Migrations are applied automatically.
- **Optional:** Check the "Create a superuser account" box and fill in:
  - Username (default: `admin`)
  - Email (default: `admin@example.com`)
  - Password
- Click **Finish Setup →** to complete.

### Step 5 — Done!
- Shows a summary of everything that was created.
- Action buttons:
  - **📂 Open Folder** — Opens the project in VS Code (or file explorer)
  - **🚀 Start Server** — Starts the Django development server
  - **🔄 Start New** — Resets the wizard for another project

---

## 6. Project Manager

> **Sidebar:** 📁 Project Manager

The Project Manager handles project creation, opening existing projects, and server management.

### 📊 Project Health Card
- Displays the **health status** of the currently loaded project.
- Shows checkmarks (✅) or warnings (⚠️/❌) for:
  - Django project detection
  - Virtual environment
  - Django installation in venv
  - Apps found
  - requirements.txt
  - Git repository
- **⟳ Rescan** button refreshes the detection.
- **Action buttons** appear based on what's missing:
  - 🐍 **Create Virtual Env** — if no venv is detected
  - 📦 **Install Django** — if venv exists but Django isn't installed
  - 🔀 **Init Git** — if no Git repository is found

### Create New Project
1. Enter a **Project Name**.
2. Select a **Parent Directory**.
3. Click **Create Project** to create the directory structure.
4. Use **Create Venv** to set up a virtual environment.
5. Use **Install Django** to install Django in the venv.

### Open Existing Project
1. Click the folder icon to **browse to an existing Django project** folder.
2. Click **Open Project**.
3. The application automatically detects:
   - Whether it's a Django project (looks for `manage.py` and `settings.py`)
   - Virtual environment (checks for `venv/`, `env/`, `.venv/`, `.env/`)
   - Whether Django is installed in the venv
   - Git repository status
   - Existing apps, requirements.txt, and database
4. All status indicators (health card, status bar, sidebar) update automatically.

### Server & Migrations
- **Run Migrations** — Runs `makemigrations` + `migrate` using the project's venv.
- **Start Server** / **Enable Env & Start Server** — Starts the Django development server.
  - If a virtual environment is detected, the button shows **"Enable Env & Start Server"** to indicate the venv will be activated first.
  - If no venv is found, the button shows **"Start Server"**.
- **Generate requirements.txt** — Creates a `requirements.txt` from the venv's installed packages.

---

## 7. App Manager

> **Sidebar:** 📱 App Manager

### Create New App
1. Enter an **App Name** (e.g., `blog`, `accounts`, `api`).
2. **Auto-register in INSTALLED_APPS** is checked by default — the app will be automatically added to your `settings.py`.
3. Click **Create App**.

### Existing Apps
- Shows a list of all apps detected in the current project.
- Click **Refresh** to re-scan.

> **Note:** You must have an active project loaded before creating apps.

---

## 8. Model Generator

> **Sidebar:** 🧱 Model Generator

The Model Generator lets you visually design Django models and generate the code.

### Define Your Model
1. Enter a **Model Name** (e.g., `BlogPost`, `Product`).
2. Enter the **Target App** where the model will be created.

### Add Fields
1. Enter a **Field Name** (e.g., `title`, `price`, `created_at`).
2. Select a **Field Type** from the dropdown:
   - `CharField`, `TextField`, `IntegerField`, `FloatField`, `DecimalField`
   - `BooleanField`, `DateField`, `DateTimeField`, `TimeField`
   - `EmailField`, `URLField`, `SlugField`, `UUIDField`
   - `FileField`, `ImageField`, `JSONField`
   - `ForeignKey`, `ManyToManyField`, `OneToOneField`
3. Click **Add Field**. Repeat for all fields.
4. Use **Clear Fields** to start over.

### Preview & Generate
1. Click **Preview Code** to see the generated Python code.
2. Check **Register in admin.py** to automatically add the model to Django admin.
3. Click **Generate Model** to write the code to your project files.

### Example Output
```python
from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)
```

---

## 9. URL Manager

> **Sidebar:** 🔗 URL Manager

The URL Manager safely adds URL patterns using AST-based code insertion (it won't break your existing code).

### Add App URL Pattern
1. Enter the **App Name** (e.g., `blog`).
2. Enter the **URL Path** (e.g., `posts/`).
3. Enter the **View Name** (e.g., `post_list`).
4. Select the **View Type**: `fbv` (function-based) or `cbv` (class-based).
5. Enter a **URL Name** for reverse lookups (e.g., `post-list`).
6. Click **Add URL Pattern**.

### Include App in Project URLs
1. Enter the **App Name** (e.g., `blog`).
2. Enter the **URL Prefix** (e.g., `blog/`).
3. Click **Add Include** to add the `include()` line to your project's `urls.py`.

> **Note:** The app must already have a `urls.py` file. If it doesn't, create one manually or use the View Generator first.

---

## 10. View Generator

> **Sidebar:** 👁 View Generator

Generate Django views with live code preview. Supports four view types:

### View Types

| Type                    | Description                                    |
|-------------------------|------------------------------------------------|
| **Function View (FBV)** | A simple function-based view                   |
| **Class View (CBV)**    | Class-based views (ListView, DetailView, etc.) |
| **DRF API View**        | Django REST Framework APIView                  |
| **DRF ViewSet**         | Django REST Framework ModelViewSet              |

### How to Use
1. Select the **View Type** from the dropdown.
2. Enter a **View Name** (e.g., `PostListView`).
3. Enter a **Model Name** (required for CBV and DRF views).
4. Enter the **Target App** where the view will be saved.
5. For CBV, select the **CBV Type**: `TemplateView`, `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`.
6. Enter a **Template** path (for views that use templates).
7. Click **Preview** to see the generated code.
8. Click **Generate & Write** to save the code to `views.py`.

### DRF Bonus
When generating DRF views, the tool **automatically creates a serializer** in `serializers.py` if one doesn't exist for the specified model.

---

## 11. Settings Manager

> **Sidebar:** ⚙️ Settings Manager

### Environment Mode Switching
Switch your Django project between development and production settings with one click:

- **🔧 Development Mode** — Sets `DEBUG = True`, allows all hosts, and applies development-friendly settings.
- **🚀 Production Mode** — Sets `DEBUG = False`, restricts `ALLOWED_HOSTS`, and applies security-hardened settings.

### Settings Recommendations
Toggle on/off and apply recommended Django configurations:

| Setting               | What it does                                        |
|-----------------------|-----------------------------------------------------|
| **Static Files**      | Configures `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT` |
| **Media Files**       | Configures `MEDIA_URL` and `MEDIA_ROOT`             |
| **Template DIRS**     | Sets the `TEMPLATES DIRS` to include a `templates/` folder |
| **CSRF Settings**     | Configures `CSRF_TRUSTED_ORIGINS`                   |
| **CORS Headers**      | Installs and configures `django-cors-headers`       |
| **PostgreSQL**        | Switches from SQLite to PostgreSQL configuration    |
| **Logging Setup**     | Adds production-ready logging configuration         |
| **Security Middleware**| Adds `SecurityMiddleware` and secure headers        |

1. Toggle the switches for the settings you want.
2. Click **Apply Selected** to write the changes to `settings.py`.

---

## 12. Git Manager

> **Sidebar:** 🔀 Git Manager

A full Git workflow without leaving the application.

### Repository Info
- Shows current **branch**, **remote**, **user name**, and **email**.
- Click **Refresh Info** to update.

### Basic Operations

| Button        | Git Command    | Description                       |
|---------------|----------------|-----------------------------------|
| **Git Init**  | `git init`     | Initialize a new Git repository   |
| **Git Add .** | `git add .`    | Stage all changes                 |
| **Git Status**| `git status`   | Show the working tree status      |
| **Git Log**   | `git log`      | Show recent commit history        |
| **Git Push**  | `git push`     | Push commits to remote            |
| **Git Pull**  | `git pull`     | Pull latest changes from remote   |

### Commit
1. Enter a **Commit Message** (e.g., `Initial commit`).
2. Click **Git Commit**.

> **Tip:** Always run **Git Add .** before committing to stage your changes.

### Branches
1. Enter a **Branch Name** (e.g., `feature/user-auth`).
2. Click **New Branch** to create and switch to it.
3. Or click **Checkout Branch** to switch to an existing branch.

### Remote
1. Enter a **Remote Name** (default: `origin`).
2. Enter the **Remote URL** (e.g., `https://github.com/user/repo.git`).
3. Click **Add Remote**.

---

## 13. Deployment

> **Sidebar:** ☁️ Deployment

Prepare your project for deployment to platforms like Heroku, Railway, or Render.

### Procfile
1. Enter the **Project Name** (uses your active project name by default).
2. Select the **Server**: `gunicorn` or `uvicorn`.
3. Click **Create Procfile**.

### Runtime & Environment
- **Create runtime.txt** — Specifies the Python version (default: `3.11`).
- **Create .env.example** — Generates a sample environment variables file.
- **Generate requirements.txt** — Creates a `requirements.txt` from installed packages.

### Export Project
- Click **Export ZIP** to create a `.zip` archive of your project.
- The export automatically **excludes**: `venv/`, `__pycache__/`, `.git/` directories.
- Useful for sharing or backing up your project.

---

## 14. Documentation Panel

> **Sidebar:** 📚 Documentation

A built-in quick reference for common Django commands and useful links.

### Common Django Commands

| Task               | Command                              |
|--------------------|--------------------------------------|
| Start project      | `django-admin startproject myproject .` |
| Start app          | `python manage.py startapp myapp`    |
| Make migrations    | `python manage.py makemigrations`    |
| Apply migrations   | `python manage.py migrate`           |
| Create superuser   | `python manage.py createsuperuser`   |
| Run dev server     | `python manage.py runserver`         |
| Collect static     | `python manage.py collectstatic`     |
| Open shell         | `python manage.py shell`             |
| Run tests          | `python manage.py test`              |
| Show URLs          | `python manage.py show_urls`         |

### Useful Links
Clickable links to official documentation for:
- Django, Django REST Framework, Celery, django-allauth, drf-spectacular, and the Django Deployment Checklist.

---

## 15. Console Output

The console panel at the bottom of the application shows **real-time, timestamped logs** for every operation:

```
[14:32:01] 📂 Active project set to: my_blog (C:\Projects\my_blog)
[14:32:01] 🔍 Scanning: C:\Projects\my_blog
[14:32:01] ✅ Django project confirmed — 2 app(s) detected
[14:32:01] 🐍 venv: venv/ — Django installed
```

- All messages are **timestamped** with `[HH:MM:SS]` format.
- The console keeps the **last 500 lines** and auto-trims older entries.
- Click the **Clear** button to reset the console.

---

## 16. Project Health & Status Indicators

The application provides **three levels** of status feedback:

### 1. Status Bar Badges (Bottom Bar)
Color-coded pill badges showing:

| Badge          | Green ✔            | Yellow ⚠              | Red ✘             | Gray —        |
|----------------|---------------------|-----------------------|-------------------|---------------|
| **venv**       | venv found          | —                     | No venv detected  | —             |
| **Django**     | Django project + installed | manage.py only / not installed | No Django project | —         |
| **Git**        | Git repo initialized| —                     | —                 | No Git repo   |
| **Apps**       | N app(s) found      | —                     | —                 | 0 apps        |
| **requirements** | requirements.txt found | —                  | —                 | Not found     |

### 2. Sidebar Indicators
Three small colored dots next to the project name:
- **venv** — 🟢 Green (found) / 🔴 Red (missing)
- **Django** — 🟢 Green (project + installed) / 🟡 Yellow (partial) / 🔴 Red (missing)
- **Git** — 🟢 Green (initialized) / ⚪ Gray (not initialized)

### 3. Project Health Card (Project Manager Panel)
Detailed text-based health report with actionable buttons for missing components.

---

## 17. Project Templates

When using the Quick Start Wizard, you can choose from these templates:

### Blank Project
- **Dependencies:** Django
- **Apps:** None
- **Best for:** Starting from scratch

### Blog Starter
- **Dependencies:** Django, Pillow, django-crispy-forms
- **Apps:** `blog`, `accounts`
- **Best for:** Content-based websites, personal blogs

### E-Commerce Starter
- **Dependencies:** Django, DRF, Pillow, Stripe, django-crispy-forms
- **Apps:** `products`, `cart`, `orders`, `accounts`
- **Best for:** Online stores, marketplace projects

### REST API Project
- **Dependencies:** Django, DRF, django-cors-headers, django-filter, drf-spectacular
- **Apps:** `api`, `accounts`
- **Best for:** Backend APIs, mobile app backends

---

## 18. Typical Workflows

### Workflow 1: Brand New Project (Recommended)

1. Open the app → You'll be on the **Quick Start** panel.
2. Enter project name and directory.
3. Choose a template → Click through all 5 steps.
4. Your project is ready! Click **Start Server** to test it.
5. Visit `http://127.0.0.1:8000/` in your browser.

### Workflow 2: Open an Existing Django Project

1. Go to **📁 Project Manager** in the sidebar.
2. Under "Open Existing Project", browse to your project folder.
3. Click **Open Project**.
4. The health card will show what's detected:
   - ✅ Django project, venv, Git, apps, etc.
   - ❌ Missing components with action buttons to fix them.
5. Use the other panels (Apps, Models, URLs, etc.) to continue development.

### Workflow 3: Add a New Feature to an Existing Project

1. Open your project (Workflow 2 above).
2. Go to **📱 App Manager** → Create a new app (e.g., `products`).
3. Go to **🧱 Model Generator** → Design and generate models.
4. Go to **📁 Project Manager** → Click **Run Migrations**.
5. Go to **👁 View Generator** → Create views for your new models.
6. Go to **🔗 URL Manager** → Add URL patterns and include them in project URLs.
7. Go to **📁 Project Manager** → Start the server and test.

### Workflow 4: Prepare for Deployment

1. Go to **⚙️ Settings Manager** → Switch to **Production Mode**.
2. Apply recommended settings (Static Files, Security Middleware, etc.).
3. Go to **🔀 Git Manager** → Init, Add, Commit, and Push your code.
4. Go to **☁️ Deployment** → Generate Procfile, runtime.txt, requirements.txt.
5. Optionally **Export ZIP** for backup.

---

## 19. Troubleshooting & FAQ

### ❓ "No Project" error when clicking buttons
**Solution:** You need to create or open a project first. Go to the Quick Start Wizard or Project Manager.

### ❓ Virtual environment is not detected
**Solution:** The tool looks for directories named `venv`, `env`, `.venv`, or `.env` that contain a `pyvenv.cfg` file. Make sure your virtual environment is inside the project directory and uses one of these standard names.

### ❓ Django project is not detected
**Solution:** The tool checks for:
- A `manage.py` file in the project root
- A subdirectory containing both `settings.py` and `__init__.py`

If your project structure differs, ensure these files exist in the expected locations.

### ❓ "Start Server" vs "Enable Env & Start Server"
- **"Enable Env & Start Server"** appears when a virtual environment is detected — it activates the venv before running the server.
- **"Start Server"** appears when no venv is detected — it runs the server directly.

### ❓ The health card doesn't update after making changes
**Solution:** Click the **⟳ Rescan** button on the health card or the **⟳** button on the status bar.

### ❓ Model generation says "App Not Found"
**Solution:** Create the app first using the App Manager, then generate models for it.

### ❓ URL pattern addition fails
**Solution:** The target app must have a `urls.py` file. Create one manually with this minimal content:
```python
from django.urls import path

urlpatterns = []
```

### ❓ Application window is too small
**Solution:** The minimum size is 1060×640 pixels. Resize the window or use a larger display.

### ❓ Console shows errors during project creation
**Solution:** Check that:
- Python 3.11+ is installed and available in your PATH
- You have write permissions to the selected directory
- No antivirus is blocking Python/pip processes

### ❓ Git operations fail
**Solution:** Ensure Git is installed and available in your system PATH. Run `git --version` in a terminal to verify.

---

## Getting Help

- Check the **📚 Documentation** panel in the app for quick Django command references.
- Visit the [Django Official Documentation](https://docs.djangoproject.com/) for detailed Django help.
- Review the console output for error messages and debugging information.

---

*Thank you for using Django Dev Assistant! Happy coding! 🎉*
