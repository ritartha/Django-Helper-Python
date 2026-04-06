"""
Git Manager — wrapper around Git CLI for common operations.
"""

import os
from typing import Optional, Callable

from core.command_executor import CommandExecutor, CommandResult


class GitManager:
    """Provides a clean interface for Git operations from the GUI."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.executor = CommandExecutor(log_callback=log_callback)
        self.log = log_callback or print

    def _run(self, command: str, cwd: str) -> CommandResult:
        return self.executor.run(command, cwd=cwd)

    # ── Basic operations ────────────────────���─────────────────────────

    def init(self, project_path: str) -> CommandResult:
        """Initialize a new Git repository."""
        self.log("🌿 Initializing Git repository...")
        return self._run("git init", project_path)

    def add_all(self, project_path: str) -> CommandResult:
        """Stage all changes."""
        self.log("📋 Staging all changes...")
        return self._run("git add .", project_path)

    def commit(self, project_path: str, message: str) -> CommandResult:
        """Create a commit with the given message."""
        self.log(f"💾 Committing: {message}")
        safe_msg = message.replace('"', '\\"')
        return self._run(f'git commit -m "{safe_msg}"', project_path)

    def status(self, project_path: str) -> CommandResult:
        """Show the working tree status."""
        self.log("📊 Checking status...")
        return self._run("git status", project_path)

    def log_history(self, project_path: str, limit: int = 10) -> CommandResult:
        """Show recent commit history."""
        self.log(f"📜 Showing last {limit} commits...")
        return self._run(f"git log --oneline -n {limit}", project_path)

    def push(self, project_path: str, remote: str = "origin", branch: str = "") -> CommandResult:
        """Push to a remote repository."""
        branch_arg = branch or ""
        self.log(f"⬆️ Pushing to {remote} {branch_arg}...")
        cmd = f"git push {remote} {branch_arg}".strip()
        return self._run(cmd, project_path)

    def pull(self, project_path: str, remote: str = "origin", branch: str = "") -> CommandResult:
        """Pull from a remote repository."""
        branch_arg = branch or ""
        self.log(f"⬇️ Pulling from {remote} {branch_arg}...")
        cmd = f"git pull {remote} {branch_arg}".strip()
        return self._run(cmd, project_path)

    # ── Branch operations ─────────────────────────────────────────────

    def checkout(self, project_path: str, branch: str) -> CommandResult:
        """Switch to an existing branch."""
        self.log(f"🔀 Switching to branch '{branch}'...")
        return self._run(f"git checkout {branch}", project_path)

    def checkout_new(self, project_path: str, branch: str) -> CommandResult:
        """Create and switch to a new branch."""
        self.log(f"🌱 Creating branch '{branch}'...")
        return self._run(f"git checkout -b {branch}", project_path)

    def current_branch(self, project_path: str) -> str:
        """Return the name of the current branch."""
        result = self._run("git branch --show-current", project_path)
        return result.stdout.strip() if result.success else "unknown"

    def list_branches(self, project_path: str) -> list[str]:
        """List all local branches."""
        result = self._run("git branch", project_path)
        if result.success:
            return [b.strip().lstrip("* ") for b in result.stdout.strip().split("\n") if b.strip()]
        return []

    # ── Remote operations ─────────────────────────────────────────────

    def add_remote(self, project_path: str, name: str, url: str) -> CommandResult:
        """Add a remote repository."""
        self.log(f"🔗 Adding remote '{name}' → {url}")
        return self._run(f"git remote add {name} {url}", project_path)

    def get_remote_url(self, project_path: str, name: str = "origin") -> str:
        """Get the URL of a remote."""
        result = self._run(f"git remote get-url {name}", project_path)
        return result.stdout.strip() if result.success else ""

    # ── Info ──────────────────────────────────────────────────────────

    def get_info(self, project_path: str) -> dict:
        """Gather repository info for display in the GUI."""
        return {
            "branch": self.current_branch(project_path),
            "remote": self.get_remote_url(project_path),
            "user_name": self._get_config(project_path, "user.name"),
            "user_email": self._get_config(project_path, "user.email"),
        }

    def _get_config(self, project_path: str, key: str) -> str:
        result = self._run(f"git config {key}", project_path)
        return result.stdout.strip() if result.success else "not set"