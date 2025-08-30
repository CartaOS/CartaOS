
from pathlib import Path
import pytest

# This import will fail, which is the first RED step of our TDD cycle.
from cartaos.triage import classify_pdf_quality

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
    monkeypatch.setattr("cartaos.triage.extract_text", lambda path: "some text")

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
