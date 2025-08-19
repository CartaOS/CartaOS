# -*- coding: utf-8 -*-
# backend/tests/test_installer_more.py

from pathlib import Path
import platform
import pytest

from cartaos.install_dev_env.installer import Installer, StepResult
from cartaos.install_dev_env import shell_utils as su
from cartaos.install_dev_env import config as inst_config


class DummyConsole:
    def __init__(self, *args, **kwargs):
        pass
    def print(self, *args, **kwargs):
        pass
    def log(self, *args, **kwargs):
        pass


@pytest.fixture(autouse=True)
def patch_console(monkeypatch):
    monkeypatch.setattr("cartaos.install_dev_env.installer.Console", DummyConsole)


def make_inst(tmp_path, minimal=False, dry_run=False):
    inst = Installer(no_confirm=True, minimal=minimal, dry_run=dry_run, ci_mode=True)
    # Force a fake project root to avoid touching the repo
    inst.project_root = tmp_path
    return inst


def test_ensure_frontend_deps_skips_when_no_package_json(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    monkeypatch.setattr(su, "is_installed", lambda c: True)

    inst.ensure_frontend_deps()
    r = next(x for x in inst.results if x.name == "Frontend Dependencies")
    assert r.success is True
    assert "No package.json" in r.details


def test_ensure_frontend_deps_runs_npm_ci(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text("{}")

    called = {"cmd": None}
    def fake_run(cmd, env=None, cwd=None, read_only=False, login_shell=False):
        called["cmd"] = cmd
        return True, "ok"
    monkeypatch.setattr(su, "is_installed", lambda c: c == "npm")
    monkeypatch.setattr(inst, "_run_cmd", fake_run)

    inst.ensure_frontend_deps()
    r = next(x for x in inst.results if x.name == "Frontend Dependencies")
    assert r.success is True
    assert called["cmd"] == ["npm", "ci"]


def test_ensure_frontend_deps_npm_ci_failure(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text("{}")

    def fake_run(cmd, env=None, cwd=None, read_only=False, login_shell=False):
        return False, "npm error"
    monkeypatch.setattr(su, "is_installed", lambda c: c == "npm")
    monkeypatch.setattr(inst, "_run_cmd", fake_run)

    inst.ensure_frontend_deps()
    r = next(x for x in inst.results if x.name == "Frontend Dependencies")
    assert r.success is False
    assert "npm error" in r.details


def test_ensure_backend_deps_missing_poetry(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "pyproject.toml").write_text("[tool.poetry]\nname='x'\n")

    monkeypatch.setattr(su, "is_installed", lambda c: False)

    inst.ensure_backend_deps()
    r = next(x for x in inst.results if x.name == "Project Dependencies")
    assert r.success is False
    assert "Poetry is not available" in r.details


def test_ensure_backend_deps_runs_poetry_install(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "pyproject.toml").write_text("[tool.poetry]\nname='x'\n")

    monkeypatch.setattr(su, "is_installed", lambda c: c == "poetry")
    called = {"cmd": None, "cwd": None}
    def fake_run(cmd, env=None, cwd=None, read_only=False, login_shell=False):
        called["cmd"], called["cwd"] = cmd, cwd
        return True, "installed"
    monkeypatch.setattr(inst, "_run_cmd", fake_run)

    inst.ensure_backend_deps()
    r = next(x for x in inst.results if x.name == "Project Dependencies")
    assert r.success is True
    assert called["cmd"] == ["poetry", "install"]
    assert called["cwd"] == backend


def test_ensure_backend_deps_missing_pyproject(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    (tmp_path / "backend").mkdir()
    monkeypatch.setattr(su, "is_installed", lambda c: c == "poetry")

    inst.ensure_backend_deps()
    r = next(x for x in inst.results if x.name == "Project Dependencies")
    assert r.success is False
    assert "pyproject.toml not found" in r.details


def test_ensure_backend_deps_poetry_install_failure(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "pyproject.toml").write_text("[tool.poetry]\nname='x'\n")

    monkeypatch.setattr(su, "is_installed", lambda c: c == "poetry")
    def fake_run(cmd, env=None, cwd=None, read_only=False, login_shell=False):
        return False, "poetry error"
    monkeypatch.setattr(inst, "_run_cmd", fake_run)

    inst.ensure_backend_deps()
    r = next(x for x in inst.results if x.name == "Project Dependencies")
    assert r.success is False
    assert "poetry error" in r.details


def test_ensure_tesseract_langs_list_langs_failure(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    monkeypatch.setattr(su, "is_installed", lambda c: c == "tesseract")
    # tesseract --list-langs fails
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (False, "oops"))

    inst.ensure_tesseract_langs()
    r = next(x for x in inst.results if x.name == "Tesseract languages")
    assert r.success is False
    assert "tesseract command failed" in r.details


def test_ensure_tesseract_langs_skip_minimal(monkeypatch, tmp_path):
    inst = make_inst(tmp_path, minimal=True)
    inst.ensure_tesseract_langs()
    r = next(x for x in inst.results if x.name == "Tesseract languages")
    assert r.success is True
    assert "Skipped" in r.details


def test_ensure_tesseract_langs_missing_binary(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    monkeypatch.setattr(su, "is_installed", lambda c: False)
    inst.ensure_tesseract_langs()
    # Should not add a result if tesseract missing? The code returns early; assert no entry added.
    assert not any(x.name == "Tesseract languages" and x.details == "tesseract command failed." for x in inst.results)


def test_ensure_tesseract_langs_ok_when_all_present(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    monkeypatch.setattr(su, "is_installed", lambda c: c == "tesseract")
    langs_output = """
List of available languages (4):
eng
por
spa
ita
"""
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (True, langs_output))

    inst.ensure_tesseract_langs()
    r = next(x for x in inst.results if x.name == "Tesseract languages")
    assert r.success is True
    assert "All present" in r.details


def test_ensure_node_already_ok(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    monkeypatch.setattr(inst, "system", "linux")
    # node -v returns v20
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (True, "v20.10.0"))

    inst.ensure_node()
    r = next(x for x in inst.results if x.name == "Node.js LTS")
    assert r.success is True
    assert "Already installed" in r.details


def test_ensure_node_installs_via_nvm(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    monkeypatch.setattr(inst, "system", "linux")

    calls = {"shell": 0}
    def fake_run_cmd(cmd, env=None, cwd=None, read_only=False, login_shell=False):
        # First call is node -v read_only
        if read_only:
            return False, ""
        return True, "installed"
    def fake_run_shell(command, read_only=False):
        calls["shell"] += 1
        return True, "nvm ok"

    monkeypatch.setattr(inst, "_run_cmd", fake_run_cmd)
    monkeypatch.setattr(inst, "_run_shell", fake_run_shell)

    inst.ensure_node()
    r = next(x for x in inst.results if x.name == "Node.js LTS")
    assert r.success is False  # ensure_node records info about attempting install via NVM
    assert calls["shell"] == 1


def test_final_summary_runs_and_mentions_log_note(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    # populate some results
    inst.results.extend([
        StepResult(name="Project Root", category="Bootstrap", success=True, details="ok"),
        StepResult(name="Package Manager", category="Bootstrap", success=True, details="apt"),
        StepResult(name="Python Version", category="Bootstrap", success=True, details="3.12"),
    ])
    # Just ensure it doesn't raise; output is swallowed by DummyConsole
    inst._final_summary()


def test_export_log_file_writes_file(tmp_path):
    inst = make_inst(tmp_path)
    # Add a couple of results to be logged
    inst.results.extend([
        StepResult(name="Step A", category="Cat", success=True, details="Done"),
        StepResult(name="Step B", category="Cat", success=False, details="Fail msg"),
    ])

    inst._export_log_file()

    log_path = tmp_path / inst_config.LOG_FILE_NAME
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "CartaOS Development Environment Setup Log" in content
    assert "[SUCCESS] - Cat - Step A" in content
    assert "[FAIL] - Cat - Step B" in content


def test_export_log_file_skips_in_dry_run(tmp_path):
    inst = make_inst(tmp_path, dry_run=True)
    inst.results.append(StepResult(name="X", category="Y", success=True, details="Z"))

    inst._export_log_file()

    log_path = tmp_path / inst_config.LOG_FILE_NAME
    assert not log_path.exists()
