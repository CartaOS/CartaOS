// src-tauri/src/lib.rs

// We add the necessary imports to run commands and read files
use std::process::Command;
use std::fs;
use std::path::Path;
use dotenv::dotenv; // Import dotenv
use std::env; // Import std::env for environment variables
use serde::{Deserialize, Serialize}; // Import for serialization/deserialization

/// Struct to hold application settings.
#[derive(Debug, Serialize, Deserialize)]
struct AppSettings {
    api_key: String,
    base_dir: String,
}

/// Loads settings from the .env file.
#[tauri::command]
async fn load_settings() -> Result<AppSettings, String> {
    dotenv().ok(); // Load .env file, ignoring if it doesn't exist

    let api_key = env::var("API_KEY").unwrap_or_else(|_| "".to_string());
    let base_dir = env::var("OBSIDIAN_VAULT_PATH").unwrap_or_else(|_| "".to_string());

    Ok(AppSettings { api_key, base_dir })
}

/// Saves settings to the .env file.
#[tauri::command]
async fn save_settings(api_key: String, base_dir: String) -> Result<(), String> {
    let env_path = Path::new("../.env"); // Path to the .env file relative to src-tauri

    let content = format!(
        "API_KEY={}\nOBSIDIAN_VAULT_PATH={}\n",
        api_key,
        base_dir
    );

    fs::write(env_path, content).map_err(|e| e.to_string())?;
    Ok(())
}

/// Executes the triage command and returns the output (success or error).
///
/// This function runs the `triage` command in the `backend/cartaos/cli.py` script.
///
/// # Returns
///
/// Returns a `Result` with `Ok(String)` if the command was executed successfully,
/// or `Err(String)` if there was an error.
#[tauri::command]
async fn run_triage() -> Result<String, String> {
    // We use std::process::Command to execute your Python script exactly as in the terminal.
    let output = Command::new("python3")
        .arg("backend/cartaos/cli.py") // Argument 1: the script
        .arg("triage")                // Argument 2: the CLI command
        .output()                     // Executes and captures the output
        .map_err(|e| e.to_string())?; // Maps errors in execution (ex: python3 not found)

    // We check if the command was executed successfully.
    if output.status.success() {
        // If yes, we return the standard output (stdout) as a success string.
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        // If not, we return the error output (stderr) as an error string.
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// Executes the OCR batch command and returns the output (success or error).
///
/// This function runs the `ocr` command in the `backend/cartaos/cli.py` script.
///
/// # Returns
///
/// Returns a `Result` with `Ok(String)` if the command was executed successfully,
/// or `Err(String)` if there was an error.
#[tauri::command]
async fn run_ocr_batch() -> Result<String, String> {
    let output = Command::new("python3")
        .arg("backend/cartaos/cli.py")
        .arg("ocr") // The only change is the command we pass to the CLI
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// Retrieves the list of files in a specific stage directory.
///
/// # Arguments
///
/// * `stage` - The name of the stage directory (ex: "03_Lab").
///
/// # Returns
///
/// Returns a `Result` with `Ok(Vec<String>)` containing the list of file names,
/// or `Err(String)` if there was an error reading the directory.
#[tauri::command]
async fn get_files_in_stage(stage: String) -> Result<Vec<String>, String> {
    // We construct the path to the stage directory (ex: ./03_Lab)
    // Note: The Tauri executable runs from the `src-tauri` folder, so we use `../` to go back to the root.
    let dir_path = Path::new(".." ).join(stage);
    let mut files = Vec::new();

    let entries = fs::read_dir(dir_path).map_err(|e| e.to_string())?;

    for entry in entries {
        let entry = entry.map_err(|e| e.to_string())?;
        // We only get the file name and add it to our vector
        if let Some(file_name) = entry.path().file_name() {
             files.push(file_name.to_string_lossy().to_string());
        }
    }
    // We return the list of file names.
    Ok(files)
}


#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    // The line below is the most important: it "registers" our functions
    // and makes them available to be called by `invoke` in Svelte.
    .invoke_handler(tauri::generate_handler![
        run_triage,
        run_ocr_batch,
        get_files_in_stage,
        load_settings,
        save_settings
    ])
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}