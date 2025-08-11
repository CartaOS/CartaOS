# install-dev-env/__main__.py

"""
CLI entry point for the installer package.
Parses arguments and runs the main installer logic.
"""

import argparse
import sys
from rich.panel import Panel

# Relative import from within the package
from .installer import Installer


def main():

    """Parses command line arguments and starts the installation process."""
    parser = argparse.ArgumentParser(
        description="A robust, modular installer for the CartaOS development environment.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--no-confirm", action="store_true", help="Auto-confirm all prompts (non-interactive mode).")
    parser.add_argument("--minimal", action="store_true", help="Install only essential tools (git, python, pipx, poetry).")
    parser.add_argument("--dry-run", action="store_true", help="Run all checks without making any system changes.")
    parser.add_argument("--ci", action="store_true", help="Run in CI mode with simplified, non-colored output.")

    args = parser.parse_args()

    installer = Installer(
        no_confirm=args.no_confirm,
        minimal=args.minimal,
        dry_run=args.dry_run,
        ci_mode=args.ci
    )

    try:
        installer.console.print(Panel.fit("[bold blue]🚀 Starting CartaOS Development Environment Setup[/bold blue]"))
        installer.run_all()
    except KeyboardInterrupt:
        installer.console.print("\n[bold red]Installation cancelled by user.[/bold red]")
        sys.exit(1)
    except Exception as e:
        installer.console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
        installer._final_summary()
        installer._export_log_file()
        sys.exit(1)


if __name__ == "__main__":
    main()
