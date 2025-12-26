# Data Model: Game History and Persistent Storage

**Feature**: Game History and Persistent Storage
**Branch**: `005-game-history`
**Date**: 2025-12-24

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for the game history feature. The model extends the existing `PuzzleSession` entity and introduces a new `GameResult` entity for persistent storage.

## Entity Definitions

### GameResult (NEW)

**Purpose**: Represents a single completed and recorded puzzle game with performance metrics and metadata.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| result_id | INTEGER | PRIMARY KEY, AUTOINCREMENT, NOT NULL | Unique identifier for each recorded game |
| puzzle_id | TEXT(36) | NOT NULL | UUID v5 of sorted, normalized puzzle words (deterministic identifier) |
| game_date | TEXT | NOT NULL | ISO 8601 timestamp with timezone, canonicalized to UTC (e.g., "2025-12-24T15:30:00+00:00") |
| puzzle_solved | TEXT | NOT NULL | Whether the puzzle was successfully completed. Stored as literal string "true" or "false" (Phase 5 pattern) |
| count_groups_found | INTEGER | NOT NULL, CHECK(count_groups_found >= 0 AND count_groups_found <= 4) | Number of groups correctly identified (0-4) |
| count_mistakes | INTEGER | NOT NULL, CHECK(count_mistakes >= 0 AND count_mistakes <= 4) | Number of incorrect attempts made (0-4) |
| total_guesses | INTEGER | NOT NULL, CHECK(total_guesses > 0) | Total number of guesses made (must be at least 1) |
| llm_provider_name | TEXT | NULLABLE | Name of LLM provider used for recommendations (e.g., "openai", "ollama", "simple") |
| llm_model_name | TEXT | NULLABLE | Specific model name used (e.g., "gpt-4", "llama2") |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Server timestamp when record was created (ISO 8601 UTC) |

**Indexes**:
- `PRIMARY KEY (result_id)`: Auto-created with primary key
- `UNIQUE INDEX idx_unique_puzzle_date ON (puzzle_id, game_date)`: Enforces uniqueness constraint
- `INDEX idx_game_date_desc ON game_date DESC`: Optimizes retrieval ordering

**Validation Rules**:
1. **Uniqueness**: (puzzle_id, game_date) tuple must be unique across all records
2. **Completeness**: Only completed games (session.is_finished == true) can be recorded
3. **Range constraints**:
   - count_groups_found: 0-4
   - count_mistakes: 0-4
   - total_guesses: minimum 1
4. **Timestamp format**: game_date must be valid ISO 8601 with timezone
5. **Derived consistency**: If puzzle_solved == true, then count_groups_found must equal 4
6. **LLM nullability**: llm_provider_name and llm_model_name can be null if no recommendation was used

**State Invariants**:
- `puzzle_solved == true` ⟹ `count_groups_found == 4`
- `count_groups_found + count_mistakes <= total_guesses` (some guesses may be "one away")
- `count_mistakes <= 4` (game ends at 4 mistakes if not won)

### PuzzleSession (ENHANCED)

**Purpose**: Manages the state of a single puzzle-solving session. Enhanced to track puzzle identity and LLM usage for recording purposes.

**New Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| puzzle_id | str | NOT NULL, computed | UUID v5 of sorted, normalized puzzle words. Generated in __init__ |
| llm_provider_name | Optional[str] | NULLABLE | LLM provider name, set when recommendation is generated |
| llm_model_name | Optional[str] | NULLABLE | LLM model name, set when recommendation is generated |

**Existing Attributes** (unchanged):
- session_id: str (UUID4)
- words: List[str] (16 words, normalized to lowercase)
- groups: List[WordGroup]
- attempts: List[UserAttempt]
- created_at: datetime
- mistakes_made: int
- max_mistakes: int (4)
- game_complete: bool
- game_won: bool
- last_recommendation: Optional[List[str]]

**Computed Properties** (NEW):
```python
@property
def is_finished(self) -> bool:
    """Returns True if game is complete (won or lost)."""
    return self.game_complete

@property
def groups_found_count(self) -> int:
    """Returns count of groups marked as found."""
    return sum(1 for group in self.groups if group.found)

@property
def total_guesses_count(self) -> int:
    """Returns total number of attempts made."""
    return len(self.attempts)
```

**Methods Enhanced**:
- `__init__(words: List[str])`: Now generates puzzle_id via UUID v5
- `record_attempt(...)`: Existing logic unchanged, continues to update game_complete/game_won

**New Methods**:
```python
def generate_puzzle_id(self) -> str:
    """Generate deterministic puzzle_id from normalized, sorted words."""
    import uuid
    normalized = [word.strip().lower() for word in self.words]
    sorted_words = sorted(normalized)
    joined = ",".join(sorted_words)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, joined))

def set_llm_info(self, provider_name: str, model_name: str) -> None:
    """Record LLM provider and model used for recommendation."""
    self.llm_provider_name = provider_name
    self.llm_model_name = model_name

def to_game_result(self, game_date: datetime) -> Dict[str, Any]:
    """Convert session state to GameResult data for recording."""
    return {
        "puzzle_id": self.puzzle_id,
        "game_date": game_date.astimezone(timezone.utc).isoformat(),
        "puzzle_solved": "true" if self.game_won else "false",  # Store as TEXT per Phase 5 pattern
        "count_groups_found": self.groups_found_count,
        "count_mistakes": self.mistakes_made,
        "total_guesses": self.total_guesses_count,
        "llm_provider_name": self.llm_provider_name,
        "llm_model_name": self.llm_model_name,
    }
```

## Entity Relationships

```
┌─────────────────┐         generates         ┌──────────────┐
│  PuzzleSession  │────────────────────────────▶│  GameResult  │
│  (in-memory)    │         0..1               │ (persistent) │
└─────────────────┘                            └──────────────┘
       │                                              │
       │ has many                                     │ indexed by
       ▼                                              ▼
┌─────────────────┐                          ┌──────────────┐
│   UserAttempt   │                          │  puzzle_id   │
│   WordGroup     │                          │  game_date   │
└─────────────────┘                          └──────────────┘
```

**Relationship Rules**:
1. One `PuzzleSession` can generate **zero or one** `GameResult`
   - Zero: If user doesn't click "Record Game"
   - One: If user records the completed game
2. One `puzzle_id` can have **multiple** `GameResult` records (different dates)
3. One (puzzle_id, game_date) tuple maps to **exactly one** `GameResult` (uniqueness constraint)
4. `GameResult` is immutable once created (no updates, only inserts and deletes)

## State Transitions

### PuzzleSession Lifecycle

```
┌──────────────┐
│   Created    │  __init__(words)
│ puzzle_id    │  - Generate puzzle_id
│ set          │  - Initialize empty attempts/groups
└──────┬───────┘
       │
       │ User makes guesses
       │ record_attempt() called
       ▼
┌──────────────┐
│   In Play    │  Recommendation may be requested
│ llm_provider │  - set_llm_info() called
│ may be set   │  - last_recommendation updated
└──────┬───────┘
       │
       │ 4 groups found OR 4 mistakes made
       │ _check_game_completion() sets game_complete=True
       ▼
┌──────────────┐
│  Completed   │  is_finished == True
│ game_won set │  - User sees GameSummary
└──────┬───────┘
       │
       │ User clicks "Record Game"
       │ POST /api/v2/game_results with session_id
       ▼
┌──────────────┐
│   Recorded   │  GameResult persisted
│ (optional)   │  - Session remains in memory
└──────────────┘  - Can be recorded only once per date
```

### GameResult Creation Flow

```
POST /api/v2/game_results
    │
    ├─▶ Validate request (session_id, game_date present)
    │
    ├─▶ Fetch PuzzleSession from SessionManager
    │     └─▶ HTTP 404 if session_id not found
    │
    ├─▶ Validate session.is_finished == True
    │     └─▶ HTTP 400 if not finished
    │
    ├─▶ Generate GameResult data via session.to_game_result()
    │
    ├─▶ Check uniqueness (puzzle_id, game_date)
    │     └─▶ HTTP 409 if duplicate exists
    │
    ├─▶ Insert into database
    │     └─▶ HTTP 500 if database error
    │
    └─▶ Return HTTP 201 with GameResult
```

## Database Schema (SQLite)

```sql
-- Game Results Table
CREATE TABLE IF NOT EXISTS game_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    puzzle_id TEXT NOT NULL,
    game_date TEXT NOT NULL,
    puzzle_solved TEXT NOT NULL,  -- Store as "true" or "false" (Phase 5 pattern)
    count_groups_found INTEGER NOT NULL CHECK(count_groups_found >= 0 AND count_groups_found <= 4),
    count_mistakes INTEGER NOT NULL CHECK(count_mistakes >= 0 AND count_mistakes <= 4),
    total_guesses INTEGER NOT NULL CHECK(total_guesses > 0),
    llm_provider_name TEXT,
    llm_model_name TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Enforce uniqueness on (puzzle_id, game_date)
CREATE UNIQUE INDEX idx_unique_puzzle_date ON game_results(puzzle_id, game_date);

-- Optimize retrieval ordering
CREATE INDEX idx_game_date_desc ON game_results(game_date DESC);
```

## Pydantic Models (Backend API)

### Request Models

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class RecordGameRequest(BaseModel):
    """Request to record a completed game."""
    session_id: str = Field(..., description="UUID of the completed puzzle session")
    game_date: datetime = Field(..., description="ISO 8601 timestamp with timezone")

    @field_validator('game_date')
    @classmethod
    def validate_timezone(cls, v: datetime) -> datetime:
        """Ensure game_date has timezone information."""
        if v.tzinfo is None:
            raise ValueError("game_date must include timezone information")
        return v
```

### Response Models

```python
class GameResultResponse(BaseModel):
    """Response for a single game result."""
    result_id: int
    puzzle_id: str
    game_date: str  # ISO 8601 string
    puzzle_solved: bool
    count_groups_found: int = Field(..., ge=0, le=4)
    count_mistakes: int = Field(..., ge=0, le=4)
    total_guesses: int = Field(..., ge=1)
    llm_provider_name: Optional[str] = None
    llm_model_name: Optional[str] = None
    created_at: str  # ISO 8601 string

    class Config:
        from_attributes = True  # Allow ORM mode for SQLite row conversion

class RecordGameResponse(BaseModel):
    """Response after successfully recording a game."""
class RecordGameResponse(BaseModel):
    """Response after successfully recording a game."""
    status: str = "created"
    result: GameResultResponse

class GameHistoryResponse(BaseModel):
    """Response for game history list."""
    status: str = "ok"
    results: list[GameResultResponse]
```

## TypeScript Interfaces (Frontend)

```typescript
// types/gameResults.ts

export interface GameResult {
  result_id: number;
  puzzle_id: string;
  game_date: string; // ISO 8601 string
  puzzle_solved: boolean; // Converted from TEXT "true"/"false"
  count_groups_found: number; // 0-4
  count_mistakes: number; // 0-4
  total_guesses: number; // minimum 1
  llm_provider_name: string | null;
  llm_model_name: string | null;
}

export interface RecordGameRequest {
  session_id: string;
  game_date: string; // ISO 8601 string
}

export interface RecordGameResponse {
  status: string; // "created"
  result: GameResult;
}

export interface GameHistoryResponse {
  status: string; // "ok"
  results: GameResult[];
}

export interface RecordGameError {
  detail?: string;
  status?: string;
  code?: string;
  message?: string;
}
```

## Validation Summary

### Server-Side Validation (Enforced)

1. **Session existence**: session_id must reference existing session in SessionManager
2. **Session completion**: session.is_finished must be true
3. **Timestamp format**: game_date must be valid ISO 8601 with timezone
4. **Uniqueness**: (puzzle_id, game_date) must be unique in database
5. **Range constraints**: Database CHECK constraints on count fields
6. **Data consistency**: Derived fields match session state

### Client-Side Validation (User Experience)

1. **Button state**: "Record Game" button only enabled when game is complete
2. **Loading state**: Button disabled during POST request
3. **Error display**: Show specific error messages based on HTTP status
4. **Duplicate prevention**: Optionally track recorded games in session storage

## Migration and Versioning

**Initial Schema Version**: v1.0

**Migration Strategy**:
- Schema creation script: `backend/src/database/schema.sql`
- On first run, create tables and indexes if not exist
- Future migrations tracked via `schema_version` table (if needed)

**Backward Compatibility**:
- GameResult records are immutable (no schema updates to existing data)
- Adding new nullable columns is safe (won't break existing records)
- Index changes don't affect data integrity

## CSV Export Format

**Column Order** (as specified in constitution appendix):
```
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name
```

**Sample CSV**:
```csv
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name
1,abc123def456...,2025-12-24T15:30:00+00:00,true,4,1,7,openai,gpt-4
2,fed654cba321...,2025-12-23T11:05:00+00:00,false,3,4,8,ollama,llama2
```

**Format Notes**:
- Boolean values exported as lowercase strings: "true"/"false"
- Null values exported as empty strings
- Timestamps remain in ISO 8601 UTC format
- All text fields use standard CSV escaping (quotes for commas/newlines)

## Summary

The data model provides:
- ✅ Clear entity definitions with comprehensive validation
- ✅ Deterministic puzzle_id generation for uniqueness (UUID v5)
- ✅ Proper temporal handling (ISO 8601 UTC)
- ✅ Strong type safety (Pydantic + TypeScript)
- ✅ Database integrity via constraints and indexes
- ✅ Immutable records for audit trail
- ✅ Efficient querying for retrieval and export

All design decisions align with constitution requirements and research findings.
