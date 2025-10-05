# Tasks: LLM Provider Integration for Connection Puzzle Solver

**Input**: Design documents from `/specs/002-in-phase-2/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.11+, FastAPI, Pydantic, React, TypeScript, langchain
   → Libraries: langchain, openai, ollama-python, python-dotenv
   → Structure: Web application with full-stack separation
2. Load design documents:
   → data-model.md: 6 entities (LLMProvider, RecommendationRequest, etc.)
   → contracts/: 2 API endpoints (/recommendations, /providers/validate)
   → research.md: langchain abstraction, environment config, template prompts
   → quickstart.md: 5 user journey validation scenarios
3. Generate tasks by category:
   → Setup: Dependencies, environment config, project structure
   → Tests: Contract tests for 2 endpoints, integration tests for 5 journeys
   → Core: 6 Pydantic models, LLM services, API endpoints, frontend components
   → Integration: Provider factory, prompt templates, error handling
   → Polish: Mocking, coverage, type checking, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel execution
   → Same file/service = sequential dependencies
   → Tests before implementation (TDD strict enforcement)
5. Number tasks sequentially (T001-T043)
6. LLM-specific considerations: Mock responses, environment variables, provider switching
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in task descriptions
- All tasks follow TDD: tests first, then implementation

## Path Conventions
- **Backend**: `backend/src/` (FastAPI + Pydantic + langchain)
- **Frontend**: `frontend/src/` (React + TypeScript)
- **Tests**: `backend/tests/`, `frontend/tests/`
- **Environment**: `.env` file in project root

## Phase 3.1: Setup & Dependencies
- [x] T001 Add backend LLM dependencies: `cd backend && uv add langchain openai langchain-community python-dotenv`
- [x] T002 Create environment configuration template `.env.example` with OPENAI_API_KEY, OLLAMA_BASE_URL variables
- [x] T003 [P] Configure backend pytest with LLM provider mocking support in `backend/pyproject.toml`
- [x] T004 [P] Configure frontend Jest for LLM provider testing in `frontend/package.json`
- [x] T005 [P] Add backend linting rules for langchain imports in `backend/pyproject.toml`

## Phase 3.2: Contract Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3 ✅ COMPLETED
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T006: Contract test POST /api/v2/recommendations 📄`backend/tests/contract/test_recommendations_api.py` ✅
- [x] T007: Contract test GET /api/v2/health 📄`backend/tests/contract/test_health_api.py` ✅
- [x] T008: Contract test configuration validation 📄`backend/tests/contract/test_configuration_service.py` ✅
- [x] T009: Integration test LLM providers 📄`backend/tests/integration/test_llm_providers.py` ✅
- [x] T010 [P] Integration test openai provider journey in `backend/tests/integration/test_openai_provider_flow.py` with mocked responses ✅
- [x] T011 [P] Integration test error scenarios in `backend/tests/integration/test_provider_error_handling.py` ✅
- [x] T012 [P] Frontend component test LLM provider input field in `frontend/tests/components/test_llm_provider_input.test.tsx` ✅
- [x] T013 [P] Frontend integration test provider selection flow in `frontend/tests/integration/test_provider_selection.test.tsx` ✅

## Phase 3.3: Backend Pydantic Models (ONLY after contract tests are failing) ✅ COMPLETED
- [x] T014 [P] LLMProvider model in `backend/src/llm_models/llm_provider.py` with provider_type validation ✅
- [x] T015 [P] GuessAttempt model in `backend/src/llm_models/guess_attempt.py` with outcome enum validation ✅
- [x] T016 [P] RecommendationRequest model in `backend/src/llm_models/recommendation_request.py` with word list validation ✅
- [x] T017 [P] RecommendationResponse model in `backend/src/llm_models/recommendation_response.py` with confidence score validation ✅
- [x] T018 [P] PuzzleState model in `backend/src/llm_models/puzzle_state.py` with 16-word constraint validation ✅
- [x] T019 [P] CompletedGroup model in `backend/src/llm_models/completed_group.py` with difficulty level enum ✅

## Phase 3.4: Backend LLM Services (ONLY after model tests pass)
- [ ] T020 [P] Environment configuration service in `backend/src/services/config_service.py` for .env loading
- [ ] T021 [P] LLM provider factory in `backend/src/services/llm_provider_factory.py` with langchain integration
- [ ] T022 [P] Prompt template service in `backend/src/services/prompt_service.py` for context injection
- [ ] T023 [P] Simple recommendation service in `backend/src/services/simple_recommendation_service.py` (Phase 1 compatibility)
- [ ] T024 Ollama integration service in `backend/src/services/ollama_service.py` with langchain ollama provider
- [ ] T025 OpenAI integration service in `backend/src/services/openai_service.py` with langchain openai provider
- [ ] T026 Response validation service in `backend/src/services/response_validator.py` for LLM output validation
- [ ] T027 Recommendation orchestration service in `backend/src/services/recommendation_service.py` that routes to providers

## Phase 3.5: Backend API Endpoints (ONLY after service tests pass)
- [ ] T028 POST /api/v2/recommendations endpoint in `backend/src/api/recommendations.py` with OpenAPI documentation
- [ ] T029 POST /api/v2/providers/validate endpoint in `backend/src/api/provider_validation.py` with availability checking
- [ ] T030 Error handling middleware in `backend/src/api/error_handlers.py` for consistent error responses
- [ ] T031 Update main FastAPI app in `backend/src/main.py` to include v2 routes with CORS for frontend

## Phase 3.6: Frontend TypeScript Types (ONLY after backend contracts defined)
- [ ] T032 [P] LLM provider types in `frontend/src/types/llm-provider.ts` matching backend models
- [ ] T033 [P] Recommendation types in `frontend/src/types/recommendation.ts` with response interfaces
- [ ] T034 [P] API client types in `frontend/src/types/api.ts` for request/response typing

## Phase 3.7: Frontend Components (ONLY after frontend tests are failing)
- [ ] T035 [P] LLM provider input component in `frontend/src/components/LLMProviderInput.tsx` with validation
- [ ] T036 [P] Enhanced loading component in `frontend/src/components/LoadingIndicator.tsx` for persistent loading
- [ ] T037 [P] Error message component in `frontend/src/components/ErrorMessage.tsx` for provider errors
- [ ] T038 [P] Recommendation display component in `frontend/src/components/RecommendationDisplay.tsx` with explanation
- [ ] T039 Update puzzle interface in `frontend/src/components/PuzzleInterface.tsx` to include LLM provider selection
- [ ] T040 API service client in `frontend/src/services/api-client.ts` for v2 endpoints integration

## Phase 3.8: Integration & Testing
- [ ] T041 Create comprehensive LLM provider mocks in `backend/tests/mocks/llm_mocks.py` for consistent testing
- [ ] T042 End-to-end testing with quickstart scenarios in `backend/tests/e2e/test_quickstart_scenarios.py`
- [ ] T043 Frontend-backend integration testing in `frontend/tests/e2e/test_full_application_flow.test.tsx`

## Dependencies
**Critical Path**:
1. Setup (T001-T005) → Contract Tests (T006-T013) → Models (T014-T019) → Services (T020-T027) → APIs (T028-T031)
2. Backend APIs complete → Frontend Types (T032-T034) → Frontend Components (T035-T040)
3. All implementation → Integration Testing (T041-T043)

**Blocking Relationships**:
- T006-T013 MUST fail before any T014+ implementation
- T014-T019 models before T020-T027 services
- T020-T027 services before T028-T031 APIs
- T024-T025 (ollama/openai services) depend on T021 (factory) and T022 (prompts)
- T028-T031 backend APIs before T032-T040 frontend
- T035-T040 frontend components before T041-T043 integration

## Parallel Execution Examples

### Phase 3.2 - Contract Tests (All Parallel)
```bash
# All contract tests can run simultaneously (different files)
Task: "Contract test POST /api/v2/recommendations in backend/tests/contract/test_recommendations_api.py"
Task: "Contract test POST /api/v2/providers/validate in backend/tests/contract/test_provider_validation_api.py"
Task: "Integration test simple provider in backend/tests/integration/test_simple_provider_flow.py"
Task: "Frontend component test LLM input in frontend/tests/components/test_llm_provider_input.test.tsx"
```

### Phase 3.3 - Pydantic Models (All Parallel)
```bash
# All models are independent and can be created simultaneously
Task: "LLMProvider model in backend/src/models/llm_provider.py"
Task: "RecommendationRequest model in backend/src/models/recommendation_request.py"
Task: "RecommendationResponse model in backend/src/models/recommendation_response.py"
Task: "GuessAttempt model in backend/src/models/guess_attempt.py"
```

### Phase 3.4 - Services (Partially Parallel)
```bash
# Independent services can run in parallel
Task: "Environment config service in backend/src/services/config_service.py"
Task: "Simple recommendation service in backend/src/services/simple_recommendation_service.py"
Task: "Response validation service in backend/src/services/response_validator.py"

# These depend on factory/prompts completing first:
# T024 ollama_service.py (after T021, T022)
# T025 openai_service.py (after T021, T022)
# T027 recommendation_service.py (after all provider services)
```

### Phase 3.6 - Frontend Types (All Parallel)
```bash
# All TypeScript type files are independent
Task: "LLM provider types in frontend/src/types/llm-provider.ts"
Task: "Recommendation types in frontend/src/types/recommendation.ts"
Task: "API client types in frontend/src/types/api.ts"
```

## LLM-Specific Implementation Notes

### Mock Strategy for Testing
- Use `unittest.mock` to mock langchain providers
- Create consistent mock responses for ollama/openai
- Mock network failures for error scenario testing
- Ensure test reproducibility with fixed mock data

### Environment Configuration
- All LLM credentials from `.env` file only
- Graceful handling of missing environment variables
- Clear error messages for configuration issues
- Support for local ollama and cloud openai simultaneously

### Provider Switching Logic
- Factory pattern for clean provider instantiation
- Validation before provider selection
- Fallback behavior for unavailable providers
- Session-only provider state (no persistence)

### Error Handling Patterns
- Consistent error response format across all providers
- User-friendly messages for common failures
- Detailed logging for debugging (backend only)
- Persistent loading states per clarifications

## Validation Checklist
✅ All 2 API contracts have dedicated test tasks  
✅ All 6 entities have Pydantic model tasks  
✅ All 5 quickstart journeys have integration test tasks  
✅ LLM provider factory and services properly sequenced  
✅ Frontend components depend on backend API completion  
✅ Mocking strategy for LLM responses defined  
✅ Environment configuration and error handling covered  
✅ TDD enforced: tests before implementation in all phases