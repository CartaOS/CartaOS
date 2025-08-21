# tests/test_cli_json_ocr_sum.py
import json
import os
import subprocess
import sys
from pathlib import Path


def run_cli(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    cli_path = repo_root / "backend" / "cartaos" / "cli.py"
    return subprocess.run(
        [sys.executable, str(cli_path), *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(repo_root / "backend")},
    )


a = None


def test_cli_ocr_json_reports_queue(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]

    # Ensure directories
    (repo_root / "04_ReadyForOCR").mkdir(parents=True, exist_ok=True)
    (repo_root / "05_ReadyForSummary").mkdir(parents=True, exist_ok=True)

    # Create some queued PDFs
    (repo_root / "04_ReadyForOCR" / "q1.pdf").write_bytes(b"%PDF-1.4\n")
    (repo_root / "04_ReadyForOCR" / "q2.pdf").write_bytes(b"%PDF-1.4\n")

    proc = run_cli(repo_root, "ocr", "--json")
    assert proc.stdout, proc.stderr
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert payload["status"] == "success"
    data = payload["data"]
    assert sorted(data["queued_for_ocr"]) == ["q1.pdf", "q2.pdf"]
    assert data["counts"]["queued"] == 2


def test_cli_summarize_json_reports_intent(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]

    # Ensure directories
    (repo_root / "05_ReadyForSummary").mkdir(parents=True, exist_ok=True)

    # Create a dummy pdf target
    target = repo_root / "05_ReadyForSummary" / "doc.pdf"
    target.write_bytes(b"%PDF-1.4\n")

    proc = run_cli(repo_root, "summarize", str(target), "--json", "--dry-run")
    assert proc.stdout, proc.stderr
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert payload["status"] == "success"
    data = payload["data"]
    assert data["target_file"] == "doc.pdf"
    assert data["options"]["dry_run"] is True
