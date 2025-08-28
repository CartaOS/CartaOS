from pathlib import Path

import pytest
from typer.testing import CliRunner

import cartaos.cli as cli_module

runner = CliRunner()


def test_help():
    result = runner.invoke(cli_module.app, ["--help"])
    assert result.exit_code == 0
    # Check for the presence of help-related text in the output
    assert any(text in result.output for text in ["--help", "Show this message", "Options:", "Commands:"])


def test_version_flag():
    result = runner.invoke(cli_module.app, ["--version"])
    assert result.exit_code == 0
    assert "cartaos, version" in result.output


def test_setup_noninteractive(monkeypatch):
    """
    Simulates an environment without .env and automatic prompt responses.
    Then verifies that the .env file was created in backend/.
    Finally, does cleanup to avoid "polluting" the repository.
    """
    # 1) Preenche o prompt duas vezes: API_KEY e OBSIDIAN_VAULT_PATH
    answers = ["FAKE_KEY", ""]  # segunda string em branco => pula vault
    monkeypatch.setattr("typer.prompt", lambda *args, **kwargs: answers.pop(0))

    # 2) Define onde o CLI grava o .env: pasta backend (pai de cartaos/cli.py)
    backend_root = Path(cli_module.__file__).parent.parent
    env_path = backend_root / ".env"

    # Garante que não exista antes do teste
    if env_path.exists():
        env_path.unlink()

    # 3) Executa o comando
    result = runner.invoke(cli_module.app, ["setup"])
    assert result.exit_code == 0

    # 4) Verify that the .env was created there
    assert env_path.exists(), f".env not found at {env_path}"

    # 5) Immediate cleanup
    env_path.unlink()
