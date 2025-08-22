from pathlib import Path
import pytest
import tempfile
from cartaos.lab import LabProcessor

def test_run_full(monkeypatch, tmp_path):
    # 1) Fake o extract_pages para sempre retornar uma lista de imagens
    monkeypatch.setattr(
    "cartaos.lab.extract_pages",
    lambda input_path, output_dir: [tmp_path / "page_1.tiff"]
    )

    # 2) Mockamos todos os passos internos para não chamar subprocess reais
    monkeypatch.setattr(
    "cartaos.lab.LabProcessor._run_unpaper_cleanup",
    lambda self, workspace, images: None
    )
    # Mock _create_scantailor_project to return a fake project file path
    monkeypatch.setattr(
        "cartaos.lab.LabProcessor._create_scantailor_project",
        lambda self, project_dir: project_dir / "project.scantailor"
    )

    # Mock _run_manual_correction with the correct signature
    monkeypatch.setattr(
        "cartaos.lab.LabProcessor._run_manual_correction",
        lambda self, workspace, project_file_path: None
    )

    # 3) Fake o recompose_pdf para criar de fato um PDF de saída vazio
    def fake_recompose(images, output_path):
        output_path.write_bytes(b"%PDF-1.4\n")  # create a minimal file
        return output_path

    monkeypatch.setattr(
        "cartaos.lab.recompose_pdf",
        fake_recompose
    )

    # 4) Mock do input() para não travar pedindo Enter
    monkeypatch.setattr("builtins.input", lambda prompt="": "")

    # Mock tempfile.mkdtemp to control the workspace directory
    monkeypatch.setattr(tempfile, "mkdtemp", lambda dir: str(tmp_path / "workspace"))

    # 5) Prepara um PDF e o diretório de saída
    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")   # conteúdo mínimo de PDF
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    # Create a fake corrected image to be found by the processor
    workspace_path = tmp_path / "workspace"
    corrected_images_dir = workspace_path / "out"
    corrected_images_dir.mkdir(parents=True, exist_ok=True)
    (corrected_images_dir / "page_01.tif").touch()

    # 6) Executa o process e valida que retorna True
    processor = LabProcessor(input_path=inp, output_dir=outdir)
    assert processor.process() is True

    # 7) Verify that the final PDF was "recomposed" in the outdir
    final_pdf = outdir / f"corrected_{inp.name}"
    assert final_pdf.exists()
    # E opcionalmente: é um PDF (começa com %PDF)
    assert final_pdf.read_bytes().startswith(b"%PDF")
