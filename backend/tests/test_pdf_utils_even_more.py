# -*- coding: utf-8 -*-
# backend/tests/test_pdf_utils_even_more.py

from pathlib import Path
from unittest.mock import MagicMock, patch

from cartaos.utils import pdf_utils


@patch("cartaos.utils.pdf_utils.pdfplumber.open")
@patch("cartaos.utils.pdf_utils.fitz.open")
def test_extract_text_short_pdfplumber_then_fitz_success(mock_fitz_open, mock_pdfplumber_open, tmp_path: Path):
    pdf = tmp_path / "s.pdf"; pdf.write_bytes(b"%PDF-1.4\n")

    # pdfplumber returns <100 chars
    short_page = MagicMock(); short_page.extract_text.return_value = "short text"
    mock_pdf = MagicMock(); mock_pdf.__enter__.return_value.pages = [short_page]
    mock_pdfplumber_open.return_value = mock_pdf

    # fitz returns non-empty
    fpage = MagicMock(); fpage.get_text.return_value = "fitz wins"
    mock_doc = MagicMock(); mock_doc.__enter__.return_value = [fpage]
    mock_fitz_open.return_value = mock_doc

    out = pdf_utils.extract_text(pdf)
    assert out == "fitz wins"


@patch("cartaos.utils.pdf_utils.pdfplumber.open")
@patch("cartaos.utils.pdf_utils.fitz.open")
def test_extract_text_fitz_whitespace_stripped_to_empty_string(mock_fitz_open, mock_pdfplumber_open, tmp_path: Path):
    pdf = tmp_path / "w.pdf"; pdf.write_bytes(b"%PDF-1.4\n")

    # pdfplumber returns empty so fallback runs
    mock_pdf = MagicMock(); mock_pdf.__enter__.return_value.pages = []
    mock_pdfplumber_open.return_value = mock_pdf

    # fitz returns whitespace which strip() makes empty
    fpage = MagicMock(); fpage.get_text.return_value = "  \n\t  "
    mock_doc = MagicMock(); mock_doc.__enter__.return_value = [fpage]
    mock_fitz_open.return_value = mock_doc

    out = pdf_utils.extract_text(pdf)
    assert out == ""
