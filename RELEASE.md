# CartaOS Release Guide

This document describes how to build and package CartaOS for distribution.

## Prerequisites

- **Rust** (latest stable)
- **Node.js** (v18+)
- **Tauri CLI**: `cargo install tauri-cli`
- **Platform-specific tools**:
  - **Linux**: `build-essential`, `libwebkit2gtk-4.0-dev`, `libssl-dev`
  - **Windows**: Visual Studio Build Tools
  - **macOS**: Xcode Command Line Tools

## Build Process

### 1. Frontend Build

```bash
cd frontend
npm install
npm run build
```

### 2. Backend Build & Package

```bash
cd src-tauri
cargo tauri build
```

This will create platform-specific installers in `src-tauri/target/release/bundle/`:

- **Linux**: `.deb`, `.rpm`, `.AppImage`
- **Windows**: `.msi`, `.exe`
- **macOS**: `.dmg`, `.app`

## Release Configuration

### Version Management

Versions are managed in:
- `src-tauri/Cargo.toml` - Rust package version
- `src-tauri/tauri.conf.json` - App version and metadata
- `frontend/package.json` - Frontend package version

### Build Optimization

The release build includes:
- **Frontend**: Vite production build with minification
- **Backend**: Rust release profile with optimizations
- **Bundle**: Platform-specific installers with proper metadata

### Testing Release Build

Before distribution, test the release build:

```bash
# Test the built executable
cd src-tauri/target/release
./cartaos  # Linux/macOS
cartaos.exe  # Windows

# Or install and test the package
sudo dpkg -i target/release/bundle/deb/cartaos_*.deb  # Linux
```

## Distribution

### Automated Releases

The project uses GitHub Actions for automated releases:
- Triggered on version tags (`v*`)
- Builds for Linux, Windows, and macOS
- Creates GitHub release with binaries

### Manual Release

1. **Update versions** in all configuration files
2. **Run tests**: `npm test && cargo test`
3. **Build release**: `cargo tauri build`
4. **Test installer** on target platform
5. **Create release** on GitHub with binaries

## Security Considerations

- All builds are signed (when certificates are configured)
- Dependencies are audited for vulnerabilities
- Release binaries are checksummed
- No debug symbols in production builds

## Troubleshooting

### Common Build Issues

1. **Missing dependencies**: Install platform prerequisites
2. **Frontend build fails**: Check Node.js version and npm install
3. **Rust compilation errors**: Update Rust toolchain
4. **Bundle creation fails**: Verify Tauri CLI version

### Platform-Specific Notes

- **Linux**: Requires system WebKit and SSL libraries
- **Windows**: May need Visual C++ Redistributable
- **macOS**: Requires code signing for distribution

## File Locations

After successful build:
```
src-tauri/target/release/
├── bundle/
│   ├── deb/           # Linux .deb packages
│   ├── rpm/           # Linux .rpm packages
│   ├── appimage/      # Linux AppImage
│   ├── msi/           # Windows installer
│   └── dmg/           # macOS disk image
└── cartaos            # Executable binary
```
