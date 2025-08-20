# -*- coding: utf-8 -*-
# backend/tests/test_ocr_more.py

from pathlib import Path
import subprocess
import pytest

from cartaos.ocr import OcrProcessor


def test_ocr_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    inp = tmp_path / "in.pdf"; inp.write_bytes(b"%PDF-1.4\n")
    outp = tmp_path / "out" / "out.pdf"

    class CP:
        def __init__(self):
            self.returncode = 0
            self.stdout = "ok"
            self.stderr = ""
    def fake_run(cmd, check=True, capture_output=True, text=True):
        return CP()
    monkeypatch.setattr(subprocess, "run", fake_run)

    p = OcrProcessor(inp, outp)
    ok = p.process()
    assert ok is True
    assert outp.parent.exists()


def test_ocr_called_process_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    inp = tmp_path / "in.pdf"; inp.write_bytes(b"%PDF-1.4\n")
    outp = tmp_path / "out" / "out.pdf"

    def fake_run(cmd, check=True, capture_output=True, text=True):
        raise subprocess.CalledProcessError(returncode=2, cmd=cmd, stderr="boom")
    monkeypatch.setattr(subprocess, "run", fake_run)

    p = OcrProcessor(inp, outp)
    ok = p.process()
    assert ok is False


def test_ocr_command_not_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    inp = tmp_path / "in.pdf"; inp.write_bytes(b"%PDF-1.4\n")
    outp = tmp_path / "out" / "out.pdf"

    def fake_run(cmd, check=True, capture_output=True, text=True):
        raise FileNotFoundError()
    monkeypatch.setattr(subprocess, "run", fake_run)

    p = OcrProcessor(inp, outp)
    ok = p.process()
    assert ok is False
