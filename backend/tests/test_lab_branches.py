# -*- coding: utf-8 -*-
# backend/tests/test_lab_branches.py

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cartaos.lab import LabProcessor


def _setup_basic_mocks(monkeypatch, tmp_path):
    """Common mocks for LabProcessor.process() to avoid external calls."""

    # deterministic workspace path
    def _mkdtemp(dir):
        p = tmp_path / "workspace"
        p.mkdir(parents=True, exist_ok=True)
        return str(p)

    monkeypatch.setattr(tempfile, "mkdtemp", _mkdtemp)

    # stub extract_pages to return one image by default
    monkeypatch.setattr(
        "cartaos.lab.extract_pages",
        lambda input_path, out_dir: [tmp_path / "page_1.tiff"],
    )

    # no-op unpaper
    monkeypatch.setattr(
        "cartaos.lab.LabProcessor._run_unpaper_cleanup",
        lambda self, workspace, images: None,
    )

    # return a valid project file path
    monkeypatch.setattr(
        "cartaos.lab.LabProcessor._create_scantailor_project",
        lambda self, project_dir: Path(project_dir) / "project.scantailor",
    )

    # no-op manual correction
    monkeypatch.setattr(
        "cartaos.lab.LabProcessor._run_manual_correction",
        lambda self, workspace, project_file_path: None,
    )


def test_process_returns_false_when_no_corrected_images(monkeypatch, tmp_path):
    _setup_basic_mocks(monkeypatch, tmp_path)

    # ensure workspace/out exists but is empty (no .tif files)
    workspace = tmp_path / "workspace"
    (workspace / "out").mkdir(parents=True, exist_ok=True)

    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    proc = LabProcessor(inp, outdir)
    assert proc.process() is False


def test_process_returns_false_when_project_creation_fails(monkeypatch, tmp_path):
    _setup_basic_mocks(monkeypatch, tmp_path)

    # make project creation return None
    monkeypatch.setattr(
        "cartaos.lab.LabProcessor._create_scantailor_project",
        lambda self, project_dir: None,
    )

    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    proc = LabProcessor(inp, outdir)
    assert proc.process() is False


def test_process_returns_false_when_extract_pages_raises(monkeypatch, tmp_path):
    _setup_basic_mocks(monkeypatch, tmp_path)

    # raise on extract_pages
    def raise_extract(_in, _out):
        raise RuntimeError("boom")

    monkeypatch.setattr("cartaos.lab.extract_pages", raise_extract)

    # capture cleanup
    called = {"rmtree": False}

    def fake_rmtree(p):
        called["rmtree"] = True

    monkeypatch.setattr("shutil.rmtree", fake_rmtree)

    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    proc = LabProcessor(inp, outdir)
    assert proc.process() is False
    assert called["rmtree"] is True


def test_process_returns_false_when_recompose_fails(monkeypatch, tmp_path):
    _setup_basic_mocks(monkeypatch, tmp_path)

    # create at least one corrected image so we reach recompose
    workspace = tmp_path / "workspace"
    out_dir = workspace / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "p1.tif").write_bytes(b"TIFF")

    # make recompose_pdf return None
    monkeypatch.setattr("cartaos.lab.recompose_pdf", lambda images, output: None)

    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    proc = LabProcessor(inp, outdir)
    assert proc.process() is False


def test_process_handles_exception_in_manual_correction(monkeypatch, tmp_path):
    _setup_basic_mocks(monkeypatch, tmp_path)

    # create corrected image so we would get past earlier checks
    workspace = tmp_path / "workspace"
    out_dir = workspace / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "p1.tif").write_bytes(b"TIFF")

    # make manual correction raise
    def raise_manual(self, workspace, project_file_path):
        raise RuntimeError("scantailor crashed")

    monkeypatch.setattr("cartaos.lab.LabProcessor._run_manual_correction", raise_manual)

    # capture cleanup
    cleaned = {"done": False}

    def fake_rmtree(p):
        cleaned["done"] = True

    monkeypatch.setattr("shutil.rmtree", fake_rmtree)

    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    proc = LabProcessor(inp, outdir)
    assert proc.process() is False
    assert cleaned["done"] is True


def test_process_success_calls_cleanup(monkeypatch, tmp_path):
    _setup_basic_mocks(monkeypatch, tmp_path)

    # ensure a corrected image exists so success path is taken
    workspace = tmp_path / "workspace"
    out_dir = workspace / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "p1.tif").write_bytes(b"TIFF")

    # recompose returns output path
    def fake_recompose(images, output):
        output.write_bytes(b"%PDF-1.4\n")
        return output

    monkeypatch.setattr("cartaos.lab.recompose_pdf", fake_recompose)

    # spy cleanup
    called = {"rmtree": False}

    def fake_rmtree(p):
        called["rmtree"] = True

    monkeypatch.setattr("shutil.rmtree", fake_rmtree)

    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    proc = LabProcessor(inp, outdir)
    assert proc.process() is True
    assert called["rmtree"] is True


def test_process_unpaper_raises_then_cleanup(monkeypatch, tmp_path):
    _setup_basic_mocks(monkeypatch, tmp_path)

    # override unpaper to raise
    def raise_unpaper(self, workspace, images):
        raise RuntimeError("unpaper failed")

    monkeypatch.setattr("cartaos.lab.LabProcessor._run_unpaper_cleanup", raise_unpaper)

    # spy cleanup
    cleaned = {"done": False}

    def fake_rmtree(p):
        cleaned["done"] = True

    monkeypatch.setattr("shutil.rmtree", fake_rmtree)

    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    proc = LabProcessor(inp, outdir)
    assert proc.process() is False
    assert cleaned["done"] is True
