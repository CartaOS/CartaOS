"""
Tests for the CLI interface of CartaOS.

The CLI interface is the main entry point for all backend operations, including
triage, lab processing, OCR, and summarization.
"""

import pytest
from click.testing import CliRunner
from cartaos.cli import app

# Create a CliRunner instance as a fixture
@pytest.fixture
def runner():
    """Fixture that provides a Click CLI runner for invoking CLI commands."""
    return CliRunner()

def test_cli_version(runner):
    """Test the version command to ensure it returns the correct version."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "cartaos, version" in result.output

def test_cli_help(runner):
    """Test the help command to ensure it displays usage information."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage: cartaos [OPTIONS] COMMAND [ARGS]..." in result.output

def test_cli_setup(runner):
    """Test the setup command to ensure it executes without errors."""
    result = runner.invoke(app, ["setup"])
    assert result.exit_code == 0

def test_cli_triage(runner):
    """Test the triage command to ensure it executes without errors."""
    result = runner.invoke(app, ["triage"])
    assert result.exit_code == 0

def test_cli_lab(runner, tmp_path):
    """Test the lab command to ensure it processes a given PDF file."""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.touch()  # Create a temporary test PDF file
    result = runner.invoke(app, ["lab", str(pdf_file)])
    assert result.exit_code == 0

def test_cli_ocr(runner, tmp_path):
    """Test the OCR command to ensure it processes a given PDF file."""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.touch()  # Create a temporary test PDF file
    result = runner.invoke(app, ["ocr", str(pdf_file)])
    assert result.exit_code == 0

def test_cli_summarize(runner, tmp_path):
    """Test the summarize command to ensure it processes a given PDF file."""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.touch()  # Create a temporary test PDF file
    result = runner.invoke(app, ["summarize", str(pdf_file)])
    assert result.exit_code == 0

