"""Configuration package for Django Dev Assistant."""

import json
import os

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config(filename: str = "settings.json") -> dict:
    """Load a JSON configuration file from the config directory."""
    filepath = os.path.join(CONFIG_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(data: dict, filename: str = "settings.json") -> None:
    """Save data to a JSON configuration file."""
    filepath = os.path.join(CONFIG_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)