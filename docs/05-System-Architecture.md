# System Architecture

## 1. Architectural Principles

The CartaOS architecture is guided by the following principles:

*   **Desktop-First, Multi-Platform Ready:** The architecture prioritizes a best-in-class desktop experience while using technologies (web standards) that allow for future expansion to web and mobile platforms.
*   **Scalability:** The backend is designed to scale horizontally, supporting everything from a single user to thousands of concurrent users under team and institutional plans.
*   **Security:** Security is a primary concern. The architecture incorporates principles of security by design, especially regarding user data and API access:
    *   All network traffic uses HTTPS/TLS 1.2+; HSTS enabled at the edge.
    *   Data at rest is encrypted (PostgreSQL disk encryption, S3/GCS server-side encryption with per-bucket KMS keys).
    *   API keys/tokens are never stored in plaintext: server-side secrets in a managed secrets store (e.g., GCP Secret Manager); client-side tokens in Tauri secure storage.
    *   Processing workers run in isolated containers with least-privilege IAM roles and no direct Internet egress unless required.
*   **Separation of Concerns:** A clear division of responsibilities exists between the client (frontend), and the server (backend).
*   **Local-First & Cloud-Enhanced:** The application must be fully functional offline for core tasks. Cloud features enhance this experience with synchronization, heavy-duty processing, and collaboration.

## 2. High-Level Architecture Diagram (C4 Model - Level 1)

```mermaid
graph TD
    subgraph "End User"
        U(Academic Researcher)
    end

    subgraph "CartaOS Ecosystem"
        C[Desktop Client<br>(Tauri + Svelte)]
        B[Backend API<br>(Python + FastAPI)]
        DB[(Database<br>PostgreSQL + pgvector)]
        S3[(File Storage<br>Cloud Storage)]
        AI_Services(External AI Services<br>Google Gemini API)
        Auth(Authentication Service<br>Firebase Auth)
    end

    U -- "Uses" --> C
    C -- "Makes API calls (HTTPS)" --> B
    C -- "Authenticates" --> Auth
    B -- "Reads/Writes user data" --> DB
    B -- "Stores/Retrieves files" --> S3
    B -- "Calls for semantic analysis" --> AI_Services
    B -- "Validates tokens" --> Auth
```

## 3. Component Details

### 3.1. Frontend (Desktop Client)

*   **Technology:** Tauri (Rust), Svelte, TypeScript, TailwindCSS.
*   **Responsibilities:**
    *   **UI:** Render the entire user interface using Svelte components running inside a Tauri-managed webview.
    *   **State Management:** Manage client-side state using Svelte stores.
    *   **Backend Communication:** Make secure HTTPS calls to the backend API.
    *   **Security:** Store tokens and secrets only via Tauri secure storage; never persist tokens in plaintext. Enforce TLS certificate validation on all API requests. Apply rate limiting on auth flows.

### 3.2. Backend (Server)

*   **Technology:** Python with FastAPI.
*   **Responsibilities:**
    *   **API Gateway:** Expose a secure RESTful API.
    *   **User & Auth Service:** Manage user profiles and integrate with Firebase Auth. The backend must validate Firebase ID tokens server-side on every authenticated request.
    *   **Processing Service (Worker):** An asynchronous, idempotent service that executes the processing pipeline. All user-uploaded files are treated as untrusted and validated.
    *   **Semantic Search Service (RAG):** Handle "Chat with Documents" queries, enforcing multi-tenant isolation in all vector searches to prevent data leakage.

### 3.3. Data Architecture

*   **Relational Database (PostgreSQL):**
    *   **Usage:** Store structured data like user info, document metadata, etc.
    *   **`pgvector` Extension:** Provides vector similarity search capabilities.

*   **Object Storage (Cloud Storage - GCS/S3):**
    *   **Usage:** Store binary files (PDFs).
    *   **Access:** The backend issues short-lived, method-scoped signed URLs (e.g., PUT for upload, GET for download) only after validating the authenticated user.

