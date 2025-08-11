# install-dev-env/config.py

"""
Centralized configuration for the CartaOS development environment installer.
"""

from typing import Dict, List

# --- Core Settings ---
MIN_PYTHON_VERSION = (3, 10)
MIN_NODE_MAJOR_VERSION = 18
REQUIRED_TESS_LANGS = ["eng", "por"]
LOG_FILE_NAME = "cartaos-install.log"

# --- Package Mappings ---
PACKAGE_MAP: Dict[str, Dict[str, List[str]]] = {
    "apt": {
        "base": ["git", "curl", "wget", "tesseract-ocr", "poppler-utils", "unpaper", "python3-pip", "python3-venv", "nodejs", "npm"],
        "pipx": ["pipx"],
        "tauri": ["libwebkit2gtk-4.1-dev", "libgtk-3-dev", "librsvg2-dev", "build-essential", "pkg-config"],
        "tess_langs": ["tesseract-ocr-eng", "tesseract-ocr-por"],
    },
    "dnf": {
        "base": ["git", "curl", "wget", "tesseract", "poppler-utils", "unpaper", "python3-pip", "python3-virtualenv", "nodejs"],
        "pipx": ["pipx"],
        "tauri": ["webkit2gtk4.1-devel", "gtk3-devel", "librsvg2-devel", "gcc-c++", "make", "pkg-config"],
        "tess_langs": ["tesseract-langpack-eng", "tesseract-langpack-por"],
    },
    "pacman": {
        "base": ["git", "curl", "wget", "tesseract", "poppler", "unpaper", "python-pip", "nodejs", "npm"],
        "pipx": ["pipx"],
        "tauri": ["webkit2gtk-4.1", "gtk3", "librsvg", "base-devel", "pkg-config"],
        "tess_langs": ["tesseract-data-eng", "tesseract-data-por"],
    },
    "brew": {
        "base": ["git", "curl", "wget", "tesseract", "poppler", "unpaper", "python@3.12", "node"],
        "pipx": ["pipx"],
        "tess_langs": ["tesseract-lang"],
    },
    "winget": {
        "base": ["Git.Git", "Python.Python.3.12", "Rustlang.Rust.MSVC", "OpenJS.NodeJS.LTS", "Tesseract.Tesseract", "Microsoft.VisualStudio.2022.BuildTools"],
    },
    "choco": {
        "base": ["git", "python", "rust", "nodejs-lts", "tesseract-ocr", "visualstudio2022buildtools"],
    }
}