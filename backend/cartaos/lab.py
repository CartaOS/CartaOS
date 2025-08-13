# -*- coding: utf-8 -*-
# backend/cartaos/lab.py

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List
from .utils.pdf_utils import extract_pages, recompose_pdf

logger = logging.getLogger(__name__)


class LabProcessor:
    def __init__(self, input_path: Path, output_dir: Path) -> None:
        """
        Initialize the LabProcessor with the input PDF and output directory.

        Args:
            input_path (Path): The path to the source PDF file.
            output_dir (Path): The destination directory for the corrected PDF.
        """
        self.input_path: Path = input_path
        self.output_dir: Path = output_dir

    def process(self) -> bool:
        """
        Send the PDF to the manual correction lab with ScanTailor.

        Returns:
            bool: True on success, False on failure.
        """
        try:
            with tempfile.TemporaryDirectory() as workspace:
                logger.info("Extracting pages from input PDF")
                images: List[Path] = extract_pages(self.input_path)
                
                logger.info("Running unpaper cleanup")
                self._run_unpaper_cleanup(workspace, images)

                logger.info("Generating ScanTailor project file")
                self._generate_scantailor_project(workspace, images)

                logger.info("Running manual correction using ScanTailor Advanced")
                print("Please correct the images using ScanTailor Advanced.")
                input("Press [Enter] to continue...")
                self._run_manual_correction(workspace, images)

                logger.info("Recomposing PDF from corrected images")
                pdf_path = recompose_pdf(images, self.output_dir, self.input_path)

                logger.info(f"PDF saved to {pdf_path}")
            return True
        except Exception as e:
            logger.error(f"Error during lab processing: {e}")
            return False

    def _run_unpaper_cleanup(self, workspace: str, images: List[Path]) -> None:
        """
        Run unpaper cleanup on the extracted TIFF images.

        Args:
            workspace (str): The temporary workspace directory.
            images (List[Path]): The list of paths to the extracted TIFF images.
        """
        for image in images:
            subprocess.run(["unpaper", image], cwd=workspace)

    def _generate_scantailor_project(self, workspace: str, images: List[Path]) -> None:
        """
        Generate a ScanTailor project file.

        Args:
            workspace (str): The temporary workspace directory.
            images (List[Path]): The list of paths to the extracted TIFF images.
        """
        with open(os.path.join(workspace, "project.scantailor"), "w") as f:
            f.write("<project>\n")
            for image in images:
                f.write(f"<image>{image.name}</image>\n")
            f.write("</project>\n")

    def _run_manual_correction(self, workspace: str, images: List[Path]) -> None:
        """
        Run manual correction using ScanTailor Advanced.

        Args:
            workspace (str): The temporary workspace directory.
            images (List[Path]): The list of paths to the extracted TIFF images.
        """
        
        subprocess.run(["flatpak", "run", "com.github._4lex4.ScanTailor-Advanced", "project.scantailor"], cwd=workspace)

