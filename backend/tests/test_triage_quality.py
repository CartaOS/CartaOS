
from pathlib import Path
import pytest

# This import will fail, which is the first RED step of our TDD cycle.
from cartaos.triage import classify_pdf_quality, extract_text


import fitz

@pytest.fixture
def pdf_with_content(tmp_path):
    """Creates a dummy PDF file with some text content."""
    pdf_path = tmp_path / "test_with_content.pdf"
    doc = fitz.open()  # Create a new PDF document
    page = doc.new_page()  # Add a new page
    page.insert_text((72, 72), "Hello, world!")  # Insert text
    doc.save(pdf_path)  # Save the PDF
    doc.close()
    return pdf_path

def test_extract_text_from_pdf_with_content(pdf_with_content):
    """Tests that extract_text can extract content from a PDF."""
    # Act
    extracted_content = extract_text(pdf_with_content)

    # Assert
    assert extracted_content != "" # Expecting some content


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "pdfs"


@pytest.fixture
def born_digital_pdf(tmp_path):
    """Creates a placeholder for a born-digital PDF."""
    p = tmp_path / "born_digital.pdf"
    p.touch()
    return p

@pytest.fixture
def scanned_pdf(tmp_path):
    """Creates a placeholder for a scanned PDF."""
    p = tmp_path / "scanned.pdf"
    p.touch()
    return p

def test_classify_born_digital_pdf(born_digital_pdf, monkeypatch):
    """Tests if a born-digital PDF is correctly classified as high_quality."""
    # Arrange
    # Mock extract_text to simulate finding text
    monkeypatch.setattr("cartaos.triage.extract_text", lambda path: "a" * 100)

    # Act
    classification = classify_pdf_quality(born_digital_pdf)

    # Assert
    assert classification == "high_quality"

def test_classify_scanned_pdf(scanned_pdf, monkeypatch):
    """Tests if a scanned PDF is correctly classified as low_quality."""
    # Arrange
    # Mock extract_text to simulate finding no text
    monkeypatch.setattr("cartaos.triage.extract_text", lambda path: "")

    # Act
    classification = classify_pdf_quality(scanned_pdf)

    # Assert
    assert classification == "low_quality"

@pytest.fixture
def problematic_pdf(tmp_path):
    """Creates a placeholder for a problematic PDF (e.g., an empty file)."""
    p = tmp_path / "problematic.pdf"
    p.touch()
    return p

def test_classify_problematic_pdf(problematic_pdf):
    """Tests if a problematic PDF is correctly classified as problematic."""
    # Act
    classification = classify_pdf_quality(problematic_pdf)

    # Assert
    assert classification == "problematic"
