# -*- coding: utf-8 -*-
# backend/cartaos/utils/pdf_utils.py

from pathlib import Path
from typing import Optional

import pdfplumber
import fitz
import logging

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

    try:
        # Attempt text extraction using pdfplumber
        with pdfplumber.open(str(pdf_path)) as pdf:
            text: str = "".join(page.extract_text() or "" for page in pdf.pages)
            if text and len(text) >= 100:
                logging.info(f"Text extracted successfully: {text[:100]}...")
                return text.strip()
    except Exception as e:
        logging.warning(f"pdfplumber extraction failed: {e}")

    logging.info("Attempting extraction with PyMuPDF (fitz)...")
    try:
        # Fallback to PyMuPDF if pdfplumber fails
        with fitz.open(str(pdf_path)) as doc:
            text: str = "".join(page.get_text() for page in doc)
            if text:
                logging.info(f"Text extracted successfully: {text[:100]}...")
                return text.strip()
    except Exception as e:
        logging.error(f"PyMuPDF extraction failed: {e}")

    return None

