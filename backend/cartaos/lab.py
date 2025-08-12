# -*- coding: utf-8 -*-
# backend/cartaos/lab.py

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List

import pdf2image
from img2pdf import convert

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
                self._extract_pages(workspace)
                self._run_unpaper_cleanup(workspace)
                self._generate_scantailor_project(workspace)
                self._run_manual_correction(workspace)
                self._recompose_pdf(workspace)
            return True
        except Exception as e:
            logger.error(f"Error during lab processing: {e}")
            return False

    def _extract_pages(self, workspace: str) -> None:
        """
        Extract the pages from the input PDF.

        Args:
            workspace (str): The temporary workspace directory.
        """
        logger.info("Extracting pages from input PDF")
        images: List[Path] = []
        for i, image in enumerate(pdf2image.convert_from_path(self.input_path, dpi=300, grayscale=True)):
            image_path: Path = Path(os.path.join(workspace, f"page_{i+1}.tiff"))
            image.save(image_path)
            images.append(image_path)

    def _run_unpaper_cleanup(self, workspace: str) -> None:
        """
        Run unpaper cleanup on the extracted TIFF images.

        Args:
            workspace (str): The temporary workspace directory.
        """
        logger.info("Running unpaper cleanup")
        for file in os.listdir(workspace):
            if file.endswith(".tiff"):
                subprocess.run(["unpaper", file], cwd=workspace)

    def _generate_scantailor_project(self, workspace: str) -> None:
        """
        Generate a ScanTailor project file.

        Args:
            workspace (str): The temporary workspace directory.
        """
        logger.info("Generating ScanTailor project file")
        with open(os.path.join(workspace, "project.scantailor"), "w") as f:
            f.write("<project>\n")
            for file in os.listdir(workspace):
                if file.endswith(".tiff"):
                    f.write(f"<image>{file}</image>\n")
            f.write("</project>\n")

    def _run_manual_correction(self, workspace: str) -> None:
        """
        Run manual correction using ScanTailor Advanced.

        Args:
            workspace (str): The temporary workspace directory.
        """
        logger.info("Running manual correction using ScanTailor Advanced")
        print("Please correct the images using ScanTailor Advanced.")
        input("Press [Enter] to continue...")
        subprocess.run(["flatpak", "run", "com.github._4lex4.ScanTailor-Advanced", "project.scantailor"], cwd=workspace)

    def _recompose_pdf(self, workspace: str) -> None:
        """
        Recompose the PDF from the corrected images.

        Args:
            workspace (str): The temporary workspace directory.
        """
        logger.info("Recomposing PDF from corrected images")
        out_dir: Path = Path(os.path.join(workspace, "out"))
        if out_dir.exists() and out_dir.is_dir() and any(out_dir.iterdir()):
            images: List[Path] = [out_dir / file for file in os.listdir(out_dir) if file.endswith(".tiff")]
            pdf_path: Path = self.output_dir / self.input_path.name
            convert(images, pdf_path)
            logger.info(f"PDF saved to {pdf_path}")
        else:
            logger.error("No output images found")

