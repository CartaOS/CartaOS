# -*- coding: utf-8 -*-
# tests/test_installer_ensure_tool.py
import pytest
import shutil
from cartaos.install_dev_env.installer import Installer, StepResult
from typing import Optional, List, Tuple, Callable
from pathlib import Path

def test_ensure_tool_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that ensure_tool sets the correct result when a tool is already installed"""
    def fake_shutil_which(
        executable: str, path: Optional[str] = None, pathext: Optional[str] = None
    ) -> Optional[str]:
        """Fake shutil.which function that always returns a path"""
        return "/fake/path"

    monkeypatch.setattr(shutil, "which", fake_shutil_which)
    inst = Installer(no_confirm=True, minimal=True, dry_run=False, ci_mode=True)
    inst.results.clear()

    inst.ensure_tool(
        name="mytool",
        check_cmd="mytool",
        install_logic=lambda: None,
        category="Category",
        skip_minimal=False,  # force installation if minimal
    )

    results: List[StepResult] = [r for r in inst.results if r.name == "mytool"]
    assert results, "No result for 'mytool'"
    assert results[0].details == "Already installed at: /fake/path"


def test_ensure_tool_not_installed_and_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that ensure_tool sets the correct result when a tool is not installed and dry_run=False"""
    def fake_shutil_which(
        executable: str, path: Optional[str] = None, pathext: Optional[str] = None
    ) -> Optional[str]:
        """Fake shutil.which function that never returns a path"""
        return None

    monkeypatch.setattr(shutil, "which", fake_shutil_which)
    inst = Installer(no_confirm=True, minimal=False, dry_run=False, ci_mode=True)
    inst.results.clear()

    def fake_run(
        cmd: List[str], 
        env: Optional[dict[str, str]] = None, 
        cwd: Optional[Path] = None, 
        read_only: bool = False, 
        login_shell: bool = False
    ) -> Tuple[bool, str]:
        """Fake implementation of Installer._run_cmd for testing"""
        return True, "Installed successfully"
    
    monkeypatch.setattr(inst, "_run_cmd", fake_run)

    inst.ensure_tool(
        name="othertool",
        check_cmd="othertool",
        install_logic=lambda: None,
        category="Category",
        skip_minimal=False,
    )

    results = [r for r in inst.results if r.name == "othertool"]
    assert results, "No StepResult for 'othertool'"
    step = results[0]
    # No código real, após install_logic, o PATH não se altera => success=False
    assert step.success is False
    assert step.details == (
        "Installation ran, but command is not in PATH. "
        "A shell restart is likely required."
    )
