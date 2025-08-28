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
    monkeypatch.setattr(
        "cartaos.processor.extract_text",
        lambda p, force_ocr=False: None
    )
    proc = CartaOSProcessor(pdf)
    assert proc.process() is False


def test_process_fails_when_generate_summary_none(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    # Set up test directories
    processed_dir = tmp_path / "07_Processed"
    summaries_dir = processed_dir / "Summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test PDF
    pdf = make_pdf(tmp_path)
    
    # Mock the required functions
    monkeypatch.setattr(
        "cartaos.processor.extract_text",
        lambda p, force_ocr=False: "sample text"
    )
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: t)
    # Mock the async function with a coroutine that returns None
    async def mock_generate_summary_none(*args, **kwargs):
        return None
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary_none)
    
    # Mock the load_config method
    def fake_load_config(self):
        self.api_key = "test-api-key"
        self.obsidian_vault_path = None
        self.processed_pdf_dir = processed_dir
        self.summary_dir = summaries_dir
    
    import cartaos.processor as proc_mod
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "load_config", fake_load_config)
    
    # Run the processor
    proc = CartaOSProcessor(pdf)
    result = proc.process()
    
    # Check the output
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify the result and output
    assert result is False
    assert "Failed to generate summary" in output


def test_save_summary_slugifies_filename(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Create the necessary directories
    processed_dir = tmp_path / "07_Processed"
    summaries_dir = processed_dir / "Summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)
    
    pdf = make_pdf(tmp_path, name="My Report (v1).pdf")
    monkeypatch.setattr(
        "cartaos.processor.extract_text",
        lambda p, force_ocr=False: "content"
    )
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: t)
    # Mock the async function with a coroutine
    async def mock_generate_summary(*args, **kwargs):
        return "Test summary"
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)

    # Mock the load_config method
    def fake_load_config(self):
        self.api_key = "test-api-key"
        self.obsidian_vault_path = None
        self.processed_pdf_dir = processed_dir
        self.summary_dir = summaries_dir

    import cartaos.processor as proc_mod
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "load_config", fake_load_config)

    # Avoid moving the PDF
    monkeypatch.setattr(
        proc_mod.CartaOSProcessor, "_move_pdf", lambda self: None, raising=True
    )

    # Run the processor
    proc = CartaOSProcessor(pdf)
    assert proc.process() is True

    # Verify the summary file was created with the correct name and content
    md = summaries_dir / "my-report-v1.md"
    assert md.exists()
    assert md.read_text(encoding="utf-8") == "Test summary"
