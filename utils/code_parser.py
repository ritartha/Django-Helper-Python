"""
AST-based Python code modification utilities.
Prefer AST manipulation over raw string editing to avoid breaking valid Python files.
"""

import ast
import textwrap
from typing import Optional


class CodeParser:
    """Utilities for safely parsing and modifying Python source files using the AST."""

    @staticmethod
    def parse_file(filepath: str) -> ast.Module:
        """Parse a Python file and return its AST."""
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        return ast.parse(source)

    @staticmethod
    def has_import(filepath: str, module: str, name: Optional[str] = None) -> bool:
        """
        Check whether a file already contains a specific import.

        - has_import(path, 'os')               → checks for `import os`
        - has_import(path, 'django.db', 'models') → checks for `from django.db import models`
        """
        tree = CodeParser.parse_file(filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and name is None:
                for alias in node.names:
                    if alias.name == module:
                        return True
            elif isinstance(node, ast.ImportFrom) and name is not None:
                if node.module == module:
                    for alias in node.names:
                        if alias.name == name:
                            return True
        return False

    @staticmethod
    def add_import(filepath: str, import_line: str) -> str:
        """
        Add an import line to the top of a Python file (after existing imports)
        if it doesn't already exist. Returns the modified source.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Avoid duplicates
        if any(import_line.strip() in line for line in lines):
            return "".join(lines)

        # Find the position after the last import
        insert_pos = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                insert_pos = i + 1

        lines.insert(insert_pos, import_line.rstrip() + "\n")
        return "".join(lines)

    @staticmethod
    def get_installed_apps(filepath: str) -> list[str]:
        """Extract the list of INSTALLED_APPS from a settings.py file."""
        tree = CodeParser.parse_file(filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "INSTALLED_APPS":
                        if isinstance(node.value, ast.List):
                            return [
                                elt.value
                                for elt in node.value.elts
                                if isinstance(elt, ast.Constant)
                            ]
        return []

    @staticmethod
    def add_to_installed_apps(filepath: str, app_name: str) -> str:
        """
        Add an app to INSTALLED_APPS in settings.py. Uses line-based insertion
        to preserve formatting and comments.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Quick check: don't add duplicates
        if f"'{app_name}'" in content or f'"{app_name}"' in content:
            return content

        lines = content.split("\n")
        in_installed_apps = False
        bracket_depth = 0
        insert_index = -1

        for i, line in enumerate(lines):
            if "INSTALLED_APPS" in line and "=" in line:
                in_installed_apps = True
            if in_installed_apps:
                bracket_depth += line.count("[") - line.count("]")
                if bracket_depth <= 0 and "]" in line:
                    insert_index = i
                    break

        if insert_index == -1:
            return content

        indent = "    "
        new_line = f"{indent}'{app_name}',"
        lines.insert(insert_index, new_line)
        return "\n".join(lines)

    @staticmethod
    def add_to_urlpatterns(filepath: str, url_line: str) -> str:
        """
        Safely add a URL pattern to the urlpatterns list in a urls.py file.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if url_line.strip() in content:
            return content

        lines = content.split("\n")
        in_urlpatterns = False
        bracket_depth = 0
        insert_index = -1

        for i, line in enumerate(lines):
            if "urlpatterns" in line and "=" in line:
                in_urlpatterns = True
            if in_urlpatterns:
                bracket_depth += line.count("[") - line.count("]")
                if bracket_depth <= 0 and "]" in line:
                    insert_index = i
                    break

        if insert_index == -1:
            return content

        indent = "    "
        new_line = f"{indent}{url_line.strip()}"
        lines.insert(insert_index, new_line)
        return "\n".join(lines)

    @staticmethod
    def modify_setting_from_content(content: str, setting_name: str, new_value: str) -> str:
        """
        Modify a top-level setting assignment in a settings.py content string.
        Operates entirely in memory — no file I/O.
        """
        lines = content.splitlines(keepends=True)
        result = []
        skip_continuation = False
        modified = False

        for line in lines:
            if skip_continuation:
                stripped = line.strip()
                # Check if this line closes the multi-line block
                if stripped.endswith("]") or stripped.endswith("}") or stripped.endswith(")"):
                    skip_continuation = False
                # Skip this old continuation line (including the closing line)
                continue

            stripped = line.strip()
            if stripped.startswith(f"{setting_name} ") or stripped.startswith(f"{setting_name}="):
                result.append(f"{setting_name} = {new_value}\n")
                modified = True
                # If the OLD value spans multiple lines, skip them
                eq_idx = stripped.index("=") + 1
                old_value_part = stripped[eq_idx:]
                if any(c in old_value_part for c in ["[", "{", "("]) and \
                   not any(c in old_value_part for c in ["]", "}", ")"]):
                    skip_continuation = True
            else:
                result.append(line)

        if not modified:
            result.append(f"\n{setting_name} = {new_value}\n")

        return "".join(result)

    @staticmethod
    def modify_setting(filepath: str, setting_name: str, new_value: str) -> str:
        """
        Modify a top-level setting assignment in settings.py.
        For example: modify_setting(path, 'DEBUG', 'False')
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return CodeParser.modify_setting_from_content(content, setting_name, new_value)