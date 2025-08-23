import os
from pathlib import Path

import pytest

import cartaos.config as _conf
from cartaos.processor import CartaOSProcessor


class DummyGen:
    text = "Resumo AI"


@pytest.fixture(autouse=True)
def mock_ai(monkeypatch, tmp_path):
    # força leitura de prompt
    p = tmp_path / "summary_prompt.md"
    p.write_text("Prompt: {text}")
    monkeypatch.setenv("GEMINI_API_KEY", "KEY")
    monkeypatch.setattr(_conf, "PROMPTS_DIR", tmp_path)
    # mock do cliente Gemini
    monkeypatch.setattr("cartaos.processor.generate_summary", lambda t: DummyGen.text)
    return p


def test_process_full_flow(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    # mock extract_text para retornar texto suficiente
    monkeypatch.setattr("cartaos.processor.extract_text", lambda p: "conteúdo longo")
    # monkeypatch move/save
    saved = tmp_path / "07_Processed" / "doc.pdf"
    summary = tmp_path / "07_Processed" / "Summaries" / "doc.md"
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", "")
    proc = CartaOSProcessor(pdf, dry_run=False, debug=False)
    # redireciona pastas para tmp_path
    proc.processed_pdf_dir = tmp_path / "07_Processed"
    proc.summary_dir = tmp_path / "07_Processed" / "Summaries"
    assert proc.process() is True
    assert saved.exists()
    assert summary.exists()
