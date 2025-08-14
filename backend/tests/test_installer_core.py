import sys
import platform
from pathlib import Path
import pytest

from cartaos.install_dev_env.installer import Installer
from cartaos.install_dev_env import shell_utils

# Evita poluir a saída com Rich
class DummyConsole:
    def __init__(self, *args, **kwargs):
        pass

    def print(self, *args, **kwargs):
        pass

    def log(self, *args, **kwargs):
        pass

@pytest.fixture(autouse=True)
def patch_console(monkeypatch):
    # Substitui o Console do installer pelo DummyConsole
    monkeypatch.setattr("cartaos.install_dev_env.installer.Console", DummyConsole)

def test_detect_project_root_uses_git(monkeypatch):
    inst = Installer(no_confirm=True, minimal=True, dry_run=True, ci_mode=True)
    # Força sucesso do git
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (True, "/fake/root"))

    root = inst._detect_project_root()
    assert root == Path("/fake/root")
    assert any(r.name == "Project Root" and r.success for r in inst.results)

def test_detect_project_root_fallback(monkeypatch, tmp_path):
    inst = Installer(no_confirm=True, minimal=True, dry_run=True, ci_mode=True)
    # Git falha
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (False, ""))
    # Cria um marker no tmp_path
    (tmp_path / "pyproject.toml").write_text("")
    sub = tmp_path / "subdir"; sub.mkdir()
    monkeypatch.chdir(sub)

    root = inst._detect_project_root()
    assert root == tmp_path
    assert any(r.name == "Project Root" for r in inst.results)

def test_detect_package_manager(monkeypatch):
    inst = Installer(no_confirm=True, minimal=True, dry_run=True, ci_mode=True)
    monkeypatch.setattr(platform, "system", lambda: "linux")
    # Somente 'apt' existe
    monkeypatch.setattr(shell_utils, "is_installed", lambda c: c == "apt")

    pm = inst._detect_package_manager()
    assert pm == "apt"
    assert any(r.name == "Package Manager" and r.success for r in inst.results)

def test_check_python_version(monkeypatch):
    inst = Installer(no_confirm=True, minimal=True, dry_run=True, ci_mode=True)
    class V: major = 3; minor = 12
    monkeypatch.setattr(sys, "version_info", V)

    ok = inst._check_python_version()
    assert ok
    assert any(r.name == "Python Version" and r.success for r in inst.results)

def test_install_system_packages_dry_run(monkeypatch):
    inst = Installer(no_confirm=True, minimal=True, dry_run=True, ci_mode=True)
    inst.pkg_manager = "apt"

    ok = inst.install_system_packages("base")
    assert ok
    entry = next(r for r in inst.results if r.name.startswith("System packages"))
    assert "DRY RUN" in entry.details
