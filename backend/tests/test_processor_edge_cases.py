# -*- coding: utf-8 -*-
# backend/tests/test_processor_edge_cases.py

from pathlib import Path

import pytest

from cartaos.processor import CartaOSProcessor


def make_pdf(tmp_path: Path, name: str = "doc.pdf") -> Path:
    p = tmp_path / name
    p.write_bytes(b"%PDF-1.4\n")
    return p


def test_process_fails_when_text_extraction_none(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path)
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: None)
    proc = CartaOSProcessor(pdf)
    assert proc.process() is False


def test_process_fails_when_generate_summary_none(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path)
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "hello")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: t)
    monkeypatch.setattr("cartaos.processor.generate_summary", lambda t: None)
    proc = CartaOSProcessor(pdf)
    assert proc.process() is False


def test_save_summary_slugifies_filename(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path, name="My Report (v1).pdf")
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "content")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: t)
    monkeypatch.setattr("cartaos.processor.generate_summary", lambda t: "Summary Text")

    # Force summary_dir and processed dir under tmp
    import cartaos.processor as proc_mod

    def fake_load_config(self):
        self.api_key = None
        self.obsidian_vault_path = None
        self.processed_pdf_dir = tmp_path / "07_Processed"
        self.summary_dir = self.processed_pdf_dir / "Summaries"

    monkeypatch.setattr(
        proc_mod.CartaOSProcessor, "load_config", fake_load_config, raising=True
    )

    # Avoid moving the PDF so we can assert summary file easily
    monkeypatch.setattr(
        proc_mod.CartaOSProcessor, "_move_pdf", lambda self: None, raising=True
    )

    proc = CartaOSProcessor(pdf)
    assert proc.process() is True

    md = tmp_path / "07_Processed" / "Summaries" / "my-report-v1.md"
    assert md.exists()
    assert md.read_text(encoding="utf-8") == "Summary Text"
