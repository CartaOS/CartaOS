import pytest
from typer.testing import CliRunner
import cartaos.cli as cli_module
from pathlib import Path

runner = CliRunner()

def test_help():
    result = runner.invoke(cli_module.app, ["--help"])
    assert result.exit_code == 0
    assert "Usage: cartaos" in result.output

def test_version_flag():
    result = runner.invoke(cli_module.app, ["--version"])
    assert result.exit_code == 0
    assert "cartaos, version" in result.output

def test_setup_noninteractive(monkeypatch):
    """
    Simula um ambiente sem .env e respostas automáticas ao prompt.
    Depois verifica se o arquivo .env foi criado em backend/.
    Por fim, faz cleanup para não “poluir” o repositório.
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

    # 4) Verifica que o .env foi criado ali
    assert env_path.exists(), f".env não encontrado em {env_path}"

    # 5) Cleanup imediato
    env_path.unlink()
