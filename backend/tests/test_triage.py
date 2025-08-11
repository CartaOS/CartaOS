# backend/tests/test_triage.py

import pytest
from pathlib import Path
import os
from unittest.mock import patch

from cartaos.triage import TriageProcessor

# Pytest fixture to create a temporary input directory
@pytest.fixture
def input_dir(tmp_path):
    """Creates a temporary input directory for testing."""
    dir_path = tmp_path / "input"
    dir_path.mkdir()
    return dir_path

# Pytest fixture to create a temporary summary directory
@pytest.fixture
def summary_dir(tmp_path):
    """Creates a temporary directory for files ready for summary."""
    dir_path = tmp_path / "summary"
    dir_path.mkdir()
    return dir_path

# Pytest fixture to create a temporary lab directory
@pytest.fixture
def lab_dir(tmp_path):
    """Creates a temporary directory for files needing correction."""
    dir_path = tmp_path / "lab"
    dir_path.mkdir()
    return dir_path

def test_triage_moves_files_based_on_content(input_dir, summary_dir, lab_dir):
    """
    Tests if the triage processor correctly moves different file types
    to their respective destination directories.
    """
    # --- 1. Setup: Create dummy files to simulate a real scenario ---
    
    # This PDF simulates a document with a good text layer.
    # It should be moved to the "summary" directory.
    (input_dir / "document_with_text.pdf").touch()

    # This PDF simulates a scanned document (image-based).
    # It should be moved to the "lab" directory for OCR.
    (input_dir / "document_as_image.pdf").touch()

    # Ebooks should go directly to the "summary" directory.
    (input_dir / "my_great_book.epub").touch()

    # Unsupported files should be ignored and remain in the input directory.
    (input_dir / "notes.txt").touch()

    # --- 2. Mocking: Control external dependencies ---
    
    # We use 'patch' to "pretend" what `_pdf_has_sufficient_text` returns.
    # This isolates our test to only the logic of the `process` method,
    # without needing to actually read PDF files.
    with patch.object(TriageProcessor, '_pdf_has_sufficient_text') as mock_pdf_check:
        # Define the behavior of the mocked function
        def side_effect(pdf_path):
            if "with_text" in pdf_path.name:
                return True  # Simulate a PDF with good text
            return False # Simulate a PDF with no text

        mock_pdf_check.side_effect = side_effect

        # --- 3. Execution: Run the processor ---
        triage_processor = TriageProcessor(input_dir, summary_dir, lab_dir)
        report = triage_processor.process()

    # --- 4. Assertion: Verificamos os movimentos de arquivos (sem alterações) E o novo relatório ---
    assert (summary_dir / "document_with_text.pdf").exists()
    assert (summary_dir / "my_great_book.epub").exists()
    assert (lab_dir / "document_as_image.pdf").exists()
    assert (input_dir / "notes.txt").exists()
    
    # NOVA VERIFICAÇÃO: O método deve retornar um dicionário com o relatório.
    assert report is not None
    assert isinstance(report, dict)
    
    # Verificamos o conteúdo do relatório
    assert len(report["moved_to_summary"]) == 2
    assert len(report["moved_to_lab"]) == 1
    assert len(report["ignored"]) == 1
    assert "notes.txt" in str(report["ignored"])
