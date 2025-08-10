# -*- coding: utf-8 -*-
"""
processor.py
Handles the processing of PDF files to generate summaries using AI.
"""

import os
import sys
import logging
import shutil
import re
import unicodedata
from pathlib import Path
from typing import Optional
from typing import List
import google.generativeai as genai
import pdfplumber
import fitz  # PyMuPDF
from dotenv import load_dotenv
from slugify import slugify
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)
from .utils import WarningCaptureHandler

class CartaOSProcessor:
    """Encapsulates the entire process of generating a summary for a PDF file."""

    def __init__(self, pdf_path: str, dry_run: bool = False, debug: bool = False, force_ocr: bool = False):
        """
        Initializes the CartaOSProcessor with paths and configuration options.
        
        Args:
            pdf_path (str): Path to the PDF file to be processed.
            dry_run (bool): If True, processes without saving or moving files.
            debug (bool): If True, saves extracted text and stops before AI call.
            force_ocr (bool): If True, forces OCR processing before summarization.
        """
        self.pdf_path = Path(pdf_path)
        self.dry_run = dry_run
        self.debug = debug
        self.force_ocr = force_ocr

        self.captured_warnings: List[str] = []
        self._setup_warning_capture()

        
        self.load_config()
        self.configure_api()
    
    def _setup_warning_capture(self):
        """Configures a handler to capture pdfminer warnings in memory."""
        # Get the specific logger for the pdfminer library
        pdfminer_logger = logging.getLogger("pdfminer")
        
        # Set the level to WARNING to only capture warnings and errors
        pdfminer_logger.setLevel(logging.WARNING)
        
        # Create an instance of our custom handler
        handler = WarningCaptureHandler(self.captured_warnings)
        pdfminer_logger.addHandler(handler)
        
        # Setting propagate to False prevents the captured warnings
        # from also being printed to the console by the root logger.
        pdfminer_logger.propagate = False


    def load_config(self):
        """Loads environment configurations from the .env file."""
        dotenv_path = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=dotenv_path)
        
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.obsidian_vault_path = os.getenv("OBSIDIAN_VAULT_PATH")

        self.processed_pdf_dir = Path(__file__).parent.parent.parent / "07_Processed"
        
        if self.obsidian_vault_path and Path(self.obsidian_vault_path).is_dir():
            self.summary_dir = Path(self.obsidian_vault_path) / "Summaries"
            logging.info(f"Using Obsidian vault to save summaries: {self.summary_dir}")
        else:
            self.summary_dir = self.processed_pdf_dir / "Summaries"

    def configure_api(self):
        """Configures the API key for the Gemini AI model."""
        if not self.api_key:
            logging.error("GOOGLE_API_KEY not found in backend/.env")
            raise ValueError("API key is not configured.")
        genai.configure(api_key=self.api_key)

    def _sanitize_text(self, text: str) -> str:
        """
        Cleans and normalizes text to prevent API issues.
        
        Args:
            text (str): The text to be sanitized.
        
        Returns:
            str: Sanitized text.
        """
        text = unicodedata.normalize('NFC', text)
        # Remove problematic control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text

    def extract_text(self) -> Optional[str]:
        """
        Extracts full text from the PDF file using multiple methods for robustness.
        
        Returns:
            Optional[str]: Extracted text or None if extraction fails.
        """
        logging.info(f"Extracting text from '{self.pdf_path.name}'...")
        text = ""
        try:
            # Attempt to extract text using pdfplumber
            with pdfplumber.open(self.pdf_path) as pdf:
                text = "".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            pass

        if not text or len(text) < 100:
            logging.info("pdfplumber result was poor. Trying extraction with PyMuPDF (fitz)...")
            try:
                # Fallback to PyMuPDF for text extraction
                with fitz.open(self.pdf_path) as doc:
                    text = "".join(page.get_text() for page in doc)
            except Exception as e:
                logging.error(f"PyMuPDF also failed: {e}")
                return None
        
        logging.info(f"Text extracted successfully: {text[:100]}...")
        return text.strip() if text else None

    def generate_summary(self, text: str) -> Optional[str]:
        """
        Generates the analytical summary using the Gemini API.
        
        Args:
            text (str): The text to be summarized.
        
        Returns:
            Optional[str]: Generated summary or None if generation fails.
        """
        logging.info("Generating summary with the AI model...")
        prompt_path = Path(__file__).parent / 'prompts' / 'summary_prompt.md'
        
        # Safety configuration for the AI model
        safety_config = {
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
        }
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            prompt = prompt_template.format(text=text)
            model = genai.GenerativeModel('models/gemini-2.5-pro')
            response = model.generate_content(prompt, safety_settings=safety_config)
            
            logging.info(f"Summary generated successfully: {response.text[:100]}...")
            return response.text if response.parts else None
        except Exception as e:
            logging.error(f"Error during Gemini API call: {e}")
            return None

    def _save_summary(self, summary_content: str):
        """
        Saves the summary content to a .md file.
        
        Args:
            summary_content (str): The content of the summary to be saved.
        """
        original_basename = self.pdf_path.name
        base_name = self.pdf_path.stem
        safe_name = slugify(base_name)
        
        md_output_path = self.summary_dir / f"{safe_name}.md"
        os.makedirs(self.summary_dir, exist_ok=True)
        with open(md_output_path, "w", encoding="utf-8") as f:
            f.write(summary_content)
        logging.info(f"Summary file saved to: {md_output_path}")

    def _move_pdf(self):
        """Moves the original PDF to the processed directory."""
        original_basename = self.pdf_path.name
        pdf_output_path = self.processed_pdf_dir / original_basename
        shutil.move(self.pdf_path, pdf_output_path)
        logging.info(f"Original PDF moved to: {pdf_output_path}")

    def process(self) -> bool:
        """
        Orchestrates the entire processing workflow.
        
        Returns:
            bool: True if processing is successful, False otherwise.
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Processing PDF...", total=100)
            
            progress.update(task, advance=20)
            logging.info("Extracting text from the PDF...")
            text = self.extract_text()
            if not text:
                logging.error("Process stopped: text could not be extracted.")
                return False

            progress.update(task, advance=20)
            if self.debug:
                # Save extracted text for debugging
                debug_path = self.pdf_path.parent / f"{self.pdf_path.stem}_extracted_text.txt"
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(text)
                logging.info(f"DEBUG MODE: Extracted text saved to {debug_path}")
                logging.info("Process stopped after text extraction as requested.")
                progress.update(task, advance=60)
                return True

            sanitized_text = self._sanitize_text(text)

            progress.update(task, advance=20)
            logging.info("Generating summary with the AI model...")
            summary = self.generate_summary(sanitized_text)
            if not summary:
                logging.error("Process stopped: summary could not be generated.")
                return False

            progress.update(task, advance=20)
            if self.dry_run:
                # Output summary in dry run mode
                logging.info("[DRY RUN] Process would be successful.")
                print(summary)
                return True

            self._save_summary(summary)
            self._move_pdf()
            logging.info("File processed successfully.")
            return True


