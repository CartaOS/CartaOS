# -*- coding: utf-8 -*-
# backend/tests/test_triage_types.py

from pathlib import Path
import pytest

from cartaos.triage import TriageProcessor


def test_get_file_type_variants(tmp_path: Path) -> None:
    triage = tmp_path / "02_Triage"; triage.mkdir()
    lab = tmp_path / "03_Lab"; lab.mkdir()
    ready = tmp_path / "05_ReadyForSummary"; ready.mkdir()

    p = TriageProcessor(input_dir=triage, summary_dir=ready, lab_dir=lab)

    assert p._get_file_type(triage / "book.epub") == "ebook"
    assert p._get_file_type(triage / "novel.mobi") == "ebook"
    assert p._get_file_type(triage / "paper.PDF") == "pdf"
    assert p._get_file_type(triage / "notes.txt") is None


def test_triage_report_ignored_and_moves(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    triage = tmp_path / "02_Triage"; triage.mkdir()
    lab = tmp_path / "03_Lab"; lab.mkdir()
    ready = tmp_path / "05_ReadyForSummary"; ready.mkdir()

    # Files
    epub = triage / "b.epub"; epub.write_text("x")
    short_pdf = triage / "s.pdf"; short_pdf.write_bytes(b"%PDF-1.4\n")
    long_pdf = triage / "l.pdf"; long_pdf.write_bytes(b"%PDF-1.4\n")
    other = triage / "x.bin"; other.write_bytes(b"\x00\x01")

    # extract_text: return small vs large lengths
    def fake_extract(path: Path):
        if path.name == "l.pdf":
            return "x" * 600
        if path.name == "s.pdf":
            return "x" * 100
        return None
    monkeypatch.setattr("cartaos.triage.extract_text", fake_extract)

    p = TriageProcessor(input_dir=triage, summary_dir=ready, lab_dir=lab)
    report = p.process()

    assert epub.name in report["moved_to_summary"]
    assert long_pdf.name in report["moved_to_summary"]

    assert short_pdf.name in report["moved_to_lab"]
    assert other.name in report["ignored"]

    # Files should be moved accordingly
    assert (ready / epub.name).exists()
    assert (ready / long_pdf.name).exists()
    assert (lab / short_pdf.name).exists()
    assert not (triage / epub.name).exists()
