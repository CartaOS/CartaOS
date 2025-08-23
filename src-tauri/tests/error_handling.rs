use app_lib::{CartaError, ErrorSeverity, FileOperation};

#[test]
fn command_error_serialization_roundtrip() {
    let err = CartaError::command(
        "Command failed",
        "python -c 'exit 7'",
        Some(7),
        Some("boom"),
    );
    let json = serde_json::to_string(&err).expect("serialize");
    let back: CartaError = serde_json::from_str(&json).expect("deserialize");
    assert_eq!(err, back);
    assert_eq!(back.error_code(), "CMD_EXEC");
    assert_eq!(back.severity(), ErrorSeverity::Medium);
}

#[test]
fn filesystem_error_serialization_roundtrip() {
    let err = CartaError::file_system(
        "Write failed",
        Some("/not/writable/file.txt"),
        FileOperation::Write,
    );
    let json = serde_json::to_string(&err).expect("serialize");
    let back: CartaError = serde_json::from_str(&json).expect("deserialize");
    assert_eq!(err, back);
    assert_eq!(back.error_code(), "FS_WRITE");
    // User-facing message should include operation and path when available
    let msg = back.user_message();
    assert!(msg.contains("write"));
    assert!(msg.contains("/not/writable/file.txt"));
}

#[test]
fn validation_error_context_and_code() {
    let err = CartaError::validation(
        "Invalid file name",
        Some("file_name"),
        Some(".."),
        Some("no traversal"),
    );
    let ctx = err.with_context();
    assert_eq!(ctx.severity, ErrorSeverity::Low);
    assert_eq!(ctx.error_code, "VAL_ERROR");
    assert!(!ctx.user_message.is_empty());
}
