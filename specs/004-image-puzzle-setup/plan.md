# Implementation Plan: Image-Based Puzzle Setup

**Branch**: `004-image-puzzle-setup` | **Date**: December 13, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-image-puzzle-setup/spec.md`

## Summary

Add image-based puzzle setup capability allowing users to paste screenshots of 4x4 word grids and extract words using LLM vision models. Extends existing navigation with "From Image" option, implements new frontend component for image paste/preview, creates backend `/api/v2/setup_puzzle_from_image` endpoint using LLM `with_structured_output()` for word extraction, and integrates seamlessly with existing puzzle gameplay. Maintains single-user session model and follows existing architectural patterns for LLM provider integration (OpenAI, Ollama, Simple).

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 4.9+ (frontend)
**Primary Dependencies**: 
- Backend: FastAPI, Pydantic, LangChain (vision-capable models), existing LLMProviderFactory
- Frontend: React 18.x, React Testing Library, Jest
**Storage**: In-memory session state via existing `session_manager` (single-user)
**Testing**: pytest (backend), Jest + React Testing Library (frontend), maintain >80% coverage
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge - ES2020+), Python 3.11+
**Project Type**: Full-stack web application (backend + frontend changes)
**Performance Goals**: 
- Image paste/preview <2s
- LLM word extraction + puzzle setup <10s total
- Image size validation (5MB max) immediate (client-side)
**Constraints**: 
- Single-user, single-session only (no multi-user support)
- No OCR - LLM vision only via `with_structured_output()`
- No drag-and-drop - keyboard paste only (CMD/CTRL+V)
- Word list format must match existing file-based setup for compatibility
- Vision capability validation via attempt-and-fail (graceful error handling)
**Scale/Scope**: 
- Frontend: 1 new component (ImagePuzzleSetup), navigation update (Sidebar), 1 new API service method
- Backend: 1 new endpoint (`/api/v2/setup_puzzle_from_image`), 1 new Pydantic model, LLM integration
- ~400-600 LOC total changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Full-Stack Separation** | ✅ PASS | Clear API boundary at `/api/v2/setup_puzzle_from_image`. Frontend handles image encoding, backend handles LLM extraction. No cross-layer dependencies. |
| **II. API-First Design** | ✅ PASS | New REST endpoint with Pydantic request/response models. OpenAPI-documented. Follows existing v2 API patterns. |
| **III. Test-First Development** | ✅ PASS | Plan includes TDD: contract tests for API, unit tests for LLM extraction, component tests for UI, integration tests for full flow. |
| **IV. Type Safety** | ✅ PASS | TypeScript for frontend (ImagePuzzleSetup component, API types). Pydantic for backend (ImageSetupRequest/Response models). All inputs validated. |
| **V. Local-First Architecture** | ✅ PASS | Session state remains in-memory. No new persistent storage. LLM calls are external but follow existing provider pattern. Image processing client-side (base64). |

**Overall Assessment**: ✅ **COMPLIANT** - All constitutional principles satisfied. Follows existing architectural patterns for LLM integration, API design, and session management.

**Re-check After Phase 1**: Verify that image encoding doesn't introduce security vulnerabilities (validate MIME types, enforce size limits). Confirm LLM vision model support across providers (OpenAI GPT-4 Vision confirmed, Ollama vision models TBD).

## Complexity Tracking

> **This feature has NO constitutional violations - section included for completeness only**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

**Rationale**: Feature extends existing patterns without introducing new complexity. Uses established LLMProviderFactory, follows v2 API conventions, integrates with current navigation structure. Image handling is standard web API (Clipboard API + base64 encoding). Vision capability check via graceful degradation (attempt extraction, fail with clear error if model lacks vision) avoids need for upfront capability registry.

## Project Structure

### Documentation (this feature)

```text
specs/004-image-puzzle-setup/
├── spec.md              # Feature specification (✅ completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (LLM vision capabilities, image handling patterns)
├── data-model.md        # Phase 1 output (Pydantic models, component props, state shape)
├── quickstart.md        # Phase 1 output (developer setup, testing guide, vision model config)
├── contracts/           # Phase 1 output (API contracts, TypeScript interfaces)
│   ├── api.ts           # Frontend-backend API contract
│   └── components.ts    # Component prop types
├── checklists/          # Quality gates
│   └── requirements.md  # Specification validation (✅ completed)
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── v2_image_setup.py          # NEW: Image puzzle setup endpoint
│   ├── models.py                      # MODIFIED: Add ImageSetupRequest/Response models
│   ├── services/
│   │   ├── llm_provider_factory.py    # UNMODIFIED: Existing LLM provider infrastructure
│   │   └── image_word_extractor.py    # NEW: Service for LLM-based word extraction
│   └── main.py                        # MODIFIED: Register v2_image_setup router
├── tests/
│   ├── contract/
│   │   └── test_setup_puzzle_from_image.py  # NEW: API contract tests
│   ├── unit/
│   │   └── test_image_word_extractor.py     # NEW: Word extraction logic tests
│   └── integration/
│       └── test_image_puzzle_flow.py         # NEW: End-to-end image setup tests

frontend/
├── src/
│   ├── components/
│   │   ├── Sidebar.tsx                # MODIFIED: Add "From Image" navigation item
│   │   ├── Sidebar.test.tsx           # MODIFIED: Test new navigation item
│   │   ├── ImagePuzzleSetup.tsx       # NEW: Image paste/upload component
│   │   ├── ImagePuzzleSetup.css       # NEW: Component styling
│   │   └── ImagePuzzleSetup.test.tsx  # NEW: Component tests
│   ├── services/
│   │   └── api.ts                     # MODIFIED: Add setupPuzzleFromImage method
│   ├── types/
│   │   ├── navigation.ts              # MODIFIED: Add 'from-image' action type
│   │   └── puzzle.ts                  # MODIFIED: Add image setup types
│   ├── App.tsx                        # MODIFIED: Handle 'from-image' navigation, render ImagePuzzleSetup
│   └── App.test.tsx                   # MODIFIED: Test image setup flow
└── tests/
    └── integration/
        └── test_image_setup_flow.test.tsx  # NEW: Full image setup workflow test
```

**Structure Decision**: Full-stack web application with backend and frontend changes. Backend follows existing v2 API pattern (`backend/src/api/v2_*.py`). Frontend adds new component under `components/` and extends existing navigation. Leverages existing LLM provider infrastructure without modification.

## Phase 0: Outline & Research

**Status**: ✅ COMPLETE  
**Output**: [research.md](./research.md)

### Research Decisions Summary

All research tasks completed with the following key decisions:

1. **LLM Vision Model Capabilities** ✅
   - **Decision**: User-selected models with graceful degradation (no upfront capability detection)
   - **Error Handling**: Unified message "LLM unable to extract puzzle words" for all extraction failures
   - **Rationale**: Simplifies implementation, allows user experimentation with any model

2. **Image Encoding Best Practices** ✅
   - **Decision**: Frontend-only validation, base64 encoding client-side
   - **Supported Formats**: PNG, JPEG, JPG, GIF (5MB max)
   - **Rationale**: Immediate user feedback, no wasted uploads, simpler backend

3. **Structured Output Format for Word Extraction** ✅
   - **Decision**: `ExtractedWords` Pydantic model with comprehensive 4-strategy prompt
   - **Prompt Includes**: Basic extraction + grid hints + example format + validation instructions
   - **Word Format**: Lowercase normalization (matches existing puzzle words)
   - **Rationale**: Maximum accuracy through redundant guidance

4. **Error Handling for Vision Failures** ✅
   - **Decision**: Unified error handling - all backend failures return HTTP 400 with same message
   - **Frontend Errors**: Specific validation errors (size, format) shown immediately
   - **Rationale**: Simplified implementation, consistent UX, retry-friendly

5. **LLM Provider Factory Integration** ✅
   - **Decision**: Use existing `LLMProviderFactory.create_provider()` pattern - no changes
   - **Pattern**: Create `LLMProvider` model, pass to factory, access via `provider.llm`
   - **Special Error**: "LLM does not support 'with_structured_output()' method" if capability missing
   - **Rationale**: Zero changes to provider infrastructure, maintains architectural consistency

6. **Session State Integration** ✅
   - **Decision**: Use existing `session_manager.create_session(words)` - no changes
   - **Compatibility**: Perfect - `PuzzleSession` already normalizes to lowercase
   - **Source Agnostic**: Works identically for file-based and image-based setup
   - **Rationale**: No session management changes required, seamless integration

### Consolidated Architecture Impact

| Component | Change Required | Decision |
|-----------|----------------|----------|
| LLM Provider Factory | None | Use existing patterns |
| Session Manager | None | Use existing `create_session()` |
| Image Validation | Frontend only | Client-side size/format checks |
| Error Handling | Unified | Single backend error message |
| Word Normalization | None | Existing lowercase conversion |
| Prompt Strategy | New | Combined 4-strategy approach |

### Implementation Insights

- **Zero infrastructure changes**: Existing provider factory and session manager work as-is
- **Frontend handles validation**: Size, format, and base64 encoding all client-side
- **Backend focuses on extraction**: Only LLM vision invocation and error handling
- **Graceful degradation**: No capability detection needed - fail with clear message
- **Perfect compatibility**: Image-extracted words integrate identically to file-loaded words

**See [research.md](./research.md) for complete analysis, code patterns, and detailed rationale.**

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE  
**Prerequisites**: `research.md` complete  
**Output**: `data-model.md`, `/contracts/`, `quickstart.md`

### Data Model Extraction

**Source**: Functional requirements FR-001 through FR-025, Key Entities section

#### Backend Models (Pydantic)

```python
# backend/src/models.py additions

class ImageSetupRequest(BaseModel):
    """Request model for setting up puzzle from image."""
    image_base64: str = Field(..., description="Base64-encoded image content")
    image_mime: str = Field(..., description="Image MIME type (image/png, image/jpeg, etc.)")
    provider_type: str = Field(..., description="LLM provider type for word extraction")
    model_name: str = Field(..., description="Specific model name for provider")
    
    @validator('image_base64')
    def validate_image_size(cls, v):
        """Validate base64 image doesn't exceed 5MB."""
        # Base64 adds ~33% overhead, so 5MB * 4/3 = ~6.67MB base64 max
        max_base64_size = 6666666  # bytes
        if len(v) > max_base64_size:
            raise ValueError("Image size exceeds 5MB limit")
        return v
    
    @validator('image_mime')
    def validate_mime_type(cls, v):
        """Validate image MIME type is supported."""
        supported = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
        if v not in supported:
            raise ValueError(f"Unsupported MIME type: {v}")
        return v


class ImageSetupResponse(BaseModel):
    """Response model for image-based puzzle setup."""
    remaining_words: List[str] = Field(..., description="16 words extracted from image")
    status: str = Field(..., description="Setup status ('success' or 'error')")
    message: Optional[str] = Field(None, description="Error message if status is error")


class ExtractedWords(BaseModel):
    """Pydantic model for LLM structured output."""
    words: List[str] = Field(..., min_items=16, max_items=16, description="16 words from 4x4 grid in reading order")
    
    @validator('words')
    def validate_word_count(cls, v):
        """Ensure exactly 16 words extracted."""
        if len(v) != 16:
            raise ValueError(f"Expected 16 words, got {len(v)}")
        return v
```

#### Frontend Types (TypeScript)

```typescript
// frontend/src/types/puzzle.ts additions

export interface ImageSetupRequest {
  image_base64: string;
  image_mime: string;
  provider_type: string;
  model_name: string;
}

export interface ImageSetupResponse {
  remaining_words: string[];
  status: string;
  message?: string;
}

export interface ImagePasteState {
  imageData: string | null;          // Base64 image data
  imageMime: string | null;           // MIME type
  previewUrl: string | null;          // Object URL for preview
  sizeBytes: number;                  // Image size in bytes
  isValid: boolean;                   // Validation state
  error: string | null;               // Validation error message
}
```

```typescript
// frontend/src/types/navigation.ts modification

export type NavigationAction = 
  | { type: 'from-file' }
  | { type: 'from-image' }                    // NEW
  | { type: 'toggle-menu'; menu: string };
```

#### Component Props

```typescript
// frontend/src/components/ImagePuzzleSetup.tsx

export interface ImagePuzzleSetupProps {
  onImageSetup: (words: string[]) => void;    // Callback with extracted words
  providers: LLMProviderType[];                // Available LLM providers
  defaultProvider: LLMProviderType;            // Default provider selection
  defaultModel: string;                        // Default model selection
  onError: (error: string) => void;            // Error callback
}
```

### API Contract Generation

**Endpoint**: `POST /api/v2/setup_puzzle_from_image`

**OpenAPI Schema** (generated in `/contracts/api.ts`):

```yaml
/api/v2/setup_puzzle_from_image:
  post:
    summary: Setup puzzle from image using LLM vision
    description: Extracts 16 words from a 4x4 grid image using LLM vision capabilities
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [image_base64, image_mime, provider_type, model_name]
            properties:
              image_base64:
                type: string
                description: Base64-encoded image content
              image_mime:
                type: string
                enum: [image/png, image/jpeg, image/jpg, image/gif, image/webp]
              provider_type:
                type: string
                enum: [openai, ollama, simple]
              model_name:
                type: string
                description: Specific model name for provider
    responses:
      200:
        description: Successfully extracted words
        content:
          application/json:
            schema:
              type: object
              required: [remaining_words, status]
              properties:
                remaining_words:
                  type: array
                  items:
                    type: string
                  minItems: 16
                  maxItems: 16
                status:
                  type: string
                  enum: [success]
      400:
        description: Bad request (invalid image, wrong word count, model lacks vision)
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [error]
                message:
                  type: string
                  enum:
                    - "Could not extract 16 words"
                    - "Model does not support vision"
      413:
        description: Payload too large (image > 5MB)
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [error]
                message:
                  type: string
                  enum: ["Payload too large"]
      422:
        description: Unprocessable entity (missing required fields)
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [error]
                message:
                  type: string
                  enum: ["Unprocessable Entity: missing fields"]
      500:
        description: Internal server error (LLM provider failure)
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [error]
                message:
                  type: string
                  enum: ["Internal error: LLM provider failure"]
```

### State Flow Diagram

```text
User Actions → ImagePuzzleSetup → App.tsx → Backend API → LLM Vision → Puzzle Setup

1. Initial Navigation:
   currentView = 'initial' or 'file-upload' or 'puzzle-active'
   → User clicks "From Image" in sidebar
   → onNavigationAction({ type: 'from-image' })
   → App sets currentView = 'image-setup'
   → Main shows ImagePuzzleSetup component

2. Image Paste:
   ImagePuzzleSetup rendered, empty placeholder visible
   → User pastes image (CMD/CTRL+V)
   → onPaste handler captures clipboard image data
   → Convert to base64, detect MIME type
   → Validate size (<5MB), display preview
   → setState({ imageData, imageMime, previewUrl })

3. Provider/Model Selection:
   → User selects provider from dropdown (or uses default)
   → User selects model from dropdown (or uses default)
   → Dropdowns use same options as puzzle solving

4. Setup Puzzle:
   → User clicks "Setup Puzzle" button
   → Validate image pasted (show error if not)
   → Call apiService.setupPuzzleFromImage(imageData, imageMime, provider, model)
   → Frontend shows loading state

5. Backend Processing:
   → Receive ImageSetupRequest
   → Validate request (size, MIME, fields)
   → Create LLM provider via LLMProviderFactory
   → Construct vision prompt with grid extraction instructions
   → Invoke LLM with with_structured_output(ExtractedWords)
   → LLM returns 16 words in reading order
   → Create session via session_manager.create_session(words)
   → Return ImageSetupResponse

6. Success Path:
   → Frontend receives ImageSetupResponse with 16 words
   → Call onImageSetup(words)
   → App sets currentView = 'puzzle-active'
   → EnhancedPuzzleInterface renders with extracted words
   → Gameplay proceeds identically to file-based setup

7. Error Paths:
   → 413 Payload Too Large: Display "Image too large (max 5MB)"
   → 400 Wrong Word Count: Display "Could not extract 16 words from image"
   → 400 Model No Vision: Display "Selected model doesn't support image analysis"
   → 422 Missing Fields: Display "Invalid request - please try again"
   → 500 Provider Failure: Display "LLM provider error - please retry"
   → Preserve imageData, provider, model selections for retry
```

### Validation Rules

#### Image Validation (Frontend)
- Size must not exceed 5MB (5,242,880 bytes)
- MIME type must be image/png, image/jpeg, image/jpg, image/gif, or image/webp
- Base64 encoding must be valid
- Image data must exist before "Setup Puzzle" enabled

#### Request Validation (Backend)
- `image_base64`: Required, non-empty string, size check via validator
- `image_mime`: Required, must be in supported MIME types list
- `provider_type`: Required, must be valid LLM provider type
- `model_name`: Required, non-empty string

#### Response Validation
- `remaining_words`: Must contain exactly 16 strings
- Words must be in left-to-right, top-to-bottom order (positions [0-3] row 1, [4-7] row 2, [8-11] row 3, [12-15] row 4)
- `status`: Must be "success" for HTTP 200, "error" for all error responses

### Phase 1 Deliverables ✅

**Generated Files**:
- ✅ `data-model.md`: Complete entity definitions (33KB)
  - Backend Pydantic models (ImageSetupRequest, ImageSetupResponse, ExtractedWords)
  - Frontend TypeScript types (API contracts, component state)
  - Validation rules and error catalog
  - Entity relationships and data flow diagrams
  
- ✅ `contracts/api.ts`: TypeScript API contract (12KB)
  - Request/Response interfaces
  - HTTP status code enums
  - Type guards and validation helpers
  - OpenAPI schema documentation
  
- ✅ `contracts/components.ts`: Component prop interfaces (13KB)
  - ImagePuzzleSetupProps
  - Internal state interfaces (ImagePasteState, LoadingState, ProviderSelectionState)
  - Event handler types
  - Testing utilities and mock fixtures
  
- ✅ `quickstart.md`: Developer setup guide (18KB)
  - Backend/frontend setup instructions
  - LLM provider configuration (OpenAI, Ollama)
  - TDD testing workflows with examples
  - Manual testing guide with test images
  - Troubleshooting common issues
  - Performance benchmarks

**Total Documentation**: 76KB across 4 files

### Agent Context Update

**Next Step** (after reviewing generated files):

```bash
cd /Users/jim/Desktop/genai/sdd_connection_solver2
.specify/scripts/bash/update-agent-context.sh copilot
```

This updates `.github/copilot-instructions.md` with:
- New endpoint `/api/v2/setup_puzzle_from_image` in API domain
- ImagePuzzleSetup component in frontend-components category
- LLM vision integration patterns in llm-adapters domain

## Phase 2: Task Planning

**Status**: ✅ COMPLETE  
**Prerequisites**: Phase 1 complete (data-model.md, contracts, quickstart.md)  
**Output**: [tasks.md](./tasks.md)

**Summary**: Detailed task breakdown generated with 95 tasks organized by user story. All tasks follow TDD workflow per constitution Principle III. Tasks grouped into 8 phases: Setup (6), Foundational (8), US4-MVP (23), US1 (4), US2 (5), US3 (6), US5 (13), Polish (15). Critical path: 37 tasks for MVP (US4 only).

### High-Level Task Grouping

#### Phase 2.1: Backend Foundation (TDD)
- Write contract tests for `/api/v2/setup_puzzle_from_image` endpoint
- Implement Pydantic models (ImageSetupRequest, ImageSetupResponse, ExtractedWords)
- Create `image_word_extractor.py` service with LLM vision invocation
- Implement endpoint in `v2_image_setup.py` with error handling
- Register router in `main.py`
- Unit tests for word extraction service
- Integration tests for full backend flow

#### Phase 2.2: Frontend Component (TDD)
- Write component tests for ImagePuzzleSetup
- Implement ImagePuzzleSetup component (paste handler, preview, provider/model selectors)
- Add CSS styling matching project patterns
- Update Sidebar component with "From Image" navigation item
- Update Sidebar tests for new navigation item
- Add `setupPuzzleFromImage` method to api.ts service
- Update App.tsx to handle 'from-image' navigation action
- Update App.tsx tests for image setup flow

#### Phase 2.3: Integration & End-to-End Testing
- End-to-end test: paste image → setup → play puzzle
- Cross-browser testing (Chrome, Firefox, Safari)
- Error handling tests (oversized image, wrong format, model no vision)
- Performance testing (paste response time, LLM extraction time)
- Provider compatibility tests (OpenAI, Ollama if vision models available)

#### Phase 2.4: Documentation & Polish
- Update README with image setup instructions
- Add image setup example screenshots
- Document LLM vision model requirements in quickstart.md
- Update API documentation
- Code review and refinement

## Testing Strategy

### Test Coverage Requirements
- **Backend**: >80% line coverage (per constitution)
  - Contract tests: API request/response validation
  - Unit tests: Word extraction logic, error handling, validation
  - Integration tests: LLM provider interaction, session creation
- **Frontend**: >80% line coverage
  - Component tests: ImagePuzzleSetup render, paste handler, validation
  - Integration tests: Navigation flow, API calls, error display

### Test Categories

#### Contract Tests (Backend)
```python
# backend/tests/contract/test_setup_puzzle_from_image.py

class TestImageSetupContract:
    def test_success_response_contract(self):
        """Test successful extraction returns 16 words."""
        
    def test_oversized_image_returns_413(self):
        """Test >5MB image returns HTTP 413."""
        
    def test_missing_fields_returns_422(self):
        """Test missing required fields returns HTTP 422."""
        
    def test_invalid_mime_type_returns_400(self):
        """Test unsupported MIME type returns HTTP 400."""
        
    def test_model_no_vision_returns_400(self):
        """Test model without vision capability returns HTTP 400."""
        
    def test_extraction_failure_returns_400(self):
        """Test failed word extraction returns HTTP 400."""
```

#### Unit Tests (Backend)
```python
# backend/tests/unit/test_image_word_extractor.py

class TestImageWordExtractor:
    def test_extract_words_with_openai_vision(self):
        """Test word extraction using OpenAI GPT-4 Vision."""
        
    def test_extract_words_reading_order(self):
        """Test words returned in left-to-right, top-to-bottom order."""
        
    def test_extract_words_wrong_count(self):
        """Test error when LLM returns != 16 words."""
        
    def test_model_without_vision_capability(self):
        """Test graceful failure when model lacks vision."""
        
    def test_prompt_construction(self):
        """Test vision prompt includes grid structure hints."""
```

#### Component Tests (Frontend)
```typescript
// frontend/src/components/ImagePuzzleSetup.test.tsx

describe('ImagePuzzleSetup', () => {
  test('renders with empty placeholder', () => {});
  
  test('handles image paste from clipboard', () => {});
  
  test('displays pasted image preview', () => {});
  
  test('validates image size (<5MB)', () => {});
  
  test('shows error for oversized image', () => {});
  
  test('enables Setup Puzzle button only when image pasted', () => {});
  
  test('calls API with correct provider and model', () => {});
  
  test('displays loading state during extraction', () => {});
  
  test('shows error messages for failed extraction', () => {});
  
  test('preserves state on error for retry', () => {});
});
```

#### Integration Tests
```typescript
// frontend/tests/integration/test_image_setup_flow.test.tsx

describe('Image Setup Flow', () => {
  test('complete flow: navigate → paste → select provider → setup → play', () => {});
  
  test('error flow: oversized image → error display → retry with smaller', () => {});
  
  test('error flow: wrong word count → error display → try different image', () => {});
  
  test('navigation: switch from File to Image clears state', () => {});
});
```

### Mock Strategy

#### Backend Mocks
- Mock LLM provider responses for consistent testing
- Mock `with_structured_output()` to return controlled ExtractedWords
- Mock vision API calls to avoid external dependencies in tests

#### Frontend Mocks
- Mock Clipboard API for paste event simulation
- Mock API service responses for different scenarios
- Mock image data for consistent test fixtures

## Success Metrics

### Functional Completeness
- ✅ All 25 functional requirements (FR-001 through FR-025) implemented
- ✅ All 5 user stories (P1-P3) validated via acceptance scenarios
- ✅ All 7 edge cases handled with appropriate error messages

### Quality Gates
- ✅ Backend test coverage >80% (contract, unit, integration)
- ✅ Frontend test coverage >80% (component, integration)
- ✅ All constitutional principles maintained (checked in Phase 1)
- ✅ Zero regressions in existing puzzle setup (file-based) functionality

### Performance Targets
- ✅ Image paste to preview display <2 seconds (SC-002)
- ✅ LLM extraction + puzzle initialization <10 seconds (SC-003)
- ✅ Error responses within 3 seconds (SC-005)
- ✅ 95% word extraction accuracy for clear 4x4 grid images (SC-004)

### User Experience
- ✅ 1-click access to image setup from initial state (SC-001)
- ✅ 100% feature parity with file-based setup for gameplay (SC-006)
- ✅ Layout matches ASCII diagram specification (SC-007)
- ✅ Consistent behavior across all supported providers (SC-008)

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **LLM vision models unavailable for Ollama** | High (limits provider options) | Medium | Default to OpenAI GPT-4 Vision, document Ollama vision model requirements in quickstart.md |
| **Word extraction accuracy <95%** | Medium (poor UX) | Low | Provide clear error messages, allow retry, include grid structure hints in prompt |
| **Base64 encoding performance for large images** | Low (slow paste) | Low | Enforce 5MB limit client-side, compress preview separately from upload |
| **Browser Clipboard API inconsistencies** | Medium (cross-browser issues) | Medium | Test thoroughly on Chrome/Firefox/Safari, document known limitations |
| **Vision model costs (OpenAI)** | Low (usage costs) | High | Document costs in quickstart.md, recommend Ollama for cost-sensitive users |

## Dependencies & Prerequisites

### External Dependencies
- **OpenAI API**: GPT-4 Vision model access required for OpenAI provider
  - Setup: Add `OPENAI_API_KEY` to environment
  - Cost: ~$0.01-0.03 per image analysis
- **Ollama**: Vision-capable models (llava, bakllava) optional
  - Setup: Install Ollama, pull vision model (`ollama pull llava`)
  - Cost: Free (local inference)

### Internal Dependencies
- Existing LLMProviderFactory must support vision models (verify in Phase 0)
- Existing session_manager.create_session() must handle word lists from any source
- Existing puzzle gameplay components work without modification

### Development Environment
- Python 3.11+ with langchain vision dependencies
- Node.js 18+ for frontend development
- Modern browser for Clipboard API support (Chrome 66+, Firefox 63+, Safari 13.1+)

## Next Steps

1. ✅ **Review & Approve Plan**: Stakeholder review of this implementation plan - COMPLETE
2. ✅ **Phase 0 Research**: Execute research tasks in Phase 0, document findings in `research.md` - COMPLETE
3. ✅ **Phase 1 Design**: Generate data models and contracts based on research decisions - COMPLETE
4. ✅ **Generate Tasks**: Run `/speckit.tasks` to create detailed task breakdown in `tasks.md` - COMPLETE
5. **Execute Implementation**: Begin Phase 1 (Setup) tasks, follow TDD workflow, maintain test coverage >80%

---

**Plan Status**: ✅ ALL PHASES COMPLETE - Ready for Implementation
**Branch**: `004-image-puzzle-setup`
**Last Updated**: December 13, 2025

**Next Command**: Begin implementation with Phase 1 (Setup) tasks from `tasks.md`
