# Data Model: NYT Connections Puzzle Assistant

## Core Entities

### PuzzleState
**Purpose**: Maintains the complete state of an active puzzle session
**Fields**:
- `remaining_words: List[str]` - Words still available for grouping (0-16 items)
- `correct_groups: List[WordGroup]` - Successfully identified groups
- `incorrect_groups: List[IncorrectGroup]` - Failed attempts with mistake indicators  
- `correct_count: int` - Count of correct groups (0-4)
- `mistake_count: int` - Count of incorrect attempts (0-4)
- `current_recommendation: Optional[WordGroup]` - Active recommendation awaiting response

**Validation Rules**:
- `remaining_words` must contain 0-16 unique strings
- `correct_count` equals length of `correct_groups` (max 4)
- `mistake_count` equals length of `incorrect_groups` (max 4)
- Total words across all groups + remaining equals 16

**State Transitions**:
- Initialize: 16 words in `remaining_words`, all counters zero
- Correct guess: Move 4 words from remaining to correct_groups, increment correct_count
- Incorrect guess: Add group to incorrect_groups, increment mistake_count
- Game end: Either correct_count=4 (success) or mistake_count=4 (failure)

### WordGroup
**Purpose**: Represents a group of 4 related words with connection rationale
**Fields**:
- `words: List[str]` - Exactly 4 words in the group
- `connection: str` - Rationale explaining the relationship
- `color: Optional[str]` - Color assignment (Yellow/Green/Blue/Purple) if correct

**Validation Rules**:
- `words` must contain exactly 4 unique strings
- `connection` must be non-empty string
- `color` only set for correct groups

### IncorrectGroup
**Purpose**: Extends WordGroup with mistake classification
**Fields**:
- Inherits all WordGroup fields
- `mistake_type: str` - Either "incorrect" or "one-away"

**Validation Rules**:
- `mistake_type` must be either "incorrect" or "one-away"
- `color` field always None for incorrect groups

## Request/Response Models

### SetupPuzzleRequest
**Purpose**: Initialize puzzle from uploaded CSV file
**Fields**:
- `file_content: str` - CSV content with 16 words in single row

**Validation Rules**:
- Must parse to exactly 16 unique words
- Words must be non-empty strings

### SetupPuzzleResponse
**Purpose**: Confirm puzzle initialization
**Fields**:
- `remaining_words: List[str]` - The 16 words loaded
- `status: str` - "success" or error message

### RecommendationRequest
**Purpose**: Request next word group recommendation
**Fields**:
- (No fields - uses current puzzle state)

### RecommendationResponse
**Purpose**: Provide word group suggestion
**Fields**:
- `words: List[str]` - 4 recommended words
- `connection: str` - Rationale for grouping
- `status: str` - "success" or error message

### GroupResponseRequest
**Purpose**: Record user's response to recommendation
**Fields**:
- `response_type: str` - "correct", "incorrect", or "one-away"
- `color: Optional[str]` - Color if correct (Yellow/Green/Blue/Purple)

### GroupResponseResponse
**Purpose**: Confirm response and provide updated state
**Fields**:
- `remaining_words: List[str]` - Updated remaining words
- `correct_count: int` - Updated correct groups count
- `mistake_count: int` - Updated mistake count
- `game_status: str` - "active", "won", or "lost"

## Data Flow

1. **Setup Phase**: CSV → SetupPuzzleRequest → PuzzleState initialization
2. **Recommendation Phase**: PuzzleState → RecommendationResponse (first 4 words)
3. **Response Phase**: GroupResponseRequest → PuzzleState update → GroupResponseResponse
4. **Repeat**: Steps 2-3 until game_status ≠ "active"

## Error States

- Invalid CSV: Return error in SetupPuzzleResponse
- Insufficient words: Return error in RecommendationResponse  
- No active recommendation: Return error in GroupResponseResponse
- Game already ended: Prevent further recommendations/responses