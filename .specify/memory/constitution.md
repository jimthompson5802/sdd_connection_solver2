<!--
Sync Impact Report:
- Version change: 1.0.0 → 2.0.0 (MAJOR: removed persistent data storage requirement)
- Modified principles: Local-First Architecture (removed SQLite requirement, session-only data)
- Modified sections: Technology Standards (removed SQLite, updated to in-memory/session data)
- Templates requiring updates:
  ✅ constitution.md (this file) - completed
  ✅ plan-template.md - removed database directory, updated constitution check and version reference
  ✅ spec-template.md - reviewed, no changes needed (business-focused)
  ✅ tasks-template.md - removed SQLite setup tasks, updated task numbering and dependencies
- Follow-up TODOs: None - all database references removed
-->

# SDD Connection Solver Constitution

## Core Principles

### I. Full-Stack Separation
Frontend and backend MUST be developed as independent applications with clear boundaries. React frontend communicates with FastAPI backend exclusively through well-defined REST APIs. No direct database access from frontend. Each stack maintains its own dependencies, build process, and testing suite.

**Rationale**: Enables independent development, testing, and potential future deployment flexibility while maintaining clear architectural boundaries.

### II. API-First Design (NON-NEGOTIABLE)
All backend functionality MUST be exposed through REST API endpoints before frontend implementation begins. APIs must be documented with OpenAPI/Swagger specifications. Pydantic models define all request/response schemas with comprehensive validation.

**Rationale**: Ensures contract-driven development, enables parallel frontend/backend work, and provides self-documenting interfaces.

### III. Test-First Development (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced. Both frontend (Jest/React Testing Library) and backend (pytest) must achieve minimum 80% code coverage on core business logic.

Required tests: At minimum, tests MUST include the `POST /api/v2/setup_puzzle_from_image` cases (success, missing fields, oversized payload, provider failure). Additional tests covering persistence and export features are encouraged when those features are enabled, but are not mandatory for the session-only default mode.

**Rationale**: Ensures code quality, prevents regressions, and drives better API design through usage-first thinking.

### IV. Type Safety
TypeScript MUST be used for all frontend code. Python backend leverages Pydantic for runtime type validation and mypy for static type checking. All public functions and API endpoints must have complete type annotations.

**Rationale**: Catches errors at compile time, improves developer experience, and ensures data contract integrity between frontend and backend.

### V. Local-First Architecture
Application MUST function as a standalone desktop application without external service dependencies. The default and preferred mode of operation is session-only: no persistent data storage is required and the application should operate on transient/session data. Network calls are only permitted for explicitly optional features (for example, user-initiated data export/import).

Optional Local Persistence: An opt-in, local-only persistence mechanism (for example, an on-host SQLite store) is permitted for single-user, local-only use-cases such as exporting and analyzing `game_results` on the user's machine. This project is a single-user local application; no server DBMS is planned or required. When enabled, persistence must be documented and configurable via an explicit flag. Any persistent storage MUST remain local to the host (no remote or centrally-backed storage) unless explicit user consent is obtained and documented.

No external telemetry of persisted game results is allowed unless explicit, documented user consent is obtained. Exporting or backing-up persisted data off-host must be opt-in and clearly disclosed in the UI and documentation.

**Rationale**: Ensures user privacy, eliminates unintentional network dependencies, and gives an explicit, auditable exception where single-user local persistence is required for functionality such as export and analytics.

## Technology Standards

**Backend Stack**: FastAPI + Pydantic + pytest + uvicorn + uv (package management) + langchain (with other dependencies for openai and ollama integrations)
**Frontend Stack**: React + TypeScript + Jest + React Testing Library
**Data Layer**: The default data handling model is in-memory/session-based with Pydantic models for validation. An optional, local-only SQLite store is permitted for single-user, local-only use-cases (for example, persisting `game_results` to support local export and personal analytics). This project does not plan for a server DBMS; SQLite is acceptable for local single-user operation.

When persistence is enabled:

- The application MUST canonicalize timestamps to ISO 8601 (UTC) before persisting and validate formats on insert.
- Booleans persisted by SQLite (for example `puzzle_solved`) MUST be normalized in the storage layer (the Phase 5 implementation uses the literal strings `"true"`/`"false"`) and must be converted back to native booleans in any UX or export output.
- Any persistent schema MUST be documented and provide an export/import facility (CSV exporter) to allow safe data portability. A simple migration note or script is recommended for future compatibility, but enterprise-grade migration tooling is not required for this single-user application.

When persistence is not enabled, the application MUST operate in session-only mode with no on-disk storage of puzzle/game state.
**Development Tools**: uv for Python dependency management, npm/yarn for Node.js dependencies
**Code Quality**: mypy (Python), ESLint/TypeScript (frontend), pytest coverage, Jest coverage
**Image support**:  Supported image types: image/png, image/jpeg, image/webp. Max upload size: 5MB and server must return 413 Payload Too Large when exceeded. Image uploads are limited to clipboard paste (per spec); drag-and-drop is out-of-scope — note that as a UI scope constraint (optional but clarifies implementation).

**Version Requirements**: Python 3.11+, Node.js 18+, modern browser support (ES2020+)

## Development Workflow

**Project Structure**: `/backend` and `/frontend` directories with independent build systems
**API Documentation**: OpenAPI specs generated automatically from FastAPI routes
**Testing Gates**: All PRs must pass full test suites for both frontend and backend
**Type Checking**: mypy and TypeScript compilation must pass without errors
**Code Formatting**: Black (Python), Prettier (TypeScript/React), with pre-commit hooks

**Documentation**: The repository MUST include clear admin/developer documentation describing how to enable/disable local persistence, where the local database file is stored, how to export/import `game_results` (CSV format and header order), and any runtime flags related to persistence. These docs must be kept in the main `docs/` directory and referenced from the README.

**Performance Targets**: API responses <100ms for local operations, frontend initial load <2s
**Local Development**: uvicorn dev server (backend), Vite/CRA dev server (frontend)

## Governance

Constitution supersedes all other development practices. All feature implementations must verify compliance with these principles. Complexity that violates core principles must be justified with documented architectural decisions.

**Amendment Process**: Changes require documentation of impact, approval, and migration plan for existing code
**Compliance Review**: Each PR must pass constitution check as defined in plan-template.md
**Violation Handling**: Architecture that cannot satisfy principles requires refactoring or explicit exception documentation

**Logging & Observability**: Implementations MUST log persistence-related errors and provide clear, user-facing messages when persistence operations fail. Log locations and severity levels should be documented in the repository docs. For this single-user application, logs may be local files; no remote telemetry is permitted without explicit user consent.

**Amendment (Phase 5 — Local Persistence Exception)**: Per Phase 5 implementation notes, this version adds an explicit, auditable exception permitting an opt-in local persistence mechanism (for example, SQLite) for the `game_results` use-case. The amendment documents requirements for timestamp canonicalization, boolean normalization, migration documentation, and CSV export compatibility. This amendment was ratified to enable local exports and developer workflows while preserving the constitution's privacy-first intent.

## Appendix: Phase 5 References

- The Phase 5 implementation notes (`docs/phase5_implementation_notes.md`) contain the normative schema for the `game_results` table, CSV exporter column order, and the deterministic `puzzle_id` hashing algorithm (normalize, sort, join, SHA1). When local persistence is enabled, implementations MUST follow these specifications for interoperability with exporters and tools.

**Version**: 2.2.0 | **Ratified**: 2025-12-24 | **Last Amended**: 2025-12-24