"""
Tests for the TriageProcessor class.

Tests:
    - Successful triage process
    - Test get_file_type
    - Test move_to_summary_dir
    - Test lab_dir fixture
    - Test pdf_has_sufficient_text
"""

import pytest
from pathlib import Path
from cartaos.triage import TriageProcessor

@pytest.fixture
def input_dir(tmp_path):
    return tmp_path / "input"

@pytest.fixture
def summary_dir(tmp_path):
    return tmp_path / "summary"

@pytest.fixture
def lab_dir(tmp_path):
    return tmp_path / "lab"

def test_triage_processor(input_dir, summary_dir, lab_dir):
    triage_processor = TriageProcessor(input_dir, summary_dir, lab_dir)
    triage_processor.process()

def test_get_file_type():
    triage_processor = TriageProcessor(None, None, None)
    assert triage_processor._get_file_type(Path("example.epub")) == "ebook"
    assert triage_processor._get_file_type(Path("example.pdf")) == "pdf"
    assert triage_processor._get_file_type(Path("example.txt")) is None

def test_pdf_has_sufficient_text():
    triage_processor = TriageProcessor(None, None, None)
    pdf_path = Path("example.pdf")
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
        assert triage_processor._pdf_has_sufficient_text(pdf_path) == (len(text) > 500)

def test_move_to_summary_dir(input_dir, summary_dir):
    triage_processor = TriageProcessor(input_dir, summary_dir, None)
    file