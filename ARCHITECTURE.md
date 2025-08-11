# 🏗 CartaOS Architecture

---

## 📂 Directory Structure
```yaml
📦 CartaOS
 ┣ 📂 backend
 ┃ ┗ 📂 cartaos
 ┃    ┣ 📜 triage.py
 ┃    ┣ 📜 lab.py
 ┃    ┣ 📜 processor.py
 ┃    ┗ 📜 install_dev_env.py
 ┣ 📂 frontend
 ┣ 📂 data
 ┣ 📂 docs
 ┗ 📜 README.md
````

---

## 🔄 Data Flow

```
00_Inbox → 02_Triage → 03_Lab → 04_ReadyForOCR → 05_ReadyForSummary → 07_Processed
```

---

## 🧩 Components

* **CLI** — Python + Typer
* **GUI** — Tauri + Svelte + Tailwind
* **OCR** — Tesseract, pdfplumber
* **AI** — Google Gemini