# 📚 CartaOS — [C]uration, [A]nalysis, and [R]efinement of [T]exts for [A]cademia ([O]pen [S]ource)

**Open-source modular document processing and knowledge structuring system — ingestion, triage, OCR, pre-processing, analysis, AI, automation, and advanced text refinement.**

CartaOS is a **fully open-source** platform for transforming raw digital documents into structured, searchable, and enriched knowledge. It is designed for researchers, educators, activists, and knowledge workers who need **full transparency, control, and extensibility** over their workflows.

> “Free your documents. Free your mind.”

---

## ✨ Key Features (Roadmap)

| Feature                       | Status        | Description                                                                                                                |
| ----------------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 📥 Document Ingestion         | ✅ Planned     | Drop any PDF, EPUB, or image-based document into the inbox for automated processing.                                       |
| 🧠 AI-Powered Analysis        | ✅ Planned     | Modular integration with LLMs (Google Gemini, OpenAI, Claude, etc.) for summaries, tagging, and semantic insights.         |
| 🖼️ OCR & Image Processing    | ✅ In Progress | High-quality text extraction with Tesseract, PyMuPDF, pdfplumber, and optional manual correction with ScanTailor Advanced. |
| 🧪 Preprocessing & Refinement | ✅ In Progress | Cleaning, deskewing, splitting, dewarping, and quality triage for optimal processing.                                      |
| 🧩 Plugin System              | ✅ Planned     | Extensible architecture to allow community-built modules for new OCR engines, AI models, or export formats.                |
| ⚡ CLI + GUI                   | ✅ Planned     | Typer-based CLI and a modern GUI using Tauri + Svelte + Tailwind.                                                          |
| 🌍 i18n & l10n                | ✅ Planned     | Internationalization and localization from the ground up.                                                                  |
| 🔍 Knowledge Integration      | ✅ Planned     | Integration with Zotero, Obsidian, markdown vaults, and other research tools.                                              |

---

## 🧱 Tech Stack

| Purpose                 | Tech Stack                              |
| ----------------------- | --------------------------------------- |
| Core logic & automation | **Python** (Typer, Rich, logging)       |
| Performance modules     | **Rust**                                |
| GUI                     | **Tauri** + Svelte + Tailwind           |
| OCR                     | Tesseract, pdfplumber, PyMuPDF          |
| AI Integration          | Google Gemini, OpenAI, etc.             |
| CLI                     | Typer (Python)                          |
| PDF/Image tools         | Unpaper, ScanTailor (optional), img2pdf |
| Logging & testing       | Python logging, pytest                  |

---

## 📁 Current Project Structure

```bash
CartaOS/
├── backend/               # Python automation, OCR, AI integration
├── frontend/              # Tauri + Svelte + Tailwind GUI
├── rust-core/             # Rust performance modules
├── tests/                 # Unit and integration tests
├── docs/                  # Documentation
├── i18n/                  # Internationalization files
├── 00_Inbox/              # Raw incoming documents
├── 01_Library/            # Organized, processed documents
├── 02_Triage/             # Files pending classification
├── 03_Lab/                # Image/PDF correction lab
├── 04_ReadyForOCR/        # Files prepared for OCR
├── 05_ReadyForSummary/    # Text-ready files for AI processing
├── 06_TooLarge/           # Oversized files requiring special handling
├── 07_Processed/          # Final outputs (summaries, processed docs)
├── README.md
├── pyproject.toml
└── .env                   # API keys and environment variables (not committed)
````

---

## 🚀 Getting Started

> ⚠️ Work-in-progress. Alpha stage.

### Requirements

* Python 3.11+
* Rust toolchain
* Node.js + pnpm
* Tesseract OCR
* Flatpak (optional, for ScanTailor Advanced)
* Poetry (Python dependency management)
* img2pdf, unpaper

### Setup

```bash
git clone https://github.com/CartaOS/CartaOS.git
cd CartaOS
poetry install
poetry shell
```

---

## 🧪 Example CLI Usage

```bash
# Triage raw files
cartaos triage ./00_Inbox/

# Run OCR
cartaos ocr ./04_ReadyForOCR/file.pdf

# Summarize with AI
cartaos summarize ./05_ReadyForSummary/file.pdf
```

---

## 🌍 Internationalization (i18n)

All code and docs use **English** as the default language.
Future releases will support multiple languages via i18n-friendly CLI/GUI.

---

## 🤝 Contributing

We welcome contributions!
Please fork the repo, work on feature branches, and submit pull requests.

---

## 🛡️ License

**Copyright © 2025 CartaOS contributors.**

This program is free software: you can redistribute it and/or modify it under the terms of the **GNU Affero General Public License v3.0 (AGPLv3)** as published by the Free Software Foundation.

See the [LICENSE](LICENSE) file for details.

> *"The revolution will be processed."* ✊