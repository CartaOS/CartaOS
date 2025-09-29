## Gemini Added Memories
- Completed comprehensive evaluation of PR #17 and local work. Fixed poetry.lock incompatibility, removed types-httpx, added build artifacts to .gitignore, verified existing logging and Ruff config, implemented HTTPS support in RcloneMount, improved error handling with custom exceptions, updated tests, and aligned CI with local development (Python 3.13, explicit venv activation, added pytest-asyncio to root pyproject.toml). Pushed all changes to dev. Investigated and explained PR #17's merge into main. Cleaned up local branches (only dev and main remain).

# Gemini Code Assistant Context

## Directory Overview

This directory contains the planning and architectural documentation for **CartaOS**, a software project currently in the design phase. The project is envisioned as an integrated research ecosystem designed to automate and enhance the workflow of academic researchers.

The directory is structured as a collection of Markdown files that together define the project's vision, architecture, technology stack, and initial product requirements.

## Key Files

The most important documents in this directory are:

*   `docs/01-Value-Proposition.md`: Explains the problem CartaOS aims to solve, the target audience, and the core value it provides.
*   `docs/02-Vision-Document.md`: Describes the long-term vision for the product, positioning it as the "operating system for academic research."
*   `docs/03-MVP-and-Requirements.md`: Defines the scope of the Minimum Viable Product (MVP), which will be a desktop application focused on local document processing.
*   `docs/05-System-Architecture.md`: Provides a high-level overview of the system's architecture, including the frontend, backend, and data storage components.
*   `docs/07-Technology-Stack.md`: Details the specific technologies chosen for the project, including Flutter for the frontend, Go for the backend, and PostgreSQL with pgvector for the database.
*   `docs/ADR-001-Flutter-for-Frontend.md`: An Architecture Decision Record that justifies the choice of Flutter for the cross-platform client application.

## Development Guidelines

This project follows a set of development guidelines inspired by the `AGENTIC-devDOCS` repository. These guidelines are documented in the following files:

*   `docs/CONTRIBUTING.md`: Provides guidelines for contributors to the CartaOS project.
*   `docs/STYLEGUIDE.md`: Defines the coding style, formatting conventions, and best practices for the CartaOS project.
*   `docs/WORKFLOW.md`: Describes the development workflow for the CartaOS project.
*   `docs/POSTPR.md`: Outlines the process to be followed after a Pull Request (PR) has been approved and merged.

## Project Management

The project's Epics, User Stories, Labels, Tags, Milestones, and Issues are defined in the following documents:

*   `docs/project-management/01-Epics.md`: Lists and describes the project's Epics.
*   `docs/project-management/02-User-Stories.md`: Lists and describes the User Stories for each Epic.
*   `docs/project-management/03-Labels-and-Tags.md`: Defines the labels and tags to be used in the issue tracker.
*   `docs/project-management/04-Milestones.md`: Defines the project's milestones.
*   `docs/project-management/05-Issues.md`: Lists the initial set of issues for the project.

## Session Progress (domingo, 28 de setembro de 2025)

During this session, we focused on setting up the project's development environment and initiating the implementation of core authentication features.

**Key Achievements:**

*   **Project Management Setup:**
    *   Analyzed existing documentation to define Epics, User Stories, Labels, Tags, Milestones, and Issues.
    *   Created a `docs/project-management` directory with detailed Markdown files for each of these elements.
    *   Successfully created all defined Labels and Milestones in the GitHub repository `CartaOS/CartaOS`.
    *   Created all initial Issues for the MVP in the GitHub repository `CartaOS/CartaOS`.
*   **Issue #1 Implementation (`feat(auth): Implementar a tela e o fluxo de login de usuário`):**
    *   Created a new branch: `feature/1-tela-login-usuario`.
    *   Implemented the `LoginScreen` with email and password fields, basic validation, and navigation to the registration screen.
    *   Integrated a mock authentication service (`AuthService`) with a loading indicator.
    *   Implemented error message display using `SnackBar` on login failure.
    *   Improved email validation using a regular expression.
    *   Added minimum password length validation (6 characters).
    *   Added `Key`s to widgets for more robust testing.
    *   All code was formatted, analyzed, and tested successfully after each major change.
    *   Committed and pushed all changes to the `feature/1-tela-login-usuario` branch.
    *   Created Pull Request #32 (https://github.com/CartaOS/CartaOS/pull/32) for the login screen implementation.

**Next Steps (Tomorrow):**

Our first steps tomorrow will be to thoroughly evaluate the new round of code reviews and any comments or suggestions made on PR #32. This will include:

*   Reviewing all new comments and suggestions from `gemini-code-assist`, `qodo-merge-pro`, and any human reviewers.
*   Addressing any identified bugs or pending implementations.
*   Incorporating suggested code improvements.
*   Making necessary documentation adjustments.
*   Resolving any remaining conflicts.
*   Considering suggested CI/CD optimizations.

## Usage

The contents of this directory should be used as a reference for understanding the goals, scope, and technical design of the CartaOS project. These documents provide the foundational context for any future development work.