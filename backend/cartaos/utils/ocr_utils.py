"""
OCR utilities with timeout and retry functionality.
Provides robust handling of OCR operations with configurable resilience patterns.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from .external_calls import ExternalCallManager

logger = logging.getLogger(__name__)


async def process_document_with_retries(document_path: str) -> Optional[str]:
    """
    Process a document with OCR using timeout and retry protection.

    Args:
        document_path (str): Path to the document to process

    Returns:
        Optional[str]: OCR result or None if processing fails
    """
    manager = ExternalCallManager(
        timeout=120.0,  # Longer timeout for OCR operations
        max_retries=2,  # Fewer retries for OCR as it's expensive
        base_delay=5.0,
        circuit_breaker_threshold=3,
    )

    async def ocr_call():
        # Simulate OCR processing - in real implementation this would
        # call actual OCR libraries like pytesseract, easyocr, etc.
        await asyncio.sleep(0.1)  # Simulate processing time

        # Check if file exists
        if not Path(document_path).exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        # Simulate OCR result
        return f"OCR result for {document_path}"

    try:
        return await manager.call_with_retry(ocr_call)
    except Exception as e:
        logger.error("Error during OCR processing with retries: %s", e, exc_info=True)
        return None
