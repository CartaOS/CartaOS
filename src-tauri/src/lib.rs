// ----- IPC JSON Types -----
#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct TriageCounts {
    pub triage: usize,
}

/// Import external files into 02_Triage by copying them into the project structure.
#[tauri::command]
async fn import_to_triage(paths: Vec<String>) -> Result<(), Error> {
    let project_root = get_project_root()?;
    let triage_dir = project_root.join("02_Triage");
    for p in paths {
        let src = PathBuf::from(&p);
        if !src.exists() {
            return Err(Error::CommandFailed(format!("Source not found: {}", p)));
        }
        let file_name = src
            .file_name()
            .and_then(|s| s.to_str())
            .ok_or_else(|| Error::CommandFailed("Invalid source file name".to_string()))?
            .to_string();
        let dest = triage_dir.join(file_name);
        // Copy file; overwrite if exists by removing then copying
        if dest.exists() {
            fs::remove_file(&dest).map_err(|e| Error::FileWrite(e.to_string()))?;
        }
        fs::copy(&src, &dest).map_err(|e| Error::FileWrite(e.to_string()))?;
    }
    Ok(())
}

/// Run OCR for a single file in 04_ReadyForOCR.
#[tauri::command]
async fn run_ocr_single(file_name: String) -> Result<String, Error> {
    let project_root = get_project_root()?;
    let script_path = project_root.join("backend/cartaos/cli.py");
    // Basic validation: avoid separators or traversal
    if file_name.contains('/') || file_name.contains('\\') || file_name.contains("..") {
        return Err(Error::CommandFailed("Invalid file name".to_string()));
    }
    let target_path = project_root.join("04_ReadyForOCR").join(&file_name);
    if !target_path.exists() {
        return Err(Error::CommandFailed(format!("File not found: {}", file_name)));
    }
    let poetry_python_path = get_poetry_python_path()?;

    let output = Command::new(&poetry_python_path)
        .arg(&script_path)
        .arg("ocr")
        .arg(&target_path)
        .current_dir(&project_root)
        .output()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(Error::CommandFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ))
    }
}

/// Typed variants that deserialize JSON strings into typed envelopes
#[tauri::command]
async fn run_triage_json_typed() -> Result<IpcEnvelope<TriageData>, Error> {
    let raw = run_triage_json().await?;
    let parsed: IpcEnvelope<TriageData> =
        serde_json::from_str(&raw).map_err(|e| Error::CommandFailed(e.to_string()))?;
    Ok(parsed)
}

#[tauri::command]
async fn run_ocr_json_typed() -> Result<IpcEnvelope<OcrData>, Error> {
    let raw = run_ocr_json().await?;
    let parsed: IpcEnvelope<OcrData> =
        serde_json::from_str(&raw).map_err(|e| Error::CommandFailed(e.to_string()))?;
    Ok(parsed)
}

#[tauri::command]
async fn run_summarize_json_typed(
    file_name: String,
    dry_run: bool,
    debug: bool,
    force_ocr: bool,
) -> Result<IpcEnvelope<SummarizeData>, Error> {
    let raw = run_summarize_json(file_name, dry_run, debug, force_ocr).await?;
    let parsed: IpcEnvelope<SummarizeData> =
        serde_json::from_str(&raw).map_err(|e| Error::CommandFailed(e.to_string()))?;
    Ok(parsed)
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct OcrCounts {
    pub queued: usize,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct OcrData {
    pub queued_for_ocr: Vec<String>,
    pub counts: OcrCounts,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct SummarizeOptions {
    pub dry_run: bool,
    pub debug: bool,
    pub force_ocr: bool,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct SummarizeData {
    pub target_file: String,
    pub options: SummarizeOptions,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct IpcEnvelope<T> {
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<T>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

/// Run OCR command in JSON mode.
#[tauri::command]
async fn run_ocr_json() -> Result<String, Error> {
    let project_root = get_project_root()?;
    let script_path = project_root.join("backend/cartaos/cli.py");
    let poetry_python_path = get_poetry_python_path()?;

    let output = Command::new(&poetry_python_path)
        .arg(&script_path)
        .arg("ocr")
        .arg("--json")
        .current_dir(&project_root)
        .output()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(Error::CommandFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ))
    }
}

/// Run summarize command in JSON mode for a single file.
#[tauri::command]
async fn run_summarize_json(
    file_name: String,
    dry_run: bool,
    debug: bool,
    force_ocr: bool,
) -> Result<String, Error> {
    let project_root = get_project_root()?;
    let script_path = project_root.join("backend/cartaos/cli.py");
    // basic path validation: disallow separators and traversal
    if file_name.contains('/') || file_name.contains('\\') || file_name.contains("..") {
        return Err(Error::CommandFailed("Invalid file name".to_string()));
    }
    let target_path = project_root.join("05_ReadyForSummary").join(&file_name);
    if !target_path.exists() {
        return Err(Error::CommandFailed(format!(
            "File not found: {}",
            file_name
        )));
    }
    let poetry_python_path = get_poetry_python_path()?;

    let mut cmd = Command::new(&poetry_python_path);
    cmd.arg(&script_path)
        .arg("summarize")
        .arg(&target_path)
        .arg("--json");
    if dry_run {
        cmd.arg("--dry-run");
    }
    if debug {
        cmd.arg("--debug");
    }
    if force_ocr {
        cmd.arg("--force-ocr");
    }

    let output = cmd
        .current_dir(&project_root)
        .output()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(Error::CommandFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ))
    }
}

/// Run the triage command in JSON mode.
///
/// Calls the backend Python script with `triage --json` and returns the stdout JSON string.
#[tauri::command]
async fn run_triage_json() -> Result<String, Error> {
    let project_root = get_project_root()?;
    let script_path = project_root.join("backend/cartaos/cli.py");
    let poetry_python_path = get_poetry_python_path()?;

    let output = Command::new(&poetry_python_path)
        .arg(script_path)
        .arg("triage")
        .arg("--json")
        .current_dir(&project_root)
        .output()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(Error::CommandFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ))
    }
}

// ----- Tests -----
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_deserialize_triage_success_payload() {
        let json = r#"{
            "status": "success",
            "data": {
                "triage_files": ["a.pdf", "b.pdf"],
                "counts": { "triage": 2 }
            }
        }"#;
        let parsed: IpcResponse = serde_json::from_str(json).expect("valid json");
        match parsed {
            IpcResponse::Success { data } => {
                assert_eq!(data.triage_files.len(), 2);
                assert_eq!(data.counts.triage, 2);
            }
            _ => panic!("expected success"),
        }
    }

    #[test]
    fn test_deserialize_triage_error_payload() {
        let json = r#"{ "status": "error", "message": "boom" }"#;
        let parsed: IpcResponse = serde_json::from_str(json).expect("valid json");
        match parsed {
            IpcResponse::Error { message } => assert_eq!(message, "boom"),
            _ => panic!("expected error"),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct TriageData {
    pub triage_files: Vec<String>,
    pub counts: TriageCounts,
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
#[serde(tag = "status")]
pub enum IpcResponse {
    #[serde(rename = "success")]
    Success { data: TriageData },
    #[serde(rename = "error")]
    Error { message: String },
}

// src-tauri/src/lib.rs

// We add the necessary imports to run commands and read files
use std::env;

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use std::process::Command;
use thiserror::Error;

mod logging;
use logging::setup_logging;

#[derive(Debug, Error, Serialize)]
pub enum Error {
    #[error("Command execution failed: {0}")]
    CommandExecution(String),
    #[error("Command returned non-zero exit code: {0}")]
    CommandFailed(String),
    #[error("Directory read failed: {0}")]
    DirectoryRead(String),
    #[error("File rename failed: {0}")]
    FileRename(String),
    #[error("Could not determine project root")]
    ProjectRoot,
    #[error("File write failed: {0}")]
    FileWrite(String),
}

// Helper function to get the project root
fn get_project_root() -> Result<PathBuf, Error> {
    let current_exe = env::current_exe().map_err(|e| Error::CommandExecution(e.to_string()))?;
    // We assume the executable is in `src-tauri/target/{debug|release}`
    if let Some(path) = current_exe.ancestors().nth(4) {
        Ok(path.to_path_buf())
    } else {
        Err(Error::ProjectRoot)
    }
}

// Helper function to get the path to the Poetry virtual environment's Python executable
fn get_poetry_python_path() -> Result<PathBuf, Error> {
    let project_root = get_project_root()?;
    let backend_dir = project_root.join("backend");

    let output = Command::new("poetry")
        .arg("env")
        .arg("info")
        .arg("--path")
        .current_dir(&backend_dir)
        .output()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;

    if output.status.success() {
        let venv_path_str = String::from_utf8_lossy(&output.stdout).trim().to_string();
        let python_path = PathBuf::from(venv_path_str).join("bin").join("python");
        Ok(python_path)
    } else {
        Err(Error::CommandFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ))
    }
}

/// Struct to hold application settings.
#[derive(Debug, Serialize, Deserialize)]
struct AppSettings {
    api_key: String,
    base_dir: String,
}

/// Loads settings from the .env file.
#[tauri::command]
async fn load_settings() -> Result<AppSettings, String> {
    let project_root = get_project_root().map_err(|e| e.to_string())?;
    let env_path = project_root.join(".env");

    dotenvy::from_path(env_path).ok();

    // Use GEMINI_API_KEY consistently with backend
    let api_key = env::var("GEMINI_API_KEY").unwrap_or_else(|_| "".to_string());
    let base_dir = env::var("OBSIDIAN_VAULT_PATH").unwrap_or_else(|_| "".to_string());

    Ok(AppSettings { api_key, base_dir })
}

/// Saves settings to the .env file.
#[tauri::command]
async fn save_settings(api_key: String, base_dir: String) -> Result<(), Error> {
    let project_root = get_project_root()?;
    let env_path = project_root.join(".env");

    let content = format!(
        "GEMINI_API_KEY={}\nOBSIDIAN_VAULT_PATH=\"{}\"\n",
        api_key, base_dir
    );

    fs::write(env_path, content).map_err(|e| Error::FileWrite(e.to_string()))?;
    Ok(())
}

/// Run the triage command.
///
/// This function calls the `triage` command of the backend Python script.
/// It returns the stdout of the command as a string.
/// In case of an error, it returns the stderr of the command as a string.
#[tauri::command]
async fn run_triage() -> Result<String, Error> {
    let project_root = get_project_root()?;
    let script_path = project_root.join("backend/cartaos/cli.py");
    let poetry_python_path = get_poetry_python_path()?;

    let output = Command::new(&poetry_python_path)
        .arg(script_path)
        .arg("triage")
        .current_dir(&project_root)
        .output()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(Error::CommandFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ))
    }
}

/// Run the OCR batch command.
///
/// This function calls the `ocr` command of the backend Python script.
/// It returns the stdout of the command as a string.
/// In case of an error, it returns the stderr of the command as a string.
#[tauri::command]
async fn run_ocr_batch() -> Result<String, Error> {
    let project_root = get_project_root()?;
    let script_path = project_root.join("backend/cartaos/cli.py");
    let poetry_python_path = get_poetry_python_path()?;

    let output = Command::new(&poetry_python_path)
        .arg(script_path)
        .arg("ocr")
        .current_dir(&project_root)
        .output()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(Error::CommandFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ))
    }
}

/// Get the list of files in a specific stage.
///
/// This function returns the list of file names in the specified stage directory.
/// The stage directory is located in the parent directory of the current directory.
#[tauri::command]
async fn get_files_in_stage(stage: String) -> Result<Vec<String>, Error> {
    let project_root = get_project_root()?;
    let dir_path = project_root.join(stage);
    let mut files = Vec::new();

    let entries = fs::read_dir(dir_path).map_err(|e| Error::DirectoryRead(e.to_string()))?;

    for entry in entries {
        let entry = entry.map_err(|e| Error::DirectoryRead(e.to_string()))?;

        // Only consider regular files; skip directories and others
        if let Ok(ft) = entry.file_type() {
            if !ft.is_file() {
                continue;
            }
        }

        if let Some(file_name) = entry.file_name().to_str() {
            // Skip hidden files and common placeholder/system files
            let lower = file_name.to_ascii_lowercase();
            let is_hidden = file_name.starts_with('.') || file_name.starts_with("._");
            let is_known_system = matches!(
                lower.as_str(),
                ".gitkeep" | ".ds_store" | "thumbs.db" | "desktop.ini"
            );
            let has_temp_suffix = ["~", ".tmp", ".temp", ".swp", ".swo", ".part", ".crdownload"]
                .iter()
                .any(|suf| lower.ends_with(suf));

            if is_hidden || is_known_system || has_temp_suffix {
                continue;
            }

            files.push(file_name.to_string());
        }
    }

    Ok(files)
}

/// Open the Scantailor application for a file.
///
/// This function calls the `lab` command of the backend Python script to open the Scantailor application for the specified file.
#[tauri::command]
async fn open_scantailor(file_name: String) -> Result<(), Error> {
    let project_root = get_project_root()?;
    let script_path = project_root.join("backend/cartaos/cli.py");
    let project_path_arg = project_root.join("03_Lab").join(&file_name);
    let poetry_python_path = get_poetry_python_path()?;

    Command::new(&poetry_python_path)
        .arg(script_path)
        .arg("lab")
        .arg(project_path_arg)
        .current_dir(&project_root)
        .spawn()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;

    Ok(())
}

/// Finalize a Lab file.
///
/// This function moves a file from the 03_Lab stage to the 04_ReadyForOCR stage.
#[tauri::command]
async fn finalize_lab_file(file_name: String) -> Result<(), Error> {
    let project_root = get_project_root()?;
    let source_path = project_root.join("03_Lab").join(&file_name);
    let destination_path = project_root.join("04_ReadyForOCR").join(&file_name);
    fs::rename(&source_path, &destination_path).map_err(|e| Error::FileRename(e.to_string()))?;

    Ok(())
}

/// Run summarize for a single file in 05_ReadyForSummary.
#[tauri::command]
async fn run_summarize_single(
    file_name: String,
    dry_run: bool,
    debug: bool,
    force_ocr: bool,
) -> Result<String, Error> {
    let project_root = get_project_root()?;
    let script_path = project_root.join("backend/cartaos/cli.py");
    let target_path = project_root.join("05_ReadyForSummary").join(&file_name);
    let poetry_python_path = get_poetry_python_path()?;

    let mut cmd = Command::new(&poetry_python_path);
    cmd.arg(&script_path).arg("summarize").arg(&target_path);
    if dry_run {
        cmd.arg("--dry-run");
    }
    if debug {
        cmd.arg("--debug");
    }
    if force_ocr {
        cmd.arg("--force-ocr");
    }

    let output = cmd
        .current_dir(&project_root)
        .output()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(Error::CommandFailed(
            String::from_utf8_lossy(&output.stderr).to_string(),
        ))
    }
}

/// Run summarize for all files in 05_ReadyForSummary sequentially.
#[tauri::command]
async fn run_summarize_batch() -> Result<String, Error> {
    let project_root = get_project_root()?;
    let dir_path = project_root.join("05_ReadyForSummary");
    let mut combined = String::new();

    let entries = fs::read_dir(&dir_path).map_err(|e| Error::DirectoryRead(e.to_string()))?;
    for entry in entries {
        let entry = entry.map_err(|e| Error::DirectoryRead(e.to_string()))?;
        let file_name = entry.file_name();
        let file_name = file_name.to_string_lossy().to_string();
        match run_summarize_single(file_name, false, false, false).await {
            Ok(out) => {
                combined.push_str(&out);
                combined.push('\n');
            }
            Err(e) => {
                combined.push_str(&format!("Error summarizing: {}\n", e));
            }
        }
    }
    Ok(combined)
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Summary {
    pub name: String,
    pub path: String,
    pub modified: String,
}

/// List all summary files from 07_Processed/Summaries or vault summaries directory.
#[tauri::command]
async fn list_summaries() -> Result<Vec<Summary>, Error> {
    let project_root = get_project_root()?;
    
    // Try vault path first, fall back to processed summaries
    let vault_path = env::var("OBSIDIAN_VAULT_PATH").ok();
    let summaries_dir = if let Some(vault) = vault_path {
        PathBuf::from(vault).join("Summaries")
    } else {
        project_root.join("07_Processed").join("Summaries")
    };

    let mut summaries = Vec::new();
    
    if !summaries_dir.exists() {
        return Ok(summaries);
    }

    let entries = fs::read_dir(&summaries_dir).map_err(|e| Error::DirectoryRead(e.to_string()))?;
    
    for entry in entries {
        let entry = entry.map_err(|e| Error::DirectoryRead(e.to_string()))?;
        let path = entry.path();
        
        if path.is_file() && path.extension().and_then(|s| s.to_str()) == Some("md") {
            if let Some(name) = path.file_name().and_then(|s| s.to_str()) {
                let metadata = fs::metadata(&path).map_err(|e| Error::DirectoryRead(e.to_string()))?;
                let modified = metadata.modified()
                    .map_err(|e| Error::DirectoryRead(e.to_string()))?
                    .duration_since(std::time::UNIX_EPOCH)
                    .map_err(|e| Error::DirectoryRead(e.to_string()))?
                    .as_secs();
                
                summaries.push(Summary {
                    name: name.to_string(),
                    path: path.to_string_lossy().to_string(),
                    modified: format!("{}", modified),
                });
            }
        }
    }
    
    // Sort by modified date (newest first)
    summaries.sort_by(|a, b| b.modified.cmp(&a.modified));
    
    Ok(summaries)
}

/// Read the content of a summary file.
#[tauri::command]
async fn read_summary(path: String) -> Result<String, Error> {
    let path_buf = PathBuf::from(&path);
    
    // Basic security check - ensure it's a markdown file
    if path_buf.extension().and_then(|s| s.to_str()) != Some("md") {
        return Err(Error::CommandFailed("Invalid file type".to_string()));
    }
    
    fs::read_to_string(&path_buf).map_err(|e| Error::DirectoryRead(e.to_string()))
}

/// Get the configured vault path.
#[tauri::command]
async fn get_vault_path() -> Result<Option<String>, Error> {
    Ok(env::var("OBSIDIAN_VAULT_PATH").ok())
}

/// Open a file in the Obsidian vault.
#[tauri::command]
async fn open_in_vault(path: String) -> Result<(), Error> {
    let vault_path = env::var("OBSIDIAN_VAULT_PATH")
        .map_err(|_| Error::CommandFailed("Vault path not configured".to_string()))?;
    
    let path_buf = PathBuf::from(&path);
    let relative_path = path_buf.strip_prefix(&vault_path)
        .map_err(|_| Error::CommandFailed("File not in vault".to_string()))?;
    
    let obsidian_url = format!("obsidian://open?vault={}&file={}", 
        PathBuf::from(&vault_path).file_name()
            .and_then(|s| s.to_str())
            .unwrap_or("vault"),
        relative_path.to_string_lossy()
    );
    
    // Open URL using system default handler
    #[cfg(target_os = "windows")]
    Command::new("cmd").args(["/C", "start", &obsidian_url]).spawn()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;
    
    #[cfg(target_os = "macos")]
    Command::new("open").arg(&obsidian_url).spawn()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;
    
    #[cfg(target_os = "linux")]
    Command::new("xdg-open").arg(&obsidian_url).spawn()
        .map_err(|e| Error::CommandExecution(e.to_string()))?;
    
    Ok(())
}

/// Run the Tauri application.
///
/// This function sets up the Tauri application and runs it.
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() -> Result<(), tauri::Error> {
    tauri::Builder::default()
        // The line below is the most important: it "registers" our functions
        // and makes them available to be called by `invoke` in Svelte.
        .invoke_handler(tauri::generate_handler![
            run_triage,
            run_triage_json,
            run_triage_json_typed,
            run_ocr_json,
            run_ocr_json_typed,
            run_ocr_batch,
            run_ocr_single,
            get_files_in_stage,
            load_settings,
            save_settings,
            open_scantailor,
            finalize_lab_file,
            run_summarize_single,
            run_summarize_json,
            run_summarize_json_typed,
            run_summarize_batch,
            import_to_triage,
            list_summaries,
            read_summary,
            get_vault_path,
            open_in_vault
        ])
        .setup(|app: &mut tauri::App| {
            setup_logging(app).expect("Failed to setup logging");
            Ok(())
        })
        .run(tauri::generate_context!())
}
