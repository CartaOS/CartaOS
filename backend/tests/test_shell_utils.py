# -*- coding: utf-8 -*-
# tests/test_shell_utils.py

import pytest
from subprocess import CompletedProcess
from typing import List, Any, Optional
from pathlib import Path
import subprocess
import platform
from cartaos.install_dev_env.shell_utils import run_command


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

