# Game History API Documentation

This document describes the Game History API endpoints for recording and retrieving puzzle game results.

## Overview

The Game History API provides endpoints for:
- Recording completed puzzle games with performance metrics
- Retrieving game history records
- Exporting game history to CSV format

All endpoints are under the `/api/v2/game_results` path and use JSON for request/response bodies (except CSV export).

## Authentication

Currently no authentication required (single-user local application).

## Endpoints

### 1. Record Game Result

Record a completed puzzle game to persistent storage.

**Endpoint**: `POST /api/v2/game_results`

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string (UUID) | Yes | The session ID of the completed game |

**Success Response** (201 Created):
```json
{
  "status": "success",
  "result": {
    "result_id": 1,
    "puzzle_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "game_date": "2025-12-24T15:30:00+00:00",
    "puzzle_solved": "true",
    "count_groups_found": 4,
    "count_mistakes": 2,
    "total_guesses": 8,
    "llm_provider_name": "openai",
    "llm_model_name": "gpt-4",
    "created_at": "2025-12-24T15:30:05+00:00"
  }
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| status | string | "success" |
| result | GameResult | The created game result record |

**GameResult Schema**:
| Field | Type | Description |
|-------|------|-------------|
| result_id | integer | Unique identifier (auto-generated) |
| puzzle_id | string (UUID) | UUID v5 of sorted puzzle words |
| game_date | string | ISO 8601 timestamp with timezone (UTC) |
| puzzle_solved | string | "true" or "false" |
| count_groups_found | integer | Number of groups found (0-4) |
| count_mistakes | integer | Number of mistakes made (0-4) |
| total_guesses | integer | Total guesses made (minimum 1) |
| llm_provider_name | string \| null | LLM provider name |
| llm_model_name | string \| null | LLM model name |
| created_at | string | Server timestamp when record was created |

**Error Responses**:

**400 Bad Request** - Incomplete session:
```json
{
  "status": "error",
  "error": "Session not finished",
  "detail": "Cannot record game: session is not complete"
}
```

**404 Not Found** - Session not found:
```json
{
  "status": "error",
  "error": "Session not found",
  "detail": "No session found with ID: 550e8400-e29b-41d4-a716-446655440000"
}
```

**409 Conflict** - Duplicate record:
```json
{
  "status": "error",
  "error": "Duplicate game result",
  "detail": "A game result for this puzzle and date already exists"
}
```

**500 Internal Server Error** - Database error:
```json
{
  "status": "error",
  "error": "Database error",
  "detail": "Failed to record game result"
}
```

---

### 2. Get Game History

Retrieve all recorded game results ordered by most recent first.

**Endpoint**: `GET /api/v2/game_results`

**Query Parameters**: None

**Success Response** (200 OK):
```json
{
  "status": "success",
  "results": [
    {
      "result_id": 2,
      "puzzle_id": "8d0e7780-8536-51ef-a55c-f18gc2g01bf8",
      "game_date": "2025-12-25T10:00:00+00:00",
      "puzzle_solved": "false",
      "count_groups_found": 2,
      "count_mistakes": 4,
      "total_guesses": 6,
      "llm_provider_name": "ollama",
      "llm_model_name": "llama2",
      "created_at": "2025-12-25T10:00:05+00:00"
    },
    {
      "result_id": 1,
      "puzzle_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "game_date": "2025-12-24T15:30:00+00:00",
      "puzzle_solved": "true",
      "count_groups_found": 4,
      "count_mistakes": 2,
      "total_guesses": 8,
      "llm_provider_name": "openai",
      "llm_model_name": "gpt-4",
      "created_at": "2025-12-24T15:30:05+00:00"
    }
  ]
}
```

**Empty State Response** (200 OK):
```json
{
  "status": "success",
  "results": []
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| status | string | "success" |
| results | GameResult[] | Array of game result records (empty if no records) |

---

### 3. Export Game History as CSV

Download all game results as a CSV file for external analysis.

**Endpoint**: `GET /api/v2/game_results?export=csv`

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| export | string | Yes | Must be "csv" to trigger CSV export |

**Success Response** (200 OK):
```csv
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name,created_at
2,8d0e7780-8536-51ef-a55c-f18gc2g01bf8,2025-12-25T10:00:00+00:00,false,2,4,6,ollama,llama2,2025-12-25T10:00:05+00:00
1,7c9e6679-7425-40de-944b-e07fc1f90ae7,2025-12-24T15:30:00+00:00,true,4,2,8,openai,gpt-4,2025-12-24T15:30:05+00:00
```

**Response Headers**:
```
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="game_results_extract.csv"
```

**CSV Format**:
- First row contains column headers
- Records ordered by game_date DESC (most recent first)
- Empty string for null values (llm_provider_name, llm_model_name)
- All fields quoted per CSV standard

**Empty State Response** (200 OK):
Returns CSV with headers only:
```csv
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name,created_at
```

---

## Data Model

### Puzzle ID Generation

The `puzzle_id` is a deterministic UUID v5 generated from the puzzle words:

1. Normalize words: lowercase, trim whitespace
2. Sort words alphabetically
3. Join with commas: "apple,banana,cherry,..."
4. Generate UUID v5 using DNS namespace

This ensures the same puzzle always has the same ID regardless of word order or case.

### Timestamp Format

All timestamps use ISO 8601 format with timezone and are canonicalized to UTC:
- Format: `YYYY-MM-DDTHH:MM:SS+00:00`
- Example: `2025-12-24T15:30:00+00:00`

### Boolean Storage

The `puzzle_solved` field stores boolean values as strings:
- `"true"` - Puzzle was successfully completed (all 4 groups found)
- `"false"` - Puzzle was not completed (4 mistakes made before completion)

### Validation Constraints

- `count_groups_found`: 0-4 (validated)
- `count_mistakes`: 0-4 (validated)
- `total_guesses`: minimum 1 (validated)
- `puzzle_id` + `game_date`: Must be unique (enforced by database)
- Session must be finished (`is_finished == true`) to record

### State Invariants

- If `puzzle_solved == "true"`, then `count_groups_found == 4`
- `count_groups_found + count_mistakes <= total_guesses`
- `count_mistakes <= 4` (game ends at 4 mistakes if not won)

---

## Usage Examples

### Example 1: Record a Game

```bash
# Complete a puzzle game and get the session_id
# Then record it:

curl -X POST http://localhost:8000/api/v2/game_results \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }'
```

### Example 2: View Game History

```bash
curl http://localhost:8000/api/v2/game_results
```

### Example 3: Export to CSV

```bash
curl http://localhost:8000/api/v2/game_results?export=csv \
  -o game_history.csv
```

Or open in browser:
```
http://localhost:8000/api/v2/game_results?export=csv
```

### Example 4: Check for Duplicate Before Recording

```bash
# This will return 409 Conflict if already recorded
curl -X POST http://localhost:8000/api/v2/game_results \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }' \
  -w "\nHTTP Status: %{http_code}\n"
```

---

## Implementation Notes

### Database Storage

- Database: SQLite
- Location: `backend/data/connect_puzzle_game.db`
- Table: `game_results`
- Indexes:
  - Primary key on `result_id`
  - Unique index on `(puzzle_id, game_date)`
  - Descending index on `game_date` for efficient ordering

### Session Management

- Sessions are stored in-memory during gameplay
- Only completed sessions (won or lost) can be recorded
- Recording is opt-in (user must click "Record Game" button)
- Same puzzle can be played multiple times (recorded with different dates)

### Error Handling

- Validation errors return 400 Bad Request
- Missing sessions return 404 Not Found
- Duplicate records return 409 Conflict
- Database errors return 500 Internal Server Error

### Performance

- Local SQLite operations: < 100ms response time
- Optimized for up to 100 game records without pagination
- CSV export streams data for memory efficiency

---

## Related Documentation

- **Feature Specification**: `specs/005-game-history/spec.md`
- **Data Model**: `specs/005-game-history/data-model.md`
- **API Contracts**: `specs/005-game-history/contracts/api_contracts.md`
- **Quickstart Guide**: `specs/005-game-history/quickstart.md`

---

## Version History

- **v1.0** (2025-12-25): Initial game history API release
  - POST /api/v2/game_results - Record game
  - GET /api/v2/game_results - Retrieve history
  - GET /api/v2/game_results?export=csv - Export CSV
