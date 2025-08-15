// src-tauri/src/lib.rs

// Adicionamos os imports necessários para executar comandos e ler arquivos
use std::process::Command;
use std::fs;
use std::path::Path;

// Este é o "decorator" que transforma uma função Rust em um comando que o frontend pode chamar.
#[tauri::command]
async fn run_triage() -> Result<String, String> {
    // Usamos std::process::Command para executar o seu script Python exatamente como no terminal.
    let output = Command::new("python3")
        .arg("backend/cartaos/cli.py") // Argumento 1: o script
        .arg("triage")                // Argumento 2: o comando do CLI
        .output()                     // Executa e captura a saída
        .map_err(|e| e.to_string())?; // Mapeia erros de execução (ex: python3 não encontrado)

    // Verificamos se o comando foi executado com sucesso.
    if output.status.success() {
        // Se sim, retornamos a saída padrão (stdout) como uma string de sucesso.
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        // Se não, retornamos a saída de erro (stderr) como uma string de erro.
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
async fn run_ocr_batch() -> Result<String, String> {
    let output = Command::new("python3")
        .arg("backend/cartaos/cli.py")
        .arg("ocr") // A única mudança é o comando que passamos para o CLI
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

// Este comando recebe um argumento do frontend (o nome da pasta/etapa)
#[tauri::command]
async fn get_files_in_stage(stage: String) -> Result<Vec<String>, String> {
    // Construímos o caminho para o diretório da etapa (ex: ./03_Lab)
    // Nota: O executável do Tauri roda a partir da pasta `src-tauri`, por isso usamos `../` para voltar à raiz.
    let dir_path = Path::new("..").join(stage);
    let mut files = Vec::new();

    let entries = fs::read_dir(dir_path).map_err(|e| e.to_string())?;

    for entry in entries {
        let entry = entry.map_err(|e| e.to_string())?;
        // Pegamos apenas o nome do arquivo e o adicionamos ao nosso vetor
        if let Some(file_name) = entry.path().file_name() {
             files.push(file_name.to_string_lossy().to_string());
        }
    }
    // Retornamos a lista de nomes de arquivos.
    Ok(files)
}


#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    // A linha abaixo é a mais importante: ela "registra" nossas funções
    // e as torna disponíveis para serem chamadas pelo `invoke` no Svelte.
    .invoke_handler(tauri::generate_handler![
        run_triage,
        run_ocr_batch,
        get_files_in_stage
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