
# Implementation Plan: LLM Provider Integration for Connection Puzzle Solver

**Branch**: `002-in-phase-2` | **Date**: October 5, 2025 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-in-phase-2/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Extend the connection puzzle solver to support LLM provider integration for AI-powered word recommendations. Users can select between "simple" algorithm (Phase 1 functionality) or LLM providers (ollama, openai) via a text input field. System generates intelligent prompts for LLMs that include puzzle context, previous guesses, and requests for specific connections. Implementation maintains backward compatibility while adding flexible provider switching through environment-based configuration.

## Technical Context
**Language/Version**: Python 3.11+ (backend), HTML/CSS/TypeScript (frontend)  
**Primary Dependencies**: FastAPI, Pydantic, React, uvicorn, uv (backend package management), langchain (with required packages for openai and ollama)  
**Storage**: In-memory/session-based only, no persistent storage  
**Testing**: pytest (backend), npm/Jest (frontend), React Testing Library  
**Target Platform**: macOS desktop web application (local development)  
**Project Type**: web - React frontend + FastAPI backend  
**Performance Goals**: No specific time requirements for recommendations (per clarifications)  
**Constraints**: Local-only operation, .env file configuration, offline-capable  
**Scale/Scope**: Single-user desktop application, 16-word puzzle interface, 4 color groups maximum

**Additional Implementation Notes**: When generating tests for LLM provider integration, mock the LLM responses to ensure consistent and repeatable tests. Any required configuration parameters, e.g., API keys or URL base, needed for the LLM providers will be provided via environment variables from a `.env` file

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Full-Stack Separation**: ✅ Frontend/backend developed independently with API boundaries  
**II. API-First Design**: ✅ REST APIs with OpenAPI specs defined before frontend implementation  
**III. Test-First Development**: ✅ TDD cycle enforced, 80% coverage requirement on business logic  
**IV. Type Safety**: ✅ TypeScript frontend, Pydantic backend, mypy static checking  
**V. Local-First Architecture**: ✅ Standalone desktop app, no external service dependencies, no persistent storage  

**Technology Standards Compliance**: ✅ FastAPI + Pydantic + React + TypeScript stack alignment  
**Development Workflow Compliance**: ✅ Independent build systems, automated testing gates

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── src/
│   ├── models/          # Pydantic models for data validation
│   ├── services/        # Business logic layer
│   └── api/            # FastAPI routes and endpoints
├── tests/
│   ├── contract/       # API contract tests
│   ├── integration/    # Full-stack integration tests
│   └── unit/          # Unit tests for services/models
└── pyproject.toml      # uv-managed dependencies

frontend/
├── src/
│   ├── components/     # Reusable React components
│   ├── pages/         # Page-level components
│   ├── services/      # API client and business logic
│   ├── types/         # TypeScript type definitions
│   └── utils/         # Helper functions
├── tests/
│   ├── components/    # Component unit tests
│   ├── integration/   # Frontend integration tests
│   └── e2e/          # End-to-end tests
└── package.json       # npm/yarn managed dependencies
```

**Structure Decision**: Web application architecture with independent frontend/backend build systems, following Full-Stack Separation principle. Each stack maintains isolated dependencies and testing suites. No persistent data storage - operates on session/transient data only.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base structure
- Generate backend tasks from API contracts (api.yaml) and data models
- Generate frontend tasks from UI requirements and provider selection logic
- Create integration tests from quickstart.md validation scenarios
- Each API endpoint → contract test task [P]
- Each Pydantic model → model creation task [P]
- Each user story from spec → integration test task
- LLM provider integrations → service implementation tasks
- Frontend provider selection → component modification tasks

**Ordering Strategy**:
- TDD order: Contract tests → Model tests → Implementation
- Dependency order: Backend models → Backend services → Frontend integration
- Backend Phase: LLM provider abstractions, API endpoints, validation
- Frontend Phase: Provider input field, loading states, error handling
- Integration Phase: End-to-end testing with mocked LLM responses
- Mark [P] for parallel execution on independent components

**LLM Integration Specific Tasks**:
- Create LLM provider factory pattern
- Implement langchain integration for ollama/openai
- Build prompt template system with context injection
- Add environment variable configuration management
- Create response validation and error handling
- Mock LLM responses for consistent testing

**Frontend Extension Tasks**:
- Add LLM Provider input field above file chooser
- Implement provider selection validation
- Create enhanced loading states for LLM requests
- Add error message display for provider failures
- Update recommendation display to show explanations
- Session-only provider state management

**Testing Strategy Tasks**:
- Contract tests for all new API endpoints
- Unit tests for LLM provider factory and services
- Integration tests for complete recommendation flow
- Frontend component tests for provider selection
- End-to-end tests covering all user journeys from quickstart
- Mock LLM responses to ensure test reliability

**Estimated Output**: 35-40 numbered, ordered tasks in tasks.md covering backend LLM integration, frontend UI updates, comprehensive testing, and validation scenarios

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.0.0 - See `.specify/memory/constitution.md`*
