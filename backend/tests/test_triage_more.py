# -*- coding: utf-8 -*-
# backend/tests/test_triage_more.py

from pathlib import Path
import pytest
from cartaos.triage import TriageProcessor


def test_unsupported_file_type_goes_to_ignored(tmp_path: Path) -> None:
    input_dir = tmp_path / "02_Triage"; input_dir.mkdir()
    summary_dir = tmp_path / "05_ReadyForSummary"; summary_dir.mkdir()
    lab_dir = tmp_path / "03_Lab"; lab_dir.mkdir()

    # Create unsupported file (e.g., .docx)
    docx = input_dir / "report.docx"
    docx.write_text("dummy")

    proc = TriageProcessor(input_dir, summary_dir, lab_dir)
    report = proc.process()

    # It should be ignored and remain in place
    assert report["ignored"] == ["report.docx"]
    assert not (summary_dir / "report.docx").exists()
    assert not (lab_dir / "report.docx").exists()
    assert (input_dir / "report.docx").exists()
