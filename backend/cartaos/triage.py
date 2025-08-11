# backend/cartaos/triage.py

import logging
import os
from pathlib import Path
from typing import Optional, Dict, List

import pdfplumber

logger = logging.getLogger(__name__)


class TriageProcessor:
    """
    Orchestrates the entire triage workflow.
    Scans the input directory recursively to find all files, determines the file type based on its extension,
    and moves it to the appropriate next stage in the processing pipeline.
    """

    def __init__(self, input_dir: Path, summary_dir: Path, lab_dir: Path):
        """
        Initializes the TriageProcessor.
        Args:
            input_dir: The path to the source directory to be scanned.
            summary_dir: The destination for files ready for AI summarization.
            lab_dir: The destination for files requiring manual correction or OCR.
        """
        self.input_dir = input_dir
        self.summary_dir = summary_dir
        self.lab_dir = lab_dir

    def process(self) -> Dict[str, List[str]]:
        """
        Orchestrates the entire triage workflow and returns a report of its actions.
        """
        # 1. Initialize the report dictionary that our test expects.
        report = {
            "moved_to_summary": [],
            "moved_to_lab": [],
            "ignored": []
        }

        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                file_path = Path(root) / file
                file_type = self._get_file_type(file_path)

                if file_type == "ebook":
                    self._move_to_summary_dir(file_path)
                    # 2. Add the file name to our report.
                    report["moved_to_summary"].append(file_path.name)
                elif file_type == "pdf":
                    if self._pdf_has_sufficient_text(file_path):
                        self._move_to_summary_dir(file_path)
                        # 2. Add the file name to our report.
                        report["moved_to_summary"].append(file_path.name)
                    else:
                        self._move_to_lab_dir(file_path)
                        # 2. Add the file name to our report.
                        report["moved_to_lab"].append(file_path.name)
                else:
                    logger.warning(f"Unsupported file type: {file_type}")
                    # 2. Add the file name to our report.
                    report["ignored"].append(file_path.name)
        
        # 3. Return the completed report at the end of the method.
        return report

    def _get_file_type(self, file_path: Path) -> Optional[str]:
        """
        Determines the file type based on its extension.
        Args:
            file_path: The path to the file.
        Returns:
            The file type (ebook, pdf, or None if unknown).
        """
        file_extension = file_path.suffix.lower()
        if file_extension in [".epub", ".mobi"]:
            return "ebook"
        elif file_extension == ".pdf":
            return "pdf"
        else:
            return None

    def _pdf_has_sufficient_text(self, pdf_path: Path) -> bool:
        """
        Checks if a PDF file contains a usable text layer.
        Args:
            pdf_path: The path to the PDF file.
        Returns:
            True if the PDF file contains a usable text layer, False otherwise.
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Check if there are any pages to avoid errors with empty/invalid PDFs
                if not pdf.pages:
                    return False
                text = pdf.pages[0].extract_text()
                # Check if text is not None and has more than 500 characters
                return text is not None and len(text) > 500
        except Exception as e:
            # If pdfplumber fails to open the file, it's likely not a valid PDF or is corrupted.
            logger.error(f"Could not process {pdf_path.name}: {e}")
            return False

    def _move_to_summary_dir(self, file_path: Path) -> None:
        """
        Moves a file to the summary directory.
        Args:
            file_path: The path to the file.
        """
        relative_path = file_path.relative_to(self.input_dir)
        destination_path = self.summary_dir / relative_path
        os.makedirs(destination_path.parent, exist_ok=True)
        os.rename(file_path, destination_path)

    def _move_to_lab_dir(self, file_path: Path) -> None:
        """
        Moves a file to the lab directory.
        Args:
            file_path: The path to the file.
        """
        relative_path = file_path.relative_to(self.input_dir)
        destination_path = self.lab_dir / relative_path
        os.makedirs(destination_path.parent, exist_ok=True)
        os.rename(file_path, destination_path)

