# Data Model: Image-Based Puzzle Setup

**Feature**: 004-image-puzzle-setup | **Date**: December 13, 2025 | **Phase**: 1 (Design & Contracts)

## Overview

This document defines all data models, types, and validation rules for the image-based puzzle setup feature. Models are organized by layer (backend Pydantic models, frontend TypeScript types, component props) with validation rules and relationships documented.

## Backend Models (Pydantic)

### ImageSetupRequest

**Purpose**: Request payload for POST `/api/v2/setup_puzzle_from_image`

**Location**: `backend/src/models.py`

```python
class ImageSetupRequest(BaseModel):
    """Request model for setting up puzzle from image."""
    
    image_base64: str = Field(
        ..., 
        description="Base64-encoded image content (without data URL prefix)"
    )
    image_mime: str = Field(
        ..., 
        description="Image MIME type (image/png, image/jpeg, image/jpg, image/gif, image/webp)"
    )
    provider_type: str = Field(
        ..., 
        description="LLM provider type for word extraction (openai, ollama, simple)"
    )
    model_name: str = Field(
        ..., 
        description="Specific model name for provider (e.g., gpt-4-vision-preview)"
    )
    
    @validator('image_base64')
    def validate_image_size(cls, v):
        """Validate base64 image doesn't exceed 5MB.
        
        Base64 encoding adds ~33% overhead: 5MB raw = ~6.67MB base64
        """
        max_base64_size = 6_666_666  # bytes (~5MB original)
        if len(v) > max_base64_size:
            raise ValueError("Image size exceeds 5MB limit")
        return v
    
    @validator('image_mime')
    def validate_mime_type(cls, v):
        """Validate image MIME type is supported."""
        supported = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
        if v not in supported:
            raise ValueError(f"Unsupported MIME type: {v}. Supported types: {supported}")
        return v
    
    @validator('provider_type')
    def validate_provider_type(cls, v):
        """Validate provider type is recognized."""
        supported = ['openai', 'ollama', 'simple']
        if v not in supported:
            raise ValueError(f"Unsupported provider: {v}. Supported providers: {supported}")
        return v
```

**Validation Rules**:
- `image_base64`: Required, non-empty string, max 6.67MB encoded size
- `image_mime`: Required, must be in supported MIME types list
- `provider_type`: Required, must be valid LLM provider type
- `model_name`: Required, non-empty string (no format validation - provider-specific)

**Relationships**:
- Consumed by `setup_puzzle_from_image` endpoint
- Passed to `ImageWordExtractor.extract_words()`

---

### ImageSetupResponse

**Purpose**: Response payload for successful or failed image setup

**Location**: `backend/src/models.py`

```python
class ImageSetupResponse(BaseModel):
    """Response model for image-based puzzle setup."""
    
    remaining_words: List[str] = Field(
        ..., 
        description="16 words extracted from image (or empty list on error)"
    )
    status: str = Field(
        ..., 
        description="Setup status ('success' or 'error')"
    )
    message: Optional[str] = Field(
        None, 
        description="Error message if status is 'error', None if 'success'"
    )
    
    @validator('remaining_words')
    def validate_word_count_on_success(cls, v, values):
        """Ensure exactly 16 words when status is success."""
        status = values.get('status')
        if status == 'success' and len(v) != 16:
            raise ValueError(f"Success response must have 16 words, got {len(v)}")
        if status == 'error' and len(v) != 0:
            raise ValueError(f"Error response must have 0 words, got {len(v)}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status is valid value."""
        if v not in ['success', 'error']:
            raise ValueError(f"Invalid status: {v}. Must be 'success' or 'error'")
        return v
    
    @validator('message')
    def validate_message_presence(cls, v, values):
        """Ensure message present on error, absent on success."""
        status = values.get('status')
        if status == 'error' and not v:
            raise ValueError("Error response must include message")
        if status == 'success' and v:
            raise ValueError("Success response should not include message")
        return v
```

**Validation Rules**:
- `remaining_words`: Exactly 16 words for success, 0 words for error
- `status`: Must be "success" or "error"
- `message`: Required for error status, None for success status
- Words must be lowercase (enforced by session_manager, not in response model)

**Relationships**:
- Returned by `setup_puzzle_from_image` endpoint
- `remaining_words` passed to `session_manager.create_session()` on success
- Serialized to JSON for frontend consumption

**Example Success Response**:
```json
{
  "remaining_words": ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince", "raspberry"],
  "status": "success"
}
```

**Example Error Response**:
```json
{
  "remaining_words": [],
  "status": "error",
  "message": "Could not extract 16 words from image"
}
```

---

### ExtractedWords

**Purpose**: Pydantic model for LLM structured output via `with_structured_output()`

**Location**: `backend/src/models.py`

```python
class ExtractedWords(BaseModel):
    """Pydantic model for LLM structured output when extracting words from image.
    
    Used with LangChain's with_structured_output() to ensure LLM returns exactly 16 words
    in the correct format.
    """
    
    words: List[str] = Field(
        ..., 
        min_items=16, 
        max_items=16,
        description="Exactly 16 words from the 4x4 grid in left-to-right, top-to-bottom reading order"
    )
    
    @validator('words')
    def validate_word_count(cls, v):
        """Ensure exactly 16 words extracted."""
        if len(v) != 16:
            raise ValueError(f"Expected exactly 16 words, got {len(v)}")
        return v
    
    @validator('words', each_item=True)
    def normalize_words(cls, v):
        """Normalize words to lowercase and strip whitespace."""
        return v.strip().lower()
```

**Validation Rules**:
- `words`: Must contain exactly 16 strings
- Each word: Normalized to lowercase, whitespace stripped
- Order: Left-to-right, top-to-bottom (positions [0-3] row 1, [4-7] row 2, [8-11] row 3, [12-15] row 4)

**Relationships**:
- Used as schema for `llm.with_structured_output(ExtractedWords)`
- Output validated by Pydantic before returning to endpoint
- `.words` list passed to `ImageSetupResponse.remaining_words`

**LLM Prompt Context** (from research.md):
```python
prompt = f"""You are analyzing an image of a 4x4 word grid (16 words total).

TASK: Extract all 16 words in left-to-right, top-to-bottom reading order.

GRID STRUCTURE:
Row 1: positions [0, 1, 2, 3]
Row 2: positions [4, 5, 6, 7]
Row 3: positions [8, 9, 10, 11]
Row 4: positions [12, 13, 14, 15]

EXAMPLE FORMAT:
["word1", "word2", "word3", "word4", "word5", "word6", "word7", "word8", "word9", "word10", "word11", "word12", "word13", "word14", "word15", "word16"]

VALIDATION:
- You MUST return exactly 16 words
- Words should be single words (compound words like "ice cream" should be "ice-cream" or "icecream")
- Preserve capitalization as shown in image (normalization happens later)
- If unsure about spelling, make your best guess

Analyze the image and extract the 16 words now.
"""
```

---

## Frontend Types (TypeScript)

### ImageSetupRequest

**Purpose**: TypeScript interface for API request payload

**Location**: `frontend/src/types/puzzle.ts`

```typescript
/**
 * Request payload for POST /api/v2/setup_puzzle_from_image
 */
export interface ImageSetupRequest {
  /** Base64-encoded image content (without data URL prefix) */
  image_base64: string;
  
  /** Image MIME type (e.g., "image/png", "image/jpeg") */
  image_mime: string;
  
  /** LLM provider type for word extraction */
  provider_type: string;
  
  /** Specific model name for provider (e.g., "gpt-4-vision-preview") */
  model_name: string;
}
```

**Validation** (client-side before sending):
- `image_base64`: Must be valid base64 string, derived from Blob
- `image_mime`: Must match pasted image MIME type from Clipboard API
- `provider_type`: Must match user's selected provider from dropdown
- `model_name`: Must match user's selected model from dropdown

---

### ImageSetupResponse

**Purpose**: TypeScript interface for API response payload

**Location**: `frontend/src/types/puzzle.ts`

```typescript
/**
 * Response payload from POST /api/v2/setup_puzzle_from_image
 */
export interface ImageSetupResponse {
  /** 16 extracted words (empty array on error) */
  remaining_words: string[];
  
  /** Status indicator: "success" or "error" */
  status: 'success' | 'error';
  
  /** Error message (present only when status is "error") */
  message?: string;
}
```

**Usage**:
- Success: `remaining_words` passed to `onImageSetup(words)` callback
- Error: `message` displayed to user, component remains in error state for retry

---

### ImagePasteState

**Purpose**: Component internal state for image paste handling

**Location**: `frontend/src/types/puzzle.ts`

```typescript
/**
 * Internal state for ImagePuzzleSetup component tracking pasted image
 */
export interface ImagePasteState {
  /** Base64-encoded image data (for API request) */
  imageData: string | null;
  
  /** Image MIME type (e.g., "image/png") */
  imageMime: string | null;
  
  /** Object URL for preview rendering (from URL.createObjectURL) */
  previewUrl: string | null;
  
  /** Image size in bytes (original, before base64 encoding) */
  sizeBytes: number;
  
  /** Validation state (true if image meets all requirements) */
  isValid: boolean;
  
  /** Validation error message (null if valid) */
  error: string | null;
}
```

**State Transitions**:
1. **Initial**: All fields null, isValid=false
2. **Image Pasted**: imageData/imageMime/previewUrl populated, validation runs
3. **Valid Image**: isValid=true, error=null, "Setup Puzzle" button enabled
4. **Invalid Image**: isValid=false, error contains message, button disabled
5. **After Setup**: State preserved for retry (on error) or cleared (on success)

**Validation Logic**:
```typescript
function validateImage(blob: Blob): { isValid: boolean; error: string | null } {
  // Size check
  if (blob.size > 5_242_880) {  // 5MB in bytes
    return { isValid: false, error: "Image too large (max 5MB)" };
  }
  
  // MIME type check
  const supportedMimes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
  if (!supportedMimes.includes(blob.type)) {
    return { isValid: false, error: `Unsupported format: ${blob.type}` };
  }
  
  return { isValid: true, error: null };
}
```

---

### NavigationAction (Modified)

**Purpose**: Union type for navigation actions (extended for image setup)

**Location**: `frontend/src/types/navigation.ts`

```typescript
/**
 * Navigation action types for sidebar and app routing
 */
export type NavigationAction = 
  | { type: 'from-file' }
  | { type: 'from-image' }                    // NEW: Image-based setup
  | { type: 'toggle-menu'; menu: string };
```

**Usage**:
- Sidebar emits `{ type: 'from-image' }` when "From Image" clicked
- App.tsx handles action: sets `currentView = 'image-setup'`
- Main component renders `<ImagePuzzleSetup>` when view is 'image-setup'

---

## Component Props

### ImagePuzzleSetup Component

**Purpose**: Main component for image-based puzzle setup workflow

**Location**: `frontend/src/components/ImagePuzzleSetup.tsx`

```typescript
/**
 * Props for ImagePuzzleSetup component
 */
export interface ImagePuzzleSetupProps {
  /**
   * Callback invoked when puzzle setup succeeds
   * @param words - Array of 16 extracted words
   */
  onImageSetup: (words: string[]) => void;
  
  /**
   * Available LLM providers for word extraction
   * Passed from App state (same providers used for puzzle solving)
   */
  providers: LLMProviderType[];
  
  /**
   * Default provider selection (from App state)
   */
  defaultProvider: LLMProviderType;
  
  /**
   * Default model name for selected provider (from App state)
   */
  defaultModel: string;
  
  /**
   * Error callback for displaying errors in parent component
   * @param error - Error message to display
   */
  onError: (error: string) => void;
}
```

**Prop Validation**:
- `providers`: Non-empty array (at least 1 provider configured)
- `defaultProvider`: Must exist in `providers` list
- `defaultModel`: Non-empty string
- `onImageSetup`, `onError`: Functions (validated at runtime)

**Example Usage in App.tsx**:
```typescript
{currentView === 'image-setup' && (
  <ImagePuzzleSetup
    onImageSetup={handleImageSetup}
    providers={availableProviders}
    defaultProvider={selectedProvider}
    defaultModel={selectedModel}
    onError={handleError}
  />
)}
```

---

### LLMProviderType

**Purpose**: Type definition for LLM provider configuration

**Location**: `frontend/src/types/puzzle.ts` (existing type, used by ImagePuzzleSetup)

```typescript
/**
 * LLM provider configuration (existing type)
 */
export interface LLMProviderType {
  /** Provider identifier (openai, ollama, simple) */
  type: string;
  
  /** Available models for this provider */
  models: string[];
  
  /** Display name for UI */
  displayName: string;
}
```

**Usage in ImagePuzzleSetup**:
- Populate provider dropdown with `providers.map(p => p.displayName)`
- Populate model dropdown with `selectedProvider.models`
- Send `provider.type` and `selectedModel` in API request

---

## Validation Rules Summary

### Request Validation (Backend)

| Field | Required | Type | Constraints | Error Message |
|-------|----------|------|-------------|---------------|
| `image_base64` | Yes | string | Max 6.67MB encoded, non-empty | "Image size exceeds 5MB limit" |
| `image_mime` | Yes | string | Must be in [png, jpeg, jpg, gif, webp] | "Unsupported MIME type: {type}" |
| `provider_type` | Yes | string | Must be in [openai, ollama, simple] | "Unsupported provider: {type}" |
| `model_name` | Yes | string | Non-empty | "Field required" (Pydantic default) |

### Response Validation (Backend)

| Field | Success Value | Error Value | Constraints |
|-------|---------------|-------------|-------------|
| `remaining_words` | 16 words (lowercase) | Empty array [] | Must match count for status |
| `status` | "success" | "error" | Only valid values |
| `message` | None | Error description | Required for error, absent for success |

### Frontend Validation (Client-side)

| Check | Condition | Error Message |
|-------|-----------|---------------|
| Image size | blob.size <= 5MB | "Image too large (max 5MB)" |
| Image format | MIME in supported list | "Unsupported format: {mime}" |
| Image pasted | imageData !== null | "Please paste an image first" |
| Provider selected | provider !== null | "Please select a provider" |
| Model selected | model !== null | "Please select a model" |

---

## Entity Relationships

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Actions                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              ImagePuzzleSetup Component                          │
│  State: ImagePasteState                                          │
│  Props: ImagePuzzleSetupProps                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ (API call)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          POST /api/v2/setup_puzzle_from_image                    │
│  Request: ImageSetupRequest                                      │
│  Response: ImageSetupResponse                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│            ImageWordExtractor Service                            │
│  - Creates LLM provider via LLMProviderFactory                   │
│  - Constructs vision prompt                                      │
│  - Invokes llm.with_structured_output(ExtractedWords)            │
│  - Returns extracted words                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           ExtractedWords (Pydantic Model)                        │
│  - Validates exactly 16 words                                    │
│  - Normalizes to lowercase                                       │
│  - Ensures reading order                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│            session_manager.create_session(words)                 │
│  - Creates PuzzleSession with 16 words                           │
│  - Initializes game state                                        │
│  - Returns session to API endpoint                               │
└─────────────────────────────────────────────────────────────────┘
```

### Model Dependencies

```
ImageSetupRequest (API input)
  ├── Used by: setup_puzzle_from_image endpoint
  ├── Validated by: Pydantic validators
  └── Passed to: ImageWordExtractor.extract_words()

ExtractedWords (LLM output schema)
  ├── Used by: llm.with_structured_output()
  ├── Validated by: Pydantic validators
  └── Consumed by: ImageWordExtractor.extract_words()

ImageSetupResponse (API output)
  ├── Produced by: setup_puzzle_from_image endpoint
  ├── Contains: ExtractedWords.words (on success)
  └── Consumed by: ImagePuzzleSetup component

ImagePasteState (Component state)
  ├── Managed by: ImagePuzzleSetup component
  ├── Drives: UI validation feedback
  └── Feeds into: ImageSetupRequest (via API call)
```

---

## Word Normalization Rules

**Consistency Requirement**: Words from image extraction must match format of file-based puzzle words for gameplay compatibility.

### Normalization Pipeline

1. **LLM Extraction**: Words extracted in original case from image
2. **ExtractedWords Validator**: `.normalize_words()` converts to lowercase, strips whitespace
3. **Session Manager**: `PuzzleSession.__init__()` normalizes all words to lowercase (existing behavior)
4. **Gameplay**: All word comparisons case-insensitive (existing behavior)

### Example Transformations

| Image Text | LLM Output | After ExtractedWords | After Session Manager |
|------------|------------|---------------------|----------------------|
| "APPLE" | "APPLE" | "apple" | "apple" |
| "Banana " | "Banana " | "banana" | "banana" |
| "  Cherry" | "  Cherry" | "cherry" | "cherry" |
| "ice-cream" | "ice-cream" | "ice-cream" | "ice-cream" |

**Key Insight**: Existing `PuzzleSession` already handles lowercase normalization, so image-extracted words integrate seamlessly with no session management changes required.

---

## Error Response Catalog

### HTTP Status Codes

| Status | Scenario | Response Body |
|--------|----------|---------------|
| 200 OK | Successful extraction | `{ remaining_words: [...16 words], status: "success" }` |
| 400 Bad Request | Wrong word count | `{ remaining_words: [], status: "error", message: "Could not extract 16 words from image" }` |
| 400 Bad Request | Model no vision | `{ remaining_words: [], status: "error", message: "Selected model does not support image analysis" }` |
| 400 Bad Request | Invalid MIME type | `{ remaining_words: [], status: "error", message: "Unsupported MIME type: {type}" }` |
| 413 Payload Too Large | Image >5MB | `{ remaining_words: [], status: "error", message: "Image size exceeds 5MB limit" }` |
| 422 Unprocessable Entity | Missing fields | `{ remaining_words: [], status: "error", message: "Field required: {field}" }` |
| 500 Internal Server Error | LLM provider failure | `{ remaining_words: [], status: "error", message: "LLM provider error - please retry" }` |

### Frontend Error Messages (User-Facing)

| Backend Error | User Message | Retry Action |
|---------------|--------------|--------------|
| "Could not extract 16 words from image" | "Unable to detect 16 words. Please try a clearer image." | Allow image repaste |
| "Selected model does not support image analysis" | "This model doesn't support image analysis. Try a different model." | Keep image, change model |
| "Unsupported MIME type" | "Unsupported image format. Use PNG, JPEG, or GIF." | Allow image repaste |
| "Image size exceeds 5MB limit" | "Image too large (max 5MB). Please resize and try again." | Allow image repaste |
| "LLM provider error" | "LLM service error. Please try again." | Keep image, retry request |

---

## Performance Considerations

### Image Size Limits

**5MB Limit Rationale**:
- Balance between quality and performance
- Base64 encoding adds ~33% overhead (5MB → ~6.67MB in transit)
- Average screenshot of 4x4 grid: 100-500KB (well under limit)
- High-resolution screenshots: 1-3MB (acceptable)

### Base64 Encoding Performance

**Client-side encoding** (from research.md):
```typescript
// Encoding happens in ImagePuzzleSetup component
async function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const dataUrl = reader.result as string;
      const base64 = dataUrl.split(',')[1];  // Remove "data:image/png;base64," prefix
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}
```

**Performance target**: <2 seconds from paste to preview (SC-002)

### LLM Extraction Timeout

**Backend timeout**: 10 seconds (from research.md)
- OpenAI GPT-4 Vision: Typically 2-5 seconds
- Ollama vision models: Variable (3-15 seconds depending on model size)
- Timeout triggers HTTP 500 with "LLM provider error" message

---

## Testing Data Fixtures

### Valid Test Image (Conceptual)

```
┌─────────────────────────────────────┐
│  APPLE    BANANA   CHERRY   DATE    │
│  ELDER    FIG      GRAPE    HONEY   │
│  KIWI     LEMON    MANGO    NECTAR  │
│  ORANGE   PAPAYA   QUINCE   RASP    │
└─────────────────────────────────────┘
```

**Expected ExtractedWords**:
```python
ExtractedWords(
  words=["apple", "banana", "cherry", "date", "elder", "fig", "grape", "honey",
         "kiwi", "lemon", "mango", "nectar", "orange", "papaya", "quince", "rasp"]
)
```

### Invalid Test Cases

| Test Case | Image Content | Expected Error |
|-----------|---------------|----------------|
| Wrong count (12 words) | 3x4 grid | "Could not extract 16 words from image" |
| Wrong count (20 words) | 5x4 grid | "Could not extract 16 words from image" |
| Oversized image | 8MB file | "Image size exceeds 5MB limit" |
| Wrong format | .bmp file | "Unsupported MIME type: image/bmp" |
| No words | Blank image | "Could not extract 16 words from image" |

---

## Configuration Requirements

### Environment Variables (Backend)

```bash
# Required for OpenAI vision models
OPENAI_API_KEY=sk-...

# Optional for Ollama vision models (if using remote Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

### Frontend Environment

```bash
# No new environment variables required
# Uses existing REACT_APP_API_URL for backend API calls
```

### LLM Model Requirements

| Provider | Vision-Capable Models | Configuration |
|----------|----------------------|---------------|
| OpenAI | gpt-4-vision-preview, gpt-4-turbo | API key required |
| Ollama | llava, bakllava, llava-llama3 | Local Ollama + model pulled |
| Simple | N/A | Does not support vision |

---

## Next Steps

1. ✅ **data-model.md created** - This document
2. ⏳ **Create contracts/api.ts** - TypeScript API interface
3. ⏳ **Create contracts/components.ts** - Component prop interfaces
4. ⏳ **Create quickstart.md** - Developer setup and testing guide
5. ⏳ **Update agent context** - Run `update-agent-context.sh copilot`

---

**Phase 1 Status**: ✅ DATA MODEL COMPLETE
**Last Updated**: December 13, 2025
