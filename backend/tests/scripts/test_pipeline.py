"""
Tests for the document processing pipeline.
"""
import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
from cartaos.processor import CartaOSProcessor
from cartaos.processors.ocr_processor import OcrProcessor
from google.genai.types import GenerateContentResponse, Content, Part
from slugify import slugify

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary test data directory with sample PDFs."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    
    # Create a simple PDF file
    create_test_pdf(test_dir / "simple_text.pdf", "This is a simple PDF with text content for testing.")
    
    # Create a PDF with special characters
    create_test_pdf(test_dir / "special_chars.pdf", "Special chars: áéíóúñ¿?¡!@#$%^&*()")
    
    # Create a large PDF file
    large_text = "Large document content. " * 1000
    create_test_pdf(test_dir / "large_document.pdf", large_text)
    
    # Create a text file (not a PDF)
    (test_dir / "test_document.txt").write_text("This is a plain text file, not a PDF.")
    
    # Create a test directory for OCR tests
    ocr_dir = test_dir / "ocr_test"
    ocr_dir.mkdir()
    create_test_pdf(ocr_dir / "test_ocr.pdf", "This is a test PDF for OCR processing")
    
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

def create_mock_response(text: str = "Mocked summary"):
    """Helper to create a mock response from the Gemini API."""
    return GenerateContentResponse(
        candidates=[
            {
                'content': {
                    'parts': [
                        {'text': text}
                    ]
                }
            }
        ]
    )

@pytest.mark.asyncio
async def test_process_pdf(tmp_path, monkeypatch):
    """Test processing a valid PDF file."""
    # Create a test PDF file
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Simple PDF) Tj\nET\nendstream\nendobj\n%%EOF")

    # Mock the async function with a coroutine
    async def mock_generate_summary(*args, **kwargs):
        return "Test summary"
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)

    # Create a test PDF file
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Simple PDF) Tj\nET\nendstream\nendobj\n%%EOF")

    # Create the processor
    processor = CartaOSProcessor(
        pdf_path=pdf_file,
        debug=True,
        dry_run=False
    )

    # Run the processor with asyncio
    result = await processor.process_async()
    assert result is True, "Processor should complete successfully"

@pytest.mark.asyncio
@patch('cartaos.processor.generate_summary_with_retries')
@patch('cartaos.processor.extract_text')
@patch('shutil.move')
async def test_process_pdf(mock_move, mock_extract_text, mock_generate_summary, test_data_dir, processed_dir, summary_dir, monkeypatch):
    """Test processing a simple PDF with text content."""
    # Mock the async function to return a test summary
    mock_generate_summary.return_value = "Test summary"
    # Mock extract_text to return test data
    mock_extract_text.return_value = "This is a simple PDF with text content for testing."
    # Track file movements
    moved_files = []
    
    def move_side_effect(src, dst):
        moved_files.append((src, dst))
        # Create the destination directory if it doesn't exist
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        # Create an empty file at the destination to simulate the move
        Path(dst).touch()
        return dst
        
    mock_move.side_effect = move_side_effect
    
    # Mock extract_text to include force_ocr parameter and return just the text
    test_text = "This is a simple PDF with text content for testing."
    
    def mock_extract_text(pdf_path, force_ocr=False):
        return test_text
    
    monkeypatch.setattr("cartaos.processor.extract_text", mock_extract_text)
    
    # Create a test PDF file
    pdf_file = test_data_dir / "simple_text.pdf"
    with open(pdf_file, 'wb') as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Simple PDF) Tj\nET\nendstream\nendobj\n%%EOF")
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}, clear=True):
        # Create the summary directory
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        processor = CartaOSProcessor(
            pdf_path=pdf_file,
            debug=True,
            dry_run=False
        )
        processor.processed_pdf_dir = processed_dir
        processor.summary_dir = summary_dir
        
        # Track written files
        written_files = []
        original_write = Path.write_text
        
        def mock_write(self, content, *args, **kwargs):
            written_files.append((str(self), content))
            # Create parent directories if they don't exist
            self.parent.mkdir(parents=True, exist_ok=True)
            return original_write(self, content, *args, **kwargs)
            
        monkeypatch.setattr(Path, 'write_text', mock_write)
        
        # In debug mode, we expect the processor to return early after saving the extracted text
        # and not move any files or generate a summary
        result = await processor.process_async()
        
        # Verify the result
        assert result is True, "Processing should complete successfully in debug mode"
        
        # In debug mode, no files should be moved
        assert len(moved_files) == 0, "No files should be moved in debug mode"
        
        # In debug mode, no summary should be generated
        assert len(written_files) == 0, "No summary should be written in debug mode"
        
        # Verify the debug output file was created
        debug_text_path = pdf_file.with_suffix(".txt")
        assert debug_text_path.exists(), "Debug text file was not created"
        assert debug_text_path.read_text() == test_text, "Debug text file content does not match"
        
        # Clean up the debug file
        debug_text_path.unlink()
        
        # In debug mode, generate_summary should not be called
        mock_generate_summary.assert_not_called()

@pytest.mark.asyncio
@patch('cartaos.utils.ai_utils.generate_summary')
@patch('shutil.move')
async def test_process_special_chars(mock_move, mock_generate_summary, test_data_dir, processed_dir, summary_dir, monkeypatch):
    """Test processing a PDF with special characters."""
    # Mock the generate_summary function
    special_chars = "áéíóúñ¿?¡!@#"
    mock_generate_summary.return_value = f"Mocked summary with special chars {special_chars}"
    
    # Track file movements
    moved_files = []
    
    def move_side_effect(src, dst):
        moved_files.append((src, dst))
        return None
        
    mock_move.side_effect = move_side_effect
    
    # Mock extract_text to include force_ocr parameter and return just the text
    def mock_extract_text(pdf_path, force_ocr=False):
        return f"Special characters: {special_chars}"
    
    monkeypatch.setattr("cartaos.processor.extract_text", mock_extract_text)
    
    # Create a test PDF file with special characters in the name
    pdf_file = test_data_dir / "special_chars_áéíóúñ.pdf"
    with open(pdf_file, 'wb') as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Special Chars) Tj\nET\nendstream\nendobj\n%%EOF")
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}, clear=True):
        # Create the summary directory
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        processor = CartaOSProcessor(
            pdf_path=pdf_file,
            debug=True,
            dry_run=False
        )
        processor.processed_pdf_dir = processed_dir
        processor.summary_dir = summary_dir
        
        # Track written files
        written_files = []
        original_write = Path.write_text
        
        def mock_write(self, content, *args, **kwargs):
            written_files.append((str(self), content))
            return original_write(self, content, *args, **kwargs)
            
        monkeypatch.setattr(Path, 'write_text', mock_write)
        
        # Process the PDF in debug mode
        result = await processor.process_async()
        
        # Verify the result
        assert result is True, "Processing should complete successfully in debug mode"
        
        # In debug mode, no files should be moved
        assert len(moved_files) == 0, "No files should be moved in debug mode"
        
        # In debug mode, no summary should be generated
        assert len(written_files) == 0, "No summary should be written in debug mode"
        
        # Verify the debug output file was created
        debug_text_path = pdf_file.with_suffix(".txt")
        assert debug_text_path.exists(), "Debug text file was not created"
        assert debug_text_path.read_text() == f"Special characters: {special_chars}", "Debug text file content does not match"
        
        # Clean up the debug file
        debug_text_path.unlink()
        
        # In debug mode, generate_summary should not be called
        mock_generate_summary.assert_not_called()

@pytest.mark.asyncio
@patch('cartaos.utils.ai_utils.generate_summary')
@patch('shutil.move')
async def test_process_large_document(mock_move, mock_generate_summary, test_data_dir, processed_dir, summary_dir, monkeypatch):
    """Test processing a large PDF document."""
    # Mock the generate_summary function
    mock_generate_summary.return_value = "Mocked large document summary"
    
    # Track file movements
    moved_files = []
    
    def move_side_effect(src, dst):
        moved_files.append((src, dst))
        return None
        
    mock_move.side_effect = move_side_effect
    
    # Mock extract_text to include force_ocr parameter and return just the text
    large_text = "Large document content. " * 1000
    
    def mock_extract_text(pdf_path, force_ocr=False):
        return large_text
    
    monkeypatch.setattr("cartaos.processor.extract_text", mock_extract_text)
    
    # Create a test PDF file for large document
    pdf_file = test_data_dir / "large_document.pdf"
    with open(pdf_file, 'wb') as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Large Document) Tj\nET\nendstream\nendobj\n%%EOF")
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}, clear=True):
        # Create the summary directory
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        processor = CartaOSProcessor(
            pdf_path=pdf_file,
            debug=True,
            dry_run=False
        )
        processor.processed_pdf_dir = processed_dir
        processor.summary_dir = summary_dir
        
        # Track written files

@pytest.mark.asyncio
@patch('cartaos.processor.extract_text')
@patch('shutil.move')
async def test_process_invalid_file(mock_move, mock_extract_text, test_data_dir, processed_dir, summary_dir):
    """Test processing an invalid/non-PDF file."""
    # Mock extract_text to return None for non-PDF files
    mock_extract_text.return_value = None
    
    # Track file movements
    moved_files = []
    
    def move_side_effect(src, dst):
        moved_files.append((src, dst))
        # Create the destination directory if it doesn't exist
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        # Create an empty file at the destination to simulate the move
        Path(dst).touch()
        return dst
        
    mock_move.side_effect = move_side_effect
    
    # Create a non-PDF file
    invalid_file = test_data_dir / "not_a_pdf.txt"
    with open(invalid_file, 'w') as f:
        f.write("This is not a PDF file")
    
    # Create the processor - this should not raise an error
    processor = CartaOSProcessor(
        pdf_path=invalid_file,
        debug=True,
        dry_run=False
    )
    
    # Process the file - should return False due to extraction failure
    result = await processor.process_async()
    assert result is False, "Processing should fail for non-PDF files"
    
    # Verify extract_text was called
    mock_extract_text.assert_called_once()
    
    # Verify no files were moved (since processing failed)
    assert len(moved_files) == 0, "No files should be moved if processing fails"

@pytest.mark.asyncio
@patch('cartaos.processor.generate_summary_with_retries')
@patch('cartaos.processor.extract_text')
@patch('shutil.move')
async def test_non_debug_mode(mock_move, mock_extract_text, mock_generate_summary, test_data_dir, processed_dir, summary_dir, monkeypatch):
    """Test processing in non-debug mode."""
    # Set up mock return values
    test_summary = "Mocked summary for non-debug mode"
    mock_generate_summary.return_value = test_summary
    mock_extract_text.return_value = "This is a simple PDF with text content for testing."
    
    # Track file movements
    moved_files = []
    
    def move_side_effect(src, dst):
        moved_files.append((src, dst))
        # Don't actually move files during test
        return None
        
    mock_move.side_effect = move_side_effect
    
    # Mock extract_text to include force_ocr parameter and return just the text
    def mock_extract_text(pdf_path, force_ocr=False):
        return "This is a simple PDF with text content for testing."
    
    monkeypatch.setattr("cartaos.processor.extract_text", mock_extract_text)
    
    # Create a test PDF file
    pdf_file = test_data_dir / "simple_text.pdf"
    with open(pdf_file, 'wb') as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Simple PDF) Tj\nET\nendstream\nendobj\n%%EOF")
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}, clear=True):
        # Create the summary directory
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        processor = CartaOSProcessor(
            pdf_path=pdf_file,
            debug=False,  # Non-debug mode
            dry_run=False
        )
        processor.processed_pdf_dir = processed_dir
        processor.summary_dir = summary_dir
        
        # Track written files
        written_files = []
        
        # Create a function to track file writes
        def track_writes(func):
            def wrapper(path, *args, **kwargs):
                # Only track writes to summary files
                if str(path).endswith('.md') and 'summary' in str(path).lower():
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(test_summary)
                    written_files.append((str(path), test_summary))
                return func(path, *args, **kwargs)
            return wrapper
        
        # Apply the tracking to Path.write_text
        original_write = Path.write_text
        monkeypatch.setattr(Path, 'write_text', track_writes(original_write))
        
        # Also patch the _save_summary method to track its calls
        original_save_summary = processor._save_summary
        def mock_save_summary(self, summary_content):
            # Create the summary file
            safe_name = slugify(self.pdf_path.stem)
            summary_file = self.summary_dir / f"{safe_name}.md"
            summary_file.parent.mkdir(parents=True, exist_ok=True)
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            written_files.append((str(summary_file), summary_content))
            # Call the original method with just summary_content (self is already bound)
            return original_save_summary(summary_content)
            
        monkeypatch.setattr(CartaOSProcessor, '_save_summary', mock_save_summary)
        
        # Run the processor
        result = await processor.process_async()
        assert result is True, "Processor should complete successfully"
    
        # In non-debug mode, the file should be moved to processed dir
        assert len(moved_files) > 0, f"No files were moved. Moved files: {moved_files}"
        assert any("processed" in str(dst).lower() and 
                  pdf_file.name in str(dst) 
                  for src, dst in moved_files), \
                  f"PDF file was not moved to processed directory. Moved files: {moved_files}"
        
        # Summary should be generated in non-debug mode
        assert len(written_files) > 0, f"No summary files were written. Written files: {written_files}"
        assert any("summaries" in str(Path(path).parent).lower() and
                  path.endswith(".md") and
                  test_summary in content
              for path, content in written_files), \
              f"Summary file does not contain expected content. Written files: {written_files}"

@pytest.mark.asyncio
@patch('cartaos.processor.generate_summary_with_retries')
@patch('shutil.move')
async def test_corrupted_pdf_handling(mock_move, mock_generate_summary, test_data_dir, processed_dir, summary_dir, monkeypatch):
    """Test handling of corrupted PDF files."""
    # Mock the generate_summary function (shouldn't be called in this case)
    mock_generate_summary.return_value = "Mocked summary"
    
    # Track file movements
    moved_files = []
    
    def move_side_effect(src, dst):
        moved_files.append((src, dst))
        # Create the destination directory if it doesn't exist
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        # Create an empty file at the destination to simulate the move
        Path(dst).touch()
        return dst
    
    mock_move.side_effect = move_side_effect
    
    # Track if extract_text was called
    extract_called = False
    
    # Mock extract_text to raise an exception
    def mock_extract_text(pdf_path, force_ocr=False):
        nonlocal extract_called
        extract_called = True
        if not str(pdf_path).endswith('.pdf'):
            raise ValueError("File must be a PDF")
        raise Exception("Invalid PDF: PDF header signature not found")
    
    monkeypatch.setattr("cartaos.processor.extract_text", mock_extract_text)
    
    # Create a corrupted PDF file
    corrupted_pdf = test_data_dir / "corrupted.pdf"
    with open(corrupted_pdf, 'wb') as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Corrupted PDF) Tj\nET\nendstream\nendobj\n%%EOF")
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}, clear=True):
        # Create the error directory in advance
        error_dir = processed_dir.parent / "error"
        error_dir.mkdir(parents=True, exist_ok=True)
        
        processor = CartaOSProcessor(
            pdf_path=corrupted_pdf,
            debug=True,
            dry_run=False
        )
        processor.processed_pdf_dir = processed_dir
        processor.summary_dir = summary_dir
        
        # The error should be caught and logged, but the test should continue
        result = await processor.process_async()
        
        # Verify extract_text was called
        assert extract_called, "extract_text should have been called"
        
        # Verify the error was handled
        assert result is False, "Should return False on error"
        
        # Verify the file was not moved (current implementation doesn't move files on error)
        assert len(moved_files) == 0, "Files should not be moved on error"
        
        # Verify generate_summary was never called
        mock_generate_summary.assert_not_called()

@pytest.mark.asyncio
@patch('cartaos.processor.generate_summary_with_retries')
@patch('cartaos.processor.extract_text')
@patch('shutil.move')
async def test_dry_run_mode(mock_move, mock_extract_text, mock_generate_summary, test_data_dir, processed_dir, summary_dir, monkeypatch):
    """Test processing in dry-run mode (no files should be modified)."""
    # Mock the async function to return a test summary
    mock_generate_summary.return_value = "Test summary"
    # Mock extract_text to return test data
    # Mock extract_text to return test data
    mock_extract_text.return_value = "This is a simple PDF with text content for testing."
    
    # Track operations
    operations = []
    
    # Track file operations
    def move_side_effect(src, dst):
        operations.append(('move', str(src), str(dst)))
        # In dry-run mode, this should never actually be called
        assert False, "shutil.move should not be called in dry-run mode"
        
    mock_move.side_effect = move_side_effect
    
    # Track written files
    written_files = []
    
    def mock_write(self, *args, **kwargs):
        written_files.append((str(self), args[0] if args else None))
        # In dry-run mode, this should never actually be called
        assert False, "write_text should not be called in dry-run mode"
        
    monkeypatch.setattr(Path, 'write_text', mock_write)
    
    # Create a test PDF file
    pdf_file = test_data_dir / "dry_run_test.pdf"
    with open(pdf_file, 'wb') as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Dry Run Test) Tj\nET\nendstream\nendobj\n%%EOF")
    
    original_size = pdf_file.stat().st_size
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}, clear=True):
        # Create the summary directory
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        # Set debug=False to ensure we test the full pipeline including generate_summary
        processor = CartaOSProcessor(
            pdf_path=pdf_file,
            debug=False,  # Disable debug to test full pipeline
            dry_run=True  # Enable dry-run mode
        )
        processor.processed_pdf_dir = processed_dir
        processor.summary_dir = summary_dir
        
        # Process the file in dry-run mode
        result = await processor.process_async()
        
        # Verify the result
        assert result is True, "Processing should complete successfully in dry-run mode"
        
        # Verify extract_text was called with the correct parameters
        mock_extract_text.assert_called_once_with(pdf_file, force_ocr=False)
        
        # Verify no files were actually moved or written
        assert not any(op[0] == 'move' for op in operations), "No files should be moved in dry-run mode"
        assert len(written_files) == 0, "No files should be written in dry-run mode"
        
        # Verify the original file still exists and wasn't modified
        assert pdf_file.exists(), "Original file should not be modified in dry-run mode"
        assert pdf_file.stat().st_size == original_size, "Original file size should not change in dry-run mode"
        
        # Verify generate_summary was called (since we still want to test the logic)
        mock_generate_summary.assert_called_once()
        
        # Get the actual call arguments
        args, kwargs = mock_generate_summary.call_args
        
        # Verify the call was made with the expected text
        assert len(args) > 0, "generate_summary should be called with at least one argument"
        assert args[0] == "This is a simple PDF with text content for testing.", "Extracted text should be passed to generate_summary"
        
        # Verify no file operations were actually performed
        assert not any(op[0] in ('move', 'write') for op in operations)

@pytest.mark.asyncio
async def test_ocr_processor_integration(test_data_dir, tmp_path, monkeypatch):
    """Test integration with the OCR processor."""
    # Mock extract_text to return just the text content
    test_text = "This is a test PDF for OCR processing"
    monkeypatch.setattr(
        "cartaos.processor.extract_text",
        lambda p, force_ocr=False: test_text if force_ocr else ""
    )
    
    # Mock the async function with a coroutine that returns None to simulate failure
    async def mock_generate_summary_none(*args, **kwargs):
        return None
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary_none)
    
    # Create a test PDF with some text
    pdf_file = test_data_dir / "ocr_test.pdf"
    create_test_pdf(pdf_file, test_text)
    
    # Initialize the OCR processor
    processor = OcrProcessor()
    
    # Process the document
    result = await processor.process_document(pdf_file)
    
    # Verify the results (result should be a string containing the extracted text)
    assert result is not None
    assert isinstance(result, str)
    assert test_text in result
    
    # Test with a non-existent file
    non_existent = test_data_dir / "nonexistent.pdf"
    with pytest.raises(FileNotFoundError):
        await processor.process_document(non_existent)
