#!/usr/bin/env python3
"""
Test script for OCR processor functionality.
"""
import asyncio
import sys
from pathlib import Path
from cartaos.processors.ocr_processor import OcrProcessor

async def test_ocr_processor(pdf_path: str):
    """Test the OCR processor with a PDF file."""
    try:
        print(f"Testing OCR processor with: {pdf_path}")
        
        # Create output directory if it doesn't exist
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Initialize the processor
        processor = OcrProcessor()
        await processor.initialize()
        
        # Process the PDF
        result = await processor.process_document(Path(pdf_path))
        
        # Save the result
        output_file = output_dir / f"{Path(pdf_path).stem}_ocr_result.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
            
        print(f"OCR processing completed. Results saved to: {output_file}")
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
        print("Usage: python test_ocr_processor.py <path_to_pdf>")
        sys.exit(1)
        
    success = asyncio.run(test_ocr_processor(sys.argv[1]))
    sys.exit(0 if success else 1)
