// src-tauri/src/lib.rs

use serde::Serialize;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use thiserror::Error;
use log::info;

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
}

// Helper function to get the project root
fn get_project_root() -> Result<PathBuf, Error> {
    let current_exe = env::current_exe().map_err(|e| Error::CommandExecution(e.to_string()))?;
    info!("Current exe path: {:?}", current_exe);
    // We assume the executable is in `src-tauri/target/{debug|release}`
    if let Some(path) = current_exe.ancestors().nth(4) {
        info!("Project root path: {:?}", path);
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
        .current_dir(&project_root) // Ensure CWD is project root
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
        if let Some(file_name) = entry.file_name().to_str() {
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

    fs::rename(&source_path, &destination_path)
        .map_err(|e| Error::FileRename(e.to_string()))?;

    Ok(())
}

/// Run the Tauri application.
///
/// This function sets up the Tauri application and runs it.
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() -> Result<(), tauri::Error> {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            run_triage,
            run_ocr_batch,
            get_files_in_stage,
            open_scantailor,
            finalize_lab_file
        ])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle()
                    .plugin(
                        tauri_plugin_log::Builder::default()
                            .level(log::LevelFilter::Info)
                            .build(),
                    )
                    .expect("failed to initialize log plugin");
            }
            Ok(())
        })
        .run(tauri::generate_context!())
}

