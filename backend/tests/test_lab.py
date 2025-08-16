from pathlib import Path
import pytest
from cartaos.lab import LabProcessor

def test_run_full(monkeypatch, tmp_path):
    # 1) Fake o extract_pages para sempre retornar uma lista de imagens
    monkeypatch.setattr(
        "cartaos.lab.extract_pages",
        lambda pdf_path: [tmp_path / "page_1.tiff"]
    )

    # 2) Mockamos todos os passos internos para não chamar subprocess reais
    monkeypatch.setattr(
        "cartaos.lab.LabProcessor._run_unpaper_cleanup",
        lambda self, workspace, images: None
    )
    monkeypatch.setattr(
        "cartaos.lab.LabProcessor._generate_scantailor_project",
        lambda self, workspace, images: None
    )
    monkeypatch.setattr(
        "cartaos.lab.LabProcessor._run_manual_correction",
        lambda self, workspace, images: None
    )

    # 3) Fake o recompose_pdf para criar de fato um PDF de saída vazio
    def fake_recompose(images, output_dir, input_path):
        out_file = output_dir / input_path.name
        out_file.write_bytes(b"%PDF-1.4\n")  # cria um arquivo mínimo
        return out_file

    monkeypatch.setattr(
        "cartaos.lab.recompose_pdf",
        fake_recompose
    )

    # 4) Mock do input() para não travar pedindo Enter
    monkeypatch.setattr("builtins.input", lambda prompt="": "")

    # 5) Prepara um PDF e o diretório de saída
    inp = tmp_path / "input.pdf"
    inp.write_bytes(b"%PDF-1.4\n")   # conteúdo mínimo de PDF
    outdir = tmp_path / "outdir"
    outdir.mkdir()

    # 6) Executa o process e valida que retorna True
    processor = LabProcessor(input_path=inp, output_dir=outdir)
    assert processor.process() is True

    # 7) Verifica que o PDF final foi “recomposed” no outdir
    final_pdf = outdir / inp.name
    assert final_pdf.exists()
    # E opcionalmente: é um PDF (começa com %PDF)
    assert final_pdf.read_bytes().startswith(b"%PDF")
