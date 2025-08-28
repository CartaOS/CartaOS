# -*- coding: utf-8 -*-
# backend/tests/test_processor_more.py

import builtins
from pathlib import Path

import pytest
from slugify import slugify

from cartaos.processor import CartaOSProcessor


def make_pdf(tmp_path: Path) -> Path:
    p = tmp_path / "doc.pdf"
    p.write_bytes(b"%PDF-1.4\n%...\n")
    return p


def test_process_extract_text_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path)

    # Patch the imported name inside cartaos.processor
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: None)

    proc = CartaOSProcessor(pdf_path=pdf)
    assert proc.process() is False


def test_process_debug_path_creates_debug_file_and_returns_true(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path)
    # Create a debug text file to simulate the output
    debug_file = pdf.parent / f"{pdf.stem}_extracted_text.txt"
    debug_file.write_text("hello text")
    
    # Mock extract_text to return sample content
    monkeypatch.setattr(
        "cartaos.processor.extract_text",
        lambda p, force_ocr=False: "hello text"
    )

    # Ensure these are not called in debug mode
    def boom(*a, **k):
        raise AssertionError("Should not be called in debug mode")

    monkeypatch.setattr("cartaos.processor.sanitize", boom)
    # Mock the async function with a coroutine that will raise an error if called
    async def mock_generate_summary(*args, **kwargs):
        raise AssertionError("Should not be called in debug mode")
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)

    # Create the processor with debug=True
    proc = CartaOSProcessor(pdf_path=pdf, debug=True)
    
    # Run the processor
    ok = proc.process()
    
    # Verify results
    assert ok is True
    assert debug_file.exists()
    assert debug_file.read_text(encoding="utf-8") == "hello text"


def test_process_dry_run_logs_summary_and_returns_true(
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
        lambda p, force_ocr=False: "sample text for dry run"
    )
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: t)
    # Mock the async function with a coroutine
    async def mock_generate_summary(*args, **kwargs):
        return "the summary"
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)
    
    # Track if file operations are called
    save_called = False
    move_called = False
    
    # Mock the load_config method
    def fake_load_config(self):
        self.api_key = "test-api-key"
        self.obsidian_vault_path = None
        self.processed_pdf_dir = processed_dir
        self.summary_dir = summaries_dir
    
    import cartaos.processor as proc_mod
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "load_config", fake_load_config)
    
    # Mock file operations to track calls
    def mock_save(self, summary):
        nonlocal save_called
        save_called = True
        print(f"[MOCK] Would save summary: {summary[:50]}...")
        return None
        
    def mock_move(self):
        nonlocal move_called
        move_called = True
        print("[MOCK] Would move PDF")
        return None
    
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "_save_summary", mock_save)
    monkeypatch.setattr(proc_mod.CartaOSProcessor, "_move_pdf", mock_move)

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
    
    # Check that the mock function printed its output
    assert "[MOCK] Would save summary: the summary..." in output
    # _move_pdf shouldn't be called in dry run mode, so we don't check for its output
    
    # Verify no files were actually created
    assert not (summaries_dir / f"{slugify(pdf.stem)}.md").exists()
    assert not (processed_dir / pdf.name).exists()


def test_process_generate_summary_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path)

    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "raw")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: "sanitized")
    # Mock the async function with a coroutine that returns None to simulate failure
    async def mock_generate_summary_none(*args, **kwargs):
        return None
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary_none)

    proc = CartaOSProcessor(pdf_path=pdf)
    assert proc.process() is False


def test_process_defaults_full_success_saves_and_moves(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path)

    # Ensure normal pipeline succeeds
    monkeypatch.setattr(
        "cartaos.processor.extract_text",
        lambda p, force_ocr=False: "raw"
    )
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: "sanitized")
    # Mock the async function with a coroutine
    async def mock_generate_summary(*args, **kwargs):
        return "the summary"
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)

    calls = {"save": 0, "move": 0}

    def fake_save(self, s):
        calls["save"] += 1

    def fake_move(self):
        calls["move"] += 1

    monkeypatch.setattr(CartaOSProcessor, "_save_summary", fake_save)
    monkeypatch.setattr(CartaOSProcessor, "_move_pdf", fake_move)

    # Default args: dry_run must be False so save/move happen
    proc = CartaOSProcessor(pdf_path=pdf)
    ok = proc.process()
    assert ok is True
    assert calls["save"] == 1
    assert calls["move"] == 1
