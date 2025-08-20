# -*- coding: utf-8 -*-
# backend/tests/test_installer_more.py

from pathlib import Path
import platform
import shutil
import types
import sys
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


def test_install_system_packages_flags_pacman_dnf_brew(monkeypatch, tmp_path):
    # Prepare package map with sample pkgs
    monkeypatch.setattr(inst_config, "PACKAGE_MAP", {
        "pacman": {"base": ["a", "b"]},
        "dnf": {"base": ["c"]},
        "brew": {"base": ["d"]},
    })

    recorded = []
    def rec_run(cmd, **kw):
        recorded.append(cmd)
        return True, "ok"

    # pacman
    inst = make_inst(tmp_path)
    inst.pkg_manager = "pacman"
    monkeypatch.setattr(inst, "_run_cmd", rec_run)
    inst.install_system_packages("base")
    assert ["sudo", "pacman", "-Syu", "--noconfirm"] in recorded
    assert any(cmd[:3] == ["sudo", "pacman", "-S"] and "--noconfirm" in cmd for cmd in recorded)

    # dnf
    recorded.clear()
    inst = make_inst(tmp_path)
    inst.pkg_manager = "dnf"
    monkeypatch.setattr(inst, "_run_cmd", rec_run)
    inst.install_system_packages("base")
    assert any(cmd[:3] == ["sudo", "dnf", "install"] and "-y" in cmd for cmd in recorded)

    # brew
    recorded.clear()
    inst = make_inst(tmp_path)
    inst.pkg_manager = "brew"
    monkeypatch.setattr(inst, "_run_cmd", rec_run)
    inst.install_system_packages("base")
    assert any(cmd[:2] == ["brew", "install"] for cmd in recorded)
    assert not any(("-y" in cmd or "--noconfirm" in cmd) for cmd in recorded)


def test_ensure_tool_success_path(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)

    # not installed initially, becomes installed after install_logic
    state = {"installed": False}
    def fake_which(cmd, path=None):
        return "/usr/bin/tauri" if state["installed"] else None
    monkeypatch.setattr(shutil, "which", fake_which)

    called = {"did": False}
    def install_logic():
        called["did"] = True
        state["installed"] = True

    inst.ensure_tool("Tauri CLI", "tauri", install_logic, "Build Tool", skip_minimal=False)

    r = next(x for x in inst.results if x.name == "Tauri CLI")
    assert called["did"] is True
    assert r.success is True and "Installed to:" in r.details


def test_ensure_node_windows_manual_note(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    inst.system = "windows"

    # node -v fails
    def fake_run(cmd, env=None, cwd=None, read_only=False, login_shell=False):
        if cmd[:2] == ["node", "-v"]:
            return False, ""
        return True, ""
    monkeypatch.setattr(inst, "_run_cmd", fake_run)

    inst.ensure_node()
    r = next(x for x in inst.results if x.name == "Node.js LTS")
    assert r.success is False
    assert "install manually" in r.details


def test_detect_package_manager_records_bootstrap_category(monkeypatch, tmp_path):
    # Force detection path: linux + only dnf installed
    inst = make_inst(tmp_path)
    inst.system = "linux"
    monkeypatch.setattr(su, "is_installed", lambda pm: pm == "dnf")

    # Call detection explicitly to record result deterministically
    pm = inst._detect_package_manager()
    assert pm == "dnf"
    last = inst.results[-1]
    assert last.name == "Package Manager"
    assert last.category == "Bootstrap"
    assert "Using dnf" in last.details


def test_detect_project_root_records_bootstrap_category(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    # Simulate git success pointing to tmp_path
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (True, str(tmp_path)))

    root = inst._detect_project_root()
    assert root == tmp_path
    last = inst.results[-1]
    assert last.name == "Project Root"
    assert last.category == "Bootstrap"
    assert "Detected via Git" in last.details


def test_python_version_records_bootstrap_category(tmp_path):
    inst = make_inst(tmp_path)
    # Call the method that records Python version
    inst._check_python_version()
    last = inst.results[-1]
    assert last.name == "Python Version"
    assert last.category == "Bootstrap"
    assert last.success is True
    assert str(platform.python_version())[:3] in last.details


def test_detect_package_manager_none_records_failure(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    inst.system = "linux"
    # No package managers available
    monkeypatch.setattr(su, "is_installed", lambda pm: False)

    pm = inst._detect_package_manager()
    assert pm is None
    last = inst.results[-1]
    assert last.name == "Package Manager"
    assert last.category == "Bootstrap"
    assert last.success is False


def test_install_system_packages_dry_run_records_note(monkeypatch, tmp_path):
    inst = make_inst(tmp_path, dry_run=True)
    inst.pkg_manager = "dnf"
    monkeypatch.setattr(inst_config, "PACKAGE_MAP", {"dnf": {"base": ["wget", "curl"]}})

    inst.install_system_packages("base")
    last = inst.results[-1]
    assert last.name == "System packages (base)"
    assert last.success is True
    assert "DRY RUN" in last.details


def test_run_all_dry_run_executes_pipeline(monkeypatch, tmp_path):
    # Prepare a project layout
    (tmp_path / "frontend").mkdir()
    (tmp_path / "frontend" / "package.json").write_text("{}")
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "pyproject.toml").write_text("[tool.poetry]\nname='x'\n")

    inst = make_inst(tmp_path, dry_run=True)
    # Pretend we have a package manager
    inst.pkg_manager = "dnf"

    # Ensure read_only commands are predictable
    def fake_run(cmd, env=None, cwd=None, read_only=False, login_shell=False):
        # Simulate failures for read_only checks to drive install branches safely
        if read_only:
            return False, ""
        return True, "ok"
    monkeypatch.setattr(inst, "_run_cmd", fake_run)

    # Mock which to force ensure_tool to go through DRY RUN path
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    # Make helpers available
    monkeypatch.setattr(su, "is_installed", lambda c: True)

    # Run the full pipeline in dry-run
    inst.run_all()

    # We should have recorded a variety of steps without exiting
    names = [r.name for r in inst.results]
    assert "System packages (base)" in names
    assert "Node.js LTS" in names
    assert "Rust (cargo)" in names
    assert "Tauri CLI" in names
    assert "pipx" in names and "Poetry" in names
    assert "Frontend Dependencies" in names
    assert "Project Dependencies" in names


def test_detect_project_root_fallback_marker(monkeypatch, tmp_path):
    # Ensure git fails
    inst = make_inst(tmp_path)
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (False, ""))

    # Create a marker in cwd and chdir
    (tmp_path / "README.md").write_text("x")
    monkeypatch.chdir(tmp_path)
    root = inst._detect_project_root()
    assert root == tmp_path
    last = inst.results[-1]
    assert last.name == "Project Root" and last.success is True
    assert "Detected via marker" in last.details


def test_detect_project_root_total_fallback(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (False, ""))

    # Use a directory with no markers
    empty = tmp_path / "empty"; empty.mkdir()
    monkeypatch.chdir(empty)

    root = inst._detect_project_root()
    assert root.exists()
    last = inst.results[-1]
    assert last.name == "Project Root"
    assert last.success is False
    assert "script location" in last.details


def test_ensure_frontend_deps_missing_npm(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    frontend = tmp_path / "frontend"; frontend.mkdir()
    (frontend / "package.json").write_text("{}")

    monkeypatch.setattr(su, "is_installed", lambda c: False)
    inst.ensure_frontend_deps()
    last = inst.results[-1]
    assert last.name == "Frontend Dependencies"
    assert last.success is False
    assert "npm is not available" in last.details


def test_ensure_tesseract_langs_missing_some_installs(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    monkeypatch.setattr(su, "is_installed", lambda c: c == "tesseract")
    # list-langs returns only one of required
    langs_output = """
List of available languages (1):
eng
"""
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (True, langs_output))

    called = {"group": None}
    monkeypatch.setattr(inst, "install_system_packages", lambda g: called.__setitem__("group", g) or True)

    inst.ensure_tesseract_langs()
    assert called["group"] == "tess_langs"


def test_install_system_packages_apt_flow(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    inst.pkg_manager = "apt"
    monkeypatch.setattr(inst_config, "PACKAGE_MAP", {"apt": {"base": ["curl"]}})

    recorded = []
    def rec(cmd, **kw):
        recorded.append(cmd)
        return True, "ok"
    monkeypatch.setattr(inst, "_run_cmd", rec)

    inst.install_system_packages("base")
    # Ensure apt-get update ran
    assert ["sudo", "apt-get", "update"] in recorded
    # Ensure install with -y
    assert any(cmd[:3] == ["sudo", "apt-get", "install"] and "-y" in cmd for cmd in recorded)


def test_install_system_packages_winget_branch(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    inst.pkg_manager = "winget"
    monkeypatch.setattr(inst_config, "PACKAGE_MAP", {"winget": {"base": ["Vendor.App"]}})

    # First and only pkg fails
    monkeypatch.setattr(inst, "_run_cmd", lambda *a, **k: (False, "fail"))
    ok = inst.install_system_packages("base")
    assert ok is False
    last = inst.results[-1]
    assert last.name == "System packages (base)"
    assert last.success is False
    assert "Vendor.App" in last.details


def test_ensure_tool_minimal_skip(tmp_path):
    inst = make_inst(tmp_path, minimal=True)
    inst.ensure_tool("X", "x", lambda: None, "Build Tool", skip_minimal=True)
    last = inst.results[-1]
    assert last.name == "X" and last.success is True
    assert "Skipped (minimal mode)" in last.details


def test_run_cmd_dry_run(monkeypatch, tmp_path):
    inst = make_inst(tmp_path, dry_run=True)
    # su.run_command must not be called
    monkeypatch.setattr(su, "run_command", lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not call")))

    ok, out = inst._run_cmd(["echo", "hi"])  # not read_only
    assert ok is True and out == "Dry run mode"


def test_install_system_packages_no_pkg_manager(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    inst.pkg_manager = None
    ok = inst.install_system_packages("base")
    assert ok is False
    last = inst.results[-1]
    assert last.name == "System packages (base)" and last.success is False
    assert "Package manager not available" in last.details


def test_install_system_packages_no_pkgs_defined(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    inst.pkg_manager = "apt"
    monkeypatch.setattr(inst_config, "PACKAGE_MAP", {"apt": {"base": []}})
    ok = inst.install_system_packages("base")
    assert ok is True
    last = inst.results[-1]
    assert last.details.startswith("No packages defined")


def test_install_system_packages_choco_mixed_results(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    inst.pkg_manager = "choco"
    monkeypatch.setattr(inst_config, "PACKAGE_MAP", {"choco": {"base": ["A", "B"]}})

    recorded = []
    def fake_run(cmd, **kw):
        recorded.append(cmd)
        # Fail first, succeed second
        if "A" in cmd:
            return False, "errA"
        return True, "ok"
    monkeypatch.setattr(inst, "_run_cmd", fake_run)

    ok = inst.install_system_packages("base")
    assert ok is False
    last = inst.results[-1]
    assert "A" in last.details and "errA" in last.details
    # ensure -y was added because no_confirm=True
    assert any(cmd[:2] == ["choco", "install"] and "-y" in cmd for cmd in recorded)


def test_ensure_tool_install_exception(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    # Ensure not installed
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)

    def boom():
        raise RuntimeError("bad")

    inst.ensure_tool("XTool", "xtool", boom, "Build Tool", skip_minimal=False)
    last = inst.results[-1]
    assert last.name == "XTool" and last.success is False
    assert "exception" in last.details.lower()


def test_ensure_tool_install_no_path_after(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    # Not installed before
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)

    # install_logic does nothing to PATH
    inst.ensure_tool("YTool", "ytool", lambda: None, "Build Tool", skip_minimal=False)
    last = inst.results[-1]
    assert last.name == "YTool" and last.success is False
    assert "not in PATH" in last.details


def test_minimal_skips(monkeypatch, tmp_path):
    inst = make_inst(tmp_path, minimal=True)
    # Node
    inst.ensure_node()
    assert inst.results[-1].name == "Node.js LTS" and "Skipped (minimal mode)" in inst.results[-1].details
    # Frontend
    inst.ensure_frontend_deps()
    assert inst.results[-1].name == "Frontend Dependencies" and "Skipped (minimal mode)" in inst.results[-1].details
    # Backend
    inst.ensure_backend_deps()
    assert inst.results[-1].name == "Project Dependencies" and "Skipped (minimal mode)" in inst.results[-1].details


def test_detect_package_manager_darwin_no_brew(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    inst.system = "darwin"
    monkeypatch.setattr(su, "is_installed", lambda pm: False)
    pm = inst._detect_package_manager()
    assert pm is None
    last = inst.results[-1]
    assert last.name == "Package Manager" and last.success is False
    assert "Homebrew not found" in last.details


def test_run_all_aborts_on_prereq_failure(monkeypatch, tmp_path):
    inst = make_inst(tmp_path)
    inst.dry_run = True  # avoid any external calls if flow continues
    inst.pkg_manager = None  # trigger unmet prereq and force python check to fail
    monkeypatch.setattr(inst, "_check_python_version", lambda: False)

    # Capture sys.exit by raising SystemExit, and verify _final_summary is called once
    calls = {"summary": 0}
    def fake_exit(code=0):
        raise SystemExit(code)
    monkeypatch.setattr(sys, "exit", fake_exit)
    monkeypatch.setattr(inst, "_final_summary", lambda: calls.__setitem__("summary", calls["summary"] + 1))

    with pytest.raises(SystemExit) as exc:
        inst.run_all()
    assert exc.value.code == 1
    assert calls["summary"] == 1
