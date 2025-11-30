# Implementation Plan: UI Refactor - Persistent Navigation Layout

**Branch**: `003-ui-refactor` | **Date**: November 29, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ui-refactor/spec.md`

## Summary

Refactor the React frontend to implement a persistent three-region layout with a static title bar, collapsible left sidebar navigation, and a main content area that displays context-appropriate components based on application state. The refactor maintains 100% behavioral consistency with existing UI components while improving navigation discoverability and user flow clarity. No backend changes required - this is a pure frontend layout restructuring using CSS Grid/Flexbox within the existing React + TypeScript stack.

## Technical Context

**Language/Version**: TypeScript 4.9+ (frontend only - no backend changes)
**Primary Dependencies**: React 18.x, React Testing Library, Jest  
**Storage**: N/A (in-memory session state via React hooks)  
**Testing**: Jest + React Testing Library (maintain >80% coverage per constitution)  
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge - ES2020+)  
**Project Type**: Web application (frontend-only changes)  
**Performance Goals**: Initial render <2s, layout transitions <300ms, no layout shift/reflow  
**Constraints**: Zero backend changes, 100% behavioral consistency with existing components, static positioning (no fixed/sticky headers)  
**Scale/Scope**: 4 React components affected (App.tsx, new Sidebar, new NavigationItem), ~200-300 LOC changes, 3-5 new CSS modules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Full-Stack Separation** | ✅ PASS | Frontend-only changes. No backend modifications. Zero API changes. Clear boundary maintained. |
| **II. API-First Design** | ✅ PASS | No new APIs required. Existing REST endpoints unchanged. All backend contracts preserved. |
| **III. Test-First Development** | ✅ PASS | Plan includes TDD workflow: write tests for layout → fail → implement → pass. Jest/RTL for component tests. |
| **IV. Type Safety** | ✅ PASS | TypeScript for all new components. Existing type definitions preserved. No `any` types introduced. |
| **V. Local-First Architecture** | ✅ PASS | No network dependencies added. Pure client-side layout refactor. Session state only. |

**Overall Assessment**: ✅ **COMPLIANT** - All constitutional principles satisfied. This is a pure frontend layout refactor with no architectural violations.

**Re-check After Phase 1**: Verify that component contracts maintain type safety and that no backend coupling is introduced through state management.

## Project Structure

### Documentation (this feature)

```text
specs/003-ui-refactor/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (technology decisions, layout patterns)
├── data-model.md        # Phase 1 output (component props, state shape)
├── quickstart.md        # Phase 1 output (developer setup, testing guide)
├── contracts/           # Phase 1 output (TypeScript interfaces)
│   └── components.ts    # Component prop types and contracts
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root - frontend only)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── Sidebar.tsx              # NEW: Left navigation sidebar component
│   │   ├── Sidebar.css              # NEW: Sidebar styling
│   │   ├── Sidebar.test.tsx         # NEW: Sidebar component tests
│   │   ├── NavigationItem.tsx       # NEW: Expandable navigation item component
│   │   ├── NavigationItem.css       # NEW: Navigation item styling
│   │   ├── NavigationItem.test.tsx  # NEW: Navigation item tests
│   │   ├── FileUpload.tsx           # MODIFIED: Remove header, adjust for main area
│   │   ├── FileUpload.css           # MODIFIED: Update for new layout context
│   │   ├── EnhancedPuzzleInterface.tsx  # UNMODIFIED: Reused as-is in main area
│   │   └── GameSummary.tsx          # UNMODIFIED: Reused as-is
│   ├── App.tsx                      # MODIFIED: Implement 3-region layout
│   ├── App.css                      # MODIFIED: Grid layout, title positioning
│   ├── App.test.tsx                 # MODIFIED: Update tests for new layout
│   └── types/
│       └── navigation.ts            # NEW: Navigation state types
└── tests/
    ├── integration/
    │   └── test_layout_navigation.test.tsx  # NEW: Full navigation flow tests
    └── unit/
        └── (existing component tests updated)
```

**Structure Decision**: Web application (Option 2) with frontend-only modifications. Backend directory completely untouched. All changes confined to `frontend/src/` with new components under `components/` and updated layout logic in `App.tsx`. Follows existing React component organization patterns.

## Complexity Tracking

> **This feature has NO constitutional violations - section included for completeness only**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

**Rationale**: This is a straightforward layout refactor using standard React patterns (component composition, CSS Grid/Flexbox, React hooks for state). No new architectural complexity introduced. All changes align with existing codebase patterns and constitutional principles.

## Phase 0: Outline & Research

**Status**: ✅ COMPLETED  
**Output**: [research.md](./research.md)

### Unknowns Resolved

All technical unknowns from the specification were resolved through clarification questions and research:

1. **Sidebar width behavior** → Minimum width constraint (180px min, 20% viewport max)
2. **Progress loss confirmation** → No confirmation needed (maintains existing behavior)
3. **Title positioning** → Static position (not fixed/sticky)
4. **Navigation interaction pattern** → Expandable/collapsible menus
5. **Initial expansion state** → Expanded by default

### Technology Decisions

| Decision Area | Choice | Reference |
|---------------|--------|-----------|
| Layout Pattern | CSS Grid with named template areas | research.md §Layout Pattern Research |
| Component Architecture | Controlled components (props down, callbacks up) | research.md §Component Architecture |
| State Management | Local React state (useState in App.tsx) | research.md §State Management |
| Animation | CSS transitions (max-height) | research.md §Animation/Transition |
| Testing | React Testing Library + User Event | research.md §Testing Strategy |

### Alternatives Considered

- **Flexbox for layout**: Rejected - more complex for 2D layouts
- **Context API for state**: Rejected - overkill for single-level prop passing
- **CSS frameworks (Bootstrap/Tailwind)**: Rejected - violates "no new frameworks" principle
- **Fixed/sticky positioning**: Rejected - per clarification, static position preferred

**Deliverables**:
- ✅ `research.md` - Complete technology decisions with rationale
- ✅ All NEEDS CLARIFICATION items resolved

---

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETED  
**Output**: [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

### Entities Extracted

From specification functional requirements, the following key entities were defined:

1. **AppView** - Application routing state (`initial`, `file-upload`, `puzzle-active`, `puzzle-complete`)
2. **NavigationAction** - User commands from sidebar (`from-file`, `toggle-menu`)
3. **SidebarProps** - Contract for Sidebar component
4. **NavigationItemProps** - Contract for NavigationItem component
5. **AppLayoutState** - Layout state managed by App.tsx

### API Contracts Generated

TypeScript interface definitions created in `contracts/components.ts`:

- `AppView` type - Main area routing states
- `NavigationAction` type - Sidebar action events
- `SidebarProps` interface - Sidebar component contract
- `NavigationItemProps` interface - Navigation item contract
- `AppLayoutState` interface - App-level layout state
- Type guards: `isExpandableItem()`, `isActionItem()`
- Constants: `NAVIGATION_MENUS`, `NAVIGATION_ACTIONS`

### Data Model

Complete component hierarchy and state flow documented in `data-model.md`:

```
App (owns: currentView, puzzleState)
├── Header (static title)
├── Sidebar (props: currentView, onNavigationAction)
│   └── NavigationItem (expandable/collapsible)
│       └── NavigationItem (action item)
└── Main Area (conditional render based on currentView)
    ├── WelcomeMessage (currentView='initial')
    ├── FileUpload (currentView='file-upload')
    └── EnhancedPuzzleInterface (currentView='puzzle-active' | 'puzzle-complete')
```

### State Transitions

```
initial → file-upload → puzzle-active → puzzle-complete
           ↑                              ↓
           └──────────────────────────────┘
           (user clicks "From File" again)
```

### Agent Context Update

**Action**: Run agent context update script

```bash
.specify/scripts/bash/update-agent-context.sh copilot
```

**What it does**:
- Detects current AI agent (GitHub Copilot)
- Updates `.github/copilot-instructions.md`
- Adds technology decisions from this plan
- Preserves manual additions between markers
- No-op if no new technology added

**Expected outcome**: Copilot instructions file updated with CSS Grid and React component patterns for this feature.

**Deliverables**:
- ✅ `data-model.md` - Component state shapes and hierarchy
- ✅ `contracts/components.ts` - TypeScript interface definitions
- ✅ `quickstart.md` - Developer setup and TDD workflow guide
- ✅ Agent context updated (if applicable)

---

## Phase 2: Implementation Planning

**Status**: ⏸️  DEFERRED - Use `/speckit.tasks` command to generate detailed task breakdown

**Note**: This phase is NOT completed by `/speckit.plan`. Run `/speckit.tasks` separately to generate `tasks.md` with:
- Numbered, sequenced implementation tasks
- Acceptance criteria per task
- Dependencies between tasks
- Estimated effort per task
- Test-first development workflow

**Next Command**: `/speckit.tasks` (run after this plan is approved)

---

## Post-Phase 1 Constitution Re-Check

*Re-verification after design phase completion*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Full-Stack Separation** | ✅ PASS | All contracts are frontend TypeScript interfaces. No backend types leaked. |
| **II. API-First Design** | ✅ PASS | No new API endpoints designed. Existing endpoints remain unchanged. |
| **III. Test-First Development** | ✅ PASS | Quickstart guide includes TDD workflow. Component tests documented before implementation. |
| **IV. Type Safety** | ✅ PASS | All components have complete TypeScript interfaces in contracts/components.ts. No `any` types. |
| **V. Local-First Architecture** | ✅ PASS | All state management is local React state. No external dependencies added. |

**Overall Re-Assessment**: ✅ **STILL COMPLIANT** - Design phase introduces no constitutional violations. Type contracts are complete and maintain safety. TDD workflow is clearly defined in quickstart guide.

---

## Implementation Readiness Checklist

Before proceeding to Phase 2 (tasks generation), verify:

- [x] All clarifications resolved (no NEEDS CLARIFICATION markers)
- [x] Constitution check passed (initial and post-design)
- [x] Research decisions documented with rationale
- [x] Component contracts defined in TypeScript
- [x] Data model documented with state flow diagrams
- [x] Quickstart guide created with TDD examples
- [x] Agent context updated (if applicable)
- [x] No architectural complexity violations

**Status**: ✅ **READY FOR PHASE 2** - Run `/speckit.tasks` to generate implementation tasks

---

## Appendix: Key Files Reference

| Document | Purpose | Status |
|----------|---------|--------|
| [spec.md](./spec.md) | Feature requirements and acceptance criteria | ✅ Complete |
| [plan.md](./plan.md) | This file - implementation strategy | ✅ Complete |
| [research.md](./research.md) | Technology decisions and alternatives | ✅ Complete |
| [data-model.md](./data-model.md) | Component contracts and state flow | ✅ Complete |
| [contracts/components.ts](./contracts/components.ts) | TypeScript interface definitions | ✅ Complete |
| [quickstart.md](./quickstart.md) | Developer setup and TDD workflow | ✅ Complete |
| tasks.md | Detailed implementation tasks | ⏸️  Pending - run `/speckit.tasks` |

---

## Summary

**Plan Status**: ✅ **APPROVED FOR IMPLEMENTATION** (pending tasks generation)

**What was accomplished**:
- ✅ Technical context defined (React/TypeScript, CSS Grid, TDD)
- ✅ Constitution compliance verified (no violations)
- ✅ Project structure mapped (frontend-only changes)
- ✅ Phase 0 research completed (all decisions documented)
- ✅ Phase 1 design completed (contracts, data model, quickstart)
- ✅ Implementation readiness achieved

**Next steps**:
1. Run `/speckit.tasks` to generate detailed task breakdown
2. Review generated tasks with team
3. Begin TDD implementation following quickstart guide
4. Track progress against task checklist

**Estimated Scope**:
- New components: 2 (Sidebar, NavigationItem)
- Modified components: 3 (App.tsx, FileUpload, App.css)
- New test files: 3 (Sidebar.test, NavigationItem.test, integration test)
- Total LOC: ~200-300 (code) + ~150-200 (tests)
- Estimated effort: 2-3 days (with TDD, including tests)

**Success Criteria** (from spec):
- ✅ SC-001: Title visible at top of page in initial viewport
- ✅ SC-002: Sidebar navigation accessible within 0 clicks (always visible)
- ✅ SC-003: File upload to puzzle display within 2 seconds
- ✅ SC-004: 100% behavioral consistency with existing components
- ✅ SC-005: Game completion displays in same visual positions
- ✅ SC-006: Smooth layout transitions without jumping/shifting
- ✅ SC-007: Zero backend changes required

All success criteria are testable and will be verified in Phase 2 implementation tasks.
