"""
Tests for the CartaOSProcessor class.

The CartaOSProcessor class is the main entry point for processing a PDF file.
It encapsulates the entire process of generating a summary for a PDF file,
including OCR, text extraction, AI summarization, and saving the summary.

The class has several methods that can be used to customize the processing:
- `load_config`: Loads environment configurations from the .env file.
- `configure_api`: Configures the API key for the Gemini AI model.
- `extract_text`: Extracts full text from the PDF file using multiple methods for robustness.
- `generate_summary`: Generates the analytical summary using the Gemini API.
- `save_summary`: Saves the generated summary to a file.
- `move_pdf`: Moves the processed PDF file to a designated directory.

The `process` method is the main entry point for processing a PDF file. It
calls the above methods in sequence to generate a summary for the PDF file.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from cartaos.processor import CartaOSProcessor


@pytest.fixture
def processor():
    """
    Creates a CartaOSProcessor instance with default settings.
    """
    return CartaOSProcessor(pdf_path="test.pdf", dry_run=False, debug=False, force_ocr=False)


def test_init(processor):
    """
    Tests that the CartaOSProcessor instance is initialized correctly.
    """
    assert processor.pdf_path == Path("test.pdf")
    assert not processor.dry_run
    assert not processor.debug
    assert not processor.force_ocr


@patch("cartaos.processor.load_dotenv")
@patch("cartaos.processor.os.getenv", return_value="dummy_key")
def test_load_config(mock_getenv, mock_load_dotenv, processor):
    """
    Tests that the CartaOSProcessor instance loads the environment configurations correctly.
    """
    processor.load_config()
    mock_load_dotenv.assert_called_once()
    assert processor.api_key == "dummy_key"


@patch("cartaos.processor.genai.configure")
def test_configure_api(mock_configure, processor):
    """
    Tests that the CartaOSProcessor instance configures the API key for the Gemini AI model correctly.
    """
    processor.api_key = "dummy_key"
    processor.configure_api()
    mock_configure.assert_called_once_with(api_key="dummy_key")


@patch("cartaos.processor.pdfplumber.open")
def test_extract_text_pdfplumber(mock_pdfplumber_open, processor):
    """
    Tests that the CartaOSProcessor instance extracts text from a PDF file using pdfplumber correctly.
    """
    mock_pdf = MagicMock()
    mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf
    mock_pdf.pages = [MagicMock(extract_text=MagicMock(return_value="Sample text."))]
    assert processor.extract_text() == "Sample text."


@patch("cartaos.processor.fitz.open")
def test_extract_text_fitz(mock_fitz_open, processor):
    """
    Tests that the CartaOSProcessor instance extracts text from a PDF file using PyMuPDF correctly.
    """
    mock_doc = MagicMock()
    mock_fitz_open.return_value.__enter__.return_value = mock_doc
    mock_doc.pages = [MagicMock(get_text=MagicMock(return_value="Sample text."))]
    assert processor.extract_text() == "Sample text."


@patch("cartaos.processor.genai.GenerativeModel")
@patch("builtins.open", new_callable=pytest.mock.patch, autospec=True)
def test_generate_summary_full(mock_open, mock_generative_model, processor, tmp_path):
    """
    Testa generate_summary com:
    - Leitura do prompt
    - Instanciação de GenerativeModel
    - Chamada a generate_content com o prompt formatado
    """
    # Prepare prompt file
    prompt_file = tmp_path / "summary_prompt.md"
    prompt_file.write_text("Prompt template: {text}")
    
    # Force the processor to use our temp prompt
    processor_prompt_dir = Path(processor.__module__).parent / "prompts"
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("PROMPT_DIR", str(tmp_path))
    monkeypatch.setattr(processor, "generate_summary.__globals__", {"Path": Path, "__file__": str(tmp_path / "dummy.py")})
    
    # Mock the model
    mock_model = MagicMock()
    mock_generative_model.return_value = mock_model
    mock_response = MagicMock()
    mock_response.text = "AI Summary"
    mock_response.parts = ["part1", "part2"]
    mock_model.generate_content.return_value = mock_response

    # Call
    summary = processor.generate_summary("Test text")

    # Verify
    mock_generative_model.assert_called_once_with("models/gemini-2.5-pro")
    mock_model.generate_content.assert_called_once()
    assert summary == "AI Summary"



@patch("cartaos.processor.Path.write_text")
def test_save_summary(mock_write_text, processor):
    """
    Tests that the CartaOSProcessor instance saves the generated summary to a file correctly.
    """
    processor._save_summary("Summary content.")
    mock_write_text.assert_called_once()


@patch("cartaos.processor.shutil.move")
def test_move_pdf(mock_move, processor):
    """
    Tests that the CartaOSProcessor instance moves the processed PDF file to a designated directory correctly.
    """
    processor._move_pdf()
    mock_move.assert_called_once()


@patch("cartaos.processor.CartaOSProcessor.extract_text", return_value="Sample text.")
@patch("cartaos.processor.CartaOSProcessor.generate_summary", return_value="Summary")
@patch("cartaos.processor.CartaOSProcessor._save_summary")
@patch("cartaos.processor.CartaOSProcessor._move_pdf")
def test_process(mock_move_pdf, mock_save_summary, mock_generate_summary, mock_extract_text, processor):
    """
    Tests that the CartaOSProcessor instance processes a PDF file correctly.
    """
    result = processor.process()
    assert result
    mock_extract_text.assert_called_once()
    mock_generate_summary.assert_called_once()
    mock_save_summary.assert_called_once()
    mock_move_pdf.assert_called_once()

