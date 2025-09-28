# Tasks: NYT Connections Puzzle Assistant Web Application

**Input**: Design documents from `/Users/jim/Desktop/genai/sdd_connection_solver2/specs/001-nyt-connections-puzzle/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Web application**: `backend/src/`, `frontend/src/` (Constitution: Full-Stack Separation)
- Backend: FastAPI + Pydantic + pytest + uvicorn + uv (no persistent storage)
- Frontend: React + TypeScript + Jest + React Testing Library
- Paths shown below follow web application structure

## Phase 3.1: Setup
- [ ] T001 Create backend project structure with uv package management in `backend/`
- [ ] T002 Create frontend project structure with TypeScript and React in `frontend/`
- [ ] T003 [P] Configure backend linting (black, mypy) and testing (pytest) in `backend/pyproject.toml`
- [ ] T004 [P] Configure frontend linting (ESLint, Prettier) and testing (Jest) in `frontend/package.json`
- [ ] T005 [P] Create `.env` file with application configuration variables
- [ ] T006 [P] Setup backend development server configuration with uvicorn in `backend/src/main.py`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
**USER APPROVAL REQUIRED: Each test must be reviewed and approved before proceeding**
- [ ] T007 Contract test POST /api/puzzle/setup_puzzle in `backend/tests/contract/test_setup_puzzle.py` → **REQUIRES USER APPROVAL**
- [ ] T008 Contract test GET /api/puzzle/next_recommendation in `backend/tests/contract/test_next_recommendation.py` → **REQUIRES USER APPROVAL**
- [ ] T009 Contract test POST /api/puzzle/record_response in `backend/tests/contract/test_record_response.py` → **REQUIRES USER APPROVAL**
- [ ] T010 Integration test complete puzzle workflow in `backend/tests/integration/test_puzzle_workflow.py` → **REQUIRES USER APPROVAL**
- [ ] T011 Integration test error handling scenarios in `backend/tests/integration/test_error_handling.py` → **REQUIRES USER APPROVAL**
- [ ] T012 Frontend App component test in `frontend/tests/components/test_App.tsx` → **REQUIRES USER APPROVAL**
- [ ] T013 Frontend PuzzleInterface component test in `frontend/tests/components/test_PuzzleInterface.tsx` → **REQUIRES USER APPROVAL**
- [ ] T014 Frontend FileUpload component test in `frontend/tests/components/test_FileUpload.tsx` → **REQUIRES USER APPROVAL**
- [ ] T015 Frontend API service test in `frontend/tests/services/test_apiService.ts` → **REQUIRES USER APPROVAL**

## Phase 3.3: Backend Implementation (ONLY after backend tests are failing)
- [ ] T016 [P] PuzzleState Pydantic model in `backend/src/models/puzzle_state.py`
- [ ] T017 [P] WordGroup Pydantic model in `backend/src/models/word_group.py`
- [ ] T018 [P] IncorrectGroup Pydantic model in `backend/src/models/incorrect_group.py`
- [ ] T019 [P] Request/Response Pydantic models in `backend/src/models/api_models.py`
- [ ] T020 CSV parsing service in `backend/src/services/csv_service.py`
- [ ] T021 CSV validation service with error recovery in `backend/src/services/csv_validation_service.py`
- [ ] T022 Puzzle state management service in `backend/src/services/puzzle_service.py`
- [ ] T023 Application recovery service for malformed data in `backend/src/services/recovery_service.py`
- [ ] T024 Word recommendation service in `backend/src/services/recommendation_service.py`
- [ ] T025 FastAPI router for puzzle endpoints in `backend/src/api/puzzle_router.py`
- [ ] T026 Error handling middleware in `backend/src/api/error_handlers.py`
- [ ] T027 CORS configuration for local development in `backend/src/api/cors_config.py`

## Phase 3.4: Frontend Implementation (ONLY after frontend tests are failing)
- [ ] T028 [P] TypeScript type definitions in `frontend/src/types/puzzle.ts`
- [ ] T029 [P] API client service in `frontend/src/services/apiService.ts`
- [ ] T030 [P] FileUpload component with CSV validation in `frontend/src/components/FileUpload.tsx`
- [ ] T031 [P] PuzzleDisplay component for remaining words in `frontend/src/components/PuzzleDisplay.tsx`
- [ ] T032 [P] RecommendationDisplay component in `frontend/src/components/RecommendationDisplay.tsx`
- [ ] T033 [P] ResponseButtons component with color coding in `frontend/src/components/ResponseButtons.tsx`
- [ ] T034 [P] GameStatus component for counters and messages in `frontend/src/components/GameStatus.tsx`
- [ ] T035 [P] PreviousGuesses component with color coding in `frontend/src/components/PreviousGuesses.tsx`
- [ ] T036 Main PuzzleInterface component integration in `frontend/src/components/PuzzleInterface.tsx`
- [ ] T037 Root App component with routing in `frontend/src/App.tsx`
- [ ] T038 CSS styling for centered layout in `frontend/src/App.css`

## Phase 3.5: Integration & Polish
- [ ] T039 End-to-end test complete puzzle success scenario from quickstart.md
- [ ] T040 End-to-end test error handling scenarios from quickstart.md
- [ ] T041 [P] Backend unit tests for CSV parsing edge cases in `backend/tests/unit/test_csv_service.py`
- [ ] T042 [P] Backend unit tests for CSV validation and error recovery in `backend/tests/unit/test_csv_validation_service.py`
- [ ] T043 [P] Backend unit tests for puzzle state transitions in `backend/tests/unit/test_puzzle_service.py`
- [ ] T044 [P] Backend unit tests for application recovery scenarios in `backend/tests/unit/test_recovery_service.py`
- [ ] T045 [P] Backend unit tests for recommendation logic in `backend/tests/unit/test_recommendation_service.py`
- [ ] T046 [P] Frontend unit tests for component interactions in `frontend/tests/unit/test_component_integration.ts`
- [ ] T047 [P] Achieve 80% test coverage on backend business logic
- [ ] T048 [P] Achieve 80% test coverage on frontend components
- [ ] T049 [P] mypy type checking passes without errors on backend
- [ ] T050 [P] TypeScript compilation passes without errors on frontend
- [ ] T051 Validate application works offline (no external dependencies)
- [ ] T052 Performance validation - UI responsiveness for all interactions

## Dependencies
- Setup tasks (T001-T006) before all other tasks
- Contract tests (T007-T009) before backend implementation (T016-T027)
- Integration tests (T010-T011) before backend implementation
- Frontend tests (T012-T015) before frontend implementation (T028-T038)
- Backend models (T016-T019) before services (T020-T025) before API (T026-T027)
- CSV parsing (T020) before CSV validation (T021) and recovery service (T023)
- Frontend types (T028) before services (T029) before components (T030-T038)
- Core components (T030-T035) before integration component (T036) before App (T037)
- All implementation before end-to-end testing (T039-T040)
- All implementation before polish and coverage tasks (T041-T052)

## Parallel Example
```bash
# Setup phase - can run T003-T006 in parallel after T001-T002
T003: Configure backend linting & testing
T004: Configure frontend linting & testing  
T005: Create .env configuration
T006: Setup uvicorn server config

# Contract tests - all can run in parallel
T007: POST setup_puzzle contract test
T008: GET next_recommendation contract test
T009: POST record_response contract test

# Backend models - all can run in parallel
T016: PuzzleState model
T017: WordGroup model
T018: IncorrectGroup model
T019: API request/response models

# Frontend components - most can run in parallel
T030: FileUpload component
T031: PuzzleDisplay component
T032: RecommendationDisplay component
T033: ResponseButtons component
T034: GameStatus component
T035: PreviousGuesses component
```

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (T007-T009)
- [x] All entities have model tasks (T016-T019)
- [x] Error recovery and CSV validation tasks added (T021, T023, T042, T044)
- [x] All tests come before implementation
- [x] TDD tests require user approval (T007-T015)
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] TDD workflow enforced (tests fail before implementation)
- [x] Constitutional requirements addressed (Full-Stack Separation, API-First, Type Safety)
- [x] 3 API endpoints → 3 contract tests → backend implementation
- [x] UI components → component tests → React implementation
- [x] Quickstart scenarios → integration tests
- [x] Coverage and quality gates included