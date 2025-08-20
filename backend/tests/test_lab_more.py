# -*- coding: utf-8 -*-
# backend/tests/test_lab_more.py

from pathlib import Path
import tempfile
import pytest

from cartaos.lab import LabProcessor


def test_lab_no_corrected_images_returns_false(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Ensure deterministic workspace path so we can control its contents
    monkeypatch.setattr(tempfile, "mkdtemp", lambda dir: str(tmp_path / "workspace"))

    # Create the workspace directory since our mkdtemp stub doesn't create it
    (tmp_path / "workspace").mkdir(parents=True, exist_ok=True)

    # Mock extract_pages to simulate initial extraction
    monkeypatch.setattr(
        "cartaos.lab.extract_pages",
        lambda input_path, output_dir: [tmp_path / "page_1.tiff"]
    )

    # Avoid side effects: do nothing in these steps
    monkeypatch.setattr("cartaos.lab.LabProcessor._run_unpaper_cleanup", lambda self, workspace, images: None)
    monkeypatch.setattr("cartaos.lab.LabProcessor._create_scantailor_project", lambda self, project_dir: Path(project_dir) / "project.scantailor")
    monkeypatch.setattr("cartaos.lab.LabProcessor._run_manual_correction", lambda self, workspace, project_file_path: None)

    # Prepare input and output
    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    # Intentionally DO NOT create any corrected images under workspace/out
    # so that LabProcessor finds an empty list and returns False

    proc = LabProcessor(input_path=inp, output_dir=outdir)
    ok = proc.process()

    assert ok is False
    # No output PDF should be created
    assert not (outdir / f"corrected_{inp.name}").exists()
