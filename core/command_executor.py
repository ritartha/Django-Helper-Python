"""
Subprocess wrapper for executing shell commands.
Provides both synchronous and threaded execution with real-time output streaming.
"""

import subprocess
import threading
import os
from typing import Callable, Optional


class CommandResult:
    """Holds the result of a command execution."""

    def __init__(self, returncode: int, stdout: str, stderr: str, command: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command

    @property
    def success(self) -> bool:
        return self.returncode == 0

    @property
    def output(self) -> str:
        return self.stdout if self.stdout else self.stderr

    def __repr__(self) -> str:
        status = "OK" if self.success else f"FAIL({self.returncode})"
        return f"CommandResult({status}, cmd='{self.command}')"


class CommandExecutor:
    """Execute shell commands with real-time output streaming."""

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        """
        Args:
            log_callback: Function called with each line of output for real-time logging.
        """
        self.log_callback = log_callback or print

    def _log(self, message: str) -> None:
        """Send a message to the log callback."""
        self.log_callback(message)

    def run(self, command: str, cwd: Optional[str] = None, env: Optional[dict] = None) -> CommandResult:
        """
        Execute a command synchronously and capture output.

        Args:
            command: Shell command string.
            cwd: Working directory (defaults to current).
            env: Environment variables (merged with os.environ).
        """
        self._log(f"$ {command}")

        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=run_env,
                text=True,
            )
            stdout, stderr = process.communicate()

            if stdout:
                for line in stdout.strip().split("\n"):
                    self._log(line)
            if stderr:
                for line in stderr.strip().split("\n"):
                    self._log(f"[stderr] {line}")

            result = CommandResult(process.returncode, stdout, stderr, command)

            if result.success:
                self._log(f"✓ Command completed successfully")
            else:
                self._log(f"✗ Command failed with exit code {process.returncode}")

            return result

        except Exception as e:
            self._log(f"✗ Error executing command: {e}")
            return CommandResult(-1, "", str(e), command)

    def run_async(
        self,
        command: str,
        cwd: Optional[str] = None,
        callback: Optional[Callable[[CommandResult], None]] = None,
    ) -> threading.Thread:
        """
        Execute a command in a background thread.

        Args:
            command: Shell command string.
            cwd: Working directory.
            callback: Function called with the CommandResult when done.

        Returns:
            The background Thread object.
        """

        def _worker():
            result = self.run(command, cwd=cwd)
            if callback:
                callback(result)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    def run_with_venv(
        self,
        command: str,
        venv_path: str,
        cwd: Optional[str] = None,
    ) -> CommandResult:
        """
        Execute a command using a specific virtualenv's Python/pip.

        Args:
            command: The command (e.g., 'pip install django').
            venv_path: Path to the virtual environment directory.
            cwd: Working directory.
        """
        if os.name == "nt":
            activate = os.path.join(venv_path, "Scripts", "activate.bat")
            full_cmd = f'"{activate}" && {command}'
        else:
            activate = os.path.join(venv_path, "bin", "activate")
            full_cmd = f'source "{activate}" && {command}'
        return self.run(full_cmd, cwd=cwd)