# Data Model: LLM Provider Integration

## Core Entities

### LLMProvider
Represents an external AI service configuration for generating word recommendations.

**Fields**:
- `provider_type`: string - The LLM service provider ("ollama", "openai", "simple")
- `model_name`: string | null - The specific model identifier (e.g., "llama2", "gpt-3.5-turbo", null for simple)
- `is_available`: boolean - Whether the provider is currently accessible
- `requires_auth`: boolean - Whether the provider needs authentication

**Validation Rules**:
- `provider_type` must be one of: "simple", "ollama", "openai"
- `model_name` is required when `provider_type` is not "simple"
- `model_name` must be null when `provider_type` is "simple"
- Format validation: when not "simple", must match pattern "{provider}:{model}"

**Relationships**:
- Used by RecommendationRequest to specify which provider to use
- Referenced in RecommendationResponse for tracking which provider generated the response

### RecommendationRequest
Contains all context needed to generate a word recommendation from any provider.

**Fields**:
- `llm_provider`: LLMProvider - The selected provider configuration
- `remaining_words`: list[string] - Words still available in the puzzle
- `previous_guesses`: list[GuessAttempt] - Historical guess attempts with outcomes
- `puzzle_context`: string | null - Optional additional context about the puzzle

**Validation Rules**:
- `remaining_words` must contain at least 1 word
- `remaining_words` must contain exactly unique strings
- `previous_guesses` can be empty list but not null
- All words in `previous_guesses` must not appear in `remaining_words`

**Relationships**:
- Contains LLMProvider configuration
- Contains list of GuessAttempt entities
- Generates RecommendationResponse

### RecommendationResponse
The result from any provider (simple algorithm or LLM) containing word recommendations.

**Fields**:
- `recommended_words`: list[string] - Exactly 4 words recommended for grouping
- `connection_explanation`: string | null - Why these words are connected (null for simple provider)
- `confidence_score`: float | null - Provider's confidence in recommendation (0.0-1.0, null for simple)
- `provider_used`: LLMProvider - Which provider generated this response
- `generation_time_ms`: int | null - Time taken to generate (null for simple)

**Validation Rules**:
- `recommended_words` must contain exactly 4 unique strings
- All `recommended_words` must be from the original `remaining_words` in request
- `confidence_score` must be between 0.0 and 1.0 when not null
- `connection_explanation` required for LLM providers, null for simple provider
- `generation_time_ms` must be positive when not null

**Relationships**:
- References the LLMProvider that generated it
- Words must be subset of RecommendationRequest.remaining_words

### GuessAttempt
Tracks a previous user guess and its outcome for context in future recommendations.

**Fields**:
- `words`: list[string] - The 4 words that were guessed together
- `outcome`: string - Result of the guess ("correct", "incorrect", "one_away")
- `actual_connection`: string | null - The real connection if correct, null otherwise
- `timestamp`: datetime - When the guess was made

**Validation Rules**:
- `words` must contain exactly 4 unique strings
- `outcome` must be one of: "correct", "incorrect", "one_away"
- `actual_connection` required when outcome is "correct", null otherwise
- `timestamp` must be valid datetime

**Relationships**:
- Part of RecommendationRequest for context
- Used to ensure no repeat guesses in new recommendations

### PuzzleState
Tracks the current state of an active puzzle session.

**Fields**:
- `all_words`: list[string] - All 16 words in the puzzle
- `remaining_words`: list[string] - Words not yet correctly grouped
- `completed_groups`: list[CompletedGroup] - Successfully found connections
- `failed_attempts`: list[GuessAttempt] - Unsuccessful guess attempts
- `current_provider`: LLMProvider - Currently selected provider configuration

**Validation Rules**:
- `all_words` must contain exactly 16 unique strings
- `remaining_words` must be subset of `all_words`
- Sum of words in `completed_groups` + `remaining_words` must equal `all_words`
- All `failed_attempts` must have outcome "incorrect" or "one_away"

**Relationships**:
- Contains GuessAttempt entities
- Contains CompletedGroup entities
- References current LLMProvider
- Source of data for RecommendationRequest

### CompletedGroup
Represents a successfully identified group of 4 connected words.

**Fields**:
- `words`: list[string] - The 4 connected words
- `connection`: string - The specific connection between the words
- `difficulty_level`: string - Color/difficulty ("yellow", "green", "blue", "purple")
- `solved_timestamp`: datetime - When this group was completed

**Validation Rules**:
- `words` must contain exactly 4 unique strings
- `difficulty_level` must be one of: "yellow", "green", "blue", "purple"
- `connection` must be non-empty string
- `solved_timestamp` must be valid datetime

**Relationships**:
- Part of PuzzleState
- Words cannot overlap with other CompletedGroup entities in same puzzle

## State Transitions

### Provider Selection Flow
```
Initial State: current_provider = LLMProvider(provider_type="simple", model_name=null)
↓
User Input: "ollama:llama2"
↓ 
Validation: Parse and validate format
↓
Valid: current_provider = LLMProvider(provider_type="ollama", model_name="llama2")
Invalid: Display error, maintain current_provider
```

### Recommendation Generation Flow
```
RecommendationRequest Created
↓
Provider Type Check:
├─ "simple" → Use Phase 1 algorithm (first 4 remaining words)
├─ "ollama" → Generate LLM prompt → Call ollama API
└─ "openai" → Generate LLM prompt → Call openai API
↓
Response Validation:
├─ Valid (4 words from remaining) → Return RecommendationResponse
└─ Invalid → Return error response
```

### Guess Processing Flow
```
User Submits 4 Words
↓
Validate against remaining_words
↓
Check Result (external validation)
↓
Create GuessAttempt:
├─ outcome="correct" → Move to CompletedGroup, remove from remaining_words
├─ outcome="one_away" → Add to failed_attempts
└─ outcome="incorrect" → Add to failed_attempts
↓
Update PuzzleState
```

## Data Validation Patterns

### Input Sanitization
- All string inputs trimmed and lowercased for consistency
- Word lists validated for uniqueness
- Provider strings validated against allowed patterns
- Numerical inputs bounded and type-checked

### Business Logic Validation
- Ensure no word appears in multiple contexts simultaneously
- Validate recommendation words exist in remaining words
- Check that guess attempts don't repeat previous guesses
- Verify puzzle state consistency (16 words total, no overlaps)

### Response Validation
- LLM responses parsed and validated before use
- Fallback to error state for malformed responses
- Timeout handling (indefinite loading per clarifications)
- Provider availability checking before requests

## Error States

### Provider Configuration Errors
- Invalid provider format → Clear error message with examples
- Unavailable provider → User-friendly connectivity message
- Missing credentials → Configuration guidance message

### Recommendation Errors
- Invalid LLM response → Request user to try again
- Provider timeout → Persistent loading (per clarifications)
- Empty remaining words → End game state

### Validation Errors
- Duplicate guess attempt → Warning with historical context
- Invalid word selection → Clear validation message
- Malformed input → Specific format guidance