# 📚 CartaOS

**An open-source modular document processing system — OCR, summarization, AI, and full automation.**

CartaOS is an evolving platform for turning raw digital documents into structured, searchable knowledge. It is designed for researchers, educators, activists, and knowledge workers who want full control over their digital archives, outside of commercial black-box ecosystems.

> “Free your PDFs. Free your mind.”

---

## ✨ Key Features (Roadmap)

| Feature                   | Status        | Description |
|---------------------------|---------------|-------------|
| 📥 Document Ingestion      | ✅ Planned     | Drop any PDF, EPUB, or image-based document into the inbox for processing. |
| 🧠 AI-Powered Summarization| ✅ Planned     | Modular integration with LLMs (Google Gemini, OpenAI, Claude, etc.) for automatic fichamentos (summaries). |
| 🖼️ OCR & Image Processing  | ✅ In Progress | High-quality text extraction using Tesseract, PyMuPDF, pdfplumber and optional manual correction with ScanTailor Advanced. |
| 🧪 Modular Preprocessing   | ✅ In Progress | Pre-OCR cleanup with Unpaper, page splitting, dewarping, and quality triage. |
| 🧩 Plugin System           | ✅ Planned     | Allow users to add their own modules (e.g., another OCR engine, AI model, export format, etc). |
| ⚡ CLI + GUI               | ✅ Planned     | Typer-based CLI + GUI with Tauri + Svelte + Tailwind for modern UX. |
| 🌍 i18n & l10n             | ✅ Planned     | Internationalization from the ground up (starting in English, future support for Portuguese and others). |
| 🔍 Integration-friendly    | ✅ Planned     | Compatible with Zotero, Obsidian, markdown vaults, and plain-text workflows. |

---

## 🧱 Tech Stack

| Purpose                | Tech Stack                        |
|------------------------|-----------------------------------|
| Core logic & automation| **Python** (Typer, rich, logging) |
| Performance modules    | **Rust**                          |
| GUI                    | **Tauri** + Svelte + Tailwind     |
| OCR                    | Tesseract, pdfplumber, PyMuPDF    |
| AI Integration         | Google Gemini (initial), OpenAI, etc. |
| CLI                    | Typer (Python)                    |
| PDF/Image tools        | Unpaper, ScanTailor (fallback), img2pdf |
| Logging & testing      | Python logging, pytest            |

---

## 📁 Project Structure

```bash
/CartaOS/
├── .git/
├── .gitignore
├── README.md
├── install-dev-env.sh
|
├── backend/               # O nosso "motor" em Python
│   ├── cartaos_core/      # O pacote principal com a lógica
│   ├── tests/             # Testes para o backend
│   └── pyproject.toml     # Gestor de dependências (Poetry)
|
├── frontend/              # A nossa interface gráfica com Svelte
│   ├── src/               # Código fonte da GUI
│   ├── package.json
│   └── ...                # Outros ficheiros de configuração do Svelte/Vite
|
└── src-tauri/             # O "invólucro" Tauri que une tudo
    ├── tauri.conf.json    # Configuração da aplicação desktop
    ├── Cargo.toml         # Dependências do Rust
    └── src/
        └── main.rs        # Ponto de entrada da aplicação Rust
````

---

## 🚀 Getting Started

> ⚠️ Work-in-progress. Alpha version only.

### Requirements

* Python 3.11+
* Tesseract OCR
* Rust toolchain (for future extensions)
* Flatpak (for ScanTailor, optional)
* Poetry or virtualenv (recommended)
* img2pdf, unpaper

### Setup

```bash
git clone https://github.com/CartaOS/CartaOS.git
cd CartaOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🧪 Example Use (CLI)

```bash
# Triage raw files
cartaos triage ./Inbox/

# Run OCR on scanned PDFs
cartaos ocr ./03_Lab/file.pdf

# Summarize with Gemini
cartaos summarize ./05_ReadyForSummary/file.pdf
```

---

## 🌍 Internationalization (i18n)

All code, variables, and docs use **English** as the default language.

* Portuguese and other languages will be supported via i18n-friendly GUI/CLI.
* i18n powered by gettext or i18next (Tauri/Svelte).

---

## 🤝 Contributing

We welcome ideas, feedback, bug reports, and pull requests!

### To Contribute:

* Fork and clone the repo.
* Follow the [contribution guide](CONTRIBUTING.md) *(coming soon)*.
* Follow conventional commits.
* Respect the modular structure.

---

## 🛡️ License

CartaOS is licensed under the **MIT License**.

---

## 📚 Philosophy

CartaOS is inspired by the idea that **knowledge processing** should be:

* **Free** (as in freedom)
* **Transparent**
* **Hackable**
* **Modular**
* **Accessible**
* And **language-inclusive**

It aims to become an **open-source alternative to commercial tools like ABBYY FineReader**, tailored for research workflows.

---

## 🧠 Future Vision

* GUI: Drag-and-drop documents, preview summaries, tweak pipelines
* Plug-and-play AI: Choose your model
* Document vault integration: Sync with Obsidian/Zotero
* Full offline capability
* Community plugins

---

> *"The revolution will be processed."* ✊