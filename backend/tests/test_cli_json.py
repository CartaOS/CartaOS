# tests/test_cli_json.py
import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_triage_json_outputs_structured_payload(tmp_path: Path):
    # Run the CLI in JSON mode; it should not crash and should print valid JSON
    repo_root = Path(__file__).resolve().parents[2]
    cli_path = repo_root / "backend" / "cartaos" / "cli.py"

    # Ensure pipeline directories exist so the command can run safely
    for stage in [
        "00_Inbox",
        "02_Triage",
        "03_Lab",
        "04_ReadyForOCR",
        "05_ReadyForSummary",
        "06_TooLarge",
        "07_Processed",
    ]:
        (repo_root / stage).mkdir(parents=True, exist_ok=True)

    proc = subprocess.run(
        [sys.executable, str(cli_path), "triage", "--json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
        env={**dict(**os.environ), "PYTHONPATH": str(repo_root / "backend")},
    )

    assert proc.stdout, proc.stderr
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert payload["status"] in {"success", "error"}
    # Must include one of these keys
    assert ("data" in payload) or ("message" in payload)
