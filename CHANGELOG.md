# Changelog

All notable changes to CartaOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Test Suite**: Fixed failing tests in `test_secure_keychain.py` by updating mocks to match current implementation
- **OCR Endpoint**: Corrected test expectations in `test_ocr_endpoint` to properly mock `OcrProcessor`
- **Test Coverage**: Improved test coverage for keychain and OCR functionality
- **Error Handling**: Enhanced error messages and validation in API endpoints
- **Integration Tests**: Fixed `test_full_pipeline_with_mocks` to properly test file movement during summarization
- **File Processing**: Ensured proper file movement in `CartaOSProcessor._move_pdf()` by updating the instance's `pdf_path`
- **Test Reliability**: Enhanced debug logging in test mocks to help diagnose file system issues

## [0.1.0] - 2024-08-21

### Added
- **Core Pipeline System**: Complete document processing pipeline with triage, OCR, and summarization
- **GUI Interface**: Modern SvelteKit-based interface with four main views:
  - Pipeline: File queue management and processing controls
  - Lab: Document analysis and experimentation workspace
  - Summaries: Generated document summaries display
  - Settings: Configuration management for API keys and vault paths
- **Tauri Desktop App**: Cross-platform desktop application with native performance
- **AI Integration**: Google Gemini API integration for document summarization
- **Obsidian Integration**: Direct vault path configuration and file management
- **File Processing**: Support for various document formats with OCR capabilities
- **Status System**: Real-time status updates with accessibility support
- **Environment Configuration**: Standardized `.env` file support with `GEMINI_API_KEY`

### Technical Features
- **Test Coverage**: Comprehensive test suite including:
  - Unit tests for core components
  - Integration tests for GUI components
  - End-to-end tests with Playwright
  - Visual regression testing with Storybook
  - Performance monitoring with Lighthouse
- **Release Packaging**: Automated build system creating:
  - Linux: `.deb`, `.rpm`, and `.AppImage` packages
  - Cross-platform installers ready for distribution
- **Code Quality**: Strict TypeScript configuration, ESLint rules, and accessibility compliance
- **CI/CD**: GitHub Actions workflows for automated testing and builds

### Security
- **API Key Protection**: Masked input fields and secure environment variable handling
- **CSP Implementation**: Content Security Policy for safe web content rendering
- **Input Validation**: Comprehensive form validation and error handling

### Accessibility
- **ARIA Support**: Proper ARIA roles, labels, and live regions
- **Keyboard Navigation**: Full keyboard accessibility throughout the interface
- **Screen Reader**: Optimized for assistive technologies

### Performance
- **Optimized Builds**: Production builds with minification and tree-shaking
- **Lazy Loading**: Dynamic imports for improved startup performance
- **Efficient Bundling**: Vite-powered build system with optimal asset handling

## [Unreleased]

### Planned
- Additional document format support
- Enhanced AI model options
- Batch processing improvements
- Plugin system for extensibility

---

## Release Notes

### Installation
Download the appropriate package for your platform:
- **Linux**: Use the `.deb` package for Debian/Ubuntu systems, `.rpm` for Red Hat/Fedora, or `.AppImage` for universal compatibility
- **Windows**: `.msi` installer (coming soon)
- **macOS**: `.dmg` disk image (coming soon)

### System Requirements
- **Linux**: Modern distribution with WebKit2GTK support
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: 100MB for application, additional space for document processing
- **Network**: Internet connection required for AI summarization features

### Configuration
1. Set up your Google Gemini API key in Settings
2. Configure your Obsidian vault path (optional)
3. Start processing documents through the Pipeline view

### Known Issues
- Large document processing may take significant time depending on content complexity
- OCR accuracy depends on document image quality
- Network connectivity required for AI features

### Support
- Documentation: See `README.md` and `SETUP.md`
- Issues: Report bugs and feature requests on GitHub
- Security: See `SECURITY.md` for security policy
