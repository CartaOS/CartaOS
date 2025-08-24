# -*- coding: utf-8 -*-
# backend/cartaos/utils/pdf_utils.py

import logging
from types import SimpleNamespace
from pathlib import Path
from typing import List, Optional

"""
NOTE: Heavy C-extension modules (e.g., PyMuPDF/fitz, pdfplumber, pdf2image, img2pdf)
are imported lazily inside functions. This mitigates rare segfaults observed when
combining coverage instrumentation with these extensions during pytest collection.
"""

# Test hooks: placeholders so tests can monkeypatch module-level symbols without
# importing C-extensions at import time. Functions below will use these if set.
# The placeholders expose the attributes that tests patch (e.g., .open).
pdfplumber = SimpleNamespace(open=None)  # type: ignore[attr-defined]
fitz = SimpleNamespace(open=None)  # type: ignore[attr-defined]
pdf2image = SimpleNamespace(convert_from_path=None)  # type: ignore[attr-defined]

def convert(*_args, **_kwargs):  # placeholder function, tests patch this
    raise NotImplementedError("img2pdf.convert placeholder; should be patched or lazily imported")


def extract_text(pdf_path: Path) -> Optional[str]:
    """
    Extracts full text from a PDF file using pdfplumber and PyMuPDF.

    If pdfplumber fails to extract text, the function falls back to PyMuPDF (fitz).

    Args:
        pdf_path (Path): Path to the PDF file.

    Returns:
        Optional[str]: The extracted text or None if extraction fails.

    Raises:
        ValueError: If the pdf_path is not a valid path to a PDF file.
    """
    logging.info(f"Extracting text from '{pdf_path.name}'...")

    # Ensure variable is defined for all paths
    text: Optional[str] = None

    try:
        # Attempt text extraction using pdfplumber
        _pdfplumber = globals().get("pdfplumber")
        if not hasattr(_pdfplumber, "open") or getattr(_pdfplumber, "open") is None:
            import pdfplumber as _pdfplumber  # type: ignore  # lazy import

        with _pdfplumber.open(str(pdf_path)) as pdf:  # type: ignore[attr-defined]
            text = "".join(page.extract_text() or "" for page in pdf.pages)
            if text and len(text) >= 100:
                logging.info(f"Text extracted successfully: {text[:100]}...")
                return text.strip()
    except Exception as e:
        logging.warning(f"pdfplumber extraction failed: {e}")

    logging.info("Attempting extraction with PyMuPDF (fitz)...")
    try:
        # Fallback to PyMuPDF if pdfplumber fails
        _fitz = globals().get("fitz")
        if not hasattr(_fitz, "open") or getattr(_fitz, "open") is None:
            import fitz as _fitz  # type: ignore  # lazy import

        with _fitz.open(str(pdf_path)) as doc:  # type: ignore[attr-defined]
            text = "".join(page.get_text() for page in doc)
            if text:
                logging.info(f"Text extracted successfully: {text[:100]}...")
                return text.strip()
    except Exception as e:
        logging.error(f"PyMuPDF extraction failed: {e}")
    return text


def extract_pages(input_path: Path, output_dir: Path) -> List[Path]:
    """
    Extract the pages from the input PDF.

    Args:
        input_path (Path): The path to the source PDF file.
        output_dir (Path): The destination directory for the extracted images.

    Returns:
        List[Path]: A list of paths to the extracted TIFF images.
    """
    _pdf2image = globals().get("pdf2image")
    if not hasattr(_pdf2image, "convert_from_path") or getattr(
        _pdf2image, "convert_from_path"
    ) is None:
        import pdf2image as _pdf2image  # type: ignore  # lazy import

    images: List[Path] = []
    for i, image in enumerate(
        _pdf2image.convert_from_path(input_path, dpi=300, grayscale=True)  # type: ignore[attr-defined]
    ):
        image_path: Path = output_dir / f"page_{i+1}.tiff"
        image.save(image_path)
        images.append(image_path)
    return images


def recompose_pdf(images: List[Path], output_path: Path) -> Path:
    """
    Recompose the PDF from the corrected images.

    Args:
        images (List[Path]): The list of paths to the corrected TIFF images.
        output_path (Path): The path to the saved PDF file.

    Returns:
        Path: The path to the saved PDF file.
    """
    _convert = globals().get("convert")
    # If still the placeholder (raises NotImplementedError) or missing, lazy import real one
    needs_import = _convert is None or getattr(_convert, "__name__", "") == "convert" and _convert.__doc__ is None
    if needs_import:
        # Lazy import to avoid importing C-extensions at module import time
        from img2pdf import convert as _convert  # type: ignore

    with open(output_path, "wb") as f:
        f.write(_convert(images))  # type: ignore[misc]
    return output_path
