# MVP and Product Requirements - CartaOS

## 1. MVP Goal

The primary goal of the Minimum Viable Product (MVP) is to validate the core hypothesis of CartaOS: **it is possible to add significant value to a researcher's workflow by automating the processing and semantic enrichment of documents within a single desktop application.**

The focus is to test the end-to-end pipeline with real users, gather feedback on the usability and utility of the AI features, and establish the technical foundation for future expansions (web, mobile, collaboration).

## 2. MVP Functional Requirements

### FR-01: User Authentication
*   **Description:** The system must allow users to create an account with an email and password and to log into the desktop application.
*   **Acceptance Criteria:**
    *   A new user can register successfully.
    *   A registered user can log in.
    *   The login state is persisted between application sessions.
    *   This system will serve as the basis for future license and subscription management.

### FR-02: Unified Local Inbox
*   **Description:** The main interface must feature a designated area where the user can add PDF files from their local file system.
*   **Acceptance Criteria:**
    *   The user can drag and drop one or more PDF files onto the designated area.
    *   The user can click a button to open a file picker and select PDFs.
    *   Added files appear in a "pending" list in the UI.

### FR-03: Simplified Automated Processing Pipeline
*   **Description:** Once a document is added, the system must initiate a background processing pipeline.
*   **Acceptance Criteria:**
    *   **Triage:** The system analyzes the PDF and classifies it as "born-digital" (contains text) or "scanned" (image-based).
    *   **Extraction/OCR:** If "born-digital", the text is extracted. If "scanned", the system runs an OCR process to extract the text.
    *   **Semantic Enrichment:** The extracted text is sent to an LLM API (Gemini) to generate a concise summary (approx. 250 words), a list of 3-5 key concepts, and a list of 5-10 relevant tags.
    *   The user can see the status of each document in the pipeline (e.g., "Processing...", "Completed", "Error").

### FR-04: Knowledge Base (Local View)
*   **Description:** After processing, the documents and their generated metadata must be presented in a viewing interface.
*   **Acceptance Criteria:**
    *   There is a section in the UI that lists all completed documents.
    *   When a document is selected, the UI displays:
        *   The original filename.
        *   The AI-generated summary.
        *   The key concepts and tags in a list or badge format.
    *   The system stores the original PDF and an associated Markdown (`.md`) file containing the generated metadata in YAML Frontmatter format locally.

### FR-05: Output Integration (Export)
*   **Description:** The user must be able to export the processed artifacts for use in other tools.
*   **Acceptance Criteria:**
    *   An "Export" option exists for each completed document.
    *   The export creates a folder in the user's chosen location containing the original PDF and the `.md` file with the metadata.
    *   The format of the `.md` file is compatible with tools like Obsidian and Logseq.

## 3. MVP Non-Functional Requirements

### NFR-01: Platform
*   The MVP will be a desktop application compatible with **Windows 10/11, macOS (Apple Silicon and Intel), and Linux (Debian/Ubuntu)**, built with **Tauri and Svelte**.

### NFR-02: Performance
*   The application should start in under 5 seconds on modern hardware.
*   The user interface must remain responsive (no freezing) while a document is being processed in the background.
*   The processing of a 20-page document should be completed in a reasonable time (e.g., < 2 minutes).

### NFR-03: Security
*   User passwords must be stored on the backend database using strong hashing (e.g., bcrypt).
*   User-specific API keys (if applicable in the initial model) must be stored securely on the client using the operating system's native mechanisms, accessed via **Tauri's secure storage APIs (e.g., `@tauri-apps/plugin-store`)**.

### NFR-04: Usability
*   The interface must be intuitive, requiring minimal documentation for a new user to understand the main workflow.
*   The system must provide clear feedback on the processing status and any errors that occur.

## 4. Out of Scope for MVP

The following features are intentionally left out of the MVP to ensure focus and speed of delivery:

*   **NO** cloud synchronization or document storage on the backend.
*   **NO** collaborative features.
*   **NO** Chat with Documents (RAG).
*   **NO** direct integration with Zotero or other tools (manual export only).
*   **NO** Web or Mobile applications.
*   **NO** plugin marketplace.
*   **NO** advanced OCR editing or image cleaning features.