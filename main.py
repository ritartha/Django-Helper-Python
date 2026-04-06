#!/usr/bin/env python3
"""
Django Dev Assistant — Main Entry Point
A production-ready desktop tool for automating Django development workflows.
"""

import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import DjangoDevAssistant


def main():
    """Launch the Django Dev Assistant application."""
    app = DjangoDevAssistant()
    app.mainloop()


if __name__ == "__main__":
    main()