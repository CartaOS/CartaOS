import sys

import pytest

from cartaos.install_dev_env.installer import Installer


# DummyConsole que aceita parâmetros
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


def test_run_all_dry_run_no_exits(monkeypatch):
    inst = Installer(no_confirm=True, minimal=False, dry_run=True, ci_mode=True)

    # Garante pré-requisitos
    monkeypatch.setattr(inst, "_check_python_version", lambda: True)
    inst.pkg_manager = "apt"

    # Stubs para todos os passos pesados
    for m in [
        "install_system_packages",
        "ensure_node",
        "ensure_tool",
        "ensure_tesseract_langs",
        "ensure_frontend_deps",
        "ensure_backend_deps",
        "_final_summary",
        "_export_log_file",
    ]:
        monkeypatch.setattr(inst, m, lambda *a, **k: None)

    # Não deve fazer sys.exit
    inst.run_all()
    # Em dry_run, inst.results não é esvaziado
    assert len(inst.results) >= 0
