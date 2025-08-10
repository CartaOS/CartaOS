# backend/tests/test_lab.py

"""
Tests for the LabProcessor class.

Tests:
    - Successful lab workflow
    - Test extract_pages method
    - Test run_unpaper_cleanup method
    - Test generate_scantailor_project method
    - Test run_manual_correction method
"""
import pytest
from unittest.mock import patch
from cartaos.lab import LabProcessor

@pytest.fixture
def input_path(tmp_path):
    """
    Fixture for creating a temporary input PDF file path.

    Args:
        tmp_path: Temporary path provided by pytest.

    Returns:
        Path: Path to the temporary input PDF file.
    """
    return tmp_path / "input.pdf"

@pytest.fixture
def output_dir(tmp_path):
    """
    Fixture for creating a temporary output directory path.

    Args:
        tmp_path: Temporary path provided by pytest.

    Returns:
        Path: Path to the temporary output directory.
    """
    return tmp_path / "output"

def test_lab_processor(input_path, output_dir):
    """
    Test for the LabProcessor process method.

    Asserts that the process method of the LabProcessor returns True.
    """
    processor = LabProcessor(input_path, output_dir)
    assert processor.process() is True

def test_extract_pages(input_path, output_dir):
    """
    Test for the _extract_pages method of LabProcessor.

    Asserts that pdf2image.convert_from_path is called with the correct arguments.
    """
    processor = LabProcessor(input_path, output_dir)
    with patch("pdf2image.convert_from_path") as mock_convert:
        processor._extract_pages("/tmp/workspace")
        mock_convert.assert_called_once_with(input_path, dpi=300, grayscale=True)

def test_run_unpaper_cleanup(input_path, output_dir):
    """
    Test for the _run_unpaper_cleanup method of LabProcessor.

    Asserts that subprocess.run is called with the correct arguments.
    """
    processor = LabProcessor(input_path, output_dir)
    with patch("subprocess.run") as mock_run:
        processor._run_unpaper_cleanup("/tmp/workspace")
        mock_run.assert_called_once_with(["unpaper", "page_1.tiff"], cwd="/tmp/workspace")
