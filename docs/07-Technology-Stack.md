# Technology Stack - CartaOS v2

## 1. Philosophy of Choice

The selection of the technology stack for CartaOS v2 is guided by the need to create a robust, scalable, and high-quality user experience, with a strong emphasis on aligning the tools with the project's core AI-driven domain. We prioritize modern technologies with strong ecosystems that allow for rapid iteration and long-term maintainability.

## 2. Detailed Stack

The stack is divided by the system's main components:

| Component | Technology Chosen | Justification |
| :--- | :--- | :--- |
| **Frontend (Client)** | **Tauri, Svelte & TypeScript** | Optimized for a lightweight and high-performance desktop MVP. Tauri provides a secure Rust-based backend for the frontend, resulting in small application binaries. Svelte offers a superb developer experience, and TypeScript ensures code quality. This stack gives us full access to the rich web ecosystem for UI components, ideal for a document-centric application. |
| **Backend (Server)** | **Python & FastAPI** | Chosen for its unparalleled ecosystem in AI, Machine Learning, and NLP, which is the core of CartaOS's value proposition. FastAPI provides a modern, high-performance framework for building APIs. This choice simplifies development and accelerates experimentation with AI-powered features. |
| **Database** | **PostgreSQL with `pgvector`** | A reliable and robust relational database. The `pgvector` extension allows us to unify relational and vector storage, simplifying the architecture for semantic search features and reducing data latency. |
| **Infrastructure Cloud** | **Google Cloud Platform (GCP)** | Offers leading managed services (GKE, Cloud Run), strong AI/ML offerings (Vertex AI, Gemini API), and a high-performance global network. |
| **Computation (Backend)** | **Google Kubernetes Engine (GKE) / Cloud Run** | GKE for large-scale container orchestration, offering auto-scaling and resilience. Cloud Run for cost-effective, scalable worker processes that can scale to zero. |
| **File Storage** | **Google Cloud Storage (GCS)** | Infinitely scalable, durable, and secure object storage with fine-grained access control through signed URLs. |
| **Authentication** | **Firebase Authentication** | A complete and secure solution for handling user authentication (email/password, social providers), with easy integration for both the Python backend and the client. |
| **AI Analysis & Processing** | **Python Ecosystem (Hugging Face, spaCy) & Google Gemini API** | The Python backend will directly integrate with leading AI/NLP libraries. `spaCy` for linguistic processing and `Hugging Face Transformers` for access to various models. The `Google Gemini API` will be used for high-level semantic tasks like summarization and tagging. |
| **Structural Document Analysis** | **Nougat, DocTR (via Python)** | These state-of-the-art tools, integrated via Python, are specialized in understanding document layouts (tables, figures, etc.), providing a level of detail beyond generic LLMs. |
| **Citation Extraction** | **GROBID (via Python wrapper)** | GROBID remains the state-of-the-art for parsing bibliographic data from PDFs, and it will be integrated directly into our Python pipeline. |
| **Vector Search (RAG)** | **LlamaIndex (Framework) on pgvector** | LlamaIndex provides the orchestration layer for our RAG implementation, handling data ingestion, chunking, and querying, while `pgvector` serves as the underlying vector store. |
| **DevOps & CI/CD** | **Docker & GitHub Actions** | Docker for creating consistent, containerized application environments. GitHub Actions for automating the CI/CD pipeline, including testing, building, and deploying. |