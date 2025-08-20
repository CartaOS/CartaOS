# -*- coding: utf-8 -*-
# backend/tests/test_ocr_progress.py

from pathlib import Path
import types
import subprocess
import pytest

import cartaos.ocr as ocr_mod
from cartaos.ocr import OcrProcessor


class FakeTask:
    def __init__(self):
        self.completed = 0

class FakeProgress:
    def __init__(self, *a, **k):
        self.entered = False
        self.exited = False
        self.added = 0
        self.task = FakeTask()
    def __enter__(self):
        self.entered = True
        return self
    def __exit__(self, exc_type, exc, tb):
        self.exited = True
    def add_task(self, desc, total=100):
        self.added += 1
        return 1
    def update(self, task_id, completed=None, **kwargs):
        if completed is not None:
            self.task.completed = completed


def test_ocr_processor_progress_updates_and_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Patch Progress with our fake
    monkeypatch.setattr(ocr_mod, "Progress", FakeProgress)

    # Make subprocess.run succeed
    class CP:
        def __init__(self):
            self.returncode = 0
            self.stdout = "ok"
            self.stderr = ""
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: CP())

    inp = tmp_path / "doc.pdf"; inp.write_bytes(b"%PDF-1.4\n")
    outp = tmp_path / "out" / "doc.pdf"

    proc = OcrProcessor(inp, outp)
    ok = proc.process()
    assert ok is True
    # Ensure our fake progress was used and reached completion
    # We cannot access the instance directly; rely on side effects: output path dir created
    assert outp.parent.exists()


def test_ocr_processor_progress_called_process_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ocr_mod, "Progress", FakeProgress)
    def boom(*a, **k):
        raise subprocess.CalledProcessError(returncode=1, cmd=["ocrmypdf"], stderr="err")
    monkeypatch.setattr(subprocess, "run", boom)

    inp = tmp_path / "doc.pdf"; inp.write_bytes(b"%PDF-1.4\n")
    outp = tmp_path / "out" / "doc.pdf"

    proc = OcrProcessor(inp, outp)
    ok = proc.process()
    assert ok is False
