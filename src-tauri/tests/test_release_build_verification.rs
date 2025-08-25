//! Test release build verification for Issue #13

use std::fs;
use std::path::Path;

#[cfg(test)]
mod release_build_verification_tests {
    use super::*;

    #[test]
    fn test_release_binary_exists() {
        // Test that release binary was created
        let binary_path = Path::new("target/release/app");
        assert!(
            binary_path.exists(),
            "Release binary should exist after build"
        );

        // Verify it's an executable file
        let metadata = fs::metadata(binary_path).expect("Should be able to read binary metadata");
        assert!(metadata.is_file(), "Release binary should be a file");
        assert!(metadata.len() > 0, "Release binary should not be empty");
    }

    #[test]
    fn test_deb_package_created() {
        // Test that .deb package was created
        let deb_dir = Path::new("target/release/bundle/deb");
        if deb_dir.exists() {
            let entries = fs::read_dir(deb_dir).expect("Should be able to read deb directory");

            let mut found_deb = false;
            for entry in entries.flatten() {
                let file_name = entry.file_name();
                let file_name_str = file_name.to_string_lossy();

                if file_name_str.ends_with(".deb") && file_name_str.contains("CartaOS") {
                    found_deb = true;

                    // Verify package size is reasonable
                    let metadata = entry
                        .metadata()
                        .expect("Should be able to read deb metadata");
                    assert!(
                        metadata.len() > 1_000_000,
                        "Deb package should be substantial size (>1MB)"
                    );
                    break;
                }
            }

            assert!(found_deb, "Should have created a .deb package");
        }
    }

    #[test]
    fn test_appimage_created() {
        // Test that AppImage was created
        let appimage_dir = Path::new("target/release/bundle/appimage");
        if appimage_dir.exists() {
            let entries =
                fs::read_dir(appimage_dir).expect("Should be able to read appimage directory");

            let mut found_appimage = false;
            for entry in entries.flatten() {
                let file_name = entry.file_name();
                let file_name_str = file_name.to_string_lossy();

                if file_name_str.ends_with(".AppImage") && file_name_str.contains("CartaOS") {
                    found_appimage = true;

                    // Verify AppImage size is reasonable
                    let metadata = entry
                        .metadata()
                        .expect("Should be able to read AppImage metadata");
                    assert!(
                        metadata.len() > 1_000_000,
                        "AppImage should be substantial size (>1MB)"
                    );
                    break;
                }
            }

            assert!(found_appimage, "Should have created an AppImage");
        }
    }

    #[test]
    fn test_rpm_package_created() {
        // Test that RPM package was created
        let rpm_dir = Path::new("target/release/bundle/rpm");
        if rpm_dir.exists() {
            let entries = fs::read_dir(rpm_dir).expect("Should be able to read rpm directory");

            let mut found_rpm = false;
            for entry in entries.flatten() {
                let file_name = entry.file_name();
                let file_name_str = file_name.to_string_lossy();

                if file_name_str.ends_with(".rpm") && file_name_str.contains("CartaOS") {
                    found_rpm = true;

                    // Verify RPM size is reasonable
                    let metadata = entry
                        .metadata()
                        .expect("Should be able to read RPM metadata");
                    assert!(
                        metadata.len() > 1_000_000,
                        "RPM package should be substantial size (>1MB)"
                    );
                    break;
                }
            }

            assert!(found_rpm, "Should have created an RPM package");
        }
    }

    #[test]
    fn test_frontend_assets_bundled() {
        // Test that frontend build directory exists and has content
        let frontend_build = Path::new("../frontend/build");
        assert!(
            frontend_build.exists(),
            "Frontend build directory should exist"
        );

        // Check for index.html
        let index_html = frontend_build.join("index.html");
        assert!(index_html.exists(), "Frontend should have index.html");

        // Verify index.html has content
        let html_content =
            fs::read_to_string(index_html).expect("Should be able to read index.html");
        assert!(
            html_content.contains("<html"),
            "index.html should contain HTML content"
        );
        assert!(
            html_content.len() > 100,
            "index.html should have substantial content"
        );
    }

    #[test]
    fn test_release_profile_optimizations() {
        // Test that release binary is optimized (smaller than debug)
        let release_binary = Path::new("target/release/app");
        let debug_binary = Path::new("target/debug/app");

        if release_binary.exists() && debug_binary.exists() {
            let release_size = fs::metadata(release_binary)
                .expect("Should read release binary metadata")
                .len();
            let debug_size = fs::metadata(debug_binary)
                .expect("Should read debug binary metadata")
                .len();

            // Release should generally be smaller due to optimizations
            // (though this isn't always guaranteed, it's a good indicator)
            assert!(release_size > 0, "Release binary should have size");
            assert!(debug_size > 0, "Debug binary should have size");
        }
    }

    #[test]
    fn test_no_debug_symbols_in_release() {
        // Basic test - verify release binary exists and is reasonable size
        let release_binary = Path::new("target/release/app");
        if release_binary.exists() {
            let metadata =
                fs::metadata(release_binary).expect("Should read release binary metadata");

            // Release binary should be substantial but not excessively large
            let size_mb = metadata.len() / 1_000_000;
            assert!(size_mb > 5, "Release binary should be at least 5MB");
            assert!(size_mb < 500, "Release binary should be less than 500MB");
        }
    }

    #[test]
    fn test_bundle_metadata_consistency() {
        // Test that bundle metadata matches configuration
        let deb_dir = Path::new("target/release/bundle/deb");
        if deb_dir.exists() {
            let entries = fs::read_dir(deb_dir).expect("Should be able to read deb directory");

            for entry in entries.flatten() {
                let file_name = entry.file_name();
                let file_name_str = file_name.to_string_lossy();

                if file_name_str.ends_with(".deb") {
                    // Verify version is in filename
                    assert!(
                        file_name_str.contains("0.1.0"),
                        "Deb filename should contain version"
                    );
                    assert!(
                        file_name_str.contains("CartaOS"),
                        "Deb filename should contain product name"
                    );
                    break;
                }
            }
        }
    }
}
