"""
Code formatting utilities.
Ensures all generated code follows consistent style guidelines.
"""

import textwrap
from typing import Optional


class CodeFormatter:
    """Format generated Python / Django code for consistency."""

    INDENT = "    "  # 4-space indent per PEP 8

    @staticmethod
    def indent(code: str, level: int = 1) -> str:
        """Indent a block of code by the given number of levels."""
        prefix = CodeFormatter.INDENT * level
        return textwrap.indent(code, prefix)

    @staticmethod
    def dedent(code: str) -> str:
        """Remove common leading whitespace from all lines."""
        return textwrap.dedent(code)

    @staticmethod
    def format_class(class_name: str, bases: list[str], body: str) -> str:
        """Generate a formatted Python class definition."""
        bases_str = ", ".join(bases) if bases else ""
        header = f"class {class_name}({bases_str}):" if bases_str else f"class {class_name}:"
        formatted_body = CodeFormatter.indent(body) if body.strip() else CodeFormatter.indent("pass")
        return f"{header}\n{formatted_body}\n"

    @staticmethod
    def format_function(
        name: str,
        params: list[str],
        body: str,
        decorators: Optional[list[str]] = None,
    ) -> str:
        """Generate a formatted Python function definition."""
        parts = []
        if decorators:
            for dec in decorators:
                parts.append(f"@{dec}")
        params_str = ", ".join(params)
        parts.append(f"def {name}({params_str}):")
        formatted_body = CodeFormatter.indent(body) if body.strip() else CodeFormatter.indent("pass")
        parts.append(formatted_body)
        return "\n".join(parts) + "\n"

    @staticmethod
    def format_imports(imports: list[str]) -> str:
        """Sort and format a list of import statements."""
        stdlib = []
        third_party = []
        local = []

        for imp in imports:
            stripped = imp.strip()
            if stripped.startswith("from .") or stripped.startswith("from " + "apps"):
                local.append(stripped)
            elif stripped.startswith("from django") or stripped.startswith("import django"):
                third_party.append(stripped)
            elif stripped.startswith("from rest_framework") or stripped.startswith("import rest_framework"):
                third_party.append(stripped)
            else:
                stdlib.append(stripped)

        sections = []
        if stdlib:
            sections.append("\n".join(sorted(stdlib)))
        if third_party:
            sections.append("\n".join(sorted(third_party)))
        if local:
            sections.append("\n".join(sorted(local)))

        return "\n\n".join(sections) + "\n" if sections else ""

    @staticmethod
    def clean_blank_lines(code: str, max_consecutive: int = 2) -> str:
        """Collapse runs of blank lines to at most `max_consecutive`."""
        lines = code.split("\n")
        result = []
        blank_count = 0
        for line in lines:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= max_consecutive:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)
        return "\n".join(result)