---
description: "Task breakdown for image-based puzzle setup feature"
feature: "004-image-puzzle-setup"
generated: "December 13, 2025"
---

# Tasks: Image-Based Puzzle Setup

**Input**: Design documents from `/specs/004-image-puzzle-setup/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: REQUIRED - Per constitution Principle III (Test-First Development), all test tasks MUST be implemented following TDD workflow (write tests → tests fail → implement → tests pass). Minimum 80% code coverage required.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: `- [ ]` (markdown checkbox)
- **[ID]**: Task ID in execution order (T001, T002, etc.)
- **[P]**: Parallelizable task (different files, no incomplete dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5) - REQUIRED for user story tasks only
- **Description**: Clear action with exact file path

## Path Conventions

- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Verify development environment and dependencies

- [x] T001 Verify Python 3.11+ environment and activate backend virtual environment at backend/.venv
- [x] T002 Verify Node.js 18+ and npm dependencies installed for frontend
- [x] T003 [P] Verify LangChain vision support available in backend environment
- [x] T004 [P] Verify Clipboard API support in target browsers (Chrome 66+, Firefox 63+, Safari 13.1+)
- [x] T005 Configure LLM provider credentials (OPENAI_API_KEY or Ollama local service)
- [x] T006 Run existing backend and frontend tests to ensure no regressions before starting

**Checkpoint**: Environment ready - all prerequisites verified

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Add ExtractedWords Pydantic model to backend/src/models.py
- [x] T008 [P] Add ImageSetupRequest Pydantic model to backend/src/models.py
- [x] T009 [P] Add ImageSetupResponse Pydantic model to backend/src/models.py
- [x] T010 Create ImageWordExtractor service at backend/src/services/image_word_extractor.py with extract_words method skeleton
- [x] T011 Add TypeScript ImageSetupRequest interface to frontend/src/types/puzzle.ts
- [x] T012 [P] Add TypeScript ImageSetupResponse interface to frontend/src/types/puzzle.ts
- [x] T013 [P] Add TypeScript ImagePasteState interface to frontend/src/types/puzzle.ts
- [x] T014 Add 'from-image' navigation action type to frontend/src/types/navigation.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 4 - Extract Words from Image and Start Puzzle (Priority: P1) 🎯 MVP

**Goal**: Core end-to-end flow - user can paste image, extract words via LLM, and start playing puzzle

**Independent Test**: Paste valid 4x4 grid image, select provider/model, click "Setup Puzzle", verify 16 words extracted and puzzle interface loads

**Why P1 and MVP**: This delivers the essential feature value - converting image to playable puzzle. All other stories enhance this core flow.

### Tests for User Story 4 (REQUIRED - TDD) ⚠️

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation per constitution Principle III**

- [x] T015 [P] [US4] Contract test for POST /api/v2/setup_puzzle_from_image success case in backend/tests/contract/test_setup_puzzle_from_image.py
- [x] T016 [P] [US4] Contract test for POST /api/v2/setup_puzzle_from_image validation errors in backend/tests/contract/test_setup_puzzle_from_image.py
- [x] T017 [P] [US4] Unit test for ImageWordExtractor.extract_words with mock LLM in backend/tests/unit/test_image_word_extractor.py
- [x] T018 [P] [US4] Integration test for image setup flow (paste → extract → puzzle) in frontend/tests/integration/test_image_setup_flow.test.tsx

### Backend Implementation for User Story 4

- [x] T019 [US4] Implement ImageWordExtractor.extract_words method in backend/src/services/image_word_extractor.py using LLMProviderFactory
- [x] T020 [US4] Add vision prompt construction with 4-strategy approach (basic + grid hints + example + validation) in backend/src/services/image_word_extractor.py
- [x] T021 [US4] Implement with_structured_output(ExtractedWords) invocation with base64 image in backend/src/services/image_word_extractor.py
- [x] T022 [US4] Create v2_image_setup.py API route file at backend/src/api/v2_image_setup.py
- [x] T023 [US4] Implement POST /api/v2/setup_puzzle_from_image endpoint in backend/src/api/v2_image_setup.py
- [x] T024 [US4] Add endpoint request validation and error handling (400, 413, 422, 500) in backend/src/api/v2_image_setup.py
- [x] T025 [US4] Integrate session_manager.create_session with extracted words in backend/src/api/v2_image_setup.py
- [x] T026 [US4] Register v2_image_setup router in backend/src/main.py

### Frontend Implementation for User Story 4

- [x] T027 [P] [US4] Create ImagePuzzleSetup component skeleton at frontend/src/components/ImagePuzzleSetup.tsx
- [x] T028 [P] [US4] Create ImagePuzzleSetup.css at frontend/src/components/ImagePuzzleSetup.css
- [x] T029 [US4] Implement handlePaste function with Clipboard API in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T030 [US4] Implement base64 encoding from Blob using FileReader in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T031 [US4] Add image preview display using Object URL in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T032 [US4] Add provider and model dropdowns (basic implementation) in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T033 [US4] Implement "Setup Puzzle" button click handler in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T034 [US4] Add setupPuzzleFromImage API method to frontend/src/services/api.ts
- [X] T035 [US4] Add 'from-image' navigation action handler in frontend/src/App.tsx
- [X] T036 [US4] Add ImagePuzzleSetup component rendering when currentView is 'image-setup' in frontend/src/App.tsx
- [X] T037 [US4] Implement onImageSetup callback to transition to puzzle-active view in frontend/src/App.tsx

**Checkpoint**: ✅ COMPLETED - Core feature works - users can paste image, extract words, and play puzzle

---

## Phase 4: User Story 1 - Access Image-Based Puzzle Setup (Priority: P1)

**Goal**: Polished navigation - users can easily find and access "From Image" option in sidebar

**Independent Test**: Click "From Image" in sidebar, verify image setup interface displays correctly

**Why after US4**: Navigation is essential UX but the feature works without pretty navigation. This makes US4 accessible.

### Tests for User Story 1 (REQUIRED - TDD) ⚠️

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation per constitution Principle III**

- [x] T038 [P] [US1] Component test for Sidebar "From Image" item in frontend/src/components/Sidebar.test.tsx
- [x] T039 [P] [US1] Integration test for navigation flow (click From Image → verify interface) in frontend/tests/integration/test_navigation_flow.test.tsx

### Implementation for User Story 1

- [x] T040 [US1] Add "From Image" navigation item below "From File" in frontend/src/components/Sidebar.tsx
- [x] T041 [US1] Add onNavigationAction handler for 'from-image' type in frontend/src/components/Sidebar.tsx
- [x] T042 [US1] Update Sidebar tests to verify "From Image" item renders in frontend/src/components/Sidebar.test.tsx
- [x] T043 [US1] Verify layout matches ASCII diagram specification with vertical component arrangement in frontend/src/components/ImagePuzzleSetup.tsx

**Checkpoint**: ✅ COMPLETED - Navigation complete - users can access image setup from sidebar

---

## Phase 5: User Story 2 - Paste and Preview Puzzle Image (Priority: P2)

**Goal**: Enhanced image handling - placeholder text, keyboard hints, clear preview, better validation feedback

**Independent Test**: Navigate to "From Image", verify placeholder with hints, paste image, verify clear preview displays

**Why P2**: Improves UX for paste area but core paste functionality already works from US4

### Tests for User Story 2 (REQUIRED - TDD) ⚠️

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation per constitution Principle III**

- [x] T044 [P] [US2] Component test for placeholder display when no image pasted in frontend/src/components/ImagePuzzleSetup.test.tsx
- [x] T045 [P] [US2] Component test for image preview after paste in frontend/src/components/ImagePuzzleSetup.test.tsx
- [x] T046 [P] [US2] Component test for invalid content paste (non-image) in frontend/src/components/ImagePuzzleSetup.test.tsx

### Implementation for User Story 2

- [x] T047 [P] [US2] Add placeholder content (icon, "Paste image here" text, CMD+V/CTRL+V hint) in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T048 [P] [US2] Style placeholder area with visual affordance in frontend/src/components/ImagePuzzleSetup.css
- [x] T049 [US2] Add non-image paste detection and error message "Please paste a valid image" in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T050 [US2] Enhance image preview with proper sizing and aspect ratio in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T051 [US2] Add image clear/replace capability when pasting new image in frontend/src/components/ImagePuzzleSetup.tsx

**Checkpoint**: ✅ COMPLETED - Image paste area is polished with clear instructions and good UX

---

## Phase 6: User Story 3 - Configure LLM Provider and Model (Priority: P2)

**Goal**: Refined provider/model selection - default values, proper dropdown population, consistent with puzzle solving

**Independent Test**: Navigate to "From Image", verify dropdowns pre-populated with defaults matching puzzle solving

**Why P2**: Improves provider selection UX but basic dropdowns already work from US4

### Tests for User Story 3 (REQUIRED - TDD) ⚠️

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation per constitution Principle III**

- [x] T052 [P] [US3] Component test for provider dropdown population in frontend/src/components/ImagePuzzleSetup.provider.test.tsx
- [x] T053 [P] [US3] Component test for model dropdown population based on selected provider in frontend/src/components/ImagePuzzleSetup.provider.test.tsx
- [x] T054 [P] [US3] Component test for default provider/model pre-selection in frontend/src/components/ImagePuzzleSetup.provider.test.tsx

### Implementation for User Story 3

- [x] T055 [P] [US3] Populate provider dropdown from ImagePuzzleSetupProps.providers in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T056 [P] [US3] Set default provider from ImagePuzzleSetupProps.defaultProvider in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T057 [US3] Implement model dropdown dynamic population based on selected provider in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T058 [US3] Set default model from ImagePuzzleSetupProps.defaultModel in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T059 [US3] Add provider change handler to update available models in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T060 [US3] Style dropdowns consistently with existing puzzle UI in frontend/src/components/ImagePuzzleSetup.css

**Checkpoint**: ✅ COMPLETED - Provider/model configuration is polished and consistent with existing UI

---

## Phase 7: User Story 5 - Handle Image Size and Extraction Errors (Priority: P3)

**Goal**: Comprehensive error handling - size validation, extraction failures, provider errors, clear user feedback

**Independent Test**: Test each error scenario independently (oversized image, unclear grid, non-vision model, provider failure)

**Why P3**: Error handling improves reliability but happy path works without it. Users can work around errors.

### Tests for User Story 5 (REQUIRED - TDD) ⚠️

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation per constitution Principle III**

- [x] T061 [P] [US5] Contract test for HTTP 413 payload too large in backend/tests/contract/test_setup_puzzle_from_image.py
- [x] T062 [P] [US5] Contract test for HTTP 400 wrong word count in backend/tests/contract/test_setup_puzzle_from_image.py
- [x] T063 [P] [US5] Contract test for HTTP 400 model no vision in backend/tests/contract/test_setup_puzzle_from_image.py
- [x] T064 [P] [US5] Contract test for HTTP 422 missing fields in backend/tests/contract/test_setup_puzzle_from_image.py
- [x] T065 [P] [US5] Contract test for HTTP 500 provider failure in backend/tests/contract/test_setup_puzzle_from_image.py
- [x] T066 [P] [US5] Component test for oversized image validation in frontend/src/components/ImagePuzzleSetup.error.test.tsx
- [x] T067 [P] [US5] Component test for error display and state preservation in frontend/src/components/ImagePuzzleSetup.error.test.tsx

### Implementation for User Story 5

- [x] T068 [P] [US5] Add image size validation (5MB max) in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T069 [P] [US5] Add MIME type validation (png, jpeg, jpg, gif) in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T070 [P] [US5] Display size validation error "Image too large (max 5MB)" in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T071 [P] [US5] Display format validation error for unsupported MIME types in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T072 [US5] Add HTTP 413 error handling in backend/src/api/v2_image_setup.py
- [x] T073 [US5] Add HTTP 400 error handling for extraction failures in backend/src/api/v2_image_setup.py
- [x] T074 [US5] Add HTTP 422 error handling for missing fields in backend/src/api/v2_image_setup.py
- [x] T075 [US5] Add HTTP 500 error handling for provider failures in backend/src/api/v2_image_setup.py
- [x] T076 [US5] Add unified error message "LLM unable to extract puzzle words" for all extraction failures in backend/src/services/image_word_extractor.py
- [x] T077 [US5] Display backend error messages in frontend with appropriate formatting in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T078 [US5] Preserve image data and selections on error for retry in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T079 [US5] Add loading state indicator during extraction in frontend/src/components/ImagePuzzleSetup.tsx
- [x] T080 [US5] Add "Setup Puzzle" button disabled state when no image pasted in frontend/src/components/ImagePuzzleSetup.tsx

**Checkpoint**: ✅ COMPLETED - All error scenarios handled gracefully with clear user feedback

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, testing, and final refinements across all user stories

- [ ] T081 [P] Update README.md with image setup instructions and examples
- [ ] T082 [P] Add screenshots of image setup interface to docs/
- [ ] T083 [P] Document LLM vision model requirements in quickstart.md
- [ ] T084 [P] Update API documentation with /api/v2/setup_puzzle_from_image endpoint
- [x] T085 Run full backend test suite and verify >80% coverage
- [x] T086 Run full frontend test suite and verify >80% coverage
- [ ] T087 Test cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] T088 [P] Test with OpenAI GPT-4 Vision model
- [ ] T089 [P] Test with Ollama llava model (if available)
- [x] T090 Verify performance targets (paste <2s, extraction <10s, errors <3s)
- [x] T091 Verify no regressions in file-based puzzle setup
- [x] T092 Verify puzzle gameplay identical between image and file setup
- [x] T093 Run quickstart.md validation steps
- [x] T094 Code review and refactoring pass
- [x] T095 Final commit and branch ready for PR

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Setup completion - **BLOCKS all user stories**
- **Phase 3 (US4 - P1)**: Depends on Foundational - **Core MVP**
- **Phase 4 (US1 - P1)**: Depends on US4 - Adds navigation to working feature
- **Phase 5 (US2 - P2)**: Depends on US4 - Enhances image paste UX
- **Phase 6 (US3 - P2)**: Depends on US4 - Enhances provider selection UX
- **Phase 7 (US5 - P3)**: Depends on US4 - Adds comprehensive error handling
- **Phase 8 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Foundational (Phase 2) - MUST complete first
         ↓
    US4 (Phase 3) - Core MVP - Extract words and play puzzle
         ↓
         ├─→ US1 (Phase 4) - Navigation (makes US4 accessible)
         ├─→ US2 (Phase 5) - Paste UX polish (enhances US4)
         ├─→ US3 (Phase 6) - Provider selection polish (enhances US4)
         └─→ US5 (Phase 7) - Error handling (makes US4 robust)
```

**Key Insight**: US4 is the critical path. All other stories enhance it. Ship US4 alone for MVP.

### Within Each User Story

- Tests (if included) MUST be written FIRST and FAIL before implementation
- Backend models → backend service → backend endpoint → backend router registration
- Frontend types → frontend component skeleton → frontend handlers → frontend integration
- Each story should be independently testable at its checkpoint

### Parallel Opportunities

#### Phase 1: Setup
- T003, T004 (verification tasks - different systems)

#### Phase 2: Foundational
- T008, T009 (Pydantic models - different models)
- T011, T012, T013 (TypeScript types - different types)

#### Phase 3: User Story 4 (within sub-phases)
- Tests: T015, T016, T017, T018 (all tests can run in parallel)
- Frontend: T027, T028 (component and CSS files)

#### Phase 4: User Story 1
- Tests: T038, T039 (different test files)

#### Phase 5: User Story 2
- Tests: T044, T045, T046 (different test cases)
- Implementation: T047, T048 (component and CSS changes)

#### Phase 6: User Story 3
- Tests: T052, T053, T054 (different test cases)
- Implementation: T055, T056 (provider and default setup)

#### Phase 7: User Story 5
- Tests: T061-T067 (all tests can run in parallel)
- Frontend validation: T068, T069, T070, T071 (independent validations)

#### Phase 8: Polish
- Documentation: T081, T082, T083, T084 (different docs)
- Provider testing: T088, T089 (different providers)

---

## Parallel Example: User Story 4 (MVP)

### Backend Parallel Group 1 (after T007-T014 complete):
```bash
Task T015: Write contract test for success case
Task T016: Write contract test for validation errors  
Task T017: Write unit test for word extraction
```

### Backend Sequential:
```bash
Task T019: Implement extract_words method
Task T020: Add vision prompt construction
Task T021: Implement with_structured_output invocation
Task T022: Create v2_image_setup.py file
Task T023: Implement endpoint
Task T024: Add error handling
Task T025: Integrate session manager
Task T026: Register router
```

### Frontend Parallel Group 1:
```bash
Task T027: Create ImagePuzzleSetup.tsx skeleton
Task T028: Create ImagePuzzleSetup.css
```

### Frontend Sequential (after T027-T028):
```bash
Task T029: Implement handlePaste
Task T030: Implement base64 encoding
Task T031: Add image preview
Task T032: Add dropdowns
Task T033: Add Setup Puzzle button
Task T034: Add API method
Task T035: Add navigation handler
Task T036: Add component rendering
Task T037: Add callback
```

---

## Implementation Strategy

### MVP First (User Story 4 Only) - RECOMMENDED

1. ✅ Complete Phase 1: Setup
2. ✅ Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. ✅ Complete Phase 3: User Story 4
4. **STOP and VALIDATE**: Test US4 independently - can users paste image and play puzzle?
5. Deploy/demo if ready

**Result**: Working feature with minimal UI polish. Users can paste images and play puzzles.

### Full Feature Delivery (All User Stories)

1. Complete Setup + Foundational
2. Implement US4 (MVP) → Test independently ✅
3. Add US1 (Navigation) → Test independently ✅
4. Add US2 (Paste UX) → Test independently ✅
5. Add US3 (Provider UX) → Test independently ✅
6. Add US5 (Error Handling) → Test independently ✅
7. Polish phase → Final validation ✅

**Result**: Polished feature with excellent UX and comprehensive error handling.

### Incremental Delivery

After US4 is working, each subsequent story can be delivered independently:
- US4 alone: Basic working feature
- US4 + US1: Feature with good navigation
- US4 + US1 + US2: Feature with polished image handling
- US4 + US1 + US2 + US3: Feature with polished everything except error handling
- US4 + US1 + US2 + US3 + US5: Complete feature

### Parallel Team Strategy

With multiple developers (after Foundational phase complete):

**Option A: Sequential Critical Path**
- Developer A: Complete US4 (MVP) first
- Developer B: Wait for US4, then implement US1
- Developer C: After US1, implement US2/US3
- Developer D: After US2/US3, implement US5

**Option B: Parallel Enhancement (after US4 complete)**
- Developer A: US1 (navigation)
- Developer B: US2 (paste UX)
- Developer C: US3 (provider UX)
- Developer D: US5 (error handling)
- Each can proceed independently after US4 is done

---

## Task Summary

- **Total Tasks**: 95 tasks
- **Setup Phase**: 6 tasks
- **Foundational Phase**: 8 tasks (BLOCKING)
- **User Story 4 (P1 - MVP)**: 23 tasks (core feature)
- **User Story 1 (P1)**: 4 tasks (navigation)
- **User Story 2 (P2)**: 5 tasks (paste UX)
- **User Story 3 (P2)**: 6 tasks (provider UX)
- **User Story 5 (P3)**: 13 tasks (error handling)
- **Polish Phase**: 15 tasks (documentation, testing)

**Parallelizable Tasks**: 29 tasks marked with [P]

**Critical Path**: Setup (6) → Foundational (8) → US4 Backend (12) → US4 Frontend (11) = 37 tasks for MVP

**Estimated Effort**:
- MVP (US4 only): 2-3 days
- MVP + Navigation (US4 + US1): 3-4 days
- Full Feature (all stories): 5-7 days
- With comprehensive testing: 7-10 days

---

## Validation Checklist

### Format Validation ✅
- [x] All tasks follow checkbox format: `- [ ] [ID] [P?] [Story?] Description`
- [x] Task IDs sequential (T001-T095)
- [x] Story labels present for all user story tasks (US1-US5)
- [x] File paths included in all implementation tasks
- [x] Parallel tasks marked with [P]

### Completeness Validation ✅
- [x] All 5 user stories have dedicated phases
- [x] All 25 functional requirements covered
- [x] Backend models from data-model.md included
- [x] Frontend types from contracts/ included
- [x] API endpoint implementation included
- [x] Navigation integration included
- [x] Error handling for all scenarios included

### Dependency Validation ✅
- [x] Setup phase has no dependencies
- [x] Foundational phase blocks all user stories
- [x] User stories depend on Foundational phase
- [x] Enhancement stories (US1, US2, US3, US5) depend on core story (US4)
- [x] Dependencies documented in Dependencies section

### Independent Testing Validation ✅
- [x] Each user story has "Independent Test" description
- [x] Each user story checkpoint confirms independent functionality
- [x] Test tasks (if included) precede implementation tasks
- [x] Integration tests cover end-to-end flows per story

---

## Notes

- **Tests are REQUIRED**: All test tasks MUST be implemented following TDD workflow per constitution Principle III (80% coverage minimum)
- **Story Independence**: Each user story after US4 enhances the feature without breaking previous stories
- **MVP Strategy**: Ship US4 alone for fastest time-to-value
- **Parallel Execution**: 29 tasks can run in parallel with proper team coordination
- **File Path Accuracy**: All paths verified against plan.md project structure
- **Format Compliance**: All tasks follow strict checklist format for LLM executability
- **Checkpoint Validation**: Stop at each checkpoint to independently validate story completion

---

**Generated**: December 13, 2025
**Feature Branch**: `004-image-puzzle-setup`
**Status**: Ready for implementation
**Next Step**: Review tasks, confirm MVP scope, begin Phase 1 (Setup)
