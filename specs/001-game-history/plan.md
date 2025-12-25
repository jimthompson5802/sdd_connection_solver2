# Implementation Plan: Game History and Persistent Storage

**Branch**: `001-game-history` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-game-history/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add database support for recording and viewing game history with persistent storage. The system will allow users to record completed puzzle games, view their game history in a scrollable table, and export results to CSV format. Server-side storage will track puzzle IDs (UUID v5 of normalized words), game dates, performance metrics (groups found, mistakes, guesses), and LLM provider/model information. Uniqueness enforced by (puzzle_id, game_date) tuple to prevent duplicates. Implementation uses SQLite for local single-user persistence with FastAPI backend and React frontend enhancements.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 4.9+ (frontend), Node.js 18+
**Primary Dependencies**: FastAPI, Pydantic, uvicorn, langchain (backend); React 19.1+, TypeScript, Jest, React Testing Library (frontend)
**Storage**: SQLite (local single-user persistence for game_results table)
**Testing**: pytest with 80% coverage requirement (backend), Jest with React Testing Library (frontend)
**Target Platform**: Desktop application (macOS/Linux/Windows) - local-first web application accessed via browser
**Project Type**: Web application (independent backend + frontend with REST API communication)
**Performance Goals**: API responses <100ms for local operations, frontend initial load <2s, supports up to 100 game records without degradation
**Constraints**: Local-first operation (no external dependencies except optional LLM calls), single-user application, SQLite file stored locally, no remote database, session-based with opt-in persistence
**Scale/Scope**: Single-user desktop application, ~10 new API endpoints/routes, ~5 new frontend components/views, database schema with 1 table (game_results), CSV export capability

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Evaluation

**I. Full-Stack Separation** ✅ PASS
- Feature maintains clear separation: React frontend calls FastAPI backend via REST API
- Database access only through backend endpoints (POST/GET /api/v2/game_results)
- Frontend components call backend via service layer pattern already established

**II. API-First Design** ✅ PASS
- New endpoints will be defined with OpenAPI/Pydantic schemas before implementation
- POST /api/v2/game_results and GET /api/v2/game_results with full request/response models
- CSV export via query parameter or dedicated route (server-side generation)

**III. Test-First Development** ✅ PASS
- Spec includes comprehensive acceptance scenarios for TDD
- Tests required: POST endpoint (success, duplicate, incomplete session, validation errors)
- Tests required: GET endpoint (with data, empty state), CSV export
- Both backend (pytest) and frontend (Jest/React Testing Library) coverage required

**IV. Type Safety** ✅ PASS
- Backend uses Pydantic models for game_results request/response
- Frontend uses TypeScript for new components (GameHistory view, RecordGame button)
- All session enhancements (puzzle_id, llm_provider_name, llm_model_name) will be typed

**V. Local-First Architecture** ✅ PASS (with documented opt-in persistence)
- SQLite storage is explicitly permitted by constitution v2.2.0 for single-user local persistence
- Persistence is opt-in and local-only (no remote database)
- Timestamps canonicalized to ISO 8601 UTC as required
- CSV export provides data portability as required
- No external network calls except optional LLM (already established pattern)

### Technology Standards Evaluation

✅ **Backend Stack**: Uses FastAPI + Pydantic + pytest + uvicorn (existing)
✅ **Frontend Stack**: Uses React + TypeScript + Jest + React Testing Library (existing)
✅ **Data Layer**: SQLite permitted for single-user game_results persistence per constitution
✅ **Schema Requirements**: Will document schema, provide CSV export, include migration notes
✅ **Timestamp Handling**: Will canonicalize to ISO 8601 UTC before persistence
✅ **Boolean Normalization**: Will normalize booleans in storage layer
✅ **Code Quality**: mypy + Black (Python), ESLint + TypeScript (frontend), test coverage gates

### Development Workflow Evaluation

✅ **Project Structure**: Maintains /backend and /frontend separation
✅ **API Documentation**: Will auto-generate OpenAPI specs from FastAPI routes
✅ **Testing Gates**: All tests must pass for both stacks
✅ **Performance**: <100ms API responses (local SQLite queries), <2s frontend load
✅ **Documentation**: Will document persistence enable/disable, database location, CSV format

### Violations Requiring Justification

**NONE** - This feature fully complies with constitution v2.2.0. The Phase 5 amendment explicitly permits opt-in local SQLite persistence for game_results with documented requirements, which this feature follows.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models.py                          # Enhanced: Add puzzle_id, llm fields to PuzzleSession
│   ├── api/
│   │   ├── v2_game_results.py            # NEW: POST/GET /api/v2/game_results endpoints
│   ├── services/
│   │   ├── recommendation_service.py      # Enhanced: Record llm provider/model in session
│   │   ├── game_results_service.py       # NEW: Game recording and retrieval logic
│   │   └── database_service.py           # NEW: SQLite connection and schema management
│   └── database/
│       ├── schema.sql                     # NEW: game_results table definition
│       └── migrations/                    # NEW: Migration scripts if needed
└── tests/
    ├── test_game_results_api.py          # NEW: API endpoint tests
    ├── test_game_results_service.py      # NEW: Service layer tests
    ├── test_database_service.py          # NEW: Database operation tests
    └── test_models.py                     # Enhanced: Test PuzzleSession enhancements

frontend/
├── src/
│   ├── components/
│   │   ├── GameSummary.tsx               # Enhanced: Add "Record Game" button
│   │   ├── GameHistoryView.tsx           # NEW: View Past Games table component
│   │   ├── RecordGameButton.tsx          # NEW: Record button with loading/error states
│   │   └── Sidebar.tsx                    # Enhanced: Add "Game History" navigation
│   ├── services/
│   │   └── gameResultsService.ts         # NEW: API client for game_results endpoints
│   └── types/
│       └── gameResults.ts                 # NEW: TypeScript interfaces for GameResult
└── tests/
    └── components/
        ├── GameHistoryView.test.tsx      # NEW: Game history view tests
        └── RecordGameButton.test.tsx     # NEW: Record button tests
```

**Structure Decision**: Web application structure (Option 2) selected. Project has established backend/ and frontend/ directories with independent build systems. This feature adds new API endpoints in backend/src/api/, new service layer in backend/src/services/, database layer in backend/src/database/, and new React components in frontend/src/components/. All existing patterns (Pydantic models, FastAPI dependency injection, React functional components, TypeScript) are maintained.

## Complexity Tracking

**No violations** - Constitution check passed. No complexity justification required.

---

## Phase 0: Research (Completed)

All research has been completed and documented in `research.md`. Key decisions:

1. **Database**: SQLite via Python standard library `sqlite3`
2. **Timestamps**: ISO 8601 UTC stored as TEXT
3. **Booleans**: TEXT with "true"/"false" strings (Phase 5 pattern)
4. **Puzzle ID**: UUID v5 of sorted, normalized words
5. **CSV Export**: Server-side using Python `csv` module with StreamingResponse
6. **Uniqueness**: Database UNIQUE constraint on (puzzle_id, game_date)
7. **Testing**: Layered approach (unit, integration, contract tests)
8. **Error Handling**: Structured HTTP responses with specific status codes
9. **Session State**: Three new fields on PuzzleSession
10. **Frontend State**: React hooks with service layer

See `research.md` for detailed rationale and alternatives considered.

---

## Phase 1: Design (Completed)

### Data Model

Complete entity definitions documented in `data-model.md`:

**GameResult Entity** (NEW):
- 10 fields including result_id, puzzle_id, game_date, performance metrics, LLM info
- UNIQUE constraint on (puzzle_id, game_date)
- CHECK constraints on count fields (0-4 range)
- Indexes for uniqueness and ordering

**PuzzleSession Enhancements**:
- New fields: puzzle_id, llm_provider_name, llm_model_name
- New methods: generate_puzzle_id(), set_llm_info(), to_game_result()
- New properties: is_finished, groups_found_count, total_guesses_count

**Relationships**:
- One PuzzleSession → zero or one GameResult
- Immutable records (insert-only, no updates)

### API Contracts

Complete endpoint specifications documented in `contracts/api_contracts.md`:

**POST /api/v2/game_results**:
- Request: RecordGameRequest (session_id, game_date)
- Success: 201 Created with GameResultResponse
- Errors: 400 (incomplete), 404 (not found), 409 (duplicate), 422 (validation), 500 (server)

**GET /api/v2/game_results**:
- Response: GameHistoryResponse (results array, count)
- Ordering: game_date DESC (most recent first)
- Empty state: Empty array with count 0

**GET /api/v2/game_results?format=csv**:
- Response: CSV file with specific column order
- Content-Disposition: attachment; filename="game_results_extract.csv"
- Header row always included

### Quickstart Guide

Complete development workflow documented in `quickstart.md`:
- Setup instructions for backend and frontend
- Step-by-step implementation guide
- Testing guide with coverage requirements
- Code quality checks (mypy, black, prettier)
- Debugging tips and common issues
- Environment configuration
- Deployment checklist

---

## Phase 1: Post-Design Constitution Re-Check

**Re-evaluation Result**: ✅ ALL GATES PASS

No new violations introduced during Phase 1 design. All design decisions align with:
- Constitution v2.2.0 requirements
- Research findings from Phase 0
- Existing codebase patterns and conventions
- Test-first development principles
- Local-first architecture with opt-in persistence

**Design artifacts validated**:
- ✅ data-model.md: SQLite schema, Pydantic models, TypeScript interfaces
- ✅ contracts/api_contracts.md: REST endpoints with comprehensive error handling
- ✅ quickstart.md: Development workflow with testing and quality gates

**Key compliance confirmations**:
1. SQLite persistence explicitly permitted (constitution v2.2.0)
2. ISO 8601 UTC timestamps as required
3. Server-side CSV generation per spec
4. Type safety via Pydantic + TypeScript
5. API-first design with OpenAPI documentation
6. 80% test coverage requirement maintained
7. Full-stack separation preserved
8. No external network dependencies (except existing LLM pattern)

---

## Next Steps

This plan document ends at Phase 1 completion as specified by speckit.plan workflow.

**Phase 2 (Implementation Tasks)**: Use `/speckit.tasks` command to generate `tasks.md` with:
- Detailed implementation tasks broken down by component
- Task dependencies and sequencing
- Acceptance criteria per task
- Estimated effort and priority

**To Begin Implementation**:
1. Review all Phase 1 artifacts (research, data-model, contracts, quickstart)
2. Run `/speckit.tasks` to generate implementation task breakdown
3. Follow quickstart.md development workflow
4. Implement with TDD (tests first, then implementation)
5. Validate against acceptance scenarios in spec.md

---

## Summary

**Branch**: `001-game-history`
**Implementation Plan**: `/Users/jim/Desktop/genai/sdd_connection_solver2/specs/001-game-history/plan.md`

**Generated Artifacts**:
- ✅ `plan.md` - This document (Technical Context, Constitution Check, Project Structure)
- ✅ `research.md` - Phase 0 research with 10 decision areas resolved
- ✅ `data-model.md` - Complete entity definitions, schemas, validation rules
- ✅ `contracts/api_contracts.md` - REST API specifications with request/response models
- ✅ `quickstart.md` - Development workflow and testing guide

**Constitution Compliance**: ✅ PASS (no violations)

**Ready for Implementation**: Phase 2 task breakdown can now be generated using `/speckit.tasks` command.

**Technology Stack**:
- Backend: Python 3.11+, FastAPI, Pydantic, SQLite, pytest
- Frontend: React 19.1+, TypeScript 4.9+, Jest, React Testing Library
- Database: SQLite (local single-user persistence)
- Testing: 80% backend coverage, 75%+ frontend coverage

**Key Features**:
- Record completed puzzle games with "Record Game" button
- View game history in scrollable table ordered by date
- Export game history to CSV format
- Deterministic puzzle_id (UUID v5) for uniqueness
- ISO 8601 UTC timestamps for consistency
- LLM provider/model tracking
- Duplicate prevention via database constraints
- Comprehensive error handling and validation
