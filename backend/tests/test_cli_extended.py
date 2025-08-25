# -*- coding: utf-8 -*-
# backend/tests/test_cli_extended.py

import types
from pathlib import Path

import pytest
from typer.testing import CliRunner

import cartaos.cli as cli_module

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


def test_setup_when_env_exists_prints_message(tmp_path, monkeypatch):
    # redirect backend root
    fake_backend_root = tmp_path / "backend"
    fake_backend_root.mkdir(parents=True, exist_ok=True)
    fake_cli_file = fake_backend_root / "cartaos" / "cli.py"
    fake_cli_file.parent.mkdir(parents=True, exist_ok=True)
    fake_cli_file.write_text("# fake cli file path\n")
    monkeypatch.setattr(cli_module, "__file__", str(fake_cli_file))

    env_path = fake_backend_root / ".env"
    env_path.write_text('GEMINI_API_KEY="X"\n', encoding="utf-8")

    result = runner.invoke(
        cli_module.app, ["setup", "--non-interactive"]
    )  # should detect exists and just return
    assert result.exit_code == 0
    assert ".env file already exists" in result.output


def test_triage_reports_output(tmp_path, monkeypatch):
    # point CLI dirs to temp
    triage = tmp_path / "02_Triage"
    triage.mkdir()
    lab = tmp_path / "03_Lab"
    lab.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"
    ready_sum.mkdir()

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
    ready_ocr = tmp_path / "04_ReadyForOCR"
    ready_ocr.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"
    ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    inp = tmp_path / "doc.pdf"
    inp.write_bytes(b"%PDF-1.4\n")

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
    # original should be removed on success (best effort)
    assert not inp.exists()


def test_ocr_single_file_not_found(tmp_path, monkeypatch):
    ready_ocr = tmp_path / "04_ReadyForOCR"
    ready_ocr.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"
    ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    missing = tmp_path / "missing.pdf"
    result = runner.invoke(cli_module.app, ["ocr", str(missing)])
    assert result.exit_code == 0  # non-interactive path shouldn't exit non-zero
    assert "File not found" in result.output


def test_summarize_success_and_failure(tmp_path, monkeypatch):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

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


def test_lab_interactive_processor_failure_exits_nonzero(tmp_path, monkeypatch):
    # simulate interactive TTY by replacing sys in cli module
    fake_sys = types.SimpleNamespace(stdin=types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(cli_module, "sys", fake_sys)

    # set OCR dir
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", tmp_path / "04_ReadyForOCR")

    # valid input pdf
    inp = tmp_path / "bad.pdf"
    inp.write_bytes(b"%PDF-1.4\n")

    class FakeLab:
        def __init__(self, input_path, output_dir):
            self.input_path = input_path
            self.output_dir = output_dir

        def process(self):
            return False

    monkeypatch.setattr(cli_module, "LabProcessor", FakeLab)

    result = runner.invoke(cli_module.app, ["lab", str(inp)])
    assert result.exit_code == 1
    assert "Lab processing reported failure." in result.output


def test_lab_exception_non_interactive_does_not_exit(tmp_path, monkeypatch):
    # non-interactive (default) should enqueue and return without invoking LabProcessor
    ready_ocr = tmp_path / "04_ReadyForOCR"
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr)
    inp = tmp_path / "bad.pdf"
    inp.write_bytes(b"%PDF-1.4\n")

    class BoomLab:
        def __init__(self, input_path, output_dir):
            pass

        def process(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(cli_module, "LabProcessor", BoomLab)

    result = runner.invoke(cli_module.app, ["lab", str(inp)])
    assert result.exit_code == 0
    # Should have enqueued without error
    target = ready_ocr / inp.name
    assert target.exists()
    assert "Enqueued for OCR" in result.output


def test_ocr_interactive_failure_exits_nonzero(tmp_path, monkeypatch):
    # simulate interactive TTY by replacing sys in cli module
    fake_sys = types.SimpleNamespace(stdin=types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(cli_module, "sys", fake_sys)

    ready_ocr = tmp_path / "04_ReadyForOCR"
    ready_ocr.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"
    ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    inp = tmp_path / "doc_fail.pdf"
    inp.write_bytes(b"%PDF-1.4\n")

    class FailOcr:
        def __init__(self, input_path, output_path):
            self.input_path = input_path
            self.output_path = output_path

        def process(self):
            return False

    monkeypatch.setattr(cli_module, "OcrProcessor", FailOcr)

    result = runner.invoke(cli_module.app, ["ocr", str(inp)])
    assert result.exit_code == 1
    assert "OCR failed for" in result.output


def test_triage_non_interactive_exception_does_not_exit(tmp_path, monkeypatch):
    # non-interactive (default CliRunner stdin)
    triage = tmp_path / "02_Triage"
    triage.mkdir()
    lab = tmp_path / "03_Lab"
    lab.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"
    ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_TRIAGE", triage)
    monkeypatch.setattr(cli_module, "DIR_LAB", lab)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    class BoomTriage:
        def __init__(self, input_dir, summary_dir, lab_dir):
            pass

        def process(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(cli_module, "TriageProcessor", BoomTriage)

    result = runner.invoke(cli_module.app, ["triage"])
    assert result.exit_code == 0  # non-interactive should not exit non-zero
    assert "An error occurred during triage" in result.output


def test_triage_interactive_exception_exits_nonzero(tmp_path, monkeypatch):
    fake_sys = types.SimpleNamespace(stdin=types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(cli_module, "sys", fake_sys)

    triage = tmp_path / "02_Triage"
    triage.mkdir()
    lab = tmp_path / "03_Lab"
    lab.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"
    ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_TRIAGE", triage)
    monkeypatch.setattr(cli_module, "DIR_LAB", lab)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    class BoomTriage:
        def __init__(self, input_dir, summary_dir, lab_dir):
            pass

        def process(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(cli_module, "TriageProcessor", BoomTriage)

    result = runner.invoke(cli_module.app, ["triage"])
    assert result.exit_code == 1
    assert "An error occurred during triage" in result.output


def test_summarize_interactive_failure_and_warning_banner(tmp_path, monkeypatch):
    fake_sys = types.SimpleNamespace(stdin=types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(cli_module, "sys", fake_sys)

    pdf = tmp_path / "warn.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    class WarnProc:
        def __init__(self, pdf_path, dry_run=False, debug=False, force_ocr=False):
            self.pdf_path = pdf_path
            self.captured_warnings = ["low quality"]

        def process(self):
            return True

    monkeypatch.setattr(cli_module, "CartaOSProcessor", WarnProc)
    result_warn = runner.invoke(cli_module.app, ["summarize", str(pdf)])
    assert result_warn.exit_code == 0
    assert "DOCUMENT QUALITY WARNING" in result_warn.output

    # Now failing path should exit non-zero when interactive
    class FailProc:
        def __init__(self, pdf_path, dry_run=False, debug=False, force_ocr=False):
            self.pdf_path = pdf_path

        def process(self):
            return False

    monkeypatch.setattr(cli_module, "CartaOSProcessor", FailProc)
    result_fail = runner.invoke(cli_module.app, ["summarize", str(pdf)])
    assert result_fail.exit_code == 1
    assert "Summary failed" in result_fail.output


def test_summarize_non_interactive_exception_does_not_exit(tmp_path, monkeypatch):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")

    class BoomProc:
        def __init__(self, pdf_path, dry_run=False, debug=False, force_ocr=False):
            pass

        def process(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(cli_module, "CartaOSProcessor", BoomProc)

    result = runner.invoke(cli_module.app, ["summarize", str(pdf)])
    assert result.exit_code == 0
    assert "Fatal error during processing" in result.output


def test_ocr_batch_no_files_message(tmp_path, monkeypatch):
    ready_ocr = tmp_path / "04_ReadyForOCR"
    ready_ocr.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"
    ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    # No PDFs present
    result = runner.invoke(cli_module.app, ["ocr"])
    assert result.exit_code == 0
    assert "No PDF files found" in result.output


def test_ocr_batch_mixed_results(tmp_path, monkeypatch: pytest.MonkeyPatch):
    ready_ocr = tmp_path / "04_ReadyForOCR"
    ready_ocr.mkdir()
    ready_sum = tmp_path / "05_ReadyForSummary"
    ready_sum.mkdir()

    monkeypatch.setattr(cli_module, "DIR_READY_FOR_OCR", ready_ocr)
    monkeypatch.setattr(cli_module, "DIR_READY_FOR_SUMMARY", ready_sum)

    pdf_ok = ready_ocr / "ok.pdf"
    pdf_ok.write_bytes(b"%PDF-1.4\n")
    pdf_fail = ready_ocr / "fail.pdf"
    pdf_fail.write_bytes(b"%PDF-1.4\n")

    class MixedOcr:
        def __init__(self, input_path, output_path):
            self.input_path = input_path
            self.output_path = output_path

        def process(self):
            if self.input_path.name == "ok.pdf":
                self.output_path.parent.mkdir(parents=True, exist_ok=True)
                self.output_path.write_bytes(b"%PDF-1.4\n")
                return True
            return False

    monkeypatch.setattr(cli_module, "OcrProcessor", MixedOcr)

    result = runner.invoke(cli_module.app, ["ocr"])
    assert result.exit_code == 0
    # ok.pdf should be removed from queue and produced at summary
    assert not pdf_ok.exists()
    assert (ready_sum / "ok.pdf").exists()
    # fail.pdf should remain and a failure message printed
    assert pdf_fail.exists()
    assert "Failed to process fail.pdf" in result.output
