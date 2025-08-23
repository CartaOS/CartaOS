# install-dev-env/installer.py

"""
Contains the main Installer class that orchestrates the entire setup process.
"""

import os
import platform
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table, box

# Relative imports from within the package
from . import config
from . import shell_utils as su


@dataclass
class StepResult:
    """Stores the result of a single installation step."""

    name: str
    category: str
    success: bool
    details: str = ""


class Installer:
    """Legacy installer - DEPRECATED. Use SimplifiedInstaller instead."""

    def __init__(self, no_confirm: bool, minimal: bool, dry_run: bool, ci_mode: bool):
        self.console = Console(force_terminal=not ci_mode, no_color=ci_mode)
        # Store flags and set sane defaults for attributes referenced by methods/tests
        self.no_confirm = no_confirm
        self.minimal = minimal
        self.dry_run = dry_run
        self.ci_mode = ci_mode
        self.results: list[StepResult] = []
        self.system = platform.system().lower()
        self.project_root = Path.cwd()
        self.pkg_manager: Optional[str] = None
        # Some tests expect this mapping to exist
        self.step_categories: dict[str, str] = {}

        # Show deprecation warning
        self.console.print(
            "[yellow]WARNING: This installer is deprecated.[/yellow]\n"
            "[yellow]Please use the simplified installer instead:[/yellow]\n"
            "[cyan]python -m cartaos.install_dev_env.cli setup[/cyan]"
        )

        # Delegate to simplified installer, but do not hard-exit in CI/tests
        try:
            from .simplified_installer import SimplifiedInstaller

            simplified = SimplifiedInstaller(dry_run=dry_run, check_only=False)
            success = simplified.run()
        except Exception as e:
            success = False
            self.console.print(
                f"[red]Simplified installer raised an exception: {e}[/red]"
            )

        if not success:
            self.console.print(
                "[red]Setup failed. Please check the output above.[/red]"
            )
            # In CI or dry-run, record failure but do NOT exit; tests will assert behavior
            self.results.append(
                StepResult(
                    "Simplified Setup",
                    "Complete",
                    False,
                    "Delegated to SimplifiedInstaller (failed)",
                )
            )
        else:
            # Legacy compatibility - set up results for any code that expects them
            self.results.append(
                StepResult(
                    "Simplified Setup",
                    "Complete",
                    True,
                    "Delegated to SimplifiedInstaller",
                )
            )

    # --- Utility Methods ---
    def _add_result(self, name: str, category: str, success: bool, details: str = ""):
        self.results.append(StepResult(name, category, success, details))

    def _run_cmd(
        self,
        cmd: List[str],
        env: Optional[dict] = None,
        cwd: Optional[Path] = None,
        read_only: bool = False,
        login_shell: bool = False,
    ) -> Tuple[bool, str]:
        """Run a command via shell_utils with optional dry-run and login shell behavior."""
        cmd_str = " ".join(cmd)
        cwd_str = str(cwd) if cwd else os.getcwd()
        if self.dry_run and not read_only:
            self.console.log(f"[cyan]$ {cmd_str}[/cyan] (in {cwd_str}) [dry-run]")
            return True, "Dry run mode"
        self.console.log(f"[cyan]$ {cmd_str}[/cyan] (in {cwd_str})")
        return su.run_command(cmd, env=env, cwd=cwd, use_login_shell=login_shell)

    def _run_shell(self, command: str, read_only: bool = False) -> Tuple[bool, str]:
        """Run a string command in a login shell to ensure environment variables are loaded."""
        return self._run_cmd([command], read_only=read_only, login_shell=True)

    def _detect_project_root(self) -> Path:
        """Detects the project root directory using Git, with a smart fallback."""
        name, category = "Project Root", "Bootstrap"
        ok, out = self._run_cmd(["git", "rev-parse", "--show-toplevel"], read_only=True)
        if ok and out:
            path = Path(out)
            self._add_result(name, category, True, f"Detected via Git: {path}")
            return path

        self.console.log(
            "[yellow]Warning:[/yellow] Could not use Git to detect project root. Trying fallback search..."
        )
        p = Path.cwd()
        markers = {".git", "pyproject.toml", "package.json", "README.md"}
        for parent in [p] + list(p.parents):
            if any((parent / m).exists() for m in markers):
                self._add_result(
                    name,
                    category,
                    True,
                    f"Detected via marker '{next(m for m in markers if (parent/m).exists())}': {parent}",
                )
                return parent

        fallback_path = Path(__file__).resolve().parent
        self._add_result(
            name,
            category,
            False,
            f"Could not detect project root. Using script location: {fallback_path}",
        )
        return fallback_path

    def _get_shell_recommendation(self) -> str:
        """Provides a shell-specific recommendation for updating the environment."""
        return su.get_shell_recommendation()

    # --- Detection and Verification ---
    def _detect_package_manager(self) -> Optional[str]:
        """Detects the system's primary package manager."""
        name, category = "Package Manager", "Bootstrap"
        if self.system == "darwin" and not su.is_installed("brew"):
            self._add_result(
                name,
                category,
                False,
                'Homebrew not found. Please install it via: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            )
            return None

        managers = {
            "linux": ["apt", "dnf", "pacman"],
            "darwin": ["brew"],
            "windows": ["winget", "choco"],
        }.get(self.system, [])
        for pm in managers:
            if su.is_installed(pm):
                self._add_result(name, category, True, f"Using {pm}")
                return pm

        self._add_result(name, category, False, "No supported package manager found.")
        return None

    def _check_python_version(self) -> bool:
        """Validates the Python version."""
        v = sys.version_info
        ok = (v.major, v.minor) >= config.MIN_PYTHON_VERSION
        self._add_result(
            "Python Version", "Bootstrap", ok, f"Detected {v.major}.{v.minor}"
        )
        return ok

    # --- Installation Logic ---
    def install_system_packages(self, group: str) -> bool:
        """Installs a group of packages ('base', 'tauri', 'tess_langs', 'pipx') from the map."""
        name = f"System packages ({group})"
        category = self.step_categories.get(name, "Essential")
        if not self.pkg_manager:
            self._add_result(name, category, False, "Package manager not available.")
            return False

        pkgs = config.PACKAGE_MAP.get(self.pkg_manager or "", {}).get(group, [])
        if not pkgs:
            self._add_result(
                name, category, True, "No packages defined for this platform/group."
            )
            return True

        if self.dry_run:
            self._add_result(name, category, True, f"DRY RUN: Would install {pkgs}")
            return True

        pm = self.pkg_manager
        confirm_flags = {
            "apt": ["-y"],
            "dnf": ["-y"],
            "pacman": ["--noconfirm"],
            "choco": ["-y"],
            "winget": ["--accept-source-agreements", "--accept-package-agreements"],
        }

        if pm == "apt":
            self._run_cmd(["sudo", "apt-get", "update"])
        if pm == "pacman":
            self._run_cmd(["sudo", "pacman", "-Syu", "--noconfirm"])

        if pm in ["winget", "choco"]:
            all_ok, errors = True, []
            for pkg in pkgs:
                cmd = (
                    [pm, "install", "-e", "--id", pkg]
                    if pm == "winget"
                    else [pm, "install", pkg]
                )
                if self.no_confirm:
                    cmd.extend(confirm_flags.get(pm, []))
                s, o = self._run_cmd(cmd)
                if not s:
                    all_ok = False
                    errors.append(f" - {pkg}: {o}")
            ok, out = all_ok, "\n".join(errors)
        else:
            cmd = {
                "apt": ["sudo", "apt-get", "install"],
                "dnf": ["sudo", "dnf", "install"],
                "pacman": ["sudo", "pacman", "-S"],
                "brew": ["brew", "install"],
            }.get(pm, [])
            if self.no_confirm:
                cmd.extend(confirm_flags.get(pm, []))
            ok, out = self._run_cmd(cmd + pkgs)

        self._add_result(name, category, ok, "Done" if ok else out)
        return ok

    def ensure_tool(
        self,
        name: str,
        check_cmd: str,
        install_logic: Callable[[], None],
        category: str,
        skip_minimal: bool = True,
    ):
        """Generic function to check, install, and verify a command-line tool."""
        if self.minimal and skip_minimal:
            self._add_result(name, category, True, "Skipped (minimal mode)")
            return

        path = shutil.which(check_cmd)
        if path:
            self._add_result(name, category, True, f"Already installed at: {path}")
            return

        if self.dry_run:
            self._add_result(name, category, True, f"DRY RUN: Would install {name}")
            return

        try:
            install_logic()
        except Exception as e:
            self._add_result(
                name, category, False, f"Install failed with an exception: {e}"
            )
            return

        path_after = shutil.which(check_cmd)
        env = os.environ.copy()
        env["PATH"] = (
            str(Path.home() / ".cargo" / "bin")
            + os.pathsep
            + str(Path.home() / ".local/bin")
            + os.pathsep
            + env.get("PATH", "")
        )
        path_after_env = shutil.which(check_cmd, path=env["PATH"])

        if path_after or path_after_env:
            final_path = path_after or path_after_env
            self._add_result(name, category, True, f"Installed to: {final_path}")
        else:
            self._add_result(
                name,
                category,
                False,
                "Installation ran, but command is not in PATH. A shell restart is likely required.",
            )

    def _install_rust(self):
        self._run_shell(
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"
        )

    def _install_tauri_cli(self):
        env = os.environ.copy()
        env["PATH"] = (
            str(Path.home() / ".cargo" / "bin") + os.pathsep + env.get("PATH", "")
        )
        self._run_cmd(["cargo", "install", "tauri-cli"], env=env)

    def _install_pipx(self):
        if not self.install_system_packages("pipx"):
            self._run_cmd([sys.executable, "-m", "pip", "install", "--user", "pipx"])
        self._run_cmd([sys.executable, "-m", "pipx", "ensurepath"])

    def _install_poetry(self):
        self._run_cmd(["pipx", "install", "poetry"])

    def ensure_node(self):
        """Checks for Node.js, falling back to NVM on Unix if not installed by system PM."""
        name, category = "Node.js LTS", "Build Tool"
        if self.minimal:
            self._add_result(name, category, True, "Skipped (minimal mode)")
            return

        ok, out = self._run_cmd(["node", "-v"], read_only=True)
        if ok:
            match = re.search(r"v(\d+)", out)
            if match and int(match.group(1)) >= config.MIN_NODE_MAJOR_VERSION:
                self._add_result(name, category, True, f"Already installed: {out}")
                return

        if self.system in ("linux", "darwin"):
            self._add_result(
                name,
                category,
                False,
                f"Node {config.MIN_NODE_MAJOR_VERSION}+ not found, attempting install via NVM.",
            )
            self._run_shell(
                'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" ; nvm install --lts && nvm use --lts'
            )
        else:
            self._add_result(
                name,
                category,
                False,
                "Node was not installed via system package manager. Please install manually.",
            )

    def ensure_tesseract_langs(self):
        """Checks and installs required Tesseract language data."""
        name, category = "Tesseract languages", "Linguistics"
        if self.minimal:
            self._add_result(name, category, True, "Skipped (minimal mode)")
            return
        if not su.is_installed("tesseract"):
            return

        ok, out = self._run_cmd(["tesseract", "--list-langs"], read_only=True)
        if not ok:
            self._add_result(name, category, False, "tesseract command failed.")
            return

        installed = {
            l.strip()
            for l in out.splitlines()
            if l.strip() and not l.lower().startswith("list of")
        }
        missing = [l for l in config.REQUIRED_TESS_LANGS if l not in installed]

        if not missing:
            self._add_result(
                name,
                category,
                True,
                f"All present: {', '.join(config.REQUIRED_TESS_LANGS)}",
            )
            return

        self.install_system_packages("tess_langs")

    def ensure_frontend_deps(self):
        """Installs frontend npm dependencies if package.json exists."""
        name, category = "Frontend Dependencies", "Project"
        if self.minimal:
            self._add_result(name, category, True, "Skipped (minimal mode)")
            return

        frontend_dir = self.project_root / "frontend"
        if not (frontend_dir / "package.json").exists():
            self._add_result(name, category, True, "No package.json found, skipping.")
            return
        if not su.is_installed("npm"):
            self._add_result(
                name, category, False, "Cannot install, npm is not available."
            )
            return

        ok, out = self._run_cmd(["npm", "ci"], cwd=frontend_dir)
        self._add_result(
            name, category, ok, "npm dependencies installed" if ok else out
        )

    def ensure_backend_deps(self):
        """Installs Python project dependencies with Poetry."""
        name, category = "Project Dependencies", "Project"
        if self.minimal:
            self._add_result(name, category, True, "Skipped (minimal mode)")
            return
        if not su.is_installed("poetry"):
            self._add_result(
                name, category, False, "Cannot install, Poetry is not available."
            )
            return

        backend_dir = self.project_root / "backend"
        if not (backend_dir / "pyproject.toml").exists():
            self._add_result(name, category, False, "pyproject.toml not found.")
            return

        ok, out = self._run_cmd(["poetry", "install"], cwd=backend_dir)
        self._add_result(
            name, category, ok, "Poetry dependencies installed" if ok else out
        )

    def run_all(self):
        """Runs the complete, logical installation sequence."""
        self.console.print(
            Panel.fit(
                "[bold blue]🚀 Setting up CartaOS Development Environment[/bold blue]"
            )
        )

        if not self._check_python_version() or (
            not self.pkg_manager and not self.dry_run
        ):
            self.console.print("[red]Aborting due to unmet prerequisites.[/red]")
            self._final_summary()
            self._add_result("Prerequisites", "Bootstrap", False, "Unmet prerequisites")
            # Tests expect a SystemExit here
            sys.exit(1)

        self.install_system_packages("base")
        self.ensure_node()
        self.ensure_tool("Rust (cargo)", "cargo", self._install_rust, "Build Tool")
        self.install_system_packages("tauri")
        self.ensure_tesseract_langs()
        self.ensure_tool("Tauri CLI", "tauri", self._install_tauri_cli, "Build Tool")
        self.ensure_tool(
            "pipx", "pipx", self._install_pipx, "Build Tool", skip_minimal=False
        )
        self.ensure_tool(
            "Poetry", "poetry", self._install_poetry, "Build Tool", skip_minimal=False
        )
        self.ensure_frontend_deps()
        self.ensure_backend_deps()

        self._final_summary()
        self._export_log_file()

    def _final_summary(self):
        """Displays the final summary table with enhanced details."""
        table = Table(
            title="Environment Installation Summary",
            box=box.ROUNDED,
            header_style="bold magenta",
        )
        table.add_column("Category", style="dim", width=12)
        table.add_column("Step", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center", width=7)
        table.add_column("Details", overflow="fold", max_width=70)

        for r in self.results:
            status_icon = "[green]✔[/green]" if r.success else "[red]✖[/red]"
            table.add_row(r.category, r.name, status_icon, r.details or "-")

        self.console.print()
        self.console.print(table)
        self.console.print()
        self.console.print("[bold green]🎉 Setup complete![/bold green]")
        recommendation = self._get_shell_recommendation()
        self.console.print(
            f"[yellow]Note:[/yellow] To ensure all tools are available, you may need to {recommendation}"
        )
        if not self.dry_run:
            log_path = self.project_root / config.LOG_FILE_NAME
            self.console.print(
                f"[yellow]Note:[/yellow] A detailed log has been saved to [bold cyan]{log_path}[/bold cyan]."
            )

    def _export_log_file(self):
        """Saves the installation results to a log file, including in CI."""
        if self.dry_run:
            return
        try:
            log_path = self.project_root / config.LOG_FILE_NAME
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("CartaOS Development Environment Setup Log\n")
                f.write(
                    f"Timestamp: {__import__('datetime').datetime.now().isoformat()}\n"
                )
                f.write("=" * 50 + "\n\n")
                for r in self.results:
                    status = "SUCCESS" if r.success else "FAIL"
                    f.write(f"[{status}] - {r.category} - {r.name}\n")
                    f.write(f"  Details: {r.details or 'N/A'}\n")
                    f.write("-" * 50 + "\n")
            self.console.log(
                f"Log file successfully exported to [cyan]{log_path}[/cyan]"
            )
        except IOError as e:
            self.console.log(f"[red]Error exporting log file: {e}[/red]")
