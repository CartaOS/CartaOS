# -*- coding: utf-8 -*-
# backend/tests/test_triage_param.py

import os
from pathlib import Path
import pytest

from cartaos.triage import TriageProcessor


@pytest.mark.parametrize(
    "filename, extracted_len, expected_bucket",
    [
        ("book.epub", None, "summary"),           # ebook -> summary directly
        ("novel.mobi", None, "summary"),          # other supported ebook ext
        ("good.pdf", 600, "summary"),            # long text pdf -> summary
        ("edge.pdf", 500, "lab"),               # exact threshold -> should go to lab
        ("bad.pdf", 100, "lab"),                 # short text pdf -> lab
        ("none.pdf", None, "lab"),               # extract_text returns None -> lab
        ("empty.pdf", 0, "lab"),                 # extract_text returns empty string -> lab
        ("report.docx", None, "ignored"),        # unsupported -> ignored
    ],
)
def test_triage_parametrized(filename, extracted_len, expected_bucket, tmp_path, monkeypatch):
    input_dir = tmp_path / "02_Triage"; input_dir.mkdir()
    summary_dir = tmp_path / "05_ReadyForSummary"; summary_dir.mkdir()
    lab_dir = tmp_path / "03_Lab"; lab_dir.mkdir()

    # create file
    fpath = input_dir / filename
    fpath.write_text("dummy")

    # Patch extract_text for PDFs only
    def fake_extract_text(p: Path):
        if p.suffix.lower() == ".pdf":
            if extracted_len is None:
                return None
            return "x" * extracted_len
        return None

    monkeypatch.setattr("cartaos.triage.extract_text", fake_extract_text)

    proc = TriageProcessor(input_dir, summary_dir, lab_dir)
    report = proc.process()

    if expected_bucket == "summary":
        assert (summary_dir / filename).exists()
        assert filename in report["moved_to_summary"]
        assert filename not in report["moved_to_lab"]
        assert filename not in report["ignored"]
    elif expected_bucket == "lab":
        assert (lab_dir / filename).exists()
        assert filename in report["moved_to_lab"]
        assert filename not in report["moved_to_summary"]
        assert filename not in report["ignored"]
    else:
        # ignored
        assert (input_dir / filename).exists()
        assert filename in report["ignored"]
        assert filename not in report["moved_to_lab"]
        assert filename not in report["moved_to_summary"]
