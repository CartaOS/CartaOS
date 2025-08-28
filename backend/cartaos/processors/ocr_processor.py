"""OCR processing functionality for CartaOS."""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OcrProcessor:
    """Handles OCR processing of documents using Tesseract OCR."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the OCR processor.
        
        Args:
            config: Optional configuration dictionary with OCR settings.
        """
        self.config = {
            'tesseract_path': 'tesseract',
            'languages': ['eng', 'por'],
            'dpi': 300,
            **(config or {})
        }
        self.initialized = False
        
    async def initialize(self):
        """Initialize the OCR processor resources."""
        if self.initialized:
            return
            
        # Verify Tesseract is installed and available
        try:
            result = subprocess.run(
                [self.config['tesseract_path'], '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Tesseract initialized: {result.stdout.splitlines()[0] if result.stdout else 'Unknown version'}")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error("Tesseract not found. Please install Tesseract OCR.")
            raise RuntimeError("Tesseract OCR is not installed or not in PATH") from e
            
        self.initialized = True
        logger.info("OCR processor initialized")
    
    async def _convert_pdf_to_images(self, pdf_path: Path) -> list[Path]:
        """Convert PDF pages to images for OCR processing.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of paths to temporary image files
        """
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            
            images = []
            doc = fitz.open(pdf_path)
            
            for i, page in enumerate(doc):
                # Render page to an image
                pix = page.get_pixmap(dpi=self.config['dpi'])
                
                # Create a temporary file for the image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                    image_path = Path(f.name)
                    
                # Save the image
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                img.save(image_path, 'PNG')
                images.append(image_path)
                
            return images
            
        except ImportError:
            logger.error("PyMuPDF and/or Pillow not installed. Install with: pip install pymupdf pillow")
            raise
    
    async def _extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from an image using Tesseract OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as a string
            
        Raises:
            RuntimeError: If OCR processing fails
        """
        # Create a temporary directory for the output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_base = Path(temp_dir) / "output"
            
            try:
                # Build the Tesseract command
                cmd = [
                    self.config['tesseract_path'],
                    str(image_path),
                    str(output_base),  # Output base path without extension
                    '-l', '+'.join(self.config['languages']),
                    '--dpi', str(self.config['dpi']),
                    '--psm', '6'  # Assume a single uniform block of text
                ]
                
                # Run Tesseract
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Read the extracted text
                output_file = output_base.with_suffix('.txt')
                if not output_file.exists():
                    raise RuntimeError(f"Tesseract did not create output file: {output_file}")
                    
                with open(output_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                return text.strip()
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Tesseract error: {e.stderr}")
                raise RuntimeError(f"OCR processing failed: {e.stderr}") from e
            except Exception as e:
                logger.error(f"Error during OCR processing: {str(e)}")
                raise RuntimeError(f"OCR processing failed: {str(e)}") from e
    
    async def process_document(self, file_path: Path) -> str:
        """Process a document with OCR.
        
        Args:
            file_path: Path to the document to process.
            
        Returns:
            Extracted text from the document.
            
        Raises:
            RuntimeError: If OCR processing fails.
            FileNotFoundError: If the input file doesn't exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
            
        logger.info(f"Processing document: {file_path}")
        
        try:
            # Convert PDF to images
            image_paths = await self._convert_pdf_to_images(file_path)
            
            # Process each page
            extracted_texts = []
            for img_path in image_paths:
                try:
                    text = await self._extract_text_from_image(img_path)
                    if text:
                        extracted_texts.append(text)
                finally:
                    # Clean up the temporary image file
                    img_path.unlink(missing_ok=True)
            
            # Combine text from all pages
            full_text = "\n\n--- Page Break ---\n\n".join(extracted_texts)
            
            if not full_text.strip():
                logger.warning(f"No text was extracted from {file_path}")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise RuntimeError(f"Failed to process document: {str(e)}") from e
            # This is a placeholder implementation
            with open(file_path, 'rb') as f:
                # Read the first few bytes to check file type
                header = f.read(4)
                
                # Simple file type detection
                if header.startswith(b'%PDF'):
                    logger.debug("Processing PDF file")
                    return "PDF content placeholder"
                elif header.startswith(b'\x89PNG') or header.startswith(b'\xff\xd8'):
                    logger.debug("Processing image file")
                    return "Image content placeholder"
                else:
                    # Assume text file
                    logger.debug("Processing text file")
                    return file_path.read_text(encoding='utf-8', errors='replace')
                    
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise RuntimeError(f"Failed to process document: {str(e)}")
    
    async def cleanup(self):
        """Clean up any resources used by the OCR processor."""
        if not self.initialized:
            return
            
        # Add any cleanup code here
        self.initialized = False
        logger.info("OCR processor cleaned up")
