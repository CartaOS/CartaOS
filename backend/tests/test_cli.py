"""
Tests for the CLI interface of CartaOS.

The CLI interface is the main entry point for all backend operations, including
triage, lab processing, OCR, and summarization.

The tests check the following:

* The version command returns the correct version string.
* The help command returns the correct help text.
* The setup command guides the user through the initial configuration of CartaOS.
* The triage command scans the Triage (02) directory and classifies files.
* The lab command sends a PDF to the manual correction lab with ScanTailor.
* The OCR command runs batch OCR on all PDFs in the ReadyForOCR (04) directory.
* The summarize command generates an analytical summary for a given PDF file.
"""

import pytest
from click.testing import CliRunner
from cartaos.cli import app

# Create a CliRunner instance as a fixture
@pytest.fixture
def runner():
    return CliRunner()

# Test the version command
def test_cli_version(runner):
    """
    Tests that the version command returns the correct version string.
    """
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "cartaos, version" in result.output

# Test the help command
def test_cli_help(runner):
    """
    Tests that the help command returns the correct help text.
    """
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage: cartaos [OPTIONS] COMMAND [ARGS]..." in result.output

# Test the setup command
def test_cli_setup(runner):
    """
    Tests that the setup command guides the user through the initial configuration of CartaOS.
    """
    result = runner.invoke(app, ["setup"])
    assert result.exit_code == 0
    assert "Guides the user through the initial configuration of CartaOS." in result.output

# Test the triage command
def test_cli_triage(runner):
    """
    Tests that the triage command scans the Triage (02) directory and classifies files.
    """
    result = runner.invoke(app, ["triage"])
    assert result.exit_code == 0
    assert "Scans the Triage (02) directory and classifies files." in result.output

# Test the lab command
def test_cli_lab(runner, tmp_path):
    """
    Tests that the lab command sends a PDF to the manual correction lab with ScanTailor.
    """
    pdf_file = tmp_path / "test.pdf"
    pdf_file.touch()
    result = runner.invoke(app, ["lab", str(pdf_file)])
    assert result.exit_code == 0
    assert "Sends a PDF to the manual correction lab with ScanTailor." in result.output

# Test the OCR command
def test_cli_ocr(runner, tmp_path):
    """
    Tests that the OCR command runs batch OCR on all PDFs in the ReadyForOCR (04) directory.
    """
    pdf_file = tmp_path / "test.pdf"
    pdf_file.touch()
    result = runner.invoke(app, ["ocr", str(pdf_file)])
    assert result.exit_code == 0
    assert "Runs batch OCR on all PDFs in the ReadyForOCR (04) directory." in result.output

# Test the summarize command
def test_cli_summarize(runner, tmp_path):
    """
    Tests that the summarize command generates an analytical summary for a given PDF file.
    """
    pdf_file = tmp_path / "test.pdf"
    pdf_file.touch()
    result = runner.invoke(app, ["summarize", str(pdf_file)])
    assert result.exit_code == 0
    assert "Generates an analytical summary for a given PDF file." in result.output


