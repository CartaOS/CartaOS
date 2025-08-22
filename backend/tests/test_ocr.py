import subprocess
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from cartaos.ocr import OcrProcessor

@pytest.fixture
def paths(tmp_path):
    inp = tmp_path / "input.pdf"
    out = tmp_path / "output.pdf"
    inp.write_bytes(b"%PDF-1.4")  # create a valid empty PDF
    return inp, out

def test_process_success(monkeypatch, paths):
    inp, out = paths
    # mock com os atributos esperados: returncode, stdout e stderr
    fake_result = MagicMock(returncode=0, stdout="OCR OK", stderr="")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: fake_result)
    
    processor = OcrProcessor(inp, out)
    assert processor.process() is True
    assert out.parent.exists()  # 04_ReadyForSummary or the directory you configured


def test_process_failure(monkeypatch, paths):
    inp, out = paths
    # simula ocrmypdf retornando erro
    def raise_called(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd="ocrmypdf", stderr="Erro de OCR")
    monkeypatch.setattr(subprocess, "run", raise_called)

    processor = OcrProcessor(inp, out)
    assert processor.process() is False
    assert not out.exists()

def test_process_command_not_found(monkeypatch, paths):
    inp, out = paths
    # simula comando não encontrado
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError()))

    processor = OcrProcessor(inp, out)
    assert processor.process() is False
    assert not out.exists()
