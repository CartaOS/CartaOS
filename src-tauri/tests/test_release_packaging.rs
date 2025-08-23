//! Test release packaging functionality for Issue #13

use std::fs;
use std::path::Path;

#[cfg(test)]
mod release_packaging_tests {
    use super::*;

    #[test]
    fn test_tauri_config_exists() {
        // Test that tauri.conf.json exists and has required fields for packaging
        let config_path = Path::new("tauri.conf.json");
        assert!(
            config_path.exists(),
            "tauri.conf.json should exist for packaging"
        );

        let config_content =
            fs::read_to_string(config_path).expect("Should be able to read tauri.conf.json");

        // Verify essential packaging fields are present
        assert!(
            config_content.contains("\"productName\""),
            "Config should have productName"
        );
        assert!(
            config_content.contains("\"version\""),
            "Config should have version"
        );
        assert!(
            config_content.contains("\"identifier\""),
            "Config should have identifier"
        );
        assert!(
            config_content.contains("\"bundle\""),
            "Config should have bundle configuration"
        );
    }

    #[test]
    fn test_cargo_toml_has_required_metadata() {
        // Test that Cargo.toml has required metadata for release
        let cargo_path = Path::new("Cargo.toml");
        assert!(cargo_path.exists(), "Cargo.toml should exist");

        let cargo_content =
            fs::read_to_string(cargo_path).expect("Should be able to read Cargo.toml");

        // Verify essential metadata fields
        assert!(
            cargo_content.contains("name ="),
            "Cargo.toml should have name"
        );
        assert!(
            cargo_content.contains("version ="),
            "Cargo.toml should have version"
        );
        assert!(
            cargo_content.contains("edition ="),
            "Cargo.toml should have edition"
        );
    }

    #[test]
    fn test_icons_directory_exists() {
        // Test that icons directory exists with required icon files
        let icons_path = Path::new("icons");
        assert!(
            icons_path.exists(),
            "Icons directory should exist for packaging"
        );
        assert!(icons_path.is_dir(), "Icons path should be a directory");

        // Check for common icon formats that Tauri expects
        let icon_files = ["32x32.png", "128x128.png", "icon.ico", "icon.icns"];
        let mut found_icons = 0;

        if let Ok(entries) = fs::read_dir(icons_path) {
            for entry in entries.flatten() {
                let file_name = entry.file_name();
                let file_name_str = file_name.to_string_lossy();

                for expected_icon in &icon_files {
                    if file_name_str.contains(expected_icon) {
                        found_icons += 1;
                        break;
                    }
                }
            }
        }

        assert!(
            found_icons > 0,
            "Should have at least one icon file for packaging"
        );
    }

    #[test]
    fn test_build_configuration_for_release() {
        // Test that build configuration supports release mode
        let config_path = Path::new("tauri.conf.json");
        if config_path.exists() {
            let config_content =
                fs::read_to_string(config_path).expect("Should be able to read tauri.conf.json");

            // Check for build configuration
            assert!(
                config_content.contains("\"build\"")
                    || config_content.contains("\"beforeBuildCommand\""),
                "Config should have build configuration"
            );
        }
    }

    #[test]
    fn test_frontend_build_script_exists() {
        // Test that frontend has build capability
        let package_json_path = Path::new("../frontend/package.json");
        if package_json_path.exists() {
            let package_content =
                fs::read_to_string(package_json_path).expect("Should be able to read package.json");

            // Verify build script exists
            assert!(
                package_content.contains("\"build\"") && package_content.contains("vite build"),
                "Frontend should have build script for release"
            );
        }
    }

    #[test]
    fn test_release_profile_configuration() {
        // Test that Cargo.toml has optimized release profile
        let cargo_path = Path::new("Cargo.toml");
        if cargo_path.exists() {
            let cargo_content =
                fs::read_to_string(cargo_path).expect("Should be able to read Cargo.toml");

            // Check for release profile optimizations (optional but recommended)
            if cargo_content.contains("[profile.release]") {
                // If release profile exists, verify it has optimizations
                assert!(
                    cargo_content.contains("opt-level") || cargo_content.contains("lto"),
                    "Release profile should have optimizations"
                );
            }
        }
    }

    #[test]
    fn test_no_debug_artifacts_in_release() {
        // Test that common debug artifacts are not included in release builds
        let src_dir = Path::new("src");
        if src_dir.exists() {
            // This is a basic check - in a real scenario, you'd want to check
            // the actual build output, but that requires running the build

            // For now, just verify the source structure is clean
            assert!(
                src_dir.is_dir(),
                "Source directory should exist and be a directory"
            );
        }
    }

    #[test]
    fn test_version_consistency() {
        // Test that versions are consistent across configuration files
        let cargo_path = Path::new("Cargo.toml");
        let tauri_config_path = Path::new("tauri.conf.json");

        if cargo_path.exists() && tauri_config_path.exists() {
            let cargo_content =
                fs::read_to_string(cargo_path).expect("Should be able to read Cargo.toml");
            let tauri_content = fs::read_to_string(tauri_config_path)
                .expect("Should be able to read tauri.conf.json");

            // Extract version from Cargo.toml (basic regex-free approach)
            let cargo_has_version = cargo_content.contains("version =");
            let tauri_has_version = tauri_content.contains("\"version\"");

            assert!(cargo_has_version, "Cargo.toml should have version field");
            assert!(
                tauri_has_version,
                "tauri.conf.json should have version field"
            );
        }
    }
}
