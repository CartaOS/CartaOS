# -*- coding: utf-8 -*-
# backend/tests/test_processor_modes.py

import os
from pathlib import Path

import pytest
from slugify import slugify

from cartaos.processor import CartaOSProcessor


def _make_pdf(tmp_path: Path, name: str = "doc.pdf") -> Path:
    p = tmp_path / name
    p.write_bytes(b"%PDF-1.4\n")
    return p


def test_debug_mode_writes_extracted_text_and_returns_true(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = _make_pdf(tmp_path)
    
    # Mock the async function with a coroutine
    async def mock_generate_summary(*args, **kwargs):
        return "Test summary"
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)

    # Mock extract_text to return sample content
    monkeypatch.setattr(
        "cartaos.processor.extract_text",
        lambda p, force_ocr=False: "sample debug text"
    )

    # Ensure these are not called in debug mode
    def boom(*a, **k):
        raise AssertionError("Should not be called in debug mode")

    monkeypatch.setattr("cartaos.processor.sanitize", boom, raising=True)
    # The generate_summary function no longer exists, so we don't need to mock it

    # Set up test directories
    processed_dir = tmp_path / "07_Processed"
    summaries_dir = processed_dir / "Summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock the load_config method
    def fake_load_config(self):
        self.api_key = "test-api-key"
        self.obsidian_vault_path = None
        self.processed_pdf_dir = processed_dir
        self.summary_dir = summaries_dir

    import cartaos.processor as proc_mod
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "load_config", fake_load_config)

    # Run the processor in debug mode
    proc = CartaOSProcessor(pdf_path=pdf, debug=True)
    ok = proc.process()
    
    # Verify results
    assert ok is True
    
    # Check debug file was created with the right content
    debug_file = pdf.with_suffix(".txt")
    assert debug_file.exists()
    assert debug_file.read_text(encoding="utf-8") == "sample debug text"
    
    # Ensure no summary was written in debug mode
    assert not (summaries_dir / f"{pdf.stem}.md").exists()
    assert pdf.exists()  # Original file should still exist


def test_dry_run_logs_summary_and_does_not_write_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    pdf = _make_pdf(tmp_path)
    
    # Mock the extract_text and generate_summary functions
    monkeypatch.setattr(
        "cartaos.processor.extract_text",
        lambda p, force_ocr=False: "sample text for dry run"
    )
    # Mock the async function with a coroutine
    async def mock_generate_summary(*args, **kwargs):
        return "Test summary"
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)

    # Set up test directories
    processed_dir = tmp_path / "07_Processed"
    summaries_dir = processed_dir / "Summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    # Track if file operations are called
    save_called = False
    move_called = False

    # Save original methods
    import cartaos.processor as proc_mod
    
    # Mock the methods to track calls and prevent actual file operations
    def mock_save(self, summary):
        nonlocal save_called
        save_called = True
        # Don't call original to prevent file operations
        print(f"[MOCK] Would save summary: {summary[:50]}...")
        return None
        
    def mock_move(self):
        nonlocal move_called
        move_called = True
        # Don't call original to prevent file operations
        print("[MOCK] Would move PDF")
        return None

    # Apply the mocks
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "_save_summary", mock_save)
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "_move_pdf", mock_move)

    # Mock the load_config method
    def fake_load_config(self):
        self.api_key = "test-api-key"
        self.obsidian_vault_path = None
        self.processed_pdf_dir = processed_dir
        self.summary_dir = summaries_dir

    monkeypatch.setattr(proc_mod.CartaOSProcessor, "load_config", fake_load_config)

    # Run the processor in dry run mode
    proc = CartaOSProcessor(pdf_path=pdf, dry_run=True)
    ok = proc.process()

    # Check the output
    captured = capsys.readouterr()
    output = captured.out

    # Verify results
    assert ok is True
    
    # In dry run mode, only _save_summary should be called
    assert save_called is True, "_save_summary mock should be called"
    assert move_called is False, "_move_pdf mock should not be called in dry run mode"
    
    # Check that the mock function printed its output with the test summary
    assert "[MOCK] Would save summary: Test summary..." in output
    # _move_pdf shouldn't be called in dry run mode, so we don't check for its output
    
    # Verify no files were actually created
    assert not (summaries_dir / f"{slugify(pdf.stem)}.md").exists()
    assert not (processed_dir / pdf.name).exists()
    assert pdf.exists()
