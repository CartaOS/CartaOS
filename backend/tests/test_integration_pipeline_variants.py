# -*- coding: utf-8 -*-
# backend/tests/test_integration_pipeline_variants.py

import shutil
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from typer.testing import CliRunner

import cartaos.cli as cli_module

runner = CliRunner()


def _setup_pipeline_dirs(tmp_path: Path):
    triage_dir = tmp_path / "02_Triage"
    triage_dir.mkdir()
    lab_dir = tmp_path / "03_Lab"
    lab_dir.mkdir()
    ready_ocr_dir = tmp_path / "04_ReadyForOCR"
    ready_ocr_dir.mkdir()
    ready_sum_dir = tmp_path / "05_ReadyForSummary"
    ready_sum_dir.mkdir()
    processed_dir = tmp_path / "07_Processed"
    processed_dir.mkdir()
    return triage_dir, lab_dir, ready_ocr_dir, ready_sum_dir, processed_dir


def _redirect_cli_dirs(
    monkeypatch: pytest.MonkeyPatch,
    triage_dir: Path,
    lab_dir: Path,
    ready_ocr_dir: Path,
    ready_sum_dir: Path,
):
    monkeypatch.setattr(cli_module, "DIR_TRIAGE", triage_dir)
    monkeypatch.setattr(cli_module, "DIR_LAB", lab_dir)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr_dir)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum_dir)


def test_ocr_failure_leaves_file_in_ready_for_ocr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    triage_dir, lab_dir, ready_ocr_dir, ready_sum_dir, processed_dir = (
        _setup_pipeline_dirs(tmp_path)
    )
    _redirect_cli_dirs(monkeypatch, triage_dir, lab_dir, ready_ocr_dir, ready_sum_dir)

    # Create one lab file
    short_pdf = lab_dir / "short.pdf"
    short_pdf.write_bytes(b"%PDF-1.4\n")

    # OCR: Fake processor that fails
    class FakeOcrFail:
        def __init__(self, input_path: Path, output_path: Path) -> None:
            self.input_path = input_path
            self.output_path = output_path

        def process(self) -> bool:
            return False

    monkeypatch.setattr(cli_module, "OcrProcessor", FakeOcrFail)

    # Run OCR batch
    res = runner.invoke(cli_module.app, ["ocr"])
    assert res.exit_code == 0

    # File should remain (or be moved) into ready for OCR and not appear in ready for summary
    assert (ready_ocr_dir / "short.pdf").exists() or (lab_dir / "short.pdf").exists()
    assert not (ready_sum_dir / "short.pdf").exists()


@pytest.mark.asyncio
async def test_summarize_fallback_when_vault_unset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Setup test directories
    triage_dir = tmp_path / "01_Triage"
    lab_dir = tmp_path / "03_Lab"
    ready_ocr_dir = tmp_path / "04_ReadyForOCR"
    ready_sum_dir = tmp_path / "05_ReadyForSummary"
    processed_dir = tmp_path / "07_Processed"
    
    # Create all necessary directories
    for d in [triage_dir, lab_dir, ready_ocr_dir, ready_sum_dir, processed_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Place a PDF ready for summary
    pdf = ready_sum_dir / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    # Ensure OBSIDIAN_VAULT_PATH is unset
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)

    # Patch processor internals
    monkeypatch.setattr(
        "cartaos.processor.extract_text",
        lambda p, force_ocr=False: "raw text"
    )
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: "sanitized text")
    
    # Create a mock for generate_summary_with_retries that returns a coroutine
    mock_generate_summary = AsyncMock(return_value="Summary Fallback")
        
    # Patch the function at the module level where it's imported
    monkeypatch.setattr(
        "cartaos.processor.generate_summary_with_retries",
        mock_generate_summary
    )

    import cartaos.processor as proc_mod
    from cartaos.processor import CartaOSProcessor

    # Create a test config
    class TestConfig:
        def __init__(self):
            self.gemini_api_key = "test_key"
            self.obsidian_vault_path = None  # Explicitly set to None for this test
            self.processed_pdf_dir = processed_dir
            self.summary_dir = processed_dir / "Summaries"
            self.summary_dir.mkdir(exist_ok=True)
            # Add pipeline_dirs to match the expected structure
            self.pipeline_dirs = {
                "01_Triage": tmp_path / "01_Triage",
                "03_Lab": tmp_path / "03_Lab",
                "04_ReadyForOCR": tmp_path / "04_ReadyForOCR",
                "05_ReadyForSummary": tmp_path / "05_ReadyForSummary",
                "07_Processed": processed_dir
            }
        
        def is_dir(self, path):
            # Mock the is_dir check for paths we know exist
            return str(path).startswith(str(tmp_path))  

    # Patch the config
    test_config = TestConfig()
    
    # Create and run the processor
    processor = CartaOSProcessor(
        pdf_path=pdf,
        config=test_config,
        dry_run=False,
        debug=False
    )
    
    # Run the async process method
    result = await processor.process_async()
    assert result is True

    # Summary should be in processed/Summaries fallback
    fallback_summary_dir = processed_dir / "Summaries"
    md = fallback_summary_dir / "doc.md"
    assert md.exists()
    assert md.read_text(encoding="utf-8") == "Summary Fallback"
    # PDF should be moved to processed
    assert (processed_dir / "doc.pdf").exists()
    assert (processed_dir / "doc.pdf").exists()
