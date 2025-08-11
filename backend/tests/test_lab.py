import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from tempfile import TemporaryDirectory
from cartaos.lab import LabProcessor


class TestLabProcessor(unittest.TestCase):
    """
    Unit tests for the LabProcessor class.
    """

    def setUp(self):
        """
        Set up the test environment.

        Creates a LabProcessor instance with a temporary input file and output directory.
        """
        self.input_path = Path("input.pdf")
        self.output_dir = Path("output")
        self.processor = LabProcessor(self.input_path, self.output_dir)

    def test_extract_pages(self):
        """
        Test that the _extract_pages method extracts TIFF images from the input PDF.
        """
        with TemporaryDirectory() as workspace:
            self.processor._extract_pages(workspace)
            tiff_files = [file for file in os.listdir(workspace) if file.endswith(".tiff")]
            self.assertTrue(
                tiff_files,
                "No TIFF images were extracted",
            )

    @patch("subprocess.run")
    def test_run_unpaper_cleanup(self, mock_run: MagicMock):
        """
        Test that the _run_unpaper_cleanup method runs unpaper on the TIFF images.
        """
        with TemporaryDirectory() as workspace:
            self.processor._run_unpaper_cleanup(workspace)
            mock_run.assert_any_call(
                ["unpaper", "page_1.tiff"],
                cwd=workspace,
            )

    @patch("builtins.open", new_callable=mock_open)
    def test_generate_scantailor_project(self, mock_open: MagicMock):
        """
        Test that the _generate_scantailor_project method generates a ScanTailor project file.
        """
        with TemporaryDirectory() as workspace:
            self.processor._generate_scantailor_project(workspace)
            mock_open.assert_called_once_with(
                os.path.join(workspace, "project.scantailor"),
                "w",
            )

    @patch("subprocess.run")
    def test_run_manual_correction(self, mock_run: MagicMock):
        """
        Test that the _run_manual_correction method runs ScanTailor Advanced.
        """
        with TemporaryDirectory() as workspace:
            self.processor._run_manual_correction(workspace)
            mock_run.assert_called_once_with(
                ["flatpak", "run", "com.github._4lex4.ScanTailor-Advanced", "project.scantailor"],
                cwd=workspace,
            )

    def test_recompose_pdf(self):
        """
        Test that the _recompose_pdf method recomposes a PDF from the corrected TIFF images.
        """
        with TemporaryDirectory() as workspace:
            out_dir = os.path.join(workspace, "out")
            os.makedirs(out_dir, exist_ok=True)
            for i in range(3):
                with open(os.path.join(out_dir, f"page_{i+1}.tiff"), "wb") as f:
                    f.write(b"")
            self.processor._recompose_pdf(workspace)
            output_pdf = os.path.join(self.output_dir, self.input_path.name)
            self.assertTrue(
                os.path.exists(output_pdf),
                "PDF was not saved",
            )

