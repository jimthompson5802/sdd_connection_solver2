---
description: "Implementation tasks for Game History and Persistent Storage feature"
---

# Tasks: Game History and Persistent Storage

**Input**: Design documents from `/specs/005-game-history/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/api_contracts.md ✅

**Tests**: Tests are included per acceptance scenarios in spec.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Web app structure: `backend/src/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and database setup

- [X] T001 Create database directory at backend/data/
- [X] T002 Create database schema file at backend/src/database/schema.py with game_results table DDL
- [X] T003 [P] Create database initialization module at backend/src/database/__init__.py with connection management
- [X] T004 [P] Add DATABASE_PATH environment variable to backend .env configuration

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Enhance PuzzleSession model in backend/src/models/puzzle_session.py with puzzle_id (UUID v5), llm_provider_name, llm_model_name attributes
- [X] T006 Implement generate_puzzle_id() method in backend/src/models/puzzle_session.py using uuid.uuid5(uuid.NAMESPACE_DNS, joined_words)
- [X] T007 [P] Create GameResult Pydantic model in backend/src/models/game_result.py with all fields from data-model.md
- [X] T008 [P] Create database repository module at backend/src/database/game_results_repository.py with insert/select/duplicate_check methods
- [X] T009 Implement set_llm_info(provider_name: str, model_name: str) method in backend/src/models/puzzle_session.py
- [X] T009a Update LLM recommendation services to call session.set_llm_info(provider, model) when generating recommendations
- [X] T010 Create database migration/initialization script at backend/src/database/migrations.py to create game_results table

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Record Completed Game (Priority: P1) 🎯 MVP

**Goal**: Enable users to save completed puzzle games to persistent storage with validation and duplicate prevention

**Independent Test**: Complete a puzzle game, click "Record Game" button on summary page, verify game saved via backend API query or database inspection

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Create contract test for POST /api/v2/game_results success case in backend/tests/api/test_v2_game_results.py
- [X] T012 [P] [US1] Create contract test for POST /api/v2/game_results duplicate detection (409 Conflict) in backend/tests/api/test_v2_game_results.py
- [X] T013 [P] [US1] Create contract test for POST /api/v2/game_results incomplete session (400 Bad Request) in backend/tests/api/test_v2_game_results.py
- [X] T014 [P] [US1] Create integration test for record game button interaction in frontend/tests/integration/RecordGameButton.test.tsx

### Backend Implementation for User Story 1

- [X] T015 [P] [US1] Create RecordGameRequest Pydantic model in backend/src/api/v2_game_results.py
- [X] T016 [P] [US1] Create GameResultResponse Pydantic model in backend/src/api/v2_game_results.py with status and result fields
- [X] T017 [US1] Implement POST /api/v2/game_results endpoint in backend/src/api/v2_game_results.py with session validation
- [X] T018 [US1] Add duplicate detection logic using (puzzle_id, game_date) uniqueness check in backend/src/api/v2_game_results.py
- [X] T019 [US1] Add session completion validation (is_finished check) in backend/src/api/v2_game_results.py
- [X] T020 [US1] Implement error handling for 400/404/409/500 responses in backend/src/api/v2_game_results.py
- [X] T021 [US1] Add route registration for POST /api/v2/game_results in backend/src/main.py

### Frontend Implementation for User Story 1

- [X] T022 [P] [US1] Create RecordGameButton component in frontend/src/components/RecordGameButton.tsx with disabled state during submission
- [X] T023 [P] [US1] Create gameResultsService in frontend/src/services/gameResultsService.ts with recordGame() API method
- [X] T024 [US1] Add RecordGameButton to game summary page in frontend/src/components/GameSummary.tsx
- [X] T025 [US1] Implement success confirmation message display in frontend/src/components/RecordGameButton.tsx
- [X] T026 [US1] Implement error message handling (duplicate, incomplete, network) in frontend/src/components/RecordGameButton.tsx
- [X] T027 [US1] Add button disable logic during API call to prevent duplicate submissions in frontend/src/components/RecordGameButton.tsx

### Session ID Integration (Missing Prerequisites)

> **NOTE: These tasks were identified as missing after T011-T027 implementation. Required for RecordGameButton to actually appear.**

- [X] T027a [US1] Add session_id field to SetupPuzzleResponse model in backend/src/models.py
- [X] T027b [US1] Return session_id in setup_puzzle endpoint response in backend/src/api_v1.py
- [X] T027c [US1] Return session_id in setup_puzzle_from_image endpoint response in backend/src/api/v2_image_setup.py
- [X] T027d [US1] Add sessionId to SetupPuzzleResponse interface in frontend/src/types/puzzle.ts
- [X] T027e [US1] Store sessionId from setup response in App.tsx state
- [X] T027f [US1] Pass sessionId prop to EnhancedPuzzleInterface in frontend/src/App.tsx
- [X] T027g [US1] Accept and pass sessionId prop from EnhancedPuzzleInterface to GameSummary in frontend/src/components/EnhancedPuzzleInterface.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can record completed games with validation

---

## Phase 4: User Story 2 - View Game History (Priority: P2)

**Goal**: Enable users to view all recorded games in a scrollable table ordered by most recent first

**Independent Test**: Record several games (manually or via seeded data), navigate to "Game History" > "View Past Games", verify all games appear in table with correct data and sorting

### Tests for User Story 2

- [X] T028 [P] [US2] Create contract test for GET /api/v2/game_results with data in backend/tests/api/test_v2_game_results.py
- [X] T029 [P] [US2] Create contract test for GET /api/v2/game_results empty state in backend/tests/api/test_v2_game_results.py
- [X] T030 [P] [US2] Create integration test for game history table rendering in frontend/tests/integration/GameHistoryTable.test.tsx
- [X] T031 [P] [US2] Create integration test for game history empty state in frontend/tests/integration/GameHistoryTable.test.tsx

### Backend Implementation for User Story 2

- [X] T032 [P] [US2] Create GameResultsListResponse Pydantic model in backend/src/api/v2_game_results.py with status and results array
- [X] T033 [US2] Implement GET /api/v2/game_results endpoint in backend/src/api/v2_game_results.py with ORDER BY game_date DESC
- [X] T034 [US2] Add route registration for GET /api/v2/game_results in backend/src/main.py

### Frontend Implementation for User Story 2

- [X] T035 [P] [US2] Create GameHistoryTable component in frontend/src/components/GameHistoryTable.tsx with horizontal and vertical scrolling
- [X] T036 [P] [US2] Create GameHistoryPage component in frontend/src/pages/GameHistoryPage.tsx
- [X] T037 [P] [US2] Add getGameResults() API method to frontend/src/services/gameResultsService.ts
- [X] T038 [US2] Add "Game History" collapsible section to navigation sidebar in frontend/src/components/Sidebar.tsx (collapsed by default)
- [X] T039 [US2] Add "View Past Games" navigation option under "Game History" section in frontend/src/components/Sidebar.tsx
- [X] T040 [US2] Implement table columns for all fields (result_id, puzzle_id, game_date, puzzle_solved, counts, LLM info) in frontend/src/components/GameHistoryTable.tsx
- [X] T041 [US2] Implement empty state message when no games recorded in frontend/src/components/GameHistoryTable.tsx
- [X] T042 [US2] Add route for /game-history path to frontend router in frontend/src/App.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can record and view games

---

## Phase 5: User Story 3 - Export Game History (Priority: P3)

**Goal**: Enable users to download game history as CSV file for external analysis and backup

**Independent Test**: View game history page with recorded games, click "Export CSV", verify CSV file downloads with all records and proper formatting

### Tests for User Story 3

- [ ] T043 [P] [US3] Create contract test for GET /api/v2/game_results?export=csv with data in backend/tests/api/test_v2_game_results.py
- [ ] T044 [P] [US3] Create contract test for GET /api/v2/game_results?export=csv empty state in backend/tests/api/test_v2_game_results.py
- [ ] T045 [P] [US3] Create integration test for export CSV button in frontend/tests/integration/ExportCSVButton.test.tsx

### Backend Implementation for User Story 3

- [ ] T046 [US3] Add CSV export logic to GET /api/v2/game_results endpoint with export query parameter in backend/src/api/v2_game_results.py
- [ ] T047 [US3] Implement CSV generation with correct column order (result_id, puzzle_id, game_date, puzzle_solved, counts, LLM info) in backend/src/api/v2_game_results.py
- [ ] T048 [US3] Add Content-Disposition header with filename "game_results_extract.csv" in backend/src/api/v2_game_results.py
- [ ] T049 [US3] Add Content-Type: text/csv header in backend/src/api/v2_game_results.py

### Frontend Implementation for User Story 3

- [ ] T050 [P] [US3] Create ExportCSVButton component in frontend/src/components/ExportCSVButton.tsx
- [ ] T051 [P] [US3] Add exportGameResultsCSV() API method to frontend/src/services/gameResultsService.ts
- [ ] T052 [US3] Add ExportCSVButton below game history table in frontend/src/pages/GameHistoryPage.tsx
- [ ] T053 [US3] Implement download trigger with proper filename handling in frontend/src/components/ExportCSVButton.tsx

**Checkpoint**: All user stories should now be independently functional - complete record/view/export workflow

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T054 [P] Add comprehensive unit tests for PuzzleSession enhancements in backend/tests/models/test_puzzle_session.py
- [ ] T055 [P] Add unit tests for GameResult model validation in backend/tests/models/test_game_result.py
- [ ] T056 [P] Add unit tests for database repository methods in backend/tests/database/test_game_results_repository.py
- [ ] T057 [P] Update API documentation in docs/ with game history endpoints and examples
- [ ] T058 [P] Add quickstart validation for game history workflow in docs/quickstart-validation-results.md
- [ ] T059 Code review and refactoring for consistency across all user stories
- [ ] T060 Performance testing with 100+ game records to verify no degradation
- [ ] T061 [P] Update frontend component tests for coverage targets (75%+) in frontend/tests/components/
- [ ] T062 Run full backend test suite and verify 80%+ coverage requirement
- [ ] T063 Run quickstart.md validation per specs/005-game-history/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (can be tested with seeded data)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2 (can be tested with seeded data)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Backend models/repositories before endpoints
- Backend endpoints before frontend services
- Frontend services before frontend components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003 and T004 can run in parallel

**Phase 2 (Foundational)**:
- T007, T008, T010 can run in parallel after T005-T006 complete

**Phase 3 (User Story 1)**:
- Tests T011-T014 can all run in parallel
- Backend models T015-T016 can run in parallel
- Frontend components T022-T023 can run in parallel
- Once backend endpoint (T017-T021) is complete and frontend service (T023) is complete, frontend components (T024-T027) can proceed

**Phase 4 (User Story 2)**:
- Tests T028-T031 can all run in parallel
- Backend model T032 independent
- Frontend components T035-T037 can run in parallel

**Phase 5 (User Story 3)**:
- Tests T043-T045 can all run in parallel
- Frontend components T050-T051 can run in parallel

**Phase 6 (Polish)**:
- T054-T058, T061 can all run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T011: "Contract test for POST /api/v2/game_results success case"
Task T012: "Contract test for POST duplicate detection (409 Conflict)"
Task T013: "Contract test for POST incomplete session (400 Bad Request)"
Task T014: "Integration test for record game button interaction"

# Launch backend Pydantic models together:
Task T015: "Create RecordGameRequest Pydantic model"
Task T016: "Create GameResultResponse Pydantic model"

# Launch frontend components together:
Task T022: "Create RecordGameButton component"
Task T023: "Create gameResultsService with recordGame() method"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → Database directory and schema ready
2. Complete Phase 2: Foundational → PuzzleSession enhanced, GameResult model ready, repository implemented
3. Complete Phase 3: User Story 1 → Record game functionality complete
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T010)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) (T011-T027)
3. Add User Story 2 → Test independently → Deploy/Demo (T028-T042)
4. Add User Story 3 → Test independently → Deploy/Demo (T043-T053)
5. Polish → Final quality pass (T054-T063)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T010)
2. Once Foundational is done:
   - Developer A: User Story 1 (T011-T027)
   - Developer B: User Story 2 (T028-T042)
   - Developer C: User Story 3 (T043-T053)
3. Stories complete and integrate independently
4. Team completes Polish together (T054-T063)

---

## Task Summary

- **Total Tasks**: 63
- **Setup Phase**: 4 tasks
- **Foundational Phase**: 6 tasks (BLOCKING)
- **User Story 1 (P1)**: 17 tasks (4 tests + 13 implementation)
- **User Story 2 (P2)**: 15 tasks (4 tests + 11 implementation)
- **User Story 3 (P3)**: 11 tasks (3 tests + 8 implementation)
- **Polish Phase**: 10 tasks
- **Parallel Opportunities**: 32 tasks marked [P] can run in parallel within their phases

---

## Notes

- [P] tasks = different files, no dependencies within same phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All tests follow TDD: write test → verify failure → implement → verify pass
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Database stored at: `backend/data/connect_puzzle_game.db`
- Puzzle ID uses UUID v5 (not SHA1) per research.md
- Boolean storage uses TEXT "true"/"false" per Phase 5 pattern
- All timestamps ISO 8601 with timezone, canonicalized to UTC
- Activate the virutal environment `cd backend && source .venv/bin/activate` to run python programs or tests
