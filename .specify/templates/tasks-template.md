# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Web application**: `backend/src/`, `frontend/src/` (Constitution: Full-Stack Separation)
- Backend: FastAPI + Pydantic + pytest + uvicorn + uv (no persistent storage)
- Frontend: React + TypeScript + Jest + React Testing Library
- Paths shown below follow web application structure

## Phase 3.1: Setup
- [ ] T001 Create backend project structure with uv package management
- [ ] T002 Create frontend project structure with TypeScript and React
- [ ] T003 [P] Configure backend linting (black, mypy) and testing (pytest)
- [ ] T004 [P] Configure frontend linting (ESLint, Prettier) and testing (Jest)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T005 [P] Contract test POST /api/[endpoint] in backend/tests/contract/
- [ ] T006 [P] Contract test GET /api/[endpoint] in backend/tests/contract/
- [ ] T007 [P] Backend integration tests in backend/tests/integration/
- [ ] T008 [P] Frontend component tests in frontend/tests/components/
- [ ] T009 [P] Frontend integration tests with API in frontend/tests/integration/

## Phase 3.3: Backend Implementation (ONLY after backend tests are failing)
- [ ] T010 [P] Pydantic models in backend/src/models/ with full type annotations
- [ ] T011 [P] Service layer with in-memory data handling in backend/src/services/
- [ ] T012 [P] FastAPI routes with OpenAPI documentation in backend/src/api/
- [ ] T013 Input validation with Pydantic validators
- [ ] T014 Error handling and structured logging

## Phase 3.4: Frontend Implementation (ONLY after frontend tests are failing)
- [ ] T015 [P] TypeScript type definitions in frontend/src/types/
- [ ] T016 [P] API client service in frontend/src/services/
- [ ] T017 [P] React components with props typing in frontend/src/components/
- [ ] T018 [P] Page components in frontend/src/pages/
- [ ] T019 State management and error handling (session-based only)
- [ ] T020 Responsive design and accessibility

## Phase 3.5: Integration & Polish
- [ ] T021 End-to-end testing with full stack
- [ ] T022 Performance validation (<100ms API, <2s frontend load)
- [ ] T023 [P] Achieve 80% test coverage on backend business logic
- [ ] T024 [P] Achieve 80% test coverage on frontend components
- [ ] T025 [P] mypy type checking passes without errors
- [ ] T026 [P] TypeScript compilation passes without errors
- [ ] T027 OpenAPI documentation generation and validation

## Dependencies
- Tests (T005-T009) before implementation (T010-T014)
- T010 blocks T011, T012
- T011 blocks T012
- Backend implementation (T010-T014) before frontend (T015-T020)
- Implementation before polish (T021-T027)

## Parallel Example
```
# Launch T004-T007 together:
Task: "Contract test POST /api/users in tests/contract/test_users_post.py"
Task: "Contract test GET /api/users/{id} in tests/contract/test_users_get.py"
Task: "Integration test registration in tests/integration/test_registration.py"
Task: "Integration test auth in tests/integration/test_auth.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [ ] All contracts have corresponding tests
- [ ] All entities have model tasks
- [ ] All tests come before implementation
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task