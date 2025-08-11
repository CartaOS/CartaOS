"""
Tests for the OcrProcessor class.

Tests that the OcrProcessor class runs ocrmypdf correctly and handles errors
gracefully.

"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from cartaos.ocr import OcrProcessor


@pytest.fixture
def input_output_paths(tmp_path):
    """
    Creates an empty input file and returns paths to the input and output files.

    Args:
        tmp_path (Path): Temporary directory path.

    Returns:
        tuple: Input and output paths.
    """
    input_path = tmp_path / "input.pdf"
    output_path = tmp_path / "output.pdf"
    input_path.touch()  # create an empty input file
    return input_path, output_path


class TestOcrProcessor:
    """
    Tests for the OcrProcessor class.
    """

    def test_process_success(self, input_output_paths):
        """
        Tests that process runs ocrmypdf successfully.

        Args:
            input_output_paths (tuple): Input and output paths.
        """
        input_path, output_path = input_output_paths
        with patch('subprocess.run', return_value=MagicMock(returncode=0)):
            processor = OcrProcessor(input_path, output_path)
            result = processor.process()
            assert result is True

    def test_process_failure(self, input_output_paths):
        """
        Tests that process handles ocrmypdf errors gracefully.

        Args:
            input_output_paths (tuple): Input and output paths.
        """
        input_path, output_path = input_output_paths
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'ocrmypdf', stderr="Error")):
            processor = OcrProcessor(input_path, output_path)
            result = processor.process()
            assert result is False

    def test_process_command_not_found(self, input_output_paths):
        """
        Tests that process handles FileNotFoundError for ocrmypdf.

        Args:
            input_output_paths (tuple): Input and output paths.
        """
        input_path, output_path = input_output_paths
        with patch('subprocess.run', side_effect=FileNotFoundError):
            processor = OcrProcessor(input_path, output_path)
            result = processor.process()
            assert result is False

