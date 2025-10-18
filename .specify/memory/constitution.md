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

**Rationale**: Ensures code quality, prevents regressions, and drives better API design through usage-first thinking.

### IV. Type Safety
TypeScript MUST be used for all frontend code. Python backend leverages Pydantic for runtime type validation and mypy for static type checking. All public functions and API endpoints must have complete type annotations.

**Rationale**: Catches errors at compile time, improves developer experience, and ensures data contract integrity between frontend and backend.

### V. Local-First Architecture
Application MUST function as a standalone desktop application without external service dependencies. No persistent data storage required - application operates on transient/session data only. Network calls only for optional features like data export/import.

**Rationale**: Ensures user privacy, eliminates network dependencies, provides instant startup, and works offline with minimal complexity.

## Technology Standards

**Backend Stack**: FastAPI + Pydantic + pytest + uvicorn + uv (package management) + langchain (with other dependencies for openai and ollama integrations)
**Frontend Stack**: React + TypeScript + Jest + React Testing Library
**Data Layer**: In-memory/session-based data handling, Pydantic models for validation
**Development Tools**: uv for Python dependency management, npm/yarn for Node.js dependencies
**Code Quality**: mypy (Python), ESLint/TypeScript (frontend), pytest coverage, Jest coverage

**Version Requirements**: Python 3.11+, Node.js 18+, modern browser support (ES2020+)

## Development Workflow

**Project Structure**: `/backend` and `/frontend` directories with independent build systems
**API Documentation**: OpenAPI specs generated automatically from FastAPI routes
**Testing Gates**: All PRs must pass full test suites for both frontend and backend
**Type Checking**: mypy and TypeScript compilation must pass without errors
**Code Formatting**: Black (Python), Prettier (TypeScript/React), with pre-commit hooks

**Performance Targets**: API responses <100ms for local operations, frontend initial load <2s
**Local Development**: uvicorn dev server (backend), Vite/CRA dev server (frontend)

## Governance

Constitution supersedes all other development practices. All feature implementations must verify compliance with these principles. Complexity that violates core principles must be justified with documented architectural decisions.

**Amendment Process**: Changes require documentation of impact, approval, and migration plan for existing code
**Compliance Review**: Each PR must pass constitution check as defined in plan-template.md
**Violation Handling**: Architecture that cannot satisfy principles requires refactoring or explicit exception documentation

**Version**: 2.0.0 | **Ratified**: 2025-09-28 | **Last Amended**: 2025-09-28