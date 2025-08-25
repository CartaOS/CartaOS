use serde::{Deserialize, Serialize};
use std::fmt;
use thiserror::Error;

/// Comprehensive error types for the CartaOS Rust layer.
///
/// This enum provides structured error handling with detailed context,
/// error codes, and user-friendly messages for the frontend.
#[derive(Debug, Error, Serialize, Deserialize, Clone, PartialEq)]
#[serde(tag = "type", content = "details")]
pub enum CartaError {
    /// File system operation errors
    #[error("File system error: {message}")]
    FileSystem {
        message: String,
        path: Option<String>,
        operation: FileOperation,
        // Store textual representation of source to keep enum Clone + PartialEq
        #[serde(skip)]
        source_text: Option<String>,
    },

    /// Command execution errors
    #[error("Command execution error: {message}")]
    Command {
        message: String,
        command: String,
        exit_code: Option<i32>,
        stderr: Option<String>,
    },

    /// Configuration and environment errors
    #[error("Configuration error: {message}")]
    Configuration {
        message: String,
        key: Option<String>,
        expected_type: Option<String>,
    },

    /// Input validation errors
    #[error("Validation error: {message}")]
    Validation {
        message: String,
        field: Option<String>,
        value: Option<String>,
        constraint: Option<String>,
    },

    /// Project structure and path resolution errors
    #[error("Project structure error: {message}")]
    ProjectStructure {
        message: String,
        expected_path: Option<String>,
        actual_path: Option<String>,
    },

    /// External service integration errors
    #[error("External service error: {message}")]
    ExternalService {
        message: String,
        service: String,
        status_code: Option<u16>,
        retry_after: Option<u64>,
    },

    /// JSON serialization/deserialization errors
    #[error("Serialization error: {message}")]
    Serialization {
        message: String,
        data_type: Option<String>,
        field: Option<String>,
    },

    /// Permission and security errors
    #[error("Permission error: {message}")]
    Permission {
        message: String,
        resource: Option<String>,
        required_permission: Option<String>,
    },

    /// Resource not found errors
    #[error("Resource not found: {message}")]
    NotFound {
        message: String,
        resource_type: String,
        identifier: String,
    },

    /// Internal application errors
    #[error("Internal error: {message}")]
    Internal {
        message: String,
        context: Option<String>,
        error_id: Option<String>,
    },
}

/// File system operation types for better error context
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub enum FileOperation {
    Read,
    Write,
    Delete,
    Move,
    Copy,
    Create,
    List,
    Metadata,
}

impl fmt::Display for FileOperation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            FileOperation::Read => write!(f, "read"),
            FileOperation::Write => write!(f, "write"),
            FileOperation::Delete => write!(f, "delete"),
            FileOperation::Move => write!(f, "move"),
            FileOperation::Copy => write!(f, "copy"),
            FileOperation::Create => write!(f, "create"),
            FileOperation::List => write!(f, "list"),
            FileOperation::Metadata => write!(f, "metadata"),
        }
    }
}

/// Error severity levels for logging and user feedback
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub enum ErrorSeverity {
    Low,      // Warnings, non-critical issues
    Medium,   // Recoverable errors that affect functionality
    High,     // Critical errors that prevent operation
    Critical, // System-level errors requiring immediate attention
}

/// Enhanced error context with additional metadata
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ErrorContext {
    pub error: CartaError,
    pub severity: ErrorSeverity,
    pub timestamp: u64,
    pub user_message: String,
    pub technical_details: Option<String>,
    pub suggested_action: Option<String>,
    pub error_code: String,
}

impl CartaError {
    /// Create a file system error with detailed context
    pub fn file_system(
        message: impl Into<String>,
        path: Option<impl Into<String>>,
        operation: FileOperation,
    ) -> Self {
        Self::FileSystem {
            message: message.into(),
            path: path.map(|p| p.into()),
            operation,
            source_text: None,
        }
    }

    /// Create a command execution error
    pub fn command(
        message: impl Into<String>,
        command: impl Into<String>,
        exit_code: Option<i32>,
        stderr: Option<impl Into<String>>,
    ) -> Self {
        Self::Command {
            message: message.into(),
            command: command.into(),
            exit_code,
            stderr: stderr.map(|s| s.into()),
        }
    }

    /// Create a configuration error
    pub fn configuration(
        message: impl Into<String>,
        key: Option<impl Into<String>>,
        expected_type: Option<impl Into<String>>,
    ) -> Self {
        Self::Configuration {
            message: message.into(),
            key: key.map(|k| k.into()),
            expected_type: expected_type.map(|t| t.into()),
        }
    }

    /// Create a validation error
    pub fn validation(
        message: impl Into<String>,
        field: Option<impl Into<String>>,
        value: Option<impl Into<String>>,
        constraint: Option<impl Into<String>>,
    ) -> Self {
        Self::Validation {
            message: message.into(),
            field: field.map(|f| f.into()),
            value: value.map(|v| v.into()),
            constraint: constraint.map(|c| c.into()),
        }
    }

    /// Create a project structure error
    pub fn project_structure(
        message: impl Into<String>,
        expected_path: Option<impl Into<String>>,
        actual_path: Option<impl Into<String>>,
    ) -> Self {
        Self::ProjectStructure {
            message: message.into(),
            expected_path: expected_path.map(|p| p.into()),
            actual_path: actual_path.map(|p| p.into()),
        }
    }

    /// Create a resource not found error
    pub fn not_found(
        message: impl Into<String>,
        resource_type: impl Into<String>,
        identifier: impl Into<String>,
    ) -> Self {
        Self::NotFound {
            message: message.into(),
            resource_type: resource_type.into(),
            identifier: identifier.into(),
        }
    }

    /// Create an internal error
    pub fn internal(message: impl Into<String>, context: Option<impl Into<String>>) -> Self {
        Self::Internal {
            message: message.into(),
            context: context.map(|c| c.into()),
            error_id: Some(generate_error_id()),
        }
    }

    /// Get the error severity level
    pub fn severity(&self) -> ErrorSeverity {
        match self {
            Self::Validation { .. } => ErrorSeverity::Low,
            Self::NotFound { .. } => ErrorSeverity::Medium,
            Self::FileSystem { .. } | Self::Command { .. } => ErrorSeverity::Medium,
            Self::Configuration { .. } => ErrorSeverity::High,
            Self::ProjectStructure { .. } => ErrorSeverity::High,
            Self::ExternalService { .. } => ErrorSeverity::Medium,
            Self::Serialization { .. } => ErrorSeverity::Medium,
            Self::Permission { .. } => ErrorSeverity::High,
            Self::Internal { .. } => ErrorSeverity::Critical,
        }
    }

    /// Get a user-friendly error message
    pub fn user_message(&self) -> String {
        match self {
            Self::FileSystem {
                operation, path, ..
            } => {
                if let Some(path) = path {
                    format!("Failed to {} file: {}", operation, path)
                } else {
                    format!("File {} operation failed", operation)
                }
            }
            Self::Command { command, .. } => {
                format!("Command '{}' failed to execute", command)
            }
            Self::Configuration { key, .. } => {
                if let Some(key) = key {
                    format!("Configuration error with '{}'", key)
                } else {
                    "Configuration error occurred".to_string()
                }
            }
            Self::Validation { field, .. } => {
                if let Some(field) = field {
                    format!("Invalid value for '{}'", field)
                } else {
                    "Input validation failed".to_string()
                }
            }
            Self::ProjectStructure { .. } => "Project structure issue detected".to_string(),
            Self::ExternalService { service, .. } => {
                format!("External service '{}' is unavailable", service)
            }
            Self::Serialization { data_type, .. } => {
                if let Some(data_type) = data_type {
                    format!("Data processing error with {}", data_type)
                } else {
                    "Data processing error".to_string()
                }
            }
            Self::Permission { resource, .. } => {
                if let Some(resource) = resource {
                    format!("Access denied to '{}'", resource)
                } else {
                    "Permission denied".to_string()
                }
            }
            Self::NotFound {
                resource_type,
                identifier,
                ..
            } => {
                format!("{} '{}' not found", resource_type, identifier)
            }
            Self::Internal { .. } => "An internal error occurred. Please try again.".to_string(),
        }
    }

    /// Get a suggested action for the user
    pub fn suggested_action(&self) -> Option<String> {
        match self {
            Self::FileSystem {
                operation: FileOperation::Read,
                ..
            } => Some("Check if the file exists and you have read permissions".to_string()),
            Self::FileSystem {
                operation: FileOperation::Write,
                ..
            } => Some("Check if you have write permissions and sufficient disk space".to_string()),
            Self::Command { command, .. } => {
                Some(format!("Ensure '{}' is installed and accessible", command))
            }
            Self::Configuration { key: Some(key), .. } => {
                Some(format!("Check the configuration for '{}' in settings", key))
            }
            Self::Validation { .. } => Some("Please check your input and try again".to_string()),
            Self::ProjectStructure { .. } => {
                Some("Verify the project directory structure is intact".to_string())
            }
            Self::ExternalService { .. } => {
                Some("Check your internet connection and try again later".to_string())
            }
            Self::Permission { .. } => {
                Some("Check file permissions or run with appropriate privileges".to_string())
            }
            Self::NotFound { .. } => {
                Some("Verify the resource exists and the path is correct".to_string())
            }
            _ => None,
        }
    }

    /// Generate an error code for tracking
    pub fn error_code(&self) -> String {
        match self {
            Self::FileSystem { operation, .. } => {
                format!("FS_{}", operation.to_string().to_uppercase())
            }
            Self::Command { .. } => "CMD_EXEC".to_string(),
            Self::Configuration { .. } => "CFG_ERROR".to_string(),
            Self::Validation { .. } => "VAL_ERROR".to_string(),
            Self::ProjectStructure { .. } => "PROJ_STRUCT".to_string(),
            Self::ExternalService { .. } => "EXT_SERVICE".to_string(),
            Self::Serialization { .. } => "SER_ERROR".to_string(),
            Self::Permission { .. } => "PERM_DENIED".to_string(),
            Self::NotFound { .. } => "NOT_FOUND".to_string(),
            Self::Internal { .. } => "INTERNAL".to_string(),
        }
    }

    /// Create an enhanced error context
    pub fn with_context(self) -> ErrorContext {
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        ErrorContext {
            severity: self.severity(),
            user_message: self.user_message(),
            suggested_action: self.suggested_action(),
            error_code: self.error_code(),
            technical_details: Some(self.to_string()),
            timestamp,
            error: self,
        }
    }
}

/// Convert from std::io::Error to CartaError
impl From<std::io::Error> for CartaError {
    fn from(err: std::io::Error) -> Self {
        let operation = match err.kind() {
            std::io::ErrorKind::NotFound => {
                return Self::not_found(err.to_string(), "file", "unknown")
            }
            std::io::ErrorKind::PermissionDenied => {
                return Self::Permission {
                    message: err.to_string(),
                    resource: None,
                    required_permission: Some("read/write".to_string()),
                }
            }
            _ => FileOperation::Read, // Default assumption
        };

        Self::file_system(err.to_string(), None::<String>, operation)
    }
}

/// Convert from serde_json::Error to CartaError
impl From<serde_json::Error> for CartaError {
    fn from(err: serde_json::Error) -> Self {
        Self::Serialization {
            message: err.to_string(),
            data_type: Some("JSON".to_string()),
            field: None,
        }
    }
}

/// Generate a unique error ID for tracking
fn generate_error_id() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis();
    format!("ERR_{}", timestamp)
}

/// Result type alias for CartaOS operations
pub type CartaResult<T> = Result<T, CartaError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_file_system_error_creation() {
        let error = CartaError::file_system(
            "Failed to read file",
            Some("/path/to/file.txt"),
            FileOperation::Read,
        );

        match error {
            CartaError::FileSystem {
                message,
                path,
                operation,
                ..
            } => {
                assert_eq!(message, "Failed to read file");
                assert_eq!(path, Some("/path/to/file.txt".to_string()));
                assert_eq!(operation, FileOperation::Read);
            }
            _ => panic!("Expected FileSystem error"),
        }
    }

    #[test]
    fn test_error_severity() {
        let validation_error = CartaError::validation(
            "Invalid input",
            None::<String>,
            None::<String>,
            None::<String>,
        );
        assert_eq!(validation_error.severity(), ErrorSeverity::Low);

        let internal_error = CartaError::internal("System failure", None::<String>);
        assert_eq!(internal_error.severity(), ErrorSeverity::Critical);
    }

    #[test]
    fn test_user_message() {
        let error = CartaError::not_found("File not found", "document", "test.pdf");
        assert_eq!(error.user_message(), "document 'test.pdf' not found");
    }

    #[test]
    fn test_error_code_generation() {
        let fs_error = CartaError::file_system("Test", None::<String>, FileOperation::Write);
        assert_eq!(fs_error.error_code(), "FS_WRITE");

        let cmd_error = CartaError::command("Test", "python", Some(1), None::<String>);
        assert_eq!(cmd_error.error_code(), "CMD_EXEC");
    }

    #[test]
    fn test_error_context_creation() {
        let error = CartaError::validation(
            "Invalid file name",
            Some("filename"),
            Some("../test"),
            None::<String>,
        );
        let context = error.with_context();

        assert_eq!(context.severity, ErrorSeverity::Low);
        assert_eq!(context.error_code, "VAL_ERROR");
        assert!(context.timestamp > 0);
        assert!(!context.user_message.is_empty());
    }

    #[test]
    fn test_io_error_conversion() {
        let io_error = std::io::Error::new(std::io::ErrorKind::NotFound, "File not found");
        let carta_error: CartaError = io_error.into();

        match carta_error {
            CartaError::NotFound {
                resource_type,
                identifier,
                ..
            } => {
                assert_eq!(resource_type, "file");
                assert_eq!(identifier, "unknown");
            }
            _ => panic!("Expected NotFound error"),
        }
    }

    #[test]
    fn test_json_error_conversion() {
        let json_str = "{ invalid json";
        let json_error = serde_json::from_str::<serde_json::Value>(json_str).unwrap_err();
        let carta_error: CartaError = json_error.into();

        match carta_error {
            CartaError::Serialization { data_type, .. } => {
                assert_eq!(data_type, Some("JSON".to_string()));
            }
            _ => panic!("Expected Serialization error"),
        }
    }

    #[test]
    fn test_error_serialization() {
        let error = CartaError::command(
            "Command failed",
            "python",
            Some(1),
            Some("Permission denied"),
        );
        let serialized = serde_json::to_string(&error).expect("Should serialize");
        let deserialized: CartaError =
            serde_json::from_str(&serialized).expect("Should deserialize");

        assert_eq!(error, deserialized);
    }
}
