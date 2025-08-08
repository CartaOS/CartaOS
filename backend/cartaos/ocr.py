# -*- coding: utf-8 -*-
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


class OcrProcessor:
    """
    Runs ocrmypdf on the input file and saves it to the output path.

    Args:
        input_path (Path): Path to the input PDF file.
        output_path (Path): Path to the output PDF file.
    """

    def __init__(self, input_path: Path, output_path: Path) -> None:
        """
        Initializes OcrProcessor with input and output paths.
        """
        self.input_path = input_path
        self.output_path = output_path

    def process(self) -> bool:
        """
        Runs ocrmypdf on the input file and saves it to the output path.

        Returns:
            bool: True on success, False on failure.
        """
        logging.info(f"Starting OCR process for '{self.input_path.name}'...")

        # Ensure the output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build the command line arguments
        command = [
            "ocrmypdf",
            "--language", "por+eng",  # Languages for OCR
            "--force-ocr",           # Forces OCR even if text is present
            "--deskew",              # Straightens skewed pages
            "--clean",               # Cleans pages before OCR
            "--jobs", str(os.cpu_count()), # Use all available CPU cores
            str(self.input_path),
            str(self.output_path)
        ]

        with Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=None),
            TimeRemainingColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%", justify="right"),
            refresh_per_second=1
        ) as progress:
            # Create a task for the current file
            task_id = progress.add_task(f"[red]{self.input_path.name}[/red]", total=100)
            try:
                # Run the ocrmypdf command
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                # Advance the task to completion
                progress.update(task_id, completed=100)
                # Log the successful completion
                logging.info(f"OCR completed successfully for '{self.input_path.name}'.")
                # Log the command output
                logging.debug(result.stdout)
                # Return True on success
                return True
            except subprocess.CalledProcessError as e:
                # Log the failure
                logging.error(f"ocrmypdf failed for '{self.input_path.name}'.")
                # Log the return code
                logging.error(f"Return Code: {e.returncode}")
                # Log the stderr output
                logging.error(f"Stderr: {e.stderr}")
                # Update the task to failure
                progress.update(task_id, completed=100)
                # Return False on failure
                return False
            except FileNotFoundError:
                # Log the error
                logging.error("`ocrmypdf` command not found. Is it installed and in your PATH?")
                # Update the task to failure
                progress.update(task_id, completed=100)
                # Return False on failure
                return False

