# 🛠️ Django Dev Assistant

A **GUI-based Python desktop application** that automates repetitive Django development tasks.

## Features

- **Project Manager** — Create projects, virtual environments, install dependencies
- **App Manager** — Create apps with auto-registration in `settings.py`
- **Model Generator** — Visual model builder with admin registration
- **URL Manager** — Safe URL route insertion using AST parsing
- **View Generator** — FBV, CBV, and DRF API view scaffolding
- **Settings Intelligence** — One-click dev/production mode switching
- **Git Manager** — Full Git workflow from GUI
- **Deployment Tools** — Procfile, requirements.txt, runtime.txt generation
- **Documentation** — Built-in Django reference guide
- **Console** — Real-time command output

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Requirements

- Python 3.11+
- Git (for Git Manager)
- Django (installed per-project)

## Architecture

- `gui/` — CustomTkinter UI layer
- `core/` — Business logic modules
- `utils/` — File handling, AST parsing, formatting
- `templates/` — Code generation templates
- `plugins/` — Extensible plugin system
- `config/` — User preferences and presets