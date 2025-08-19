# -*- coding: utf-8 -*-
# backend/tests/test_cli_extended.py

from pathlib import Path
from typer.testing import CliRunner
import cartaos.cli as cli_module
import types

runner = CliRunner()


def test_lab_non_interactive_enqueues_pdf(tmp_path, monkeypatch):
    # point CLI dirs to temp
    ready_ocr = tmp_path / "04_ReadyForOCR"
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr)

    # create input pdf
    inp = tmp_path / "sample.pdf"
    inp.write_bytes(b"%PDF-1.4\n")

    # Run 'lab' (CliRunner stdin is non-interactive by default)
    result = runner.invoke(cli_module.app, ["lab", str(inp)])
    assert result.exit_code == 0

    target = ready_ocr / inp.name
    assert target.exists()
    assert target.read_bytes().startswith(b"%PDF-1.4")
    assert "Enqueued for OCR" in result.output


def test_triage_reports_output(tmp_path, monkeypatch):
    # point CLI dirs to temp
    triage = tmp_path / "02_Triage"; triage.mkdir()
    lab = tmp_path / "03_Lab"; lab.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"; ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_TRIAGE", triage)
    monkeypatch.setattr(cli_module, "DIR_LAB", lab)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    # fake TriageProcessor
    class FakeTriage:
        def __init__(self, input_dir, summary_dir, lab_dir):
            self.input_dir = input_dir
            self.summary_dir = summary_dir
            self.lab_dir = lab_dir
        def process(self):
            return {
                "moved_to_summary": ["a.pdf"],
                "moved_to_lab": ["b.pdf"],
                "ignored": ["c.txt"],
            }

    monkeypatch.setattr(cli_module, "TriageProcessor", FakeTriage)

    result = runner.invoke(cli_module.app, ["triage"]) 
    assert result.exit_code == 0
    assert "Moved to 'Ready for Summary'" in result.output
    assert "Moved to 'Lab'" in result.output
    assert "Ignored (unsupported file type)" in result.output


def test_ocr_single_file_success(tmp_path, monkeypatch):
    ready_ocr = tmp_path / "04_ReadyForOCR"; ready_ocr.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"; ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    inp = tmp_path / "doc.pdf"; inp.write_bytes(b"%PDF-1.4\n")

    class FakeOcr:
        def __init__(self, input_path, output_path):
            self.input_path = input_path
            self.output_path = output_path
        def process(self):
            # Simulate success
            self.output_path.write_bytes(b"%PDF-1.4\n")
            return True

    monkeypatch.setattr(cli_module, "OcrProcessor", FakeOcr)

    result = runner.invoke(cli_module.app, ["ocr", str(inp)])
    assert result.exit_code == 0
    out_pdf = ready_sum / inp.name
    assert out_pdf.exists()
    assert "OCR complete:" in result.output


def test_ocr_single_file_not_found(tmp_path, monkeypatch):
    ready_ocr = tmp_path / "04_ReadyForOCR"; ready_ocr.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"; ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    missing = tmp_path / "missing.pdf"
    result = runner.invoke(cli_module.app, ["ocr", str(missing)])
    assert result.exit_code == 0  # non-interactive path shouldn't exit non-zero
    assert "File not found" in result.output


def test_summarize_success_and_failure(tmp_path, monkeypatch):
    pdf = tmp_path / "paper.pdf"; pdf.write_bytes(b"%PDF-1.4\n")

    class FakeProc:
        def __init__(self, pdf_path, dry_run=False, debug=False, force_ocr=False):
            self.pdf_path = pdf_path
            self._ok = True
            self.captured_warnings = []
        def process(self):
            return self._ok

    # First run: success
    monkeypatch.setattr(cli_module, "CartaOSProcessor", FakeProc)
    result_ok = runner.invoke(cli_module.app, ["summarize", str(pdf)])
    assert result_ok.exit_code == 0
    assert "completed successfully" in result_ok.output

    # Second run: simulate failure
    def failing_ctor(pdf_path, dry_run=False, debug=False, force_ocr=False):
        inst = FakeProc(pdf_path, dry_run, debug, force_ocr)
        inst._ok = False
        return inst
    monkeypatch.setattr(cli_module, "CartaOSProcessor", failing_ctor)

    result_fail = runner.invoke(cli_module.app, ["summarize", str(pdf)])
    assert result_fail.exit_code == 0  # non-interactive should not exit with error
    assert "Summary failed" in result_fail.output
