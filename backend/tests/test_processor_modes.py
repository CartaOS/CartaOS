# -*- coding: utf-8 -*-
# backend/tests/test_processor_modes.py

import os
from pathlib import Path

import pytest

from cartaos.processor import CartaOSProcessor


def _make_pdf(tmp_path: Path, name: str = "doc.pdf") -> Path:
    p = tmp_path / name
    p.write_bytes(b"%PDF-1.4\n")
    return p


def test_debug_mode_writes_extracted_text_and_returns_true(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = _make_pdf(tmp_path)
    # ensure extract returns content; generate_summary must not be called in debug path
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "raw content")

    # force dirs under tmp so no side effects
    import cartaos.processor as proc_mod

    def fake_load_config(self):
        self.api_key = None
        self.obsidian_vault_path = None
        self.processed_pdf_dir = tmp_path / "07_Processed"
        self.summary_dir = self.processed_pdf_dir / "Summaries"

    monkeypatch.setattr(
        proc_mod.CartaOSProcessor, "load_config", fake_load_config, raising=True
    )

    proc = CartaOSProcessor(pdf_path=pdf, debug=True)
    ok = proc.process()
    assert ok is True

    debug_file = pdf.with_name(f"{pdf.stem}_extracted_text.txt")
    assert debug_file.exists()
    assert debug_file.read_text(encoding="utf-8") == "raw content"

    # Ensure no summary was written and original PDF still exists in place
    assert not (tmp_path / "07_Processed" / "Summaries" / f"{pdf.stem}.md").exists()
    assert pdf.exists()


def test_dry_run_logs_summary_and_does_not_write_files(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    pdf = _make_pdf(tmp_path)
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "some text")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: t)
    monkeypatch.setattr("cartaos.processor.generate_summary", lambda t: "DRY SUMMARY")

    # force dirs under tmp
    import cartaos.processor as proc_mod

    def fake_load_config(self):
        self.api_key = None
        self.obsidian_vault_path = None
        self.processed_pdf_dir = tmp_path / "07_Processed"
        self.summary_dir = self.processed_pdf_dir / "Summaries"

    monkeypatch.setattr(
        proc_mod.CartaOSProcessor, "load_config", fake_load_config, raising=True
    )

    # avoid moving
    monkeypatch.setattr(
        proc_mod.CartaOSProcessor, "_move_pdf", lambda self: None, raising=True
    )

    with caplog.at_level('INFO'):
        proc = CartaOSProcessor(pdf_path=pdf, dry_run=True)
        ok = proc.process()
        assert ok is True
        
        # Check log messages
        log_messages = [rec.message for rec in caplog.records]
        assert any("[DRY RUN] Process would be successful." in msg for msg in log_messages)
        assert any("Summary: DRY SUMMARY" in msg for msg in log_messages)

    # No summary file created and PDF not moved
    assert not (tmp_path / "07_Processed" / "Summaries" / f"{pdf.stem}.md").exists()
    assert pdf.exists()
