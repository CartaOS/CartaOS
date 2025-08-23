# -*- coding: utf-8 -*-
# backend/tests/test_integration_pipeline.py

import shutil
import types
from pathlib import Path

import pytest
from typer.testing import CliRunner

import cartaos.cli as cli_module

runner = CliRunner()


def test_full_pipeline_with_mocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Setup isolated pipeline directories
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

    # Redirect CLI constants to our temp dirs
    monkeypatch.setattr(cli_module, "DIR_TRIAGE", triage_dir)
    monkeypatch.setattr(cli_module, "DIR_LAB", lab_dir)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr_dir)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum_dir)

    # Create two PDFs in triage
    long_pdf = triage_dir / "long.pdf"
    long_pdf.write_bytes(b"%PDF-1.4\n")
    short_pdf = triage_dir / "short.pdf"
    short_pdf.write_bytes(b"%PDF-1.4\n")

    # Triage: mock extract_text to control decisions
    def triage_extract_text(path: Path):
        if path.name == "long.pdf":
            return "x" * 600  # large => goes to summary
        if path.name == "short.pdf":
            return "x" * 100  # small => goes to lab
        return None

    monkeypatch.setattr("cartaos.triage.extract_text", triage_extract_text)

    # 1) Run triage
    res_triage = runner.invoke(cli_module.app, ["triage"])
    assert res_triage.exit_code == 0
    # Check moves
    assert (ready_sum_dir / "long.pdf").exists()
    assert (lab_dir / "short.pdf").exists()

    # 2) Run lab for the short file (non-interactive => enqueue to OCR dir)
    res_lab = runner.invoke(cli_module.app, ["lab", str(lab_dir / "short.pdf")])
    assert res_lab.exit_code == 0
    assert (ready_ocr_dir / "short.pdf").exists()

    # OCR: monkeypatch OcrProcessor to copy to output and return True
    class FakeOcr:
        def __init__(self, input_path: Path, output_path: Path) -> None:
            self.input_path = input_path
            self.output_path = output_path

        def process(self) -> bool:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_bytes(b"%PDF-1.4\n")
            return True

    monkeypatch.setattr(cli_module, "OcrProcessor", FakeOcr)

    # 3) Run OCR batch
    res_ocr = runner.invoke(cli_module.app, ["ocr"])
    assert res_ocr.exit_code == 0
    assert (ready_sum_dir / "short.pdf").exists()
    assert not (ready_ocr_dir / "short.pdf").exists()

    # Summarize: patch processor internals to avoid external AI
    # - extract_text -> raw; sanitize -> sanitized; generate_summary -> the summary text
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "raw text")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: "sanitized text")
    monkeypatch.setattr(
        "cartaos.processor.generate_summary", lambda t: "Integration summary"
    )

    # - force summaries to be written into a vault/Summaries under tmp
    vault = tmp_path / "vault"
    (vault / "Summaries").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(vault))

    # - redirect the move of PDF into our processed_dir
    import cartaos.processor as proc_mod

    def fake_move_pdf(self):
        processed_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(self.pdf_path, processed_dir / self.pdf_path.name)

    monkeypatch.setattr(
        proc_mod.CartaOSProcessor, "_move_pdf", fake_move_pdf, raising=True
    )

    # 4) Run summarize for both PDFs now in ready_sum_dir
    for pdf in [ready_sum_dir / "long.pdf", ready_sum_dir / "short.pdf"]:
        res_sum = runner.invoke(cli_module.app, ["summarize", str(pdf)])
        assert res_sum.exit_code == 0

    # Assertions: PDFs moved to processed, MDs written in vault/Summaries
    for name in ["long.pdf", "short.pdf"]:
        assert (processed_dir / name).exists()
        md = vault / "Summaries" / f"{Path(name).stem}.md"
        assert md.exists()
        assert md.read_text(encoding="utf-8") == "Integration summary"
