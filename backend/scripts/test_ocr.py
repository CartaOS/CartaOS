#!/usr/bin/env python3
"""
Test script for OCR functionality.
"""
import sys
from pathlib import Path
from cartaos.processors.ocr_processor import OcrProcessor

def test_ocr(pdf_path: str):
    """Test OCR on a single PDF file."""
    try:
        print(f"Testing OCR on: {pdf_path}")
        
        # Create output directory if it doesn't exist
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Process the PDF
        processor = OcrProcessor(pdf_path, debug=True)
        result = processor.process()
        
        # Save the result
        output_file = output_dir / f"{Path(pdf_path).stem}_ocr.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
            
        print(f"OCR completed. Results saved to: {output_file}")
        print("First 200 characters of extracted text:")
        print("-" * 50)
        print(result[:200])
        print("-" * 50)
        
        return True
    except Exception as e:
        print(f"Error during OCR processing: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_ocr.py <path_to_pdf>")
        sys.exit(1)
        
    success = test_ocr(sys.argv[1])
    sys.exit(0 if success else 1)
