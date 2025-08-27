"""
Tests for the OCR processor functionality.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cartaos.processors.ocr_processor import OcrProcessor

@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a sample PDF file for testing."""
    pdf_path = tmp_path / "test_document.pdf"
    # Create a simple PDF file for testing
    with open(pdf_path, 'wb') as f:
        f.write(b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>endobj\n4 0 obj<</Length 44>>stream\nBT\n/F1 24 Tf\n100 700 Td\n(Test Document) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000105 00000 n \n0000000179 00000 n \ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n233\n%%EOF')
    return pdf_path

@pytest.fixture
def ocr_processor():
    """Create an instance of the OCR processor."""
    return OcrProcessor()

@pytest.mark.asyncio
async def test_ocr_processor_initialization(ocr_processor):
    """Test that the OCR processor initializes correctly."""
    await ocr_processor.initialize()
    assert ocr_processor.initialized is True

@pytest.mark.asyncio
async def test_process_document(ocr_processor, sample_pdf_path, tmp_path):
    """Test processing a document with the OCR processor."""
    await ocr_processor.initialize()
    
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Process the document
    result = await ocr_processor.process_document(sample_pdf_path)
    
    # Verify the result
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Test Document" in result

@pytest.mark.asyncio
async def test_process_document_nonexistent(ocr_processor, tmp_path):
    """Test processing a non-existent document raises an error."""
    await ocr_processor.initialize()
    non_existent = tmp_path / "nonexistent.pdf"
    
    with pytest.raises(FileNotFoundError):
        await ocr_processor.process_document(non_existent)
