# -*- coding: utf-8 -*-
# backend/tests/test_cli_more.py

from pathlib import Path
from typer.testing import CliRunner
import cartaos.cli as cli_module
import pytest
import types

runner = CliRunner()


def test_setup_noninteractive_writes_expected_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Redirect cli_module.__file__ so that Path(__file__).parent.parent resolves under tmp_path
    fake_backend_root = tmp_path / "backend"
    fake_backend_root.mkdir(parents=True, exist_ok=True)
    fake_cli_file = fake_backend_root / "cartaos" / "cli.py"
    fake_cli_file.parent.mkdir(parents=True, exist_ok=True)
    fake_cli_file.write_text("# fake cli file path for tests\n", encoding="utf-8")

    monkeypatch.setattr(cli_module, "__file__", str(fake_cli_file))

    env_path = fake_backend_root / ".env"
    assert not env_path.exists()

    # Run non-interactive setup; it should create .env at fake_backend_root
    result = runner.invoke(cli_module.app, ["setup", "--non-interactive"])
    assert result.exit_code == 0
    assert env_path.exists()
    content = env_path.read_text(encoding="utf-8")
    assert content == 'GEMINI_API_KEY=""\n# Optional: OBISIDIAN_VAULT_PATH=""\n'


def test_setup_interactive_writes_full_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate interactive TTY
    fake_sys = types.SimpleNamespace(stdin=types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(cli_module, "sys", fake_sys)

    # Redirect backend root
    fake_backend_root = tmp_path / "backend"
    fake_backend_root.mkdir(parents=True, exist_ok=True)
    fake_cli_file = fake_backend_root / "cartaos" / "cli.py"
    fake_cli_file.parent.mkdir(parents=True, exist_ok=True)
    fake_cli_file.write_text("# fake cli file path for tests\n", encoding="utf-8")
    monkeypatch.setattr(cli_module, "__file__", str(fake_cli_file))

    # Provide prompts: API key, OBSIDIAN_VAULT_PATH
    answers = ["KEY123", str(tmp_path / "vault")]  # both filled
    monkeypatch.setattr("typer.prompt", lambda *a, **k: answers.pop(0))

    env_path = fake_backend_root / ".env"
    assert not env_path.exists()

    result = runner.invoke(cli_module.app, ["setup"])  # interactive path
    assert result.exit_code == 0
    content = env_path.read_text(encoding="utf-8").splitlines()
    assert 'GEMINI_API_KEY="KEY123"' in content
    assert f'OBSIDIAN_VAULT_PATH="{(tmp_path / "vault").as_posix()}"' in content
