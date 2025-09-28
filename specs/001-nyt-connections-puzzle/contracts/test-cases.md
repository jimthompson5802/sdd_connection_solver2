# Contract Tests: NYT Connections Puzzle Assistant API

## Test: POST /api/puzzle/setup_puzzle

### Test Case: Valid CSV Setup
**Given**: Valid CSV with 16 words in single row  
**When**: POST to /api/puzzle/setup_puzzle with file_content  
**Then**: 
- Response status 200
- Response contains remaining_words array with 16 items
- Response status field equals "success"
- All words are unique strings

### Test Case: Invalid CSV Format
**Given**: CSV with wrong format (multiple rows, <16 words, etc.)  
**When**: POST to /api/puzzle/setup_puzzle with invalid file_content  
**Then**: 
- Response status 400
- Response status field contains error message
- No puzzle state initialized

### Test Case: Empty CSV Content
**Given**: Empty or whitespace-only file_content  
**When**: POST to /api/puzzle/setup_puzzle  
**Then**: 
- Response status 400
- Response status field: "Display error message and prevent setup"

## Test: GET /api/puzzle/next_recommendation

### Test Case: Valid Recommendation Request
**Given**: Puzzle initialized with 16 words  
**When**: GET /api/puzzle/next_recommendation  
**Then**: 
- Response status 200
- Response contains words array with exactly 4 items
- Response contains connection string (non-empty)
- Response status field equals "success"
- Words are from remaining_words list

### Test Case: Insufficient Words Remaining
**Given**: Puzzle state with fewer than 4 remaining words  
**When**: GET /api/puzzle/next_recommendation  
**Then**: 
- Response status 400
- Response status field: "Not enough words remaining"

### Test Case: No Puzzle Initialized
**Given**: No active puzzle state  
**When**: GET /api/puzzle/next_recommendation  
**Then**: 
- Response status 400
- Response contains appropriate error message

## Test: POST /api/puzzle/record_response

### Test Case: Correct Response with Color
**Given**: Active recommendation exists  
**When**: POST to /api/puzzle/record_response with response_type="correct" and color="Yellow"  
**Then**: 
- Response status 200
- remaining_words reduced by 4 items
- correct_count incremented by 1
- game_status appropriate ("active" or "won")

### Test Case: Incorrect Response
**Given**: Active recommendation exists  
**When**: POST to /api/puzzle/record_response with response_type="incorrect"  
**Then**: 
- Response status 200
- remaining_words unchanged
- mistake_count incremented by 1
- game_status appropriate ("active" or "lost")

### Test Case: One-Away Response
**Given**: Active recommendation exists  
**When**: POST to /api/puzzle/record_response with response_type="one-away"  
**Then**: 
- Response status 200
- remaining_words unchanged
- mistake_count incremented by 1
- game_status appropriate ("active" or "lost")

### Test Case: No Active Recommendation
**Given**: No current recommendation displayed  
**When**: POST to /api/puzzle/record_response with any response_type  
**Then**: 
- Response status 400
- Response status field: "No recommendation to respond to"

### Test Case: Missing Color for Correct Response
**Given**: Active recommendation exists  
**When**: POST to /api/puzzle/record_response with response_type="correct" but no color  
**Then**: 
- Response status 400
- Response contains validation error

### Test Case: Game Already Won
**Given**: Puzzle with 4 correct groups (game_status="won")  
**When**: POST to /api/puzzle/record_response  
**Then**: 
- Response status 400
- Response indicates game already completed

### Test Case: Game Already Lost
**Given**: Puzzle with 4 mistakes (game_status="lost")  
**When**: POST to /api/puzzle/record_response  
**Then**: 
- Response status 400
- Response indicates game already completed

## Schema Validation Tests

### Pydantic Model Validation
- WordGroup: Exactly 4 unique words, non-empty connection
- PuzzleState: Counts match array lengths, total words equal 16
- IncorrectGroup: Valid mistake_type enum value
- Request models: Required fields present and valid types
- Response models: All fields match OpenAPI schema

### Type Safety Tests
- All string fields reject null/undefined values
- Integer fields reject non-numeric values  
- Array fields reject non-array values
- Enum fields reject invalid values
- Required fields reject missing values