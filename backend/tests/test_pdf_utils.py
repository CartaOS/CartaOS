# -*- coding: utf-8 -*-
# backend/tests/test_pdf_utils.py

from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from cartaos.utils import pdf_utils


# ---------------------- extract_text ----------------------
@patch("cartaos.utils.pdf_utils.pdfplumber.open")
@patch("cartaos.utils.pdf_utils.fitz.open")
def test_extract_text_pdfplumber_success(
    mock_fitz_open, mock_pdfplumber_open, tmp_path
):
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    # pdfplumber returns pages with text
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "A" * 60
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "B" * 60

    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value.pages = [mock_page1, mock_page2]
    mock_pdfplumber_open.return_value = mock_pdf

    text = pdf_utils.extract_text(pdf_path)

    assert text == ("A" * 60 + "B" * 60)
    mock_pdfplumber_open.assert_called_once()
    mock_fitz_open.assert_not_called()


@patch("cartaos.utils.pdf_utils.pdfplumber.open")
@patch("cartaos.utils.pdf_utils.fitz.open")
def test_extract_text_fallback_to_fitz_success(
    mock_fitz_open, mock_pdfplumber_open, tmp_path
):
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    # pdfplumber returns empty text
    mock_pdf_empty = MagicMock()
    empty_page = MagicMock()
    empty_page.extract_text.return_value = None
    mock_pdf_empty.__enter__.return_value.pages = [empty_page]
    mock_pdfplumber_open.return_value = mock_pdf_empty

    # fitz returns text
    mock_doc = MagicMock()
    page_fitz = MagicMock()
    page_fitz.get_text.return_value = "Fallback text"
    mock_doc.__enter__.return_value = [page_fitz]
    mock_fitz_open.return_value = mock_doc

    text = pdf_utils.extract_text(pdf_path)

    assert text == "Fallback text"
    mock_pdfplumber_open.assert_called_once()
    mock_fitz_open.assert_called_once()


@patch("cartaos.utils.pdf_utils.pdfplumber.open")
@patch("cartaos.utils.pdf_utils.fitz.open")
def test_extract_text_both_produce_empty_string(
    mock_fitz_open, mock_pdfplumber_open, tmp_path
):
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    # pdfplumber returns empty strings
    p1 = MagicMock()
    p1.extract_text.return_value = None
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value.pages = [p1]
    mock_pdfplumber_open.return_value = mock_pdf

    # fitz returns empty string as well
    fpage = MagicMock()
    fpage.get_text.return_value = ""
    mock_doc = MagicMock()
    mock_doc.__enter__.return_value = [fpage]
    mock_fitz_open.return_value = mock_doc

    text = pdf_utils.extract_text(pdf_path)
    # Function returns the (empty) text gathered in the fallback branch
    assert text == ""


# ---------------------- extract_pages ----------------------
@patch("cartaos.utils.pdf_utils.pdf2image.convert_from_path")
def test_extract_pages_success(mock_convert_from_path, tmp_path):
    input_pdf = tmp_path / "input.pdf"
    input_pdf.write_bytes(b"%PDF-1.4\n")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    # simulate two PIL images with .save()
    img1 = MagicMock()
    img2 = MagicMock()
    mock_convert_from_path.return_value = [img1, img2]

    images: List[Path] = pdf_utils.extract_pages(input_pdf, out_dir)

    assert len(images) == 2
    assert images[0].name == "page_1.tiff"
    assert images[1].name == "page_2.tiff"
    img1.save.assert_called_once_with(out_dir / "page_1.tiff")
    img2.save.assert_called_once_with(out_dir / "page_2.tiff")


@patch("cartaos.utils.pdf_utils.pdf2image.convert_from_path")
def test_extract_pages_no_images(mock_convert_from_path, tmp_path):
    input_pdf = tmp_path / "input.pdf"
    input_pdf.write_bytes(b"%PDF-1.4\n")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    mock_convert_from_path.return_value = []

    images = pdf_utils.extract_pages(input_pdf, out_dir)
    assert images == []


# ---------------------- recompose_pdf ----------------------
@patch("cartaos.utils.pdf_utils.convert")
def test_recompose_pdf_success(mock_convert, tmp_path):
    out = tmp_path / "out.pdf"
    img1 = tmp_path / "page_1.tiff"
    img1.write_bytes(b"TIFFDATA")
    img2 = tmp_path / "page_2.tiff"
    img2.write_bytes(b"TIFFDATA")

    mock_convert.return_value = b"%PDF-1.4%\n"

    result_path = pdf_utils.recompose_pdf([img1, img2], out)

    assert result_path == out
    assert out.exists()
    assert out.read_bytes().startswith(b"%PDF-1.4")
    mock_convert.assert_called_once()
