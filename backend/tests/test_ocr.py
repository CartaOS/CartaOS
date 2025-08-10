# backend/tests/test_ocr.py

import logging
import os
import pytest
from pathlib import Path
from cartaos.ocr import OcrProcessor

"""
Tests for the OcrProcessor class.

Tests:
    - Successful OCR process
    - Failed OCR process due to missing ocrmypdf command
    - Invalid input file
"""

@pytest.fixture
def input_file(tmp_path):
    """
    Creates a temporary PDF file as input for the OCR processor.

    Returns:
        Path: Path to the temporary PDF file.
    """
    # Create a temporary PDF file
    input_file = tmp_path / "input.pdf"
    with open(input_file, "w") as f:
        f.write("This is a test PDF file.")
    return input_file

@pytest.fixture
def output_file(tmp_path):
    """
    Creates a temporary output directory and file for the OCR processor.

    Returns:
        Path: Path to the temporary output file.
    """
    # Create a temporary output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir / "output.pdf"

def test_ocr_processor(input_file, output_file):
    """
    Tests a successful OCR process.

    Asserts:
        - The OCR process returns True
    """
    # Create an OcrProcessor instance
    processor = OcrProcessor(input_file, output_file)
    # Run the OCR process
    result = processor.process()
    # Check the result
    assert result is True

def test_ocr_processor_failure(input_file, output_file):
    """
    Tests a failed OCR process due to missing ocrmypdf command.

    Asserts:
        - The OCR process returns False
    """
    # Create an OcrProcessor instance
    processor = OcrProcessor(input_file, output_file)
    # Simulate a failure by removing the ocrmypdf command
    os.environ["PATH"] = ""
    # Run the OCR process
    result = processor.process()
    # Check the result
    assert result is False

def test_ocr_processor_invalid_input(input_file, output_file):
    """
    Tests a failed OCR process due to invalid input file.

    Asserts:
        - The OCR process returns False
    """
    # Create an OcrProcessor instance
    processor = OcrProcessor(input_file, output_file)
    # Simulate an invalid input file
    input_file.unlink()
    # Run the OCR process
    result = processor.process()
    # Check the result
    assert result is False
