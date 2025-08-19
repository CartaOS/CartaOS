use chrono::Local;
use fern::Dispatch;
use log::LevelFilter;
use serde::Serialize;
use tauri::{App, Manager, Wry, Emitter};

#[derive(Clone, Serialize)]
struct LogPayload {
    message: String,
    timestamp: String,
}

pub fn setup_logging(app: &mut App<Wry>) -> Result<(), fern::InitError> {
    let app_handle = app.handle().clone();
    let log_path = app
        .path()
        .app_log_dir()
        .expect("failed to get app log dir")
        .join("app.log");

    Dispatch::new()
        .format(move |out, message, record| {
            let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
            out.finish(format_args!(
                "{} [{}][{}] {}",
                timestamp,
                record.level(),
                record.target(),
                message
            ));
            let log_payload = LogPayload {
                message: message.to_string(),
                timestamp,
            };
            app_handle.emit("log-message", log_payload)
                .expect("failed to emit log event");
        })
        .level(LevelFilter::Info)
        .chain(std::io::stdout())
        .chain(fern::log_file(log_path)?)
        .apply()?;

    Ok(())
}
