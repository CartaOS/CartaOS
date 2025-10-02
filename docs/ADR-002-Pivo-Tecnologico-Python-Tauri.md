# ADR-002: Strategic Pivot to Python Backend and Tauri/Svelte Frontend

*   **Status:** Proposed
*   **Date:** 2025-10-02

## Context

The initial architecture for CartaOS, defined in `docs/07-Technology-Stack.md` and `ADR-001`, proposed a stack based on **Go** for the backend and **Flutter** for the frontend. The rationale was to leverage Go for its high performance and concurrency, and Flutter for its cross-platform compilation capabilities from a single codebase.

Upon deeper analysis of the product requirements and long-term vision, a strategic misalignment was identified between this stack and the problem domain CartaOS aims to solve. The product's core is heavily dependent on Natural Language Processing (NLP) and integration with AI models, an ecosystem where Python is the de facto standard. Additionally, the MVP's focus on a lightweight and efficient desktop application revealed that the advantages of a webview-based architecture, like Tauri's, could outweigh those of Flutter for the initial product.

This ADR documents the decision to execute a technology pivot to better align the tools with the project's goals.

## Decision

1.  **Invalidate `ADR-001-Flutter-for-Frontend.md`**.
2.  Adopt **Python** as the primary language for the API server development, using a modern framework like **FastAPI**. The Go language will be reserved as an option for future, high-performance microservices that do not have a direct dependency on the AI ecosystem.
3.  Adopt the **Tauri / Svelte / TailwindCSS** stack for desktop client development.
    *   **Tauri (Rust):** For the application shell, window management, and low-level client-side logic.
    *   **Svelte:** For building the user interface within the webview.
    *   **TailwindCSS:** For styling the interface.

## Justification

The decision is based on optimizing the technology's fit for the product, for both the backend and the frontend.

### Backend: Python + FastAPI

*   **Alignment with the Problem Domain:** CartaOS is, at its core, an AI product. Features like text extraction, RAG, semantic analysis, and citation extraction are central. Python is the lingua franca of data science and AI, with immediate, native access to state-of-the-art libraries such as `spaCy`, `Hugging Face Transformers`, `LlamaIndex`, `Pandas`, `scikit-learn`, etc.
*   **Architectural Simplification:** A Go-based backend would require a complex architecture of remote procedure calls (RPC) or command-line invocations to use Python services. Bringing the main logic into Python eliminates this complexity, creating a more cohesive and maintainable system.
*   **Speed of Iteration:** Prototyping and experimenting with new AI models and techniques, which is essential for innovation in CartaOS, is drastically faster and simpler in Python.

### Frontend: Tauri + Svelte + TailwindCSS

*   **Optimization for the Desktop MVP:** The primary focus is to deliver the best possible desktop application. The proposed stack is specialized for this.
*   **Lightweight and Efficient Binaries:** Tauri applications produce significantly smaller binaries compared to Flutter because they use the OS's native webview instead of bundling a full rendering engine. This improves distribution and the user's first impression.
*   **Access to the Vast Web Ecosystem:** The CartaOS interface is intensive in text manipulation and data visualization. The JavaScript/TypeScript ecosystem offers the best and most mature libraries for PDF rendering, complex text editors, syntax highlighting, and data visualizations (e.g., D3.js). Svelte integrates seamlessly with this ecosystem.
*   **Security and Performance of the Rust Core:** Tauri's architecture allows sensitive or high-performance client-side operations (e.g., file system access, local database manipulation) to be written in Rust, executing outside the JavaScript sandbox with maximum security and speed.
*   **Developer Experience (DX):** Svelte and TailwindCSS are widely recognized for providing a modern, fast, and enjoyable developer experience, boosting productivity.

## Consequences

### Positive

*   **Increased Development Velocity:** Acceleration in the development of AI features, which are the core of the product's value proposition.
*   **Simplified Architecture:** The backend becomes simpler, more cohesive, and aligned with the domain's tools.
*   **Superior Desktop Product:** The desktop application will be lighter, faster, and can more easily incorporate UI components from the web ecosystem.
*   **Strategic Alignment:** The technology now directly serves the product vision instead of creating friction against it.

### Negative or Risks to Mitigate

*   **Rewrite Debt:** The code already developed in Go and Dart/Flutter for the backend and frontend, respectively, will be discarded. This is a calculated and accepted cost to ensure the long-term success of the project.
*   **Future Mobile Strategy:** This decision optimizes for the desktop. When a mobile version becomes a priority, it will require a dedicated development effort (e.g., adapting the Svelte UI with CapacitorJS or developing a new React Native/Flutter app). This is the main trade-off.
*   **Toolchain Complexity:** The development environment setup becomes slightly more complex, requiring both the Rust and Node.js toolchains, in contrast to Flutter's unified toolchain.