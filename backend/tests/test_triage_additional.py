# -*- coding: utf-8 -*-
# backend/tests/test_triage_additional.py

from pathlib import Path
import os
import pytest

from cartaos.triage import TriageProcessor


def test_get_file_type_case_insensitive(tmp_path: Path) -> None:
    triage = tmp_path / "02_Triage"; triage.mkdir()
    ready = tmp_path / "05_ReadyForSummary"; ready.mkdir()
    lab = tmp_path / "03_Lab"; lab.mkdir()

    p = TriageProcessor(triage, ready, lab)
    assert p._get_file_type(triage / "Book.EPUb") == "ebook"
    assert p._get_file_type(triage / "Novel.MobI") == "ebook"
    assert p._get_file_type(triage / "Paper.PDF") == "pdf"


def test_nested_dir_moves_and_ignored_logs_warning(tmp_path: Path, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch) -> None:
    triage = tmp_path / "02_Triage"; triage.mkdir()
    ready = tmp_path / "05_ReadyForSummary"; ready.mkdir()
    lab = tmp_path / "03_Lab"; lab.mkdir()

    # Create nested structure with a small PDF (goes to lab) and an unsupported file
    nested = triage / "sub/dir"; nested.mkdir(parents=True, exist_ok=True)
    small_pdf = nested / "short.pdf"; small_pdf.write_bytes(b"%PDF-1.4\n")
    other = nested / "data.bin"; other.write_bytes(b"\x00")

    # extract_text small
    monkeypatch.setattr("cartaos.triage.extract_text", lambda p: "x" * 120)

    proc = TriageProcessor(triage, ready, lab)

    with caplog.at_level("WARNING"):
        report = proc.process()

    # Relative movement preserved
    assert (lab / "sub/dir/short.pdf").exists()
    assert "data.bin" in report["ignored"]
    # Warning logged for unsupported type
    assert any("Unsupported file type" in rec.message for rec in caplog.records)
