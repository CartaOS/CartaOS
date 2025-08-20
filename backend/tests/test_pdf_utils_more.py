# -*- coding: utf-8 -*-
# backend/tests/test_pdf_utils_more.py

from pathlib import Path
from unittest.mock import MagicMock, patch

from cartaos.utils import pdf_utils


@patch("cartaos.utils.pdf_utils.pdfplumber.open")
@patch("cartaos.utils.pdf_utils.fitz.open")
def test_extract_text_both_backends_raise_returns_none(mock_fitz_open, mock_pdfplumber_open, tmp_path: Path):
    pdf = tmp_path / "x.pdf"; pdf.write_bytes(b"%PDF-1.4\n")

    mock_pdfplumber_open.side_effect = RuntimeError("fail plumber")
    mock_fitz_open.side_effect = RuntimeError("fail fitz")

    out = pdf_utils.extract_text(pdf)
    assert out is None
