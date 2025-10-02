#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

fn main() {
  if let Err(e) = tauri::Builder::default()
    .run(tauri::generate_context!())
  {
    eprintln!("Error while running tauri application: {:?}", e);
    std::process::exit(1);
  }
}