#!/usr/bin/env python3
"""
install_dev_env.py - Cross-platform setup script for CartaOS development environment.

Supported:
- Linux (Debian/Ubuntu, Fedora, Arch)
- macOS (brew)
- Windows (winget / choco)

Requirements:
- Python 3.8+
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.progress import track
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"], check=True)
    from rich.console import Console
    from rich.progress import track

console = Console()

# -------------------------------
# Utility functions
# -------------------------------

def run_cmd(cmd, check=True):
    """Run a shell command with visible output."""
    console.print(f"[cyan]$ {' '.join(cmd)}[/cyan]")
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0

def detect_package_manager():
    """Detect package manager for Linux/macOS/Windows."""
    system = platform.system().lower()

    if system == "linux":
        if shutil.which("apt"):
            return "apt"
        elif shutil.which("dnf"):
            return "dnf"
        elif shutil.which("pacman"):
            return "pacman"
    elif system == "darwin":
        if shutil.which("brew"):
            return "brew"
        else:
            console.print("[red]Homebrew not found. Installing...[/red]")
            run_cmd(['/bin/bash', '-c',
                     "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"])
            return "brew"
    elif system == "windows":
        if shutil.which("winget"):
            return "winget"
        elif shutil.which("choco"):
            return "choco"
    return None

def install_packages(pkg_manager, packages):
    """Install packages using the detected package manager."""
    console.print(f"[green]Installing system packages with {pkg_manager}...[/green]")
    if pkg_manager == "apt":
        run_cmd(["sudo", "apt", "update"])
        run_cmd(["sudo", "apt", "install", "-y"] + packages)
    elif pkg_manager == "dnf":
        run_cmd(["sudo", "dnf", "install", "-y"] + packages)
    elif pkg_manager == "pacman":
        run_cmd(["sudo", "pacman", "-Sy", "--noconfirm"] + packages)
    elif pkg_manager == "brew":
        run_cmd(["brew", "install"] + packages)
    elif pkg_manager == "winget":
        for pkg in packages:
            run_cmd(["winget", "install", "--id", pkg, "--accept-source-agreements", "--accept-package-agreements"])
    elif pkg_manager == "choco":
        for pkg in packages:
            run_cmd(["choco", "install", pkg, "-y"])
    else:
        console.print("[red]No supported package manager found.[/red]")
        sys.exit(1)

def install_rust():
    if shutil.which("cargo"):
        console.print("[yellow]Rust already installed.[/yellow]")
        return
    console.print("[green]Installing Rust...[/green]")
    run_cmd(["curl", "--proto", "=https", "--tlsv1.2", "-sSf", "https://sh.rustup.rs", "-o", "rustup-init.sh"])
    run_cmd(["sh", "rustup-init.sh", "-y"])
    os.remove("rustup-init.sh")

def install_node():
    if shutil.which("node") and shutil.which("npm"):
        console.print("[yellow]Node.js already installed.[/yellow]")
        return
    console.print("[green]Installing Node.js LTS via nvm...[/green]")
    nvm_install_script = "https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh"
    run_cmd(["curl", "-o-", nvm_install_script, "|", "bash"], check=False)
    console.print("[cyan]Restart your shell to use nvm and install Node.js LTS with:[/cyan] nvm install --lts")

def install_poetry():
    if shutil.which("poetry"):
        console.print("[yellow]Poetry already installed.[/yellow]")
        return
    console.print("[green]Installing Poetry...[/green]")
    run_cmd([sys.executable, "-m", "pip", "install", "--user", "poetry"])

def install_tauri_cli():
    if shutil.which("tauri"):
        console.print("[yellow]Tauri CLI already installed.[/yellow]")
        return
    console.print("[green]Installing Tauri CLI...[/green]")
    run_cmd(["cargo", "install", "tauri-cli"])

# -------------------------------
# Main install logic
# -------------------------------

def main():
    console.print("[bold blue]🚀 Setting up CartaOS Development Environment[/bold blue]")

    pkg_manager = detect_package_manager()
    if not pkg_manager:
        console.print("[red]No supported package manager detected. Please install dependencies manually.[/red]")
        sys.exit(1)

    base_packages = [
        "git", "curl", "wget", "tesseract-ocr", "poppler-utils",
        "unpaper", "python3", "python3-pip", "python3-venv"
    ]
    if pkg_manager == "brew":
        base_packages.remove("python3")  # brew python3 already up to date

    if pkg_manager == "winget":
        # IDs differ on winget
        base_packages = ["Git.Git", "Python.Python.3.12", "Rustlang.Rust.MSVC", "OpenJS.NodeJS.LTS"]

    install_packages(pkg_manager, base_packages)

    install_rust()
    install_node()
    install_poetry()
    install_tauri_cli()

    console.print("[bold green]🎉 Environment setup completed successfully![/bold green]")
    console.print("[yellow]Restart your terminal before running CartaOS commands.[/yellow]")

if __name__ == "__main__":
    main()
