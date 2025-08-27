# -*- coding: utf-8 -*-
# backend/cartaos/utils/pdf_utils.py

import logging
import sys
from types import SimpleNamespace
from pathlib import Path
from typing import Any, Callable, List, Optional, Sequence, cast

"""
NOTE: Heavy C-extension modules (e.g., PyMuPDF/fitz, pdfplumber, pdf2image, img2pdf)
are imported lazily inside functions. This mitigates rare segfaults observed when
combining coverage instrumentation with these extensions during pytest collection.
"""

# Test hooks: placeholders so tests can monkeypatch module-level symbols without
# importing C-extensions at import time. Functions below will use these if set.
# The placeholders expose the attributes that tests patch (e.g., .open).
pdfplumber = SimpleNamespace(open=None)
fitz = SimpleNamespace(open=None)
pdf2image = SimpleNamespace(convert_from_path=None)

# Typed placeholder for img2pdf.convert so mypy understands usage where patched or lazily imported
ConvertFunc = Callable[[Sequence[str]], bytes]

def convert(_images: Sequence[str]) -> bytes:  # placeholder function, tests may patch this
    """Placeholder for img2pdf.convert; should be patched in tests or lazily imported at runtime."""
    raise NotImplementedError("img2pdf.convert placeholder; should be patched or lazily imported")

# Sentinel to detect the original placeholder versus a patched/mock implementation
_PLACEHOLDER_CONVERT = convert


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
    logger = logging.getLogger(__name__)
    logger.info(f"Extracting text from '{pdf_path.name}'...")

    # Ensure variable is defined for all paths
    text: Optional[str] = None

    try:
        # Attempt text extraction using pdfplumber
        _plumb_any = globals().get("pdfplumber")
        if not (hasattr(_plumb_any, "open") and getattr(_plumb_any, "open") is not None):
            import pdfplumber as _plumb_mod
        else:
            _plumb_mod = cast(Any, _plumb_any)

        with _plumb_mod.open(str(pdf_path)) as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages)
            if text and len(text) >= 100:
                logger.debug(f"Text sample: {text[:100]}...")  # Reduzindo para debug
                return text.strip()
    except Exception as e:
        logger.error(f"pdfplumber extraction failed: {str(e)}", exc_info=logger.level <= logging.DEBUG)

    logging.info("Attempting extraction with PyMuPDF (fitz)...")
    try:
        # Fallback to PyMuPDF if pdfplumber fails
        _fitz_any = globals().get("fitz")
        if not (hasattr(_fitz_any, "open") and getattr(_fitz_any, "open") is not None):
            import fitz as _fitz_mod
        else:
            _fitz_mod = cast(Any, _fitz_any)

        with _fitz_mod.open(str(pdf_path)) as doc:
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
    _pdf2_any = globals().get("pdf2image")
    if not (
        hasattr(_pdf2_any, "convert_from_path") and getattr(_pdf2_any, "convert_from_path") is not None
    ):
        import pdf2image as _pdf2_mod
    else:
        _pdf2_mod = cast(Any, _pdf2_any)

    images: List[Path] = []
    for i, image in enumerate(
        _pdf2_mod.convert_from_path(input_path, dpi=300, grayscale=True)
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
    _convert_any = globals().get("convert")
    # If still the placeholder (which raises NotImplementedError) or missing, lazy import real one
    if _convert_any is None or _convert_any is _PLACEHOLDER_CONVERT:
        from img2pdf import convert as _real_convert
        convert_fn: ConvertFunc = cast(ConvertFunc, _real_convert)
    else:
        convert_fn = cast(ConvertFunc, _convert_any)

    # Convert image paths to strings for a well-typed call
    image_paths: List[str] = [str(p) for p in images]

    with open(output_path, "wb") as f:
        f.write(convert_fn(image_paths))
    return output_path
