# -*- coding: utf-8 -*-
# backend/tests/test_integration_pipeline.py

import shutil
import types
from pathlib import Path

import pytest
from typer.testing import CliRunner

import cartaos.cli as cli_module

runner = CliRunner()


def test_full_pipeline_with_mocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Setup isolated pipeline directories
    triage_dir = tmp_path / "02_Triage"
    triage_dir.mkdir()
    lab_dir = tmp_path / "03_Lab"
    lab_dir.mkdir()
    ready_ocr_dir = tmp_path / "04_ReadyForOCR"
    ready_ocr_dir.mkdir()
    ready_sum_dir = tmp_path / "05_ReadyForSummary"
    ready_sum_dir.mkdir()
    processed_dir = tmp_path / "07_Processed"
    processed_dir.mkdir()

    # Redirect CLI constants to our temp dirs
    monkeypatch.setattr(cli_module, "DIR_TRIAGE", triage_dir)
    monkeypatch.setattr(cli_module, "DIR_LAB", lab_dir)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr_dir)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum_dir)

    # Create two PDFs in triage
    long_pdf = triage_dir / "long.pdf"
    long_pdf.write_bytes(b"%PDF-1.4\n")
    short_pdf = triage_dir / "short.pdf"
    short_pdf.write_bytes(b"%PDF-1.4\n")

    # Triage: mock extract_text to control decisions
    def triage_extract_text(path: Path):
        if path.name == "long.pdf":
            return "x" * 600  # large => goes to summary
        if path.name == "short.pdf":
            return "x" * 100  # small => goes to lab
        return None

    monkeypatch.setattr("cartaos.triage.extract_text", triage_extract_text)

    # 1) Run triage
    res_triage = runner.invoke(cli_module.app, ["triage"])
    assert res_triage.exit_code == 0
    # Check moves
    assert (ready_sum_dir / "long.pdf").exists()
    assert (lab_dir / "short.pdf").exists()

    # 2) Run lab for the short file (non-interactive => enqueue to OCR dir)
    res_lab = runner.invoke(cli_module.app, ["lab", str(lab_dir / "short.pdf")])
    assert res_lab.exit_code == 0
    assert (ready_ocr_dir / "short.pdf").exists()

    # OCR: monkeypatch OcrProcessor to copy to output and return True
    class FakeOcr:
        def __init__(self, input_path: Path, output_path: Path) -> None:
            self.input_path = input_path
            self.output_path = output_path

        def process(self) -> bool:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_bytes(b"%PDF-1.4\n")
            return True

    monkeypatch.setattr(cli_module, "OcrProcessor", FakeOcr)

    # 3) Run OCR batch
    res_ocr = runner.invoke(cli_module.app, ["ocr"])
    assert res_ocr.exit_code == 0
    assert (ready_sum_dir / "short.pdf").exists()
    assert not (ready_ocr_dir / "short.pdf").exists()

    # Summarize: patch processor internals to avoid external AI
    # - extract_text -> raw; sanitize -> sanitized; generate_summary_with_retries -> the summary text
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "raw text")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda t: "sanitized text")
    # Mock the async function with a coroutine
    async def mock_generate_summary(*args, **kwargs):
        return "Integration summary"
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)
    # Mock the extract_text function to return test content
    monkeypatch.setattr("cartaos.processor.extract_text", lambda x: "Test content")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda x: x)

    # - force summaries to be written into a vault/Summaries under tmp
    vault = tmp_path / "vault"
    (vault / "Summaries").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(vault))

    # Import the processor module to patch
    import cartaos.processor as proc_mod
    from unittest.mock import MagicMock, patch
    
    # Create a mock for the processor that will handle file movement
    class MockCartaOSProcessor:
        def __init__(self, pdf_path, dry_run=False, debug=False, force_ocr=False):
            self.pdf_path = Path(pdf_path)
            self.dry_run = dry_run
            self.debug = debug
            self.force_ocr = force_ocr
            # Initialize the paths that would normally be set by load_config
            self.processed_pdf_dir = processed_dir
            self.summary_dir = vault / "Summaries"
            # Store the original path for reference
            self.original_pdf_path = Path(pdf_path)
            # Create a mock for the process method that we can check was called
            self._process_mock = MagicMock(side_effect=self._process_impl)

        def load_config(self):
            # Override load_config to use our test directories
            self.processed_pdf_dir = processed_dir
            self.summary_dir = vault / "Summaries"
            self.summary_dir.mkdir(parents=True, exist_ok=True)

        def _move_pdf(self):
            if not self.dry_run:
                print(f"[DEBUG] _move_pdf called with pdf_path: {self.pdf_path}")
                print(f"[DEBUG] processed_pdf_dir: {self.processed_pdf_dir}")
                print(f"[DEBUG] processed_pdf_dir exists: {self.processed_pdf_dir.exists()}")
                
                # Ensure target directory exists
                self.processed_pdf_dir.mkdir(parents=True, exist_ok=True)
                
                # Calculate target path
                target_path = self.processed_pdf_dir / self.pdf_path.name
                print(f"[DEBUG] Moving {self.pdf_path} to {target_path}")
                
                # Verify source exists
                if not self.pdf_path.exists():
                    error_msg = (
                        f"[ERROR] Source file does not exist: {self.pdf_path}\n"
                        f"[ERROR] Current working directory: {Path.cwd()}\n"
                        f"[ERROR] Contents of source directory: {list(self.pdf_path.parent.glob('*'))}"
                    )
                    print(error_msg)
                    raise FileNotFoundError(f"Source file not found: {self.pdf_path}")
                
                # Perform the move
                shutil.move(str(self.pdf_path), str(target_path))
                
                # Update the path to point to the new location
                self.pdf_path = target_path
                print(f"[DEBUG] Move completed. New pdf_path: {self.pdf_path}")
                print(f"[DEBUG] Target exists after move: {target_path.exists()}")

        def _save_summary(self, summary):
            if not self.dry_run:
                self.summary_dir.mkdir(parents=True, exist_ok=True)
                md_filename = f"{self.original_pdf_path.stem}.md"
                md_path = self.summary_dir / md_filename
                print(f"[DEBUG] Saving summary to {md_path}")
                md_path.write_text(summary, encoding="utf-8")
                print(f"[DEBUG] Summary file exists after save: {md_path.exists()}")

        def _process_impl(self):
            # Simulate successful processing
            print("[DEBUG] Mock process() called")
            if not self.dry_run:
                self._save_summary("Integration summary")
                self._move_pdf()
            return True
                
        # This makes the instance callable like a method
        def __call__(self, *args, **kwargs):
            return self._process_mock(*args, **kwargs)
                
        # This makes the instance's process method call _process_impl
        def process(self, *args, **kwargs):
            return self._process_impl()
    
    # Patch the CartaOSProcessor class and related functions
    monkeypatch.setattr(proc_mod, "CartaOSProcessor", MockCartaOSProcessor)
    
    # Mock the async function with a coroutine
    async def mock_generate_summary(*args, **kwargs):
        return "This is a test summary"
    monkeypatch.setattr("cartaos.processor.generate_summary_with_retries", mock_generate_summary)
    # Mock the extract_text function to return test content
    monkeypatch.setattr("cartaos.processor.extract_text", lambda x: "Test content")
    monkeypatch.setattr("cartaos.processor.sanitize", lambda x: x)

    # 4) Run summarize for both PDFs now in ready_sum_dir
    for pdf in [ready_sum_dir / "long.pdf", ready_sum_dir / "short.pdf"]:
        # Debug: Print directory structure before summarization
        print("\n=== Before summarization ===")
        print(f"Working directory: {Path.cwd()}")
        print(f"Ready summary dir contents: {list(ready_sum_dir.glob('*'))}")
        print(f"Processed dir: {processed_dir}")
        print(f"Processed dir exists: {processed_dir.exists()}")
        print(f"Source PDF exists: {pdf.exists()}")

        # Ensure the source file exists before summarizing
        assert pdf.exists(), f"Source file {pdf} does not exist before summarization"

        # Run the summarize command
        print(f"\nRunning summarize on: {pdf}")
        res_sum = runner.invoke(cli_module.app, ["summarize", "--debug", str(pdf)])
        print(f"Summarize command output: {res_sum.output}")
        assert res_sum.exit_code == 0, f"Summarize command failed with output: {res_sum.output}"

        # Debug: Print directory structure after summarization
        print("\n=== After summarization ===")
        print(f"Ready summary dir contents: {list(ready_sum_dir.glob('*'))}")
        print(f"Processed dir contents: {list(processed_dir.glob('*'))}")

        # Verify the source file was moved to processed dir
        processed_file = processed_dir / pdf.name
        print(f"Checking for processed file: {processed_file}")
        print(f"Processed file exists: {processed_file.exists()}")
        if not processed_file.exists():
            print("\n=== Directory structure ===")
            print(f"Current directory: {Path.cwd()}")
            print(f"All files in test directory:")
            for f in tmp_path.rglob('*'):
                print(f"  {f.relative_to(tmp_path)}")
        
        assert processed_file.exists(), f"File {pdf.name} was not moved to processed directory. Expected at: {processed_file}"
    
        # Verify the summary was created
        md_file = vault / "Summaries" / f"{pdf.stem}.md"
        assert md_file.exists(), f"Summary file {md_file} was not created"
        assert md_file.read_text(encoding="utf-8") == "Integration summary"
    
    # Final verification that all files were processed
    assert len(list(processed_dir.glob("*.pdf"))) == 2, "Not all PDFs were processed"
    assert len(list((vault / "Summaries").glob("*.md"))) == 2, "Not all summaries were created"
