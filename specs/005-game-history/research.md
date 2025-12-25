# Research: Game History and Persistent Storage

**Feature**: Game History and Persistent Storage
**Branch**: `005-game-history`
**Date**: 2025-12-24

## Overview

This document captures research findings that inform the technical design of the game history feature. All NEEDS CLARIFICATION items from the Technical Context have been resolved through analysis of project constitution, existing codebase patterns, and best practices.

## Research Areas

### 1. Database Choice for Local Persistence

**Decision**: SQLite via Python `sqlite3` standard library

**Rationale**:
- Constitution v2.2.0 explicitly permits SQLite for local single-user persistence
- No external dependencies required (sqlite3 is part of Python standard library)
- Perfect fit for local-first, single-user desktop application
- Lightweight, zero-configuration, file-based storage
- Excellent support for ACID transactions and concurrent reads
- Well-tested integration patterns with FastAPI

**Alternatives Considered**:
- **PostgreSQL**: Rejected - overkill for single-user local application, requires external service
- **JSON files**: Rejected - no query capabilities, no ACID guarantees, poor concurrent access
- **In-memory only**: Rejected - spec explicitly requires persistent storage across sessions
- **Embedded NoSQL (e.g., TinyDB)**: Rejected - adds dependency, SQLite is more mature and performant

**Implementation Notes**:
- Database file location: `backend/data/connect_puzzle_game.db` (or configurable via environment variable)
- Use connection pooling for FastAPI (connection per request via dependency injection)
- Enable WAL mode for better concurrent access: `PRAGMA journal_mode=WAL`
- Foreign key constraints enabled: `PRAGMA foreign_keys=ON`

### 2. Timestamp Handling and ISO 8601 Canonicalization

**Decision**: Store timestamps as TEXT in ISO 8601 UTC format with timezone (e.g., "2025-12-24T15:30:00+00:00")

**Rationale**:
- Constitution explicitly requires ISO 8601 format with timezone, canonicalized to UTC
- SQLite doesn't have native datetime type with timezone support
- TEXT storage with ISO 8601 ensures portability and human readability
- Python's `datetime.isoformat()` and `datetime.fromisoformat()` handle parsing/formatting
- Sorting works correctly lexicographically due to ISO 8601 format

**Alternatives Considered**:
- **Unix timestamp (INTEGER)**: Rejected - loses timezone information, less human-readable
- **Local datetime without timezone**: Rejected - violates constitution requirement
- **DATETIME type in SQLite**: Rejected - doesn't support timezone, would require conversion

**Implementation Notes**:
- Backend always converts client timestamps to UTC before storage: `dt.astimezone(timezone.utc)`
- Schema uses TEXT type for `game_date` column with ISO 8601 format (e.g., "2025-12-24T15:30:00Z" or with offset)
- Validation ensures incoming timestamps are valid ISO 8601 with timezone
- CSV export maintains ISO 8601 format for consistency (may preserve original timezone or normalize to UTC)

### 3. Boolean Storage and Normalization

**Decision**: Store booleans as TEXT with literal strings "true"/"false" in SQLite

**Rationale**:
- Maintains consistency with existing Phase 5 implementation (phase5_implementation_notes.md specifies this pattern)
- SQLite lacks native boolean type, Phase 5 established TEXT storage convention
- Constitution v2.2.0 explicitly notes Phase 5 used string literals "true"/"false" and requires normalization
- Application layer must convert between Python bool and SQLite TEXT strings
- Compatibility with existing data and export formats

**Alternatives Considered**:
- **INTEGER (0/1)**: Rejected - would break compatibility with existing Phase 5 data and patterns
- **Native BOOLEAN (SQLite affinity)**: Rejected - not explicit enough, Phase 5 pattern is normative

**Implementation Notes**:
- Schema defines `puzzle_solved TEXT NOT NULL` with literal strings "true" or "false"
- Python layer converts: `"true" if session.game_won else "false"` when writing
- Python layer converts: `row["puzzle_solved"] == "true"` when reading
- CSV export outputs boolean as "true"/"false" strings for consistency
- Pydantic models handle string-to-bool conversion in API layer

### 4. Puzzle ID Generation (UUID v5)

**Decision**: Use `uuid.uuid5()` to generate deterministic puzzle_id from sorted, normalized words

**Rationale**:
- Spec provides explicit algorithm: normalize (trim, lowercase), sort lexicographically, join with commas, generate UUID v5
- UUID v5 uses SHA-1 internally and provides 128-bit UUID (negligible collision probability for puzzle uniqueness)
- Deterministic: same 16 words always produce same puzzle_id
- Standard UUID format ensures compatibility and follows RFC 4122
- Fast computation, standard library support

**Alternatives Considered**:
- **hashlib.sha1**: Rejected - UUID format preferred for consistency with existing system patterns
- **uuid.uuid4**: Rejected - not deterministic, random UUIDs would create duplicates for same puzzle
- **uuid.uuid3 (MD5)**: Rejected - UUID v5 (SHA-1) is more collision-resistant
- **Custom hashing**: Rejected - reinventing the wheel, UUID v5 is proven standard

**Implementation Notes**:
```python
import uuid

def generate_puzzle_id(words: List[str]) -> str:
    normalized = [word.strip().lower() for word in words]
    sorted_words = sorted(normalized)
    joined = ",".join(sorted_words)
    # Use DNS namespace for consistency
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, joined))
```
- Add this method to `PuzzleSession` class in `models.py`
- Generate puzzle_id during session initialization
- Store as TEXT in database (36 character UUID string with hyphens)

### 5. CSV Export Implementation

**Decision**: Server-side CSV generation using Python `csv` module, returned via FastAPI streaming response

**Rationale**:
- Constitution and spec require server-side generation to ensure data consistency
- Reduces client-side processing burden
- FastAPI `StreamingResponse` efficiently handles file downloads
- Python csv.DictWriter provides clean, maintainable code

**Alternatives Considered**:
- **Client-side CSV generation**: Rejected - spec explicitly requires server-side
- **Third-party CSV library (pandas)**: Rejected - adds heavy dependency for simple task
- **Manual string formatting**: Rejected - error-prone, csv module is robust

**Implementation Notes**:
```python
from fastapi.responses import StreamingResponse
import csv
import io

def generate_csv(records: List[GameResult]) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[...])
    writer.writeheader()
    writer.writerows([r.dict() for r in records])
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=game_results_extract.csv"}
    )
```
- Add query parameter to GET endpoint: `GET /api/v2/game_results?format=csv`
- Column order: result_id, puzzle_id, game_date, puzzle_solved, count_groups_found, count_mistakes, total_guesses, llm_provider_name, llm_model_name

### 6. Uniqueness Enforcement (puzzle_id, game_date)

**Decision**: SQLite UNIQUE constraint on (puzzle_id, game_date) composite key

**Rationale**:
- Database-level enforcement is most reliable (prevents race conditions)
- Spec requires uniqueness on (puzzle_id, game_date) tuple
- SQLite returns UNIQUE constraint violation error, which we catch and return HTTP 409 Conflict

**Alternatives Considered**:
- **Application-level check only**: Rejected - race condition vulnerability
- **Unique on puzzle_id only**: Rejected - spec allows same puzzle on different dates
- **Unique on all fields**: Rejected - over-constraining, date can have time component

**Implementation Notes**:
```sql
CREATE UNIQUE INDEX idx_unique_puzzle_date ON game_results(puzzle_id, game_date);
```
- Catch `sqlite3.IntegrityError` in service layer
- Parse error message to distinguish UNIQUE constraint from other integrity errors
- Return HTTP 409 Conflict with message: "Game already recorded for this puzzle on this date"

### 7. Testing Strategy

**Decision**: Layered testing approach with unit, integration, and contract tests

**Test Categories**:

**Backend Unit Tests** (`pytest`):
- `test_models.py`: Test puzzle_id generation, PuzzleSession enhancements
- `test_game_results_service.py`: Test service layer logic (validation, duplicate detection)
- `test_database_service.py`: Test database operations (insert, query, schema creation)

**Backend Integration Tests**:
- `test_game_results_api.py`: Test full request/response cycle
  - POST /api/v2/game_results: success (201), duplicate (409), incomplete session (400), missing fields (422)
  - GET /api/v2/game_results: with data, empty state, ordering by date DESC
  - GET /api/v2/game_results?format=csv: CSV download with correct headers and data

**Frontend Unit Tests** (`Jest + React Testing Library`):
- `RecordGameButton.test.tsx`: Button rendering, click handling, loading/error states
- `GameHistoryView.test.tsx`: Table rendering, empty state, scrolling behavior
- Mock API calls using `jest.mock()`

**Frontend Integration Tests**:
- `GameSummary.test.tsx`: End-to-end flow from game complete to record button click
- Verify navigation updates when viewing game history

**Coverage Requirements**:
- Backend: 80% minimum (existing requirement in pyproject.toml)
- Frontend: Reasonable coverage on new components (75%+ recommended)
- All acceptance scenarios from spec must have corresponding tests

**Implementation Notes**:
- Use pytest fixtures for database setup/teardown (in-memory SQLite for tests)
- Mock LLM calls with `@pytest.mark.llm_mock` (existing pattern)
- Use `@pytest.mark.integration` for API tests
- Frontend: Mock `gameResultsService` for component isolation

### 8. Error Handling Patterns

**Decision**: Structured error responses with specific HTTP status codes and messages

**Error Cases**:

| Scenario | HTTP Status | Response Structure | Frontend Handling |
|----------|-------------|-------------------|-------------------|
| Successful record | 201 Created | `{"message": "Game recorded successfully", "result": {...}}` | Success toast |
| Duplicate record | 409 Conflict | `{"detail": "Game already recorded for this puzzle on this date"}` | Error message |
| Incomplete session | 400 Bad Request | `{"detail": "Session must be completed before recording"}` | Error message |
| Invalid session_id | 404 Not Found | `{"detail": "Session not found"}` | Error message |
| Missing required field | 422 Unprocessable Entity | `{"detail": [...]}` (Pydantic validation) | Field-level errors |
| Database error | 500 Internal Server Error | `{"detail": "Failed to record game"}` | Generic error message |

**Implementation Notes**:
- Use FastAPI's `HTTPException` for error responses
- Log detailed errors server-side, return user-friendly messages
- Frontend displays errors via toast/banner (consider adding toast notification system)
- Button disabled during POST request to prevent double-submit

### 9. Session State Management

**Decision**: Enhance existing `PuzzleSession` class with three new fields

**New Fields**:
```python
class PuzzleSession:
    puzzle_id: str              # UUID v5, generated in __init__
    llm_provider_name: Optional[str] = None  # Set by recommendation_service
    llm_model_name: Optional[str] = None     # Set by recommendation_service
```

**Rationale**:
- Minimal changes to existing session structure
- Fields populated at appropriate lifecycle points (init for puzzle_id, recommendation generation for LLM fields)
- Nullable LLM fields support games completed without recommendations

**Implementation Notes**:
- Add puzzle_id generation to `PuzzleSession.__init__()`
- Update `recommendation_service.py` to populate LLM fields when generating recommendations
- Add type annotations consistent with existing mypy configuration
- Update `SessionManager` to include new fields in session serialization

### 10. Frontend State Management

**Decision**: Use React hooks (useState, useEffect) for local state, API calls via service layer

**Rationale**:
- Project doesn't use Redux/MobX - keep it simple with hooks
- Service layer pattern already established in `frontend/src/services/`
- Consistent with existing components (e.g., `EnhancedPuzzleInterface.tsx`)

**Implementation Notes**:
- Create `gameResultsService.ts` with methods:
  - `recordGame(sessionId: string, gameDate: string): Promise<GameResult>`
  - `fetchGameHistory(): Promise<GameResult[]>`
  - `exportCSV(): Promise<Blob>`
- Components use hooks: `const [isRecording, setIsRecording] = useState(false)`
- Error states managed locally in components
- Loading states show spinner/disabled button

## Configuration and Environment

**Environment Variables**:
- `DATABASE_PATH`: Path to SQLite database file (default: `backend/data/connect_puzzle_game.db`)
- `ENABLE_PERSISTENCE`: Flag to enable/disable persistence (default: true for this feature)

**Documentation Requirements**:
- Add section to main README explaining game history feature
- Document database location and how to reset/backup
- Include CSV export format specification
- Add migration notes for future schema changes

## Performance Considerations

**Expected Load**:
- Single-user application: 1-10 games recorded per day
- Reasonable upper bound: 1000 games in database (years of gameplay)
- Query performance: O(n) table scan acceptable at this scale

**Optimizations**:
- Index on game_date for DESC ordering: `CREATE INDEX idx_game_date ON game_results(game_date DESC)`
- Compound index on (puzzle_id, game_date) already created for uniqueness
- No pagination needed initially (spec states up to 100 records without degradation)
- CSV export streams to avoid loading all records into memory

**Future Considerations** (out of scope for this phase):
- Pagination/filtering if records exceed 1000
- Full-text search on puzzle words (would require additional table)
- Archival/compression for old records

## Dependencies

**New Backend Dependencies**: None (using Python standard library sqlite3, csv)
**New Frontend Dependencies**: None (using existing React, TypeScript)

**Rationale**: Constitution favors minimal dependencies. SQLite and CSV handling are built-in, no need for additional packages.

## Summary

All technical decisions have been made based on:
1. **Constitution compliance**: Local-first, SQLite permitted, ISO 8601 UTC timestamps
2. **Existing patterns**: Pydantic models, FastAPI DI, React hooks, service layer
3. **Best practices**: Database-level constraints, server-side generation, layered testing
4. **Simplicity**: Standard library preferred, no unnecessary dependencies

The feature is ready for Phase 1 detailed design (data model, contracts, quickstart).
