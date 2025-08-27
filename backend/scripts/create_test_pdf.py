#!/usr/bin/env python3
"""
Create a test PDF file with sample text.
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

def create_test_pdf(output_path: str):
    """Create a test PDF file with sample text."""
    # Create output directory if it doesn't exist
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a PDF document
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Add a title
    c.setFont("Helvetica-Bold", 16)
    title = "Test Document for OCR Verification"
    c.drawString(72, height - 72, title)
    
    # Add some sample text
    c.setFont("Helvetica", 12)
    text = [
        "This is a test document for OCR verification.",
        "",
        "It contains multiple lines of text to ensure the OCR processor",
        "can handle different formatting and line breaks.",
        "",
        "Here are some special characters: !@#$%^&*()_+{}|:\"<>?`~-=[]\\;',./",
        "",
        "And some numbers: 1234567890",
        "",
        "End of test document."
    ]
    
    y_position = height - 100
    for line in text:
        c.drawString(72, y_position, line)
        y_position -= 15
    
    # Save the PDF
    c.save()
    print(f"Test PDF created at: {output_path}")

if __name__ == "__main__":
    output_path = "test_output/test_document.pdf"
    create_test_pdf(output_path)
