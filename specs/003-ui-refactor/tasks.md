---
description: "Implementation tasks for UI Refactor - Persistent Navigation Layout"
---

# Tasks: UI Refactor - Persistent Navigation Layout

**Input**: Design documents from `/specs/003-ui-refactor/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/components.ts, quickstart.md  
**Branch**: `003-ui-refactor`

**Tests**: Following TDD per constitution - all test tasks are REQUIRED before implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification

- [ ] T001 Verify current frontend tests pass with `cd frontend && npm test`
- [ ] T002 Start development server with `cd frontend && npm start` to baseline current behavior
- [ ] T003 [P] Create TypeScript types file in frontend/src/types/navigation.ts from contracts/components.ts
- [ ] T004 [P] Take screenshots of current UI states (waiting, active, won, lost) for regression testing

**Checkpoint**: Baseline established - all existing tests pass, current behavior documented

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core components that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### NavigationItem Component (Foundation)

- [ ] T005 [P] Create test file frontend/src/components/NavigationItem.test.tsx
- [ ] T006 Write failing tests for NavigationItem: renders label, shows chevron when expandable, handles click events, aria-expanded attribute
- [ ] T007 Run tests with `npm test -- NavigationItem.test.tsx` to verify they FAIL
- [ ] T008 Create component file frontend/src/components/NavigationItem.tsx implementing NavigationItemProps interface
- [ ] T009 [P] Create styles file frontend/src/components/NavigationItem.css with indentation, hover states, chevron rotation
- [ ] T010 Implement NavigationItem component to pass all tests
- [ ] T011 Run tests with `npm test -- NavigationItem.test.tsx` to verify they PASS

### Sidebar Component (Foundation)

- [ ] T012 [P] Create test file frontend/src/components/Sidebar.test.tsx
- [ ] T013 Write failing tests for Sidebar: renders navigation hierarchy, "Start New Game" expanded by default, handles "From File" click, sidebar width constraints (min 180px, max 20%)
- [ ] T014 Run tests with `npm test -- Sidebar.test.tsx` to verify they FAIL
- [ ] T015 Create component file frontend/src/components/Sidebar.tsx implementing SidebarProps interface
- [ ] T016 [P] Create styles file frontend/src/components/Sidebar.css with width constraints, CSS Grid area placement
- [ ] T017 Implement Sidebar component using NavigationItem, pass all tests
- [ ] T018 Run tests with `npm test -- Sidebar.test.tsx` to verify they PASS

**Checkpoint**: Foundation ready - NavigationItem and Sidebar components complete and tested

---

## Phase 3: User Story 1 - Initial Application Launch (Priority: P1) 🎯 MVP

**Goal**: Users see a clear, organized interface with persistent navigation showing the title, sidebar with "Start New Game" expanded, and "Select action in Left Side Bar" message in the main area.

**Independent Test**: Open application at `http://localhost:3000` and verify title is visible at top, sidebar shows "Start New Game" expanded with "From File" visible, main area shows "Select action in Left Side Bar".

### Tests for User Story 1 (TDD - REQUIRED)

- [ ] T019 [P] [US1] Update frontend/src/App.test.tsx with test: renders title "NYT Connections Puzzle Assistant" at top
- [ ] T020 [P] [US1] Add test to App.test.tsx: renders Sidebar component in initial state
- [ ] T021 [P] [US1] Add test to App.test.tsx: renders "Select action in Left Side Bar" message when currentView='initial'
- [ ] T022 [P] [US1] Add test to App.test.tsx: layout uses CSS Grid with three regions (header, sidebar, main)
- [ ] T023 [US1] Run tests with `npm test -- App.test.tsx` to verify they FAIL

### Implementation for User Story 1

- [ ] T024 [US1] Update frontend/src/App.tsx: add currentView state (initial as default) and sidebarExpanded state (true as default)
- [ ] T025 [US1] Update frontend/src/App.tsx: import Sidebar component and add to render tree
- [ ] T026 [US1] Update frontend/src/App.tsx: implement onNavigationAction handler for sidebar actions
- [ ] T027 [US1] Update frontend/src/App.tsx: add conditional rendering for main area based on currentView
- [ ] T028 [US1] Update frontend/src/App.tsx: render "Select action in Left Side Bar" when currentView='initial'
- [ ] T029 [US1] Update frontend/src/App.css: replace flexbox layout with CSS Grid using named template areas (header, sidebar, main)
- [ ] T030 [US1] Update frontend/src/App.css: add grid-template-rows and grid-template-columns for layout
- [ ] T031 [US1] Update frontend/src/App.css: style .App-header for title positioning
- [ ] T032 [US1] Run tests with `npm test -- App.test.tsx` to verify they PASS
- [ ] T033 [US1] Visual verification: npm start and check initial layout matches spec

**Checkpoint**: User Story 1 complete - initial application launch shows correct layout with title, sidebar, and welcome message

---

## Phase 4: User Story 2 - Start New Game from File (Priority: P2)

**Goal**: Users can click "From File" in the sidebar to upload a CSV puzzle file, with the puzzle interface appearing in the main area while title and sidebar remain visible.

**Independent Test**: Start from initial state, click "From File", upload a valid CSV file (e.g., data/puzzle_2025_10_09.csv), verify puzzle interface appears in main area with all existing functionality working.

### Tests for User Story 2 (TDD - REQUIRED)

- [ ] T034 [P] [US2] Add test to App.test.tsx: clicking "From File" changes currentView to 'file-upload'
- [ ] T035 [P] [US2] Add test to App.test.tsx: currentView='file-upload' renders FileUpload component in main area
- [ ] T036 [P] [US2] Add test to App.test.tsx: successful file upload changes currentView to 'puzzle-active'
- [ ] T037 [P] [US2] Add test to App.test.tsx: currentView='puzzle-active' renders EnhancedPuzzleInterface in main area
- [ ] T038 [P] [US2] Add test to App.test.tsx: title and sidebar remain visible when currentView='file-upload'
- [ ] T039 [P] [US2] Add test to App.test.tsx: title and sidebar remain visible when currentView='puzzle-active'
- [ ] T040 [US2] Run tests with `npm test -- App.test.tsx` to verify they FAIL

### Implementation for User Story 2

- [ ] T041 [US2] Update frontend/src/App.tsx: implement 'from-file' action in onNavigationAction to set currentView='file-upload'
- [ ] T042 [US2] Update frontend/src/App.tsx: render FileUpload component when currentView='file-upload'
- [ ] T043 [US2] Update frontend/src/App.tsx: update handleFileUpload callback to set currentView='puzzle-active' after successful upload
- [ ] T044 [US2] Update frontend/src/App.tsx: render EnhancedPuzzleInterface when currentView='puzzle-active'
- [ ] T045 [P] [US2] Update frontend/src/components/FileUpload.tsx: remove internal header/title (now in App header)
- [ ] T046 [P] [US2] Update frontend/src/components/FileUpload.css: adjust styles for main area context (remove header padding)
- [ ] T047 [US2] Run tests with `npm test -- App.test.tsx` and `npm test -- FileUpload.test.tsx` to verify they PASS
- [ ] T048 [US2] Visual verification: click "From File", upload puzzle, verify layout integrity

**Checkpoint**: User Story 2 complete - file upload workflow functional with persistent navigation

---

## Phase 5: User Story 3 - Persistent Navigation During Gameplay (Priority: P2)

**Goal**: During active gameplay, sidebar remains accessible and users can restart by clicking "From File" without confirmation, matching existing behavior.

**Independent Test**: Start a puzzle, verify sidebar is visible and clickable during all game interactions (word selection, getting recommendations, submitting responses). Click "From File" during gameplay and verify file upload interface appears immediately.

### Tests for User Story 3 (TDD - REQUIRED)

- [ ] T049 [P] [US3] Add test to App.test.tsx: sidebar onNavigationAction handler works when currentView='puzzle-active'
- [ ] T050 [P] [US3] Add test to App.test.tsx: clicking "From File" during active game changes currentView to 'file-upload' (no confirmation)
- [ ] T051 [P] [US3] Add test to App.test.tsx: sidebar does not overlap main content when puzzle interface is active
- [ ] T052 [P] [US3] Add test to App.test.tsx: sidebar maintains min 180px width and max 20% viewport width
- [ ] T053 [US3] Run tests with `npm test -- App.test.tsx` to verify they FAIL

### Implementation for User Story 3

- [ ] T054 [US3] Verify frontend/src/App.tsx: onNavigationAction handler works from any currentView state (already implemented in T041)
- [ ] T055 [US3] Verify frontend/src/App.css: sidebar width constraints use min(180px) and max(20vw) in grid-template-columns
- [ ] T056 [US3] Update frontend/src/App.css: ensure main area uses fr unit to fill remaining space
- [ ] T057 [US3] Run tests with `npm test -- App.test.tsx` to verify they PASS
- [ ] T058 [US3] Visual verification: start puzzle, interact with words/recommendations, verify sidebar remains accessible
- [ ] T059 [US3] Regression test: click "From File" during active puzzle, verify immediate transition (no confirmation dialog)

**Checkpoint**: User Story 3 complete - persistent navigation works during gameplay with no behavioral regressions

---

## Phase 6: User Story 4 - End Game Display (Priority: P3)

**Goal**: When game concludes (won or lost), success/failure message and GameSummary display in main area at the same relative positions as current implementation, with title and sidebar visible.

**Independent Test**: Complete a puzzle (win or lose), verify success/failure message appears, GameSummary shows correct stats, and relative positioning matches current implementation.

### Tests for User Story 4 (TDD - REQUIRED)

- [ ] T060 [P] [US4] Add test to App.test.tsx: gameStatus='won' shows success message "🎉 Congratulations! You solved the puzzle!" in main area
- [ ] T061 [P] [US4] Add test to App.test.tsx: gameStatus='lost' shows failure message "Game Over - Maximum mistakes reached" in main area
- [ ] T062 [P] [US4] Add test to App.test.tsx: gameStatus='won' or 'lost' renders GameSummary component in main area
- [ ] T063 [P] [US4] Add test to App.test.tsx: title and sidebar remain visible when gameStatus='won' or 'lost'
- [ ] T064 [P] [US4] Add test to App.test.tsx: clicking "From File" after game end changes currentView to 'file-upload'
- [ ] T065 [US4] Run tests with `npm test -- App.test.tsx` to verify they FAIL

### Implementation for User Story 4

- [ ] T066 [US4] Update frontend/src/App.tsx: add currentView='puzzle-complete' state transition when gameStatus becomes 'won' or 'lost'
- [ ] T067 [US4] Update frontend/src/App.tsx: render EnhancedPuzzleInterface when currentView='puzzle-complete' (preserves GameSummary rendering)
- [ ] T068 [US4] Verify frontend/src/components/EnhancedPuzzleInterface.tsx: GameSummary component renders unchanged (no modifications needed)
- [ ] T069 [US4] Verify frontend/src/components/GameSummary.tsx: component unchanged, renders in same relative position (no modifications needed)
- [ ] T070 [US4] Run tests with `npm test -- App.test.tsx` to verify they PASS
- [ ] T071 [US4] Visual regression: complete puzzle to win, verify message and GameSummary positions match baseline screenshots from T004
- [ ] T072 [US4] Visual regression: complete puzzle to lose, verify message and GameSummary positions match baseline screenshots from T004

**Checkpoint**: User Story 4 complete - end game display maintains visual consistency with current implementation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and verification across all user stories

### Accessibility & UX

- [ ] T073 [P] Add aria-label to Sidebar component in frontend/src/components/Sidebar.tsx
- [ ] T074 [P] Verify NavigationItem keyboard navigation (Enter/Space to activate) in frontend/src/components/NavigationItem.tsx
- [ ] T075 [P] Test reduced-motion preference with CSS transitions in frontend/src/components/NavigationItem.css
- [ ] T076 [P] Verify focus indicators visible on all interactive elements in Sidebar and NavigationItem

### Layout Edge Cases

- [ ] T077 Test responsive behavior at viewport widths 320px, 768px, 1024px, 1920px
- [ ] T078 Test sidebar min-width constraint (180px) prevents collapse on small screens
- [ ] T079 Test sidebar max-width constraint (20% viewport) prevents excessive width on large screens
- [ ] T080 Verify no horizontal scrollbars appear in main area during puzzle gameplay

### Performance & Quality

- [ ] T081 Run full test suite with `npm test` and verify >80% coverage maintained
- [ ] T082 Run type check with `npx tsc --noEmit` to verify no TypeScript errors
- [ ] T083 [P] Measure layout transition times (should be <300ms per plan.md)
- [ ] T084 [P] Verify initial render time <2s (per plan.md performance goal)

### Documentation

- [ ] T085 [P] Update frontend/README.md with new component structure (Sidebar, NavigationItem)
- [ ] T086 [P] Add JSDoc comments to Sidebar and NavigationItem components
- [ ] T087 [P] Create architecture diagram showing new 3-region layout in docs/

### Final Validation

- [ ] T088 Run complete quickstart.md workflow from fresh clone to verify setup instructions
- [ ] T089 Verify zero backend changes with `git diff backend/` (should be empty)
- [ ] T090 Test all acceptance scenarios from spec.md user stories (US1-US4)
- [ ] T091 Code cleanup: remove unused imports, ensure consistent formatting with Prettier
- [ ] T092 Final PR review: verify all FR-001 through FR-013 requirements met from spec.md

**Checkpoint**: All polish complete - feature ready for production deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational (Phase 2) completion
  - User Story 1 (Phase 3): Can start after Phase 2 - No dependencies on other stories
  - User Story 2 (Phase 4): Can start after Phase 2 - Integrates with US1 but independently testable
  - User Story 3 (Phase 5): Can start after Phase 2 - Verifies US1 and US2 behavior continues to work
  - User Story 4 (Phase 6): Can start after Phase 2 - Extends US2 with end-game scenarios
- **Polish (Phase 7)**: Depends on all user stories (Phases 3-6) completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - ZERO dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 layout but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Verifies US1/US2 integration but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Extends US2 with end-game states but independently testable

### Critical Path (Sequential - Recommended for Solo Developer)

1. Phase 1: Setup (T001-T004) → ~30 minutes
2. Phase 2: Foundational (T005-T018) → ~4 hours
3. Phase 3: User Story 1 (T019-T033) → ~3 hours
4. Phase 4: User Story 2 (T034-T048) → ~3 hours
5. Phase 5: User Story 3 (T049-T059) → ~2 hours
6. Phase 6: User Story 4 (T060-T072) → ~2 hours
7. Phase 7: Polish (T073-T092) → ~3 hours

**Total Estimated Effort**: ~17-20 hours (2-3 days with breaks)

### Parallel Opportunities (Team of 2-3 Developers)

**After Phase 2 completes**, user stories can be worked in parallel:

```bash
# Developer A: User Story 1 (MVP)
npm test -- App.test.tsx  # T019-T023
# Implement T024-T033

# Developer B: User Story 2 (File Upload Flow)
npm test -- App.test.tsx  # T034-T040 (in separate test file or different describe blocks)
# Implement T041-T048

# Developer C: Documentation and Accessibility (non-blocking)
# T085-T087 in parallel
```

**Within Each User Story** (TDD workflow):

- Tests tasks (marked [P]) can be written in parallel by same developer
- Implementation tasks are sequential due to dependencies
- Visual verification tasks can be done in parallel with next story's test writing

**Within Foundational Phase**:

- NavigationItem (T005-T011) and Sidebar (T012-T018) are sequential (Sidebar depends on NavigationItem)
- Test writing (T006, T013) and component creation (T008-T009, T015-T016) can overlap with careful coordination

---

## Parallel Example: User Story 1

```bash
# Write all tests in parallel (same file, different test cases)
# T019: test('renders title')
# T020: test('renders Sidebar')  
# T021: test('renders welcome message')
# T022: test('uses CSS Grid layout')

npm test -- App.test.tsx  # All fail

# Implement sequentially (dependencies)
# T024: Add state
# T025: Import Sidebar
# T026: Add handler
# T027-T028: Conditional rendering
# T029-T031: CSS Grid

npm test -- App.test.tsx  # All pass
```

---

## Parallel Example: Foundational Phase

```bash
# NavigationItem component (sequential - foundation)
npm test -- NavigationItem.test.tsx  # T006-T007 FAIL
# Implement T008-T010
npm test -- NavigationItem.test.tsx  # T011 PASS

# Sidebar component (sequential - depends on NavigationItem)
npm test -- Sidebar.test.tsx  # T013-T014 FAIL
# Implement T015-T017
npm test -- Sidebar.test.tsx  # T018 PASS
```

---

## MVP Scope Recommendation

**Minimum Viable Product**: User Story 1 (Phase 3) only

**Rationale**: User Story 1 delivers the core value of the refactor:
- ✅ Persistent navigation layout established
- ✅ Title visible at all times
- ✅ Sidebar with "Start New Game" navigation
- ✅ Clear initial state guidance ("Select action in Left Side Bar")

**MVP Deliverables**:
- New components: Sidebar, NavigationItem
- Modified: App.tsx, App.css
- Tests: NavigationItem.test.tsx, Sidebar.test.tsx, updated App.test.tsx
- ~150-200 LOC implementation + ~100-150 LOC tests

**Post-MVP Increments**:
- **Increment 2**: User Story 2 (file upload workflow)
- **Increment 3**: User Story 3 (navigation during gameplay)
- **Increment 4**: User Story 4 (end-game display)
- **Increment 5**: Phase 7 (polish and accessibility)

---

## Task Summary

**Total Tasks**: 92

**Breakdown by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 14 tasks (7 for NavigationItem, 7 for Sidebar)
- Phase 3 (User Story 1): 15 tasks (5 tests, 10 implementation)
- Phase 4 (User Story 2): 15 tasks (7 tests, 8 implementation)
- Phase 5 (User Story 3): 11 tasks (5 tests, 6 implementation)
- Phase 6 (User Story 4): 13 tasks (6 tests, 7 implementation)
- Phase 7 (Polish): 20 tasks (accessibility, layout, performance, docs, validation)

**Breakdown by User Story**:
- User Story 1 (P1): 15 tasks
- User Story 2 (P2): 15 tasks
- User Story 3 (P2): 11 tasks
- User Story 4 (P3): 13 tasks

**Parallel Tasks**: 35 tasks marked [P] (38% of total)

**Independent Test Criteria**:
- ✅ User Story 1: Open app, verify layout with title/sidebar/welcome message
- ✅ User Story 2: Click "From File", upload CSV, verify puzzle appears with navigation
- ✅ User Story 3: Start puzzle, verify sidebar accessible, test restart flow
- ✅ User Story 4: Complete puzzle, verify end-game display positions match baseline

**Format Validation**: ✅ All tasks follow checklist format:
- Checkbox: `- [ ]`
- Task ID: T001-T092 (sequential)
- [P] marker: 35 parallelizable tasks identified
- [Story] label: US1-US4 for user story phases
- File paths: Included in all implementation tasks
- Descriptions: Clear, actionable, single-responsibility

---

## Next Steps

1. **Review this task list** with team and validate task breakdown
2. **Begin Phase 1** (Setup) to establish baseline
3. **Complete Phase 2** (Foundational) before any user story work
4. **Implement User Story 1** as MVP to validate approach
5. **Iterate** through remaining user stories in priority order (P2, P3)
6. **Polish** and deploy when all user stories complete

**Success Criteria Verification** (from spec.md):
- [ ] SC-001: Title visible at top (verified in T033)
- [ ] SC-002: Sidebar accessible within 0 clicks (verified in T048)
- [ ] SC-003: File upload to puzzle <2s (verified in T084)
- [ ] SC-004: 100% behavioral consistency (verified in T048, T059, T072)
- [ ] SC-005: End-game positions match baseline (verified in T071, T072)
- [ ] SC-006: Smooth layout transitions <300ms (verified in T083)
- [ ] SC-007: Zero backend changes (verified in T089)
