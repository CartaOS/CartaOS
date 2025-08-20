# -*- coding: utf-8 -*-
# tests/test_shell_utils.py

import os
import pytest
from subprocess import CompletedProcess
from typing import List, Any, Optional
from pathlib import Path
import subprocess
import platform
from cartaos.install_dev_env.shell_utils import run_command, get_shell_recommendation, check_vs_build_tools
from pathlib import Path as SysPath


def test_run_command_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verifies that when subprocess.run returns returncode=0, it returns (True, stdout).

    Args:
        monkeypatch: pytest.MonkeyPatch for mocking subprocess.run.
    """
    def fake_run(
        args: List[str],
        capture_output: bool = True,
        text: bool = True,
        encoding: Optional[str] = None,
        env: Optional[dict] = None,
        cwd: Optional[Path] = None,
    ) -> CompletedProcess:
        """
        Mocked implementation of subprocess.run that returns a CompletedProcess with returncode=0 and stdout="OK".
        """
        return CompletedProcess(args, returncode=0, stdout="OK", stderr="")
    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, output = run_command(["echo", "hello"])
    assert ok is True
    assert output == "OK"


def test_run_command_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verifies that when subprocess.run raises FileNotFoundError, run_command captures and returns (False, msg).

    Args:
        monkeypatch: pytest.MonkeyPatch for mocking subprocess.run.
    """
    def fake_run(*args: Any, **kwargs: Any) -> None:
        """
        Mocked implementation of subprocess.run that raises FileNotFoundError.
        """
        raise FileNotFoundError()
    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, output = run_command(["doesnotexist"])
    assert ok is False
    assert "Command not found: doesnotexist" in output


def test_run_command_login_shell_unix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    On Linux/macOS, use_login_shell should prefix ['bash','-lc', cmdstr].

    Args:
        monkeypatch: pytest.MonkeyPatch for mocking platform.system and subprocess.run.
    """
    def fake_run(
        called: List[str],
        **kwargs: Any,
    ) -> CompletedProcess:
        """
        Mocked implementation of subprocess.run that checks the called arguments.
        """
        # called should be ['bash','-lc','command']
        assert called[:2] == ["bash", "-lc"]
        return CompletedProcess(called, returncode=0, stdout="done", stderr="")
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, out = run_command(["command"], use_login_shell=True)
    assert ok and out == "done"


def test_run_command_login_shell_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    On Windows, use_login_shell should prefix ['powershell','-Command', cmdstr].

    Args:
        monkeypatch: pytest.MonkeyPatch for mocking platform.system and subprocess.run.
    """
    def fake_run(
        called: List[str],
        **kwargs: Any,
    ) -> CompletedProcess:
        """
        Mocked implementation of subprocess.run that checks the called arguments.
        """
        assert called[:2] == ["powershell", "-Command"]
        return CompletedProcess(called, returncode=0, stdout="done", stderr="")
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, out = run_command(["command"], use_login_shell=True)
    assert ok and out == "done"


def test_run_command_nonzero_combined_output(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(
        args: List[str],
        **kwargs: Any,
    ) -> CompletedProcess:
        return CompletedProcess(args, returncode=1, stdout="some out", stderr="some err")
    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, out = run_command(["cmd"]) 
    assert ok is False
    assert out == "some out\nsome err"


def test_run_command_nonzero_empty_output(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(
        args: List[str],
        **kwargs: Any,
    ) -> CompletedProcess:
        return CompletedProcess(args, returncode=1, stdout="", stderr="")
    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, out = run_command(["cmd"]) 
    assert ok is False
    assert out == ""


def test_run_command_generic_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args: Any, **kwargs: Any):
        raise RuntimeError("boom")
    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, out = run_command(["cmd"]) 
    assert ok is False
    assert "An unexpected error occurred" in out


def test_get_shell_recommendation_variants(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHELL", "/bin/zsh")
    assert "zshrc" in get_shell_recommendation()

    monkeypatch.setenv("SHELL", "/bin/bash")
    rec = get_shell_recommendation()
    assert "bashrc" in rec or "profile" in rec

    monkeypatch.setenv("SHELL", "/usr/bin/fish")
    assert "restart your terminal" in get_shell_recommendation()

    monkeypatch.delenv("SHELL", raising=False)
    assert "restart your terminal" in get_shell_recommendation()


def test_run_command_passes_env_and_cwd(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    called = {"env": None, "cwd": None}
    def fake_run(args: List[str], capture_output=True, text=True, encoding=None, env=None, cwd=None):
        called["env"] = env
        called["cwd"] = cwd
        return CompletedProcess(args, returncode=0, stdout="ok", stderr="")
    monkeypatch.setattr(subprocess, "run", fake_run)

    env = {"A": "1"}
    cwd = tmp_path / "wd"; cwd.mkdir()
    ok, out = run_command(["echo", "x"], env=env, cwd=cwd)
    assert ok and out == "ok"
    assert called["env"] == env
    assert called["cwd"] == cwd


def test_run_command_passes_env_and_cwd_with_login_shell(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    called = {"env": None, "cwd": None}
    def fake_run(args: List[str], capture_output=True, text=True, encoding=None, env=None, cwd=None):
        called["env"] = env
        called["cwd"] = cwd
        return CompletedProcess(args, returncode=0, stdout="ok", stderr="")
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(subprocess, "run", fake_run)

    env = {"B": "2"}
    cwd = tmp_path / "wd2"; cwd.mkdir()
    ok, out = run_command(["echo", "y"], env=env, cwd=cwd, use_login_shell=True)
    assert ok and out == "ok"
    assert called["env"] == env
    assert called["cwd"] == cwd


def test_check_vs_build_tools_non_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    assert check_vs_build_tools() is True


def test_check_vs_build_tools_windows_paths(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate Windows
    monkeypatch.setattr(platform, "system", lambda: "Windows")

    # Point ProgramFiles(x86) to temp and create vswhere.exe
    pf86 = tmp_path / "PF86"; pf86.mkdir()
    monkeypatch.setenv("ProgramFiles(x86)", str(pf86))
    vswhere = pf86 / "Microsoft Visual Studio/Installer/vswhere.exe"
    vswhere.parent.mkdir(parents=True, exist_ok=True)
    vswhere.write_bytes(b"MZ")

    # Make run_command succeed
    def fake_run_cmd(args: List[str], **kwargs: Any):
        return True, "id"
    monkeypatch.setattr(
        pytest.importorskip("cartaos.install_dev_env.shell_utils"),
        "run_command",
        fake_run_cmd,
    )

    assert check_vs_build_tools() is True

    # Remove vswhere and expect False
    vswhere.unlink()
    assert check_vs_build_tools() is False

