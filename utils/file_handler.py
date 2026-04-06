"""
Safe file read/write operations with backup support.
All file modifications go through this module to ensure data safety.
"""

import os
import shutil
from datetime import datetime
from typing import Optional


class FileHandler:
    """Provides safe file operations with automatic backup."""

    BACKUP_SUFFIX = ".bak"

    @staticmethod
    def read(filepath: str) -> str:
        """Read and return the full contents of a file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def write(filepath: str, content: str, backup: bool = True) -> None:
        """
        Write content to a file.
        If backup=True and the file already exists, a timestamped backup is created first.
        """
        if backup and os.path.exists(filepath):
            FileHandler.create_backup(filepath)

        # Ensure the directory tree exists
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def append(filepath: str, content: str, backup: bool = True) -> None:
        """Append content to the end of a file."""
        if backup and os.path.exists(filepath):
            FileHandler.create_backup(filepath)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def create_backup(filepath: str) -> str:
        """Create a timestamped backup copy of a file. Returns the backup path."""
        if not os.path.exists(filepath):
            return ""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{filepath}.{timestamp}{FileHandler.BACKUP_SUFFIX}"
        shutil.copy2(filepath, backup_path)
        return backup_path

    @staticmethod
    def ensure_directory(dirpath: str) -> None:
        """Create a directory (and parents) if it doesn't exist."""
        os.makedirs(dirpath, exist_ok=True)

    @staticmethod
    def file_exists(filepath: str) -> bool:
        """Check if a file exists."""
        return os.path.exists(filepath)

    @staticmethod
    def find_file(directory: str, filename: str) -> Optional[str]:
        """
        Recursively search for a file by name within a directory tree.
        Returns the full path if found, else None.
        """
        for root, _dirs, files in os.walk(directory):
            if filename in files:
                return os.path.join(root, filename)
        return None