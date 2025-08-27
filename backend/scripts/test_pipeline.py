#!/usr/bin/env python3
"""
Test script for verifying file movement in the processing pipeline.
"""
import asyncio
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from cartaos.processor import CartaOSProcessor
from cartaos.processors.ocr_processor import OcrProcessor

def create_test_pdf(path: Path, content: str = "Test Document") -> None:
    """Create a test PDF file with the given content."""
    with open(path, "wb") as f:
        f.write(f"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R/Parent 2 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n({content}) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000105 00000 n \n0000000179 00000 n \ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n233\n%%EOF".encode())

def create_test_txt(path: Path, content: str) -> None:
    """Create a test text file with the given content."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

async def test_with_file(file_path: Path, debug: bool = True) -> bool:
    """Test the processor with a specific file."""
    processed_dir = Path("07_Processed").resolve()
    summary_dir = processed_dir / "Summaries"
    
    # Ensure directories exist
    processed_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"\nTesting with file: {file_path.name}")
        print(f"  File size: {file_path.stat().st_size} bytes")
        
        # Initialize the processor
        processor = CartaOSProcessor(
            pdf_path=file_path.absolute(),
            debug=debug,
            dry_run=False
        )
        
        # Process the document
        print("  Starting processing...")
        result = processor.process()
        
        # Check results based on debug mode
        if debug:
            # In debug mode, check for extracted text file
            extracted_text_path = file_path.parent / f"{file_path.stem}_extracted_text.txt"
            if extracted_text_path.exists():
                print(f"  ✓ Extracted text file created: {extracted_text_path.name}")
                with open(extracted_text_path, 'r') as f:
                    content = f.read()
                    print(f"     Extracted: {content[:50]}{'...' if len(content) > 50 else ''}")
            else:
                print(f"  ✗ No extracted text file found for {file_path.name}")
        
        return result
        
    except Exception as e:
        print(f"  ✗ Error processing {file_path.name}: {str(e)}")
        return False

async def test_non_debug_mode():
    """Test the complete processing pipeline in non-debug mode with file movement."""
    # Set up paths
    processed_dir = Path("07_Processed").resolve()
    summary_dir = processed_dir / "Summaries"
    test_dir = Path("test_non_debug")
    input_dir = test_dir / "input"
    
    # Clean up from previous tests
    if processed_dir.exists():
        shutil.rmtree(processed_dir)
    
    # Create test directory and test PDF
    input_dir.mkdir(parents=True, exist_ok=True)
    test_content = "This is a test document for non-debug mode."
    test_pdf = input_dir / "test_document.pdf"
    create_test_pdf(test_pdf, test_content)
    
    # Set up expected output paths after creating the test file
    processed_pdf = processed_dir / test_pdf.name
    summary_file = summary_dir / f"{test_pdf.stem}_summary.md"
    
    # Mock the AI service to return a test summary
    mock_ai = MagicMock()
    mock_ai.generate_summary.return_value = f"Test summary for: {test_content}"
    
    try:
        print("\nTesting in non-debug mode...")
        print(f"  Test file: {test_pdf}")
        print(f"  File size: {test_pdf.stat().st_size} bytes")
        
        # Clean up any existing test directories
        test_base_dir = Path('test_pipeline_output')
        if test_base_dir.exists():
            shutil.rmtree(test_base_dir)
        
        # Create required directories with proper permissions
        processed_dir = test_base_dir / 'processed'
        summary_dir = test_base_dir / 'summaries'
        
        processed_dir.mkdir(parents=True, mode=0o755)
        summary_dir.mkdir(mode=0o755)
        
        # Set up environment variables for the processor
        os.environ['PROCESSED_PDF_DIR'] = str(processed_dir)
        os.environ['OBSIDIAN_VAULT_PATH'] = str(test_base_dir)  # Set OBSIDIAN_VAULT_PATH to test_base_dir
        
        # Print debug info
        print(f"  Test base dir: {test_base_dir.absolute()}")
        print(f"  Processed PDF dir: {processed_dir.absolute()}")
        print(f"  Summary dir: {summary_dir.absolute()}")
        print(f"  Summary dir exists: {summary_dir.exists()}")
        print(f"  Summary dir writable: {os.access(summary_dir, os.W_OK)}")
        
        # Update the expected summary path
        # The processor uses slugify which converts underscores to hyphens
        expected_summary_name = f"{test_pdf.stem.lower().replace('_', '-')}.md"
        expected_summary_file = summary_dir / expected_summary_name
        print(f"  Expected summary file: {expected_summary_file}")
        
        # Patch the AI client to use our mock
        with patch('cartaos.processor.generate_summary', return_value=f"Test summary for: {test_content}"):
            # Initialize the processor with debug=False and set the output directories
            processor = CartaOSProcessor(
                pdf_path=test_pdf.absolute(),
                debug=False,  # This will process the full pipeline
                dry_run=False
            )
            
            # Set the output directories directly (bypassing environment variables)
            processor.processed_pdf_dir = processed_dir
            processor.summary_dir = summary_dir
            
            # Process the document
            print("  Starting processing...")
            result = processor.process()
            
            # Print debug info
            print(f"  Processed PDF dir: {processed_dir}")
            print(f"  Summary dir: {summary_dir}")
            print(f"  Original file exists: {test_pdf.exists()}")
            print(f"  Processed PDF exists: {processed_pdf.exists()}")
            
            # List all files in the summary directory for debugging
            print(f"  Contents of {summary_dir}:")
            for f in summary_dir.glob('*'):
                print(f"    - {f.name} (size: {f.stat().st_size} bytes)")
        
        # Verify the results
        print("\nVerifying results...")
        
        # Check if the PDF was moved to the processed directory
        moved_pdf = processed_dir / test_pdf.name
        if moved_pdf.exists():
            print(f"  ✓ PDF moved to processed directory: {moved_pdf}")
        else:
            print(f"  ✗ PDF not found in processed directory: {moved_pdf}")
        
        # Check if the summary file was created in the expected location
        if expected_summary_file.exists():
            print(f"  ✓ Summary file created: {expected_summary_file}")
            with open(expected_summary_file, 'r') as f:
                summary_content = f.read()
                print(f"  Summary content: {summary_content[:100]}...")
            
            # Verify the summary content contains the expected text
            with open(expected_summary_file, 'r') as f:
                content = f.read()
                if "Test summary for:" in content:
                    print("  ✓ Summary content contains expected text")
                else:
                    print(f"  ✗ Unexpected summary content: {content[:100]}...")
        else:
            print(f"  ✗ Summary file not found. Expected: {expected_summary_file}")
            # Print directory contents for debugging
            print(f"  Contents of {summary_dir}:")
            for f in summary_dir.glob('*'):
                print(f"    - {f.name} (size: {f.stat().st_size} bytes)")
        
        # Check if the original file was removed
        if not test_pdf.exists():
            print("  ✓ Original file was removed")
        else:
            print(f"  ✗ Original file still exists: {test_pdf}")
        
        return moved_pdf.exists() and expected_summary_file.exists() and not test_pdf.exists()
        
    except Exception as e:
        print(f"  ✗ Error in non-debug mode test: {str(e)}")
        return False
    finally:
        # Clean up
        if test_dir.exists():
            shutil.rmtree(test_dir)
        if processed_dir.exists():
            shutil.rmtree(processed_dir)

async def test_pipeline():
    """Test the complete processing pipeline with different file types."""
    # Initialize results dictionary at the beginning
    results = {}
    
    create_test_pdf(special_pdf, "Special chars: áéíóúñ¿?¡!@#$%^&*()")
    test_files.append(special_pdf)
    
    # 3. Large PDF (simulated by repeating content)
    large_pdf = input_dir / "large_document.pdf"
    try:
        # Clean up from previous tests
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        # Create test directory
        input_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files
        test_files = []
        
        # 1. Simple PDF with text
        pdf_path = input_dir / "simple_text.pdf"
        create_test_pdf(pdf_path, "This is a simple PDF with text content for testing.")
        test_files.append(pdf_path)
        
        # 2. PDF with special characters
        special_pdf = input_dir / "special_chars.pdf"
        create_test_pdf(special_pdf, "Special chars: áéíóúñ¿?¡!@#$%^&*()")
        test_files.append(special_pdf)
        
        # 3. Large PDF (simulated by repeating content)
        large_pdf = input_dir / "large_document.pdf"
        create_test_pdf(large_pdf, "Large document content. " * 1000)
        test_files.append(large_pdf)
        
        # 4. Text file (should fail gracefully)
        txt_file = input_dir / "test_document.txt"
        create_test_txt(txt_file, "This is a plain text file, not a PDF.")
        test_files.append(txt_file)
        
        # 5. Corrupted PDF - should fail
        bad_pdf = input_dir / "corrupted.pdf"
        with open(bad_pdf, 'wb') as f:
            f.write(b"%PDF-1.4\nThis is not a valid PDF file")
        print(f"\nTesting with file: {bad_pdf.name}")
        print(f"  File size: {bad_pdf.stat().st_size} bytes")
        print("  Starting processing...")
        
        try:
            processor = CartaOSProcessor(
                pdf_path=bad_pdf,
                debug=True  # Even in debug mode, this should fail
            )
            
            result = processor.process()
            if not result:
                print("  ✓ Processing failed as expected (returned False)")
                results["corrupted.pdf"] = "PASS"
            else:
                print("  ✗ Processing should have failed but didn't")
                results["corrupted.pdf"] = "FAIL"
        except Exception as e:
            print(f"  ✓ Processing failed as expected with error: {str(e)}")
            results["corrupted.pdf"] = "PASS"
        
        # Clean up
        if bad_pdf.exists():
            bad_pdf.unlink()
            
        # Skip adding to test_files since we already processed it
        
        # Print test configuration
        print("Test configuration:")
        print(f"  Working directory: {Path.cwd()}")
        print(f"  Test directory: {test_dir}")
        print(f"  Number of test files: {len(test_files)}\n")
        
        # Test each file in debug mode
        results = {}
        for test_file in test_files:
            success = await test_with_file(test_file, debug=True)
            results[test_file.name] = "PASS" if success else "FAIL"
        
        # Run non-debug mode test
        print("\n" + "="*50)
        non_debug_result = await test_non_debug_mode()
        results["non_debug_processing"] = "PASS" if non_debug_result else "FAIL"
        
        # Print summary
        print("\nTest Summary:")
        print("-" * 50)
        for filename, result in results.items():
            status = "✓ PASS" if result == "PASS" else "✗ FAIL"
            print(f"{status} - {filename}")
        
        # Count passes and fails
        pass_count = sum(1 for r in results.values() if r == "PASS")
        fail_count = len(results) - pass_count
        
        print("\nTest Results:")
        print(f"Total tests: {len(results)}")
        print(f"Passed: {pass_count}")
        print(f"Failed: {fail_count}")
        
        return fail_count == 0
        
    except Exception as e:
        print(f"Error during pipeline test: {str(e)}")
        return False
    finally:
        # Clean up
        if test_dir.exists():
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    success = asyncio.run(test_pipeline())
    exit(0 if success else 1)
