# -*- coding: utf-8 -*-
# backend/cartaos/utils/pdf_utils.py

from pathlib import Path
from typing import Optional, List

import pdfplumber
import fitz
import logging
import pdf2image
from img2pdf import convert

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
    return text

def extract_pages(input_path: Path) -> List[Path]:
    """
    Extract the pages from the input PDF.

    Args:
        input_path (Path): The path to the source PDF file.

    Returns:
        List[Path]: A list of paths to the extracted TIFF images.
    """
    images: List[Path] = []
    for i, image in enumerate(pdf2image.convert_from_path(input_path, dpi=300, grayscale=True)):
        image_path: Path = input_path.parent / f"page_{i+1}.tiff"
        image.save(image_path)
        images.append(image_path)
    return images


def recompose_pdf(images: List[Path], output_dir: Path, input_path: Path) -> Path:
    """
    Recompose the PDF from the corrected images.

    Args:
        images (List[Path]): The list of paths to the corrected TIFF images.
        output_dir (Path): The destination directory for the corrected PDF.
        input_path (Path): The path to the source PDF file.

    Returns:
        Path: The path to the saved PDF file.
    """
    pdf_path: Path = output_dir / input_path.name
    convert(images, pdf_path)
    return pdf_path
