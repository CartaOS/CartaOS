# -*- coding: utf-8 -*-
# backend/cartaos/ocr.py

"""
OCR processor module for CartaOS.

Handles OCR processing for a single PDF file using ocrmypdf.

Example:
    >>> from cartaos.ocr import OcrProcessor
    >>> processor = OcrProcessor(Path("input.pdf"), Path("output.pdf"))
    >>> processor.process()
    True
"""

import subprocess
import logging
import os
from pathlib import Path
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from typing import Union

class OcrProcessor:
    """
    Runs ocrmypdf on the input file and saves it to the output path.

    Attributes:
        input_path (Path): Path to the input PDF file.
        output_path (Path): Path to the output PDF file.
    """

    def __init__(self, input_path: Path, output_path: Path) -> None:
        """
        Initializes OcrProcessor with input and output paths.

        Args:
            input_path (Path): Path to the input PDF file.
            output_path (Path): Path to the output PDF file.
        """
        self.input_path: Path = input_path
        self.output_path: Path = output_path

    def process(self) -> bool:
        """
        Runs ocrmypdf on the input file and saves it to the output path.

        Returns:
            bool: True on success, False on failure.
        """
        logging.info(f"Starting OCR process for '{self.input_path.name}'...")

        # Ensure the output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Construct command line for ocrmypdf
        command: list[Union[str, Path]] = [
            "ocrmypdf",
            "--language", "por+eng",
            "--force-ocr",
            "--deskew",
            "--clean",
            "--jobs", str(os.cpu_count()),
            str(self.input_path),
            str(self.output_path)
        ]

        # Initialize progress bar for OCR processing
        with Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=None),
            TimeRemainingColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%", justify="right"),
            refresh_per_second=1
        ) as progress:
            task_id = progress.add_task(f"[red]{self.input_path.name}[/red]", total=100)
            try:
                # Execute the ocrmypdf command
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                # Mark task as completed on success
                progress.update(task_id, completed=100)
                logging.info(f"OCR completed successfully for '{self.input_path.name}'.")
                logging.debug(result.stdout)
                return True
            except subprocess.CalledProcessError as e:
                # Handle errors from ocrmypdf execution
                logging.error(f"ocrmypdf failed for '{self.input_path.name}'. Return Code: {e.returncode}")
                logging.error(f"Stderr: {e.stderr}")
                progress.update(task_id, completed=100)
                return False
            except FileNotFoundError:
                # Handle command not found error
                logging.error("`ocrmypdf` command not found. Is it installed and in your PATH?")
                progress.update(task_id, completed=100)
                return False

