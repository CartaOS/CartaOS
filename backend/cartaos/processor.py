# -*- coding: utf-8 -*-
# backend/cartaos/processor.py

"""
processor.py
Handles the processing of PDF files to generate summaries using AI.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from rich.progress import (BarColumn, Progress, SpinnerColumn, TaskID,
                           TextColumn, TimeRemainingColumn)
from slugify import slugify

from typing import Optional

from .app_config import AppConfig, get_config
from .utils.ai_utils import generate_summary_with_retries
from .utils.pdf_utils import extract_text
from .utils.text_utils import sanitize
from .utils.utils import WarningCaptureHandler


class CartaOSProcessor:
    """Encapsulates the entire process of generating a summary for a PDF file."""

    def __init__(
        self,
        pdf_path: Path,
        config: Optional[AppConfig] = None,
        dry_run: bool = False,
        debug: bool = False,
        force_ocr: bool = False,
    ) -> None:
        """
        Initializes the CartaOSProcessor with paths and configuration options.

        Args:
            pdf_path (Path): Path to the PDF file to be processed.
            config (AppConfig, optional): Application configuration instance.
            dry_run (bool): If True, processes without saving or moving files.
            debug (bool): If True, saves extracted text and stops before AI call.
            force_ocr (bool): If True, forces OCR processing before summarization.
        """
        self.pdf_path: Path = pdf_path
        self.config: AppConfig = config or get_config()
        self.dry_run: bool = dry_run
        self.debug: bool = debug
        self.force_ocr: bool = force_ocr
        
        # Set API key from config
        if not self.config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured in the application settings")
            
        os.environ["GEMINI_API_KEY"] = self.config.gemini_api_key

        self.captured_warnings: List[str] = []
        self._setup_warning_capture()

        self.load_config()

    def _setup_warning_capture(self) -> None:
        """Configures a handler to capture pdfminer warnings in memory."""
        pdfminer_logger: logging.Logger = logging.getLogger("pdfminer")
        pdfminer_logger.setLevel(logging.WARNING)
        handler: WarningCaptureHandler = WarningCaptureHandler(self.captured_warnings)
        pdfminer_logger.addHandler(handler)
        pdfminer_logger.propagate = False

    def load_config(self) -> None:
        """Loads configurations from the AppConfig instance."""
        # Use the processed directory from the pipeline directories
        self.processed_pdf_dir: Path = self.config.pipeline_dirs["07_Processed"]
        
        # Set up summary directory - use Obsidian vault if available, otherwise use default
        if self.config.obsidian_vault_path and self.config.obsidian_vault_path.is_dir():
            self.summary_dir = self.config.obsidian_vault_path / "Summaries"
        else:
            self.summary_dir = self.processed_pdf_dir / "Summaries"
            
        # Ensure the summary directory exists
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        
        # Set API key from config
        self.api_key: str = self.config.gemini_api_key

    def _save_summary(self, summary_content: str) -> None:
        """
        Saves the summary content to a .md file in the configured summary directory.

        Args:
            summary_content (str): The content of the summary to be saved.
        """
        # Generate a safe filename from the PDF name
        safe_name: str = slugify(self.pdf_path.stem)
        md_output_path: Path = self.summary_dir / f"{safe_name}.md"
        
        # In dry run mode, just log the action without writing the file
        if self.dry_run:
            print(f"[DRY RUN] Would save summary to: {md_output_path}")
            return
            
        # Write the summary content to the file
        with open(md_output_path, "w", encoding="utf-8") as f:
            f.write(summary_content)
            
        if self.debug:
            print(f"[DEBUG] Summary saved to: {md_output_path}")

    def _move_pdf(self) -> None:
        """
        Moves the original PDF to the processed directory.
        
        In dry run mode, only logs the action without moving the file.
        """
        # Determine the destination path in the processed directory
        pdf_output_path: Path = self.processed_pdf_dir / self.pdf_path.name
        
        # In dry run mode, just log the action
        if self.dry_run:
            print(f"[DRY RUN] Would move PDF from {self.pdf_path} to {pdf_output_path}")
            return
            
        # Ensure the processed directory exists
        self.processed_pdf_dir.mkdir(parents=True, exist_ok=True)
        
        # Move the file and update the path
        shutil.move(str(self.pdf_path), str(pdf_output_path))
        self.pdf_path = pdf_output_path
        
        if self.debug:
            print(f"[DEBUG] Moved PDF to: {pdf_output_path}")

    async def _process_async(self) -> bool:
        """
        Internal async implementation of the processing workflow.

        Returns:
            bool: True if processing is successful, False otherwise.
        """
        if not self.pdf_path.exists():
            print(f"Error: File not found: {self.pdf_path}")
            return False
            
        if self.debug:
            print(f"[DEBUG] Starting async processing of {self.pdf_path}")
            print(f"[DEBUG] Configuration - Dry Run: {self.dry_run}, Debug: {self.debug}")
            print(f"[DEBUG] Using API Key: {'*' * 8 + (self.config.gemini_api_key[-4:] if self.config.gemini_api_key else '') if self.config.gemini_api_key else 'Not set'}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            transient=True,
            disable=self.debug,  # Disable progress bar in debug mode for cleaner output
        ) as progress:
            task = progress.add_task("Processing PDF...", total=100)

            # Step 1: Extract text from PDF
            progress.update(task, description="Extracting text from PDF...", completed=20)
            try:
                if self.debug:
                    print(f"[DEBUG] Extracting text from {self.pdf_path}")
                    
                text = extract_text(self.pdf_path)
                
                if text is None:
                    raise ValueError("Failed to extract text from PDF")
                    
                if self.debug:
                    print(f"[DEBUG] Extracted {len(text)} characters of text")
                    
            except Exception as e:
                error_msg = f"Error extracting text from {self.pdf_path}: {e}"
                if self.debug:
                    import traceback
                    error_msg += f"\n{traceback.format_exc()}"
                print(error_msg)
                return False

            # If in debug mode, save the extracted text and stop
            if self.debug:
                debug_text_path = self.pdf_path.with_suffix(".txt")
                with open(debug_text_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"[DEBUG] Extracted text saved to {debug_text_path}")
                return True

            # Step 2: Generate summary using AI with retries
            progress.update(task, description="Generating summary...", completed=60)
            try:
                if self.debug:
                    print("[DEBUG] Generating summary using AI...")
                    
                summary = await generate_summary_with_retries(text)
                
                if summary is None:
                    error_msg = "Failed to generate summary: generate_summary_with_retries returned None"
                    if self.debug:
                        print(f"[DEBUG] {error_msg}")
                    print(error_msg)
                    return False
                    
                if self.debug:
                    print(f"[DEBUG] Generated summary of {len(summary)} characters")
                    
            except Exception as e:
                error_msg = f"Error generating summary: {e}"
                if self.debug:
                    import traceback
                    error_msg += f"\n{traceback.format_exc()}"
                print(error_msg)
                return False

            # Step 3: Save the summary
            progress.update(task, description="Saving summary...", completed=90)
            self._save_summary(summary)

            # Step 4: Move the processed PDF if not in dry run mode
            if not self.dry_run:
                progress.update(task, description="Moving processed file...", completed=95)
                self._move_pdf()
            elif self.debug:
                print("[DEBUG] Dry run - skipping file move")

            progress.update(task, completed=100)

        if self.debug:
            print("[DEBUG] Processing completed successfully")
            
        return True
        
    async def process_async(self) -> bool:
        """
        Public async method to process the PDF.
        
        Returns:
            bool: True if processing is successful, False otherwise.
        """
        return await self._process_async()
        
    def process(self) -> bool:
        """
        Process the PDF file synchronously.
        
        Returns:
            bool: True if processing was successful, False otherwise.
        """
        import asyncio
        try:
            # If we're already in an event loop, use run_until_complete
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(self._process_async())
        except RuntimeError:  # No event loop running
            return asyncio.run(self._process_async())
