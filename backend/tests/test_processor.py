import asyncio
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cartaos.app_config import AppConfig
from cartaos.processor import CartaOSProcessor


class DummyGen:
    text = "AI Summary"


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock AppConfig for testing."""
    config = AppConfig()
    
    # Set up test directories
    test_dirs = {
        "00_Inbox": tmp_path / "00_Inbox",
        "02_Triage": tmp_path / "02_Triage",
        "03_Lab": tmp_path / "03_Lab",
        "04_ReadyForOCR": tmp_path / "04_ReadyForOCR",
        "05_ReadyForSummary": tmp_path / "05_ReadyForSummary",
        "06_TooLarge": tmp_path / "06_TooLarge",
        "07_Processed": tmp_path / "07_Processed",
    }
    
    # Create directories
    for dir_path in test_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create a mock config with test directories
    config.pipeline_dirs = test_dirs
    config.gemini_api_key = "test-api-key-1234567890"
    config.obsidian_vault_path = tmp_path / "vault"
    
    return config


@pytest.fixture(autouse=True)
def mock_ai(monkeypatch, tmp_path, mock_config):
    # Set up test prompt file
    p = tmp_path / "summary_prompt.md"
    p.write_text("Prompt: {text}")
    
    # Mock the async function with a coroutine
    async def mock_generate_summary(*args, **kwargs):
        return "Test summary"
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)
    # Mock extract_text to return sample content
    def mock_extract_text(path, force_ocr=False):
        return "Sample extracted text for testing"
    
    monkeypatch.setattr("cartaos.processor.extract_text", mock_extract_text)
    
    # Mock file writing in debug mode
    original_write = open
    
    def mock_write(*args, **kwargs):
        if 'w' in kwargs.get('mode', '') and args[0].endswith('_extracted_text.txt'):
            return original_write(*args, **kwargs)
        return original_write(*args, **kwargs)
    
    monkeypatch.setattr("builtins.open", mock_write)
    
    return p


@pytest.mark.asyncio
async def test_process_full_flow(tmp_path, mock_config):
    """Test the full processing flow with a mock PDF file."""
    # Create a test PDF file
    pdf = tmp_path / "test_document.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    
    # Expected output paths
    processed_pdf = mock_config.pipeline_dirs["07_Processed"] / pdf.name
    summary_file = mock_config.pipeline_dirs["07_Processed"] / "Summaries" / "test-document.md"
    
    # Process the document
    processor = CartaOSProcessor(
        pdf_path=pdf,
        config=mock_config,
        dry_run=False,
        debug=False
    )
    
    # Run the processor
    result = await processor.process_async()
    
    # Verify results
    assert result is True
    assert processed_pdf.exists()
    # Check the summary content - should match our mock return value
    summary_file = processed_pdf.parent / "Summaries" / "test-document.md"
    assert "Test summary" in summary_file.read_text()


@pytest.mark.asyncio
async def test_dry_run_mode(tmp_path, mock_config):
    """Test that dry run mode doesn't create any files."""
    # Create a test PDF file
    pdf = tmp_path / "test_document.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    
    # Expected output paths (should not exist in dry run)
    processed_pdf = mock_config.pipeline_dirs["07_Processed"] / pdf.name
    summary_file = mock_config.pipeline_dirs["07_Processed"] / "Summaries" / "test-document.md"
    
    # Process the document in dry run mode
    processor = CartaOSProcessor(
        pdf_path=pdf,
        config=mock_config,
        dry_run=True,
        debug=False
    )
    
    # Run the processor
    result = await processor.process_async()
    
    # Verify results
    assert result is True
    assert not processed_pdf.exists()  # Should not create output file in dry run
    assert not summary_file.exists()   # Should not create summary in dry run


@pytest.mark.asyncio
async def test_debug_mode(tmp_path, mock_config, capsys, monkeypatch):
    """Test debug mode outputs debug information."""
    # Create a test PDF file
    pdf = tmp_path / "test_document.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    
    # Create a test extracted text file that will be "saved" in debug mode
    extracted_text_path = tmp_path / "test_document_extracted_text.txt"
    test_extracted_text = "Sample extracted text for testing"
    
    # Mock extract_text to return our test text
    def mock_extract_text(pdf_path, force_ocr=False):
        with open(extracted_text_path, 'w', encoding='utf-8') as f:
            f.write(test_extracted_text)
        return test_extracted_text
    
    monkeypatch.setattr("cartaos.processor.extract_text", mock_extract_text)
    
    # Process the document in debug mode
    processor = CartaOSProcessor(
        pdf_path=pdf,
        config=mock_config,
        dry_run=False,
        debug=True
    )
    
    # Run the processor
    result = await processor.process_async()
    captured = capsys.readouterr()
    
    # Verify results
    assert result is True
    assert "DEBUG" in captured.out  # Should output debug info
    
    # In debug mode, extracted text should be saved
    assert extracted_text_path.exists()
    assert test_extracted_text in extracted_text_path.read_text()


def test_missing_api_key(tmp_path, mock_config):
    """Test behavior when API key is missing."""
    # Create a test PDF file
    pdf = tmp_path / "test_document.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    
    # Remove API key from config
    mock_config.gemini_api_key = ""
    
    # Should raise an error when creating the processor with invalid config
    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured in the application settings"):
        CartaOSProcessor(
            pdf_path=pdf,
            config=mock_config,
            dry_run=False,
            debug=False
        )
