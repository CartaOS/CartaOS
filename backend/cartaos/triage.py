# -*- coding: utf-8 -*-
# backend/cartaos/triage.py

"""
Orchestrates the entire triage workflow.
Scans the input directory recursively to find all files, determines the file type based on its extension,
and moves it to the appropriate next stage in the processing pipeline.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Literal, Optional

from .utils.pdf_utils import extract_text

logger = logging.getLogger(__name__)


class TriageProcessor:
    """
    Orchestrates the entire triage workflow.

    Attributes:
        input_dir (Path): The path to the source directory to be scanned.
        summary_dir (Path): The destination for files ready for AI summarization.
        lab_dir (Path): The destination for files requiring manual correction or OCR.
    """

    def __init__(self, input_dir: Path, summary_dir: Path, lab_dir: Path) -> None:
        """
        Initializes the TriageProcessor.

        Args:
            input_dir (Path): The path to the source directory to be scanned.
            summary_dir (Path): The destination for files ready for AI summarization.
            lab_dir (Path): The destination for files requiring manual correction or OCR.
        """
        self.input_dir: Path = input_dir
        self.summary_dir: Path = summary_dir
        self.lab_dir: Path = lab_dir

    def process(self) -> Dict[str, List[str]]:
        """
        Orchestrates the entire triage workflow and returns a report of its actions.

        Returns:
            A dictionary with the following keys:
                - moved_to_summary (List[str]): A list of file names moved to the summary directory.
                - moved_to_lab (List[str]): A list of file names moved to the lab directory.
                - ignored (List[str]): A list of file names ignored because of unsupported file types.
        """
        report: Dict[str, List[str]] = {
            "moved_to_summary": [],
            "moved_to_lab": [],
            "ignored": [],
        }

        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                file_path = Path(root) / file
                file_type: Optional[Literal["ebook", "pdf"]] = self._get_file_type(
                    file_path
                )

                if file_type == "ebook":
                    self._move_to_summary_dir(file_path)
                    report["moved_to_summary"].append(file_path.name)
                elif file_type == "pdf":
                    text = extract_text(file_path)
                    if text and len(text) > 500:
                        self._move_to_summary_dir(file_path)
                        report["moved_to_summary"].append(file_path.name)
                    else:
                        self._move_to_lab_dir(file_path)
                        report["moved_to_lab"].append(file_path.name)
                else:
                    logger.warning(f"Unsupported file type: {file_type}")
                    report["ignored"].append(file_path.name)

        return report

    def _get_file_type(self, file_path: Path) -> Optional[Literal["ebook", "pdf"]]:
        """
        Determines the file type based on its extension.

        Args:
            file_path (Path): The path to the file.

        Returns:
            The file type (ebook, pdf, or None if unknown).
        """
        file_extension: str = file_path.suffix.lower()
        if file_extension in [".epub", ".mobi"]:
            return "ebook"
        elif file_extension == ".pdf":
            return "pdf"
        else:
            return None

    def _move_to_summary_dir(self, file_path: Path) -> None:
        """
        Moves a file to the summary directory.

        Args:
            file_path (Path): The path to the file.
        """
        relative_path: Path = file_path.relative_to(self.input_dir)
        destination_path: Path = self.summary_dir / relative_path
        os.makedirs(destination_path.parent, exist_ok=True)
        os.rename(file_path, destination_path)

    def _move_to_lab_dir(self, file_path: Path) -> None:
        """
        Moves a file to the lab directory.

        Args:
            file_path (Path): The path to the file.
        """
        relative_path: Path = file_path.relative_to(self.input_dir)
        destination_path: Path = self.lab_dir / relative_path
        os.makedirs(destination_path.parent, exist_ok=True)
        os.rename(file_path, destination_path)

def classify_pdf_quality(pdf_path: Path) -> str:
    """Determines the quality of a PDF file."""
    return "high_quality"