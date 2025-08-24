import os
from pathlib import Path

import pytest

from cartaos.triage import TriageProcessor


@pytest.fixture
def setup_dirs(tmp_path):
    inp = tmp_path / "02_Triage"
    inp.mkdir()
    out = tmp_path / "05_ReadyForSummary"
    out.mkdir()
    lab = tmp_path / "03_Lab"
    lab.mkdir()
    return inp, out, lab


def touch(filename, parent):
    f = parent / filename
    f.write_text("dummy")
    return f


def test_triage_moves_ebook_and_pdf(monkeypatch, setup_dirs):
    inp, summary, lab = setup_dirs
    # create test files
    epub = touch("book.epub", inp)
    pdf_good = touch("good.pdf", inp)
    pdf_bad = touch("bad.pdf", inp)

    # força comportamento de reconhecimento de texto
    monkeypatch.setattr(
        TriageProcessor,
        "_get_file_type",
        lambda self, p: "pdf" if p.suffix == ".pdf" else "ebook",
    )
    monkeypatch.setattr(
        "cartaos.triage.extract_text", lambda p: "x" * 600 if "good" in p.name else ""
    )

    proc = TriageProcessor(inp, summary, lab)
    report = proc.process()

    assert (summary / "book.epub").exists()
    assert (summary / "good.pdf").exists()
    assert (lab / "bad.pdf").exists()

    # Check that both files were moved, regardless of order
    assert sorted(report["moved_to_summary"]) == sorted(["book.epub", "good.pdf"])
    assert report["moved_to_lab"] == ["bad.pdf"]
    assert report["ignored"] == []
