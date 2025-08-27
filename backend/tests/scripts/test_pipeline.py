"""
Tests for the document processing pipeline.
"""
import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cartaos.processor import CartaOSProcessor
from cartaos.processors.ocr_processor import OcrProcessor

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a test directory with sample files."""
    # Create test files
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    
    # Create test PDF files
    pdf_files = [
        ("simple_text.pdf", "This is a simple PDF with text content for testing."),
        ("special_chars.pdf", "Special chars: áéíóúñ¿?¡!@#$%^&*()"),
        ("large_document.pdf", "Large document content. " * 1000)
    ]
    
    for filename, content in pdf_files:
        create_test_pdf(test_dir / filename, content)
    
    # Create a text file (should fail processing)
    with open(test_dir / "test_document.txt", 'w', encoding='utf-8') as f:
        f.write("This is a plain text file, not a PDF.")
    
    return test_dir

@pytest.fixture
def processed_dir(tmp_path):
    """Create a processed directory for testing."""
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    return processed_dir

@pytest.fixture
def summary_dir(processed_dir):
    """Create a summary directory for testing."""
    summary_dir = processed_dir / "summaries"
    summary_dir.mkdir()
    return summary_dir

def create_test_pdf(path: Path, content: str = "Test Document") -> None:
    """Create a test PDF file with the given content."""
    with open(path, "wb") as f:
        f.write(f"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n({content}) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000105 00000 n \n0000000179 00000 n \ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n233\n%%EOF".encode())

@pytest.mark.asyncio
async def test_process_pdf(test_data_dir, processed_dir, summary_dir):
    """Test processing a PDF file through the pipeline."""
    pdf_file = test_data_dir / "simple_text.pdf"
    
    # Initialize the processor
    processor = CartaOSProcessor(
        pdf_path=pdf_file,
        debug=True,
        dry_run=False
    )
    
    # Set custom output directories
    processor.processed_pdf_dir = processed_dir
    processor.summary_dir = summary_dir
    
    # Process the document
    result = processor.process()
    
    # Verify the results
    assert result is True
    
    # Check if output files were created
    processed_pdf = processed_dir / pdf_file.name
    assert processed_pdf.exists()
    
    # Check if summary was created
    summary_file = summary_dir / "simple-text.md"
    assert summary_file.exists()
    
    # Verify summary content
    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert len(content) > 0
        assert "This is a simple PDF with text content for testing" in content

@pytest.mark.asyncio
async def test_process_special_chars(test_data_dir, processed_dir, summary_dir):
    """Test processing a PDF with special characters."""
    pdf_file = test_data_dir / "special_chars.pdf"
    
    processor = CartaOSProcessor(
        pdf_path=pdf_file,
        debug=True,
        dry_run=False
    )
    processor.processed_pdf_dir = processed_dir
    processor.summary_dir = summary_dir
    
    result = processor.process()
    assert result is True
    
    # Verify special characters were preserved
    summary_file = summary_dir / "special-chars.md"
    assert summary_file.exists()
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "áéíóúñ¿?¡!@#" in content

@pytest.mark.asyncio
async def test_process_large_document(test_data_dir, processed_dir, summary_dir):
    """Test processing a large PDF document."""
    pdf_file = test_data_dir / "large_document.pdf"
    
    processor = CartaOSProcessor(
        pdf_path=pdf_file,
        debug=True,
        dry_run=False
    )
    processor.processed_pdf_dir = processed_dir
    processor.summary_dir = summary_dir
    
    result = processor.process()
    assert result is True
    
    # Verify large document was processed
    summary_file = summary_dir / "large-document.md"
    assert summary_file.exists()
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert len(content) > 100  # Should have significant content

@pytest.mark.asyncio
async def test_process_invalid_file(test_data_dir):
    """Test processing an invalid/non-PDF file."""
    txt_file = test_data_dir / "test_document.txt"
    
    processor = CartaOSProcessor(
        pdf_path=txt_file,
        debug=True,
        dry_run=False
    )
    
    # Should raise an exception for non-PDF files
    with pytest.raises(ValueError):
        processor.process()

@pytest.mark.asyncio
async def test_non_debug_mode(test_data_dir, processed_dir, summary_dir):
    """Test processing in non-debug mode."""
    pdf_file = test_data_dir / "simple_text.pdf"
    
    processor = CartaOSProcessor(
        pdf_path=pdf_file,
        debug=False,  # Non-debug mode
        dry_run=False
    )
    processor.processed_pdf_dir = processed_dir
    processor.summary_dir = summary_dir
    
    result = processor.process()
    assert result is True
    
    # In non-debug mode, the original file should be moved
    assert not pdf_file.exists()
    assert (processed_dir / pdf_file.name).exists()
    assert (summary_dir / "simple-text.md").exists()

@pytest.mark.asyncio
async def test_corrupted_pdf_handling(test_data_dir, processed_dir, summary_dir):
    """Test handling of corrupted PDF files."""
    # Create a corrupted PDF file
    corrupted_pdf = test_data_dir / "corrupted.pdf"
    with open(corrupted_pdf, 'wb') as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Corrupted PDF) Tj\nET\nendstream\nendobj\n%%EOF")
    
    processor = CartaOSProcessor(
        pdf_path=corrupted_pdf,
        debug=True,
        dry_run=False
    )
    processor.processed_pdf_dir = processed_dir
    processor.summary_dir = summary_dir
    
    # Should raise an exception for corrupted PDF
    with pytest.raises(Exception):
        processor.process()
    
    # Verify error handling (file should be moved to error directory)
    error_dir = processed_dir.parent / "error"
    assert (error_dir / corrupted_pdf.name).exists()

@pytest.mark.asyncio
async def test_dry_run_mode(test_data_dir, processed_dir, summary_dir):
    """Test processing in dry-run mode (no files should be modified)."""
    pdf_file = test_data_dir / "simple_text.pdf"
    original_size = pdf_file.stat().st_size
    
    processor = CartaOSProcessor(
        pdf_path=pdf_file,
        debug=True,
        dry_run=True  # Dry run mode
    )
    processor.processed_pdf_dir = processed_dir
    processor.summary_dir = summary_dir
    
    result = processor.process()
    assert result is True  # Should still return success in dry-run mode
    
    # In dry-run mode, no files should be moved or created
    assert pdf_file.exists()  # Original file should still exist
    assert not (processed_dir / pdf_file.name).exists()
    assert not (summary_dir / "simple-text.md").exists()
    assert pdf_file.stat().st_size == original_size  # File should be unchanged

@pytest.mark.asyncio
async def test_ocr_processor_integration(test_data_dir, tmp_path):
    """Test integration with the OCR processor."""
    # Create a test PDF with some text
    pdf_file = test_data_dir / "ocr_test.pdf"
    test_text = "This is a test PDF for OCR processing"
    create_test_pdf(pdf_file, test_text)
    
    # Initialize the OCR processor
    processor = OcrProcessor()
    
    # Process the document
    result = await processor.process_document(pdf_file)
    
    # Verify the results
    assert result is not None
    assert test_text in result["text"]
    assert result["page_count"] == 1
    
    # Test with a non-existent file
    non_existent = test_data_dir / "nonexistent.pdf"
    with pytest.raises(FileNotFoundError):
        await processor.process_document(non_existent)
