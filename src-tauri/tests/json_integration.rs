use std::path::PathBuf;
use std::process::Command;

#[test]
fn triage_cli_json_is_pure_and_parses() {
    // Determine project root: src-tauri is the manifest dir; parent is repo root
    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let project_root = manifest_dir
        .parent()
        .expect("src-tauri has a parent project root")
        .to_path_buf();

    let backend_dir = project_root.join("backend");

    // Resolve python: prefer Poetry venv, else PYTHON env, else python3
    let python: PathBuf = match Command::new("poetry")
        .arg("env")
        .arg("info")
        .arg("--path")
        .current_dir(&backend_dir)
        .output()
    {
        Ok(poetry) if poetry.status.success() => {
            let venv = String::from_utf8_lossy(&poetry.stdout).trim().to_string();
            PathBuf::from(venv).join("bin").join("python")
        }
        _ => {
            if let Ok(py) = std::env::var("PYTHON") {
                PathBuf::from(py)
            } else {
                PathBuf::from("python3")
            }
        }
    };

    // Quick availability check; skip if not found
    let py_check = Command::new(&python).arg("--version").output();
    if py_check.is_err() {
        eprintln!("SKIP: No usable python interpreter found for integration test");
        return;
    }

    // Run triage --json
    let cli = project_root.join("backend/cartaos/cli.py");
    let out = Command::new(&python)
        .arg(&cli)
        .arg("triage")
        .arg("--json")
        .current_dir(&project_root)
        .output()
        .expect("run cli triage json");

    assert!(
        out.status.success(),
        "triage failed: {}",
        String::from_utf8_lossy(&out.stderr)
    );

    let stdout = String::from_utf8_lossy(&out.stdout);

    // Ensure JSON purity (no leading banner/newlines outside JSON)
    let parsed: serde_json::Value = serde_json::from_str(&stdout).expect("valid json output");
    assert_eq!(parsed["status"], "success");
    assert!(parsed["data"].get("counts").is_some());
}
