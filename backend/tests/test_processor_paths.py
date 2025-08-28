# -*- coding: utf-8 -*-
# backend/tests/test_processor_paths.py

import os
from pathlib import Path

import pytest

from cartaos.processor import CartaOSProcessor


def make_pdf(tmp_path: Path) -> Path:
    p = tmp_path / "doc.pdf"
    p.write_bytes(b"%PDF-1.4\n%...\n")
    return p


def test_summary_dir_prefers_obsidian_vault_when_valid(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path)
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(vault))

    proc = CartaOSProcessor(pdf_path=pdf)
    assert proc.summary_dir == vault / "Summaries"


def test_summary_dir_fallback_when_vault_invalid_or_unset(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path)
    # Ensure env var is unset
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)

    proc = CartaOSProcessor(pdf_path=pdf)
    assert proc.summary_dir == proc.processed_pdf_dir / "Summaries"

    # Even if set but not a directory, should fallback
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path / "missing_dir"))
    proc2 = CartaOSProcessor(pdf_path=pdf)
    assert proc2.summary_dir == proc2.processed_pdf_dir / "Summaries"


def test_generate_summary_empty_string_is_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf = make_pdf(tmp_path)
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "raw")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: "sanitized")
    # Mock the async function with a coroutine that returns an empty string (falsy)
    async def mock_generate_summary(*args, **kwargs):
        return ""
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)

    proc = CartaOSProcessor(pdf_path=pdf)
    assert proc.process() is False
