# -*- coding: utf-8 -*-
# backend/tests/test_integration_pipeline_variants.py

from pathlib import Path
import shutil
import pytest
from typer.testing import CliRunner

import cartaos.cli as cli_module

runner = CliRunner()


def _setup_pipeline_dirs(tmp_path: Path):
    triage_dir = tmp_path / "02_Triage"; triage_dir.mkdir()
    lab_dir = tmp_path / "03_Lab"; lab_dir.mkdir()
    ready_ocr_dir = tmp_path / "04_ReadyForOCR"; ready_ocr_dir.mkdir()
    ready_sum_dir = tmp_path / "05_ReadyForSummary"; ready_sum_dir.mkdir()
    processed_dir = tmp_path / "07_Processed"; processed_dir.mkdir()
    return triage_dir, lab_dir, ready_ocr_dir, ready_sum_dir, processed_dir


def _redirect_cli_dirs(monkeypatch: pytest.MonkeyPatch, triage_dir: Path, lab_dir: Path, ready_ocr_dir: Path, ready_sum_dir: Path):
    monkeypatch.setattr(cli_module, "DIR_TRIAGE", triage_dir)
    monkeypatch.setattr(cli_module, "DIR_LAB", lab_dir)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr_dir)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum_dir)


def test_ocr_failure_leaves_file_in_ready_for_ocr(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    triage_dir, lab_dir, ready_ocr_dir, ready_sum_dir, processed_dir = _setup_pipeline_dirs(tmp_path)
    _redirect_cli_dirs(monkeypatch, triage_dir, lab_dir, ready_ocr_dir, ready_sum_dir)

    # Create one lab file
    short_pdf = lab_dir / "short.pdf"; short_pdf.write_bytes(b"%PDF-1.4\n")

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


def test_summarize_fallback_when_vault_unset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    triage_dir, lab_dir, ready_ocr_dir, ready_sum_dir, processed_dir = _setup_pipeline_dirs(tmp_path)
    _redirect_cli_dirs(monkeypatch, triage_dir, lab_dir, ready_ocr_dir, ready_sum_dir)

    # Place a PDF ready for summary
    pdf = ready_sum_dir / "doc.pdf"; pdf.write_bytes(b"%PDF-1.4\n")

    # Ensure OBSIDIAN_VAULT_PATH is unset
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)

    # Patch processor internals
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "raw text")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: "sanitized text")
    monkeypatch.setattr("cartaos.processor.generate_summary", lambda t: "Summary Fallback")

    import cartaos.processor as proc_mod

    # Ensure the processor writes into our tmp processed dir when vault is unset
    def fake_load_config(self):
        self.api_key = None
        self.obsidian_vault_path = None
        self.processed_pdf_dir = processed_dir
        self.summary_dir = self.processed_pdf_dir / "Summaries"
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "load_config", fake_load_config, raising=True)

    # Redirect move to our processed dir
    def fake_move_pdf(self):
        processed_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(self.pdf_path, processed_dir / self.pdf_path.name)
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "_move_pdf", fake_move_pdf, raising=True)

    # Run summarize
    res = runner.invoke(cli_module.app, ["summarize", str(pdf)])
    assert res.exit_code == 0

    # Summary should be in processed/Summaries fallback
    fallback_summary_dir = processed_dir / "Summaries"
    md = fallback_summary_dir / "doc.md"
    assert md.exists()
    assert md.read_text(encoding="utf-8") == "Summary Fallback"
    # PDF moved to processed
    assert (processed_dir / "doc.pdf").exists()
