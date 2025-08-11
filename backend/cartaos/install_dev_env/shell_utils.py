# install-dev-env/shell_utils.py

"""
Utility functions for shell interactions, such as running commands and checking for executables.
"""

import os
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional, Tuple, List


def is_installed(cmd: str) -> bool:
    """Checks if a command is available in the system's PATH."""
    return shutil.which(cmd) is not None


def run_command(
    cmd: List[str],
    env: Optional[dict] = None,
    cwd: Optional[Path] = None,
    use_login_shell: bool = False
) -> Tuple[bool, str]:
    """
    Runs a command, captures its output, and handles errors gracefully.

    Args:
        cmd: The command to run as a list of strings.
        env: Optional dictionary of environment variables.
        cwd: Optional Path object for the working directory.
        use_login_shell: If True, wraps the command in a login shell (e.g., 'bash -lc').

    Returns:
        A tuple of (success: bool, output: str).
    """
    if use_login_shell:
        shell_cmd = " ".join(cmd)
        system = platform.system().lower()
        if system in ("linux", "darwin"):
            cmd = ["bash", "-lc", shell_cmd]
        else:  # Windows
            cmd = ["powershell", "-Command", shell_cmd]

    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=env,
            cwd=cwd
        )
        if p.returncode == 0:
            return True, (p.stdout or "").strip()
        else:
            return False, ((p.stdout or "").strip() + "\n" + (p.stderr or "").strip()).strip()
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"


def get_shell_recommendation() -> str:
    """Provides a shell-specific recommendation for updating the environment."""
    shell_path = os.environ.get("SHELL", "").lower()
    if "zsh" in shell_path:
        return "run 'source ~/.zshrc' or restart your terminal."
    if "bash" in shell_path:
        return "run 'source ~/.bashrc' or 'source ~/.profile', or restart your terminal."
    if "fish" in shell_path:
        return "restart your terminal."
    return "restart your terminal for all PATH changes to take effect."


def check_vs_build_tools() -> bool:
    """
    Checks for Visual Studio Build Tools on Windows, which are required for Rust.
    """
    if platform.system().lower() != "windows":
        return True  # Not applicable

    # A simple but effective check is for vswhere, installed with VS
    vswhere_path = Path(os.environ.get("ProgramFiles(x86)", "")) / "Microsoft Visual Studio/Installer/vswhere.exe"
    if vswhere_path.exists():
        ok, _ = run_command([str(vswhere_path), "-property", "instanceId"])
        return ok

    return False
