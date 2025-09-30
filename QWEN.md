# CartaOS - QWEN Code Assistant Context

## Project Overview

CartaOS is an integrated research ecosystem designed to automate and enhance the workflow of academic researchers. It's envisioned as the "operating system for academic research" and is being developed as a Flutter-based cross-platform application with a Go backend and PostgreSQL database.

### Architecture
- **Frontend**: Flutter application (Dart) - Cross-platform client
- **Backend**: Go services 
- **Database**: PostgreSQL with pgvector for vector storage
- **Infrastructure**: Docker-based deployment with docker-compose

### Project Structure
```
CartaOS/
├── backend/                 # Go backend services
├── lib/                     # Flutter application source code
│   └── src/
│       ├── features/        # Feature modules (e.g., auth)
│       └── app.dart         # Main application entry point
├── docs/                    # Comprehensive documentation
├── test/                    # Test files (Dart/Flutter tests)
├── docker-compose.yml       # Docker orchestration
├── pubspec.yaml             # Flutter project configuration
└── GEMINI.md                # Project planning documentation
```

## Building and Running

### Prerequisites
- Flutter SDK (>=3.3.0)
- Go 1.21+
- Docker and Docker Compose
- PostgreSQL client (optional, for local development)

### Setup and Running

1. **Environment Setup**:
   ```bash
   # Create .env file based on the project requirements (not in repo)
   cp .env.example .env  # if available, or create your own
   ```

2. **Flutter Application**:
   ```bash
   # Install Flutter dependencies
   flutter pub get
   
   # Run the application
   flutter run
   ```

3. **Full Stack with Docker**:
   ```bash
   # Start the entire stack (backend + database)
   docker-compose up --build
   ```

4. **Running Tests**:
   ```bash
   # Run Flutter tests
   flutter test
   
   # Run backend tests
   cd backend && go test ./...
   ```

### Development Commands
- `flutter analyze` - Static analysis
- `flutter format .` - Format code
- `flutter pub get` - Install dependencies
- `flutter build <platform>` - Build for specific platform

## Development Conventions

### Code Structure
- **Feature-based organization**: Features are organized in `lib/src/features/` directories
- **Clean Architecture**: Each feature follows a layered architecture (data, domain, presentation)
- **Authentication Module**: Currently implemented with login screen and mock authentication service

### Coding Standards
- Follow Flutter/Dart official style guide
- Use Material Design components
- Implement proper error handling and loading states
- Use keys for widgets that need robust testing
- Apply proper validation (e.g., email regex, minimum password length)

### Project Management
- Issues, Epics, and User Stories are defined in `docs/project-management/`
- GitHub Labels, Milestones, and Issue templates are configured
- Development workflow follows the documented process in `docs/WORKFLOW.md`

## Key Documentation

### Core Documents
- `docs/01-Value-Proposition.md` - Problem statement and value proposition
- `docs/02-Vision-Document.md` - Long-term vision for CartaOS
- `docs/03-MVP-and-Requirements.md` - Minimum Viable Product scope
- `docs/05-System-Architecture.md` - High-level system architecture
- `docs/07-Technology-Stack.md` - Technology choices and rationale

### Developer Guidelines
- `docs/CONTRIBUTING.md` - Contribution guidelines
- `docs/STYLEGUIDE.md` - Coding style and conventions
- `docs/WORKFLOW.md` - Development workflow
- `docs/ADR-001-Flutter-for-Frontend.md` - Architecture decision record

## Current Status

The project is actively under development with:
- Initial authentication feature implemented (Login screen)
- Proper validation and error handling in place
- Unit and integration tests for core features
- Complete Docker-based local development setup
- Comprehensive project documentation in the `docs/` directory
- Project management infrastructure with GitHub issues, labels, and milestones

## Important Files and Directories

- `pubspec.yaml` - Flutter project dependencies and configuration
- `docker-compose.yml` - Multi-container application orchestration
- `backend/go.mod` - Go module dependencies
- `test/` - Application test suite
- `lib/src/features/auth/` - Current authentication implementation
- `docs/` - Complete project documentation (architecture, requirements, etc.)