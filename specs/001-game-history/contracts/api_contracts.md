# API Contracts: Game History Endpoints

**Feature**: Game History and Persistent Storage
**Branch**: `001-game-history`
**Date**: 2025-12-24
**Base URL**: `http://localhost:8000/api/v2`

## Overview

This document specifies the REST API contracts for game history functionality, including recording completed games, retrieving game history, and exporting data to CSV format. All endpoints follow FastAPI conventions with Pydantic validation.

---

## Endpoints

### 1. Record Completed Game

**Endpoint**: `POST /api/v2/game_results`

**Description**: Records a completed puzzle game to persistent storage. Validates that the session is finished and enforces uniqueness on (puzzle_id, game_date) to prevent duplicates.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "session_id": "string (UUID4 format)",
  "game_date": "string (ISO 8601 with timezone, e.g., '2025-12-24T15:30:00-08:00')"
}
```

**Request Schema** (Pydantic):
```python
class RecordGameRequest(BaseModel):
    session_id: str
    game_date: datetime  # Must include timezone
```

**Success Response** (HTTP 201 Created):
```json
{
  "status": "created",
  "result": {
    "result_id": 1,
    "puzzle_id": "a7b3c4d5-e6f7-5a8b-9c0d-1e2f3a4b5c6d",
    "game_date": "2025-12-23T15:30:00+00:00",
    "puzzle_solved": true,
    "count_groups_found": 4,
    "count_mistakes": 1,
    "total_guesses": 7,
    "llm_provider_name": "openai",
    "llm_model_name": "gpt-4"
  }
}
```

**Error Responses**:

| Status Code | Condition | Response Body |
|-------------|-----------|---------------|
| 400 Bad Request | Session not finished | `{"detail": "Session must be completed before recording"}` |
| 404 Not Found | Session ID not found | `{"detail": "Session not found"}` |
| 409 Conflict | Duplicate record (same puzzle_id + game_date) | `{"status": "conflict", "code": "duplicate_record", "message": "A game result for this puzzle and game_date already exists. No new record was created."}` |
| 422 Unprocessable Entity | Invalid request format (missing fields, invalid date) | `{"detail": [{"loc": ["body", "game_date"], "msg": "field required", "type": "value_error.missing"}]}` |
| 500 Internal Server Error | Database error | `{"detail": "Failed to record game"}` |

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/v2/game_results" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "game_date": "2025-12-24T15:30:00-08:00"
  }'
```

**Validation Rules**:
- `session_id`: Must be valid UUID format
- `game_date`: Must be valid ISO 8601 with timezone
- Session must exist in SessionManager
- Session must have `is_finished == true`
- Combination of (puzzle_id, game_date) must be unique

---

### 2. Retrieve Game History

**Endpoint**: `GET /api/v2/game_results`

**Description**: Retrieves all recorded game results, ordered by game_date descending (most recent first).

**Query Parameters**: None (filtering/pagination out of scope for this phase)

**Request Headers**: None required

**Success Response** (HTTP 200 OK):
```json
{
  "status": "ok",
  "results": [
    {
      "result_id": 2,
      "puzzle_id": "b8c4d5e6-f7a8-5b9c-0d1e-2f3a4b5c6d7e",
      "game_date": "2025-12-24T23:30:00+00:00",
      "puzzle_solved": false,
      "count_groups_found": 3,
      "count_mistakes": 4,
      "total_guesses": 7,
      "llm_provider_name": "ollama",
      "llm_model_name": "llama2"
    },
    {
      "result_id": 1,
      "puzzle_id": "a7b3c4d5-e6f7-5a8b-9c0d-1e2f3a4b5c6d",
      "game_date": "2025-12-23T15:30:00+00:00",
      "puzzle_solved": true,
      "count_groups_found": 4,
      "count_mistakes": 1,
      "total_guesses": 5,
      "llm_provider_name": "openai",
      "llm_model_name": "gpt-4"
    }
  ]
}
```

**Empty State Response** (HTTP 200 OK):
```json
{
  "status": "ok",
  "results": []
}
```

**Error Responses**:

| Status Code | Condition | Response Body |
|-------------|-----------|---------------|
| 500 Internal Server Error | Database error | `{"detail": "Failed to retrieve game history"}` |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v2/game_results"
```

**Response Schema** (Pydantic):
```python
class GameHistoryResponse(BaseModel):
    results: list[GameResultResponse]
    count: int
```

**Ordering**: Results ordered by `game_date DESC` (most recent first)

---

### 3. Export Game History to CSV

**Endpoint**: `GET /api/v2/game_results?format=csv`

**Alternative**: `GET /api/v2/game_results/export` (if dedicated route preferred)

**Description**: Downloads all recorded game results as a CSV file. Server-side generation ensures data consistency.

**Query Parameters**:
- `format`: "csv" (required for CSV export on GET endpoint)

**Request Headers**: None required

**Success Response** (HTTP 200 OK):
- **Content-Type**: `text/csv; charset=utf-8`
- **Content-Disposition**: `attachment; filename="game_results_extract.csv"`
- **Body**: CSV formatted data with headers

**CSV Format**:
```csv
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name
1,abc123def456...,2025-12-24T23:30:00+00:00,true,4,1,7,openai,gpt-4
2,fed654cba321...,2025-12-23T15:30:00+00:00,false,3,4,8,ollama,llama2
```

**CSV Specifications**:
- Header row included
- Boolean values: "true" or "false" (lowercase strings)
- Null values: empty string
- Timestamps: ISO 8601 UTC format
- Standard CSV escaping (quotes for commas/newlines in text)
- Column order: `result_id, puzzle_id, game_date, puzzle_solved, count_groups_found, count_mistakes, total_guesses, llm_provider_name, llm_model_name`

**Empty State Response** (HTTP 200 OK):
- Returns CSV with header row only:
```csv
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name
```

**Error Responses**:

| Status Code | Condition | Response Body |
|-------------|-----------|---------------|
| 500 Internal Server Error | Database or CSV generation error | `{"detail": "Failed to generate CSV export"}` |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v2/game_results?format=csv" \
  -o game_results_extract.csv
```

**Implementation Note**: Uses FastAPI `StreamingResponse` with Python `csv` module for efficient generation.

---

## Data Models

### GameResultResponse (Pydantic)

```python
from pydantic import BaseModel, Field
from typing import Optional

class GameResultResponse(BaseModel):
    result_id: int
    puzzle_id: str
    game_date: str  # ISO 8601 string
    puzzle_solved: bool  # Converts from TEXT "true"/"false" in database
    count_groups_found: int = Field(..., ge=0, le=4)
    count_mistakes: int = Field(..., ge=0, le=4)
    total_guesses: int = Field(..., ge=1)
    llm_provider_name: Optional[str] = None
    llm_model_name: Optional[str] = None

    class Config:
        from_attributes = True
```

### RecordGameRequest (Pydantic)

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class RecordGameRequest(BaseModel):
    session_id: str = Field(..., description="UUID of the completed puzzle session")
    game_date: datetime = Field(..., description="ISO 8601 timestamp with timezone")

    @field_validator('game_date')
    @classmethod
    def validate_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("game_date must include timezone information")
        return v
```

### RecordGameResponse (Pydantic)

```python
class RecordGameResponse(BaseModel):
    status: str = "created"
    result: GameResultResponse
```

### GameHistoryResponse (Pydantic)

```python
class GameHistoryResponse(BaseModel):
    status: str = "ok"
    results: list[GameResultResponse]
```---

## Error Handling

### Standard Error Response Format

All error responses follow FastAPI's standard exception format:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (HTTP 422):
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### HTTP Status Code Summary

| Status | Usage |
|--------|-------|
| 200 OK | Successful GET request |
| 201 Created | Successful POST (game recorded) |
| 400 Bad Request | Business logic validation failure (e.g., session not finished) |
| 404 Not Found | Resource not found (e.g., session_id doesn't exist) |
| 409 Conflict | Duplicate record attempt |
| 422 Unprocessable Entity | Request format validation failure (Pydantic) |
| 500 Internal Server Error | Server or database error |

---

## OpenAPI Schema

FastAPI auto-generates OpenAPI documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Endpoint Tags

All game history endpoints use the tag: `"game_results"`

### Example OpenAPI Route Definition

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

router = APIRouter(prefix="/api/v2", tags=["game_results"])

@router.post("/game_results",
             response_model=RecordGameResponse,
             status_code=201,
             summary="Record a completed game",
             description="Records a completed puzzle game to persistent storage. Validates session completion and enforces uniqueness.")
async def record_game(
    request: RecordGameRequest,
    game_results_service: GameResultsService = Depends(get_game_results_service)
) -> RecordGameResponse:
    # Implementation
    pass

@router.get("/game_results",
            response_model=GameHistoryResponse,
            summary="Retrieve game history",
            description="Returns all recorded games ordered by date descending")
async def get_game_history(
    format: Optional[str] = None,
    game_results_service: GameResultsService = Depends(get_game_results_service)
):
    if format == "csv":
        # Return CSV StreamingResponse
        pass
    # Return JSON GameHistoryResponse
    pass
```

---

## Testing Contract

### Required Test Cases

**POST /api/v2/game_results**:
1. ✅ Success: Valid completed session → 201 Created
2. ✅ Duplicate: Same puzzle_id + game_date → 409 Conflict
3. ✅ Incomplete: Session not finished → 400 Bad Request
4. ✅ Not Found: Invalid session_id → 404 Not Found
5. ✅ Invalid Date: Missing timezone → 422 Unprocessable Entity
6. ✅ Missing Field: No session_id → 422 Unprocessable Entity

**GET /api/v2/game_results**:
1. ✅ Success with data: Returns ordered results → 200 OK
2. ✅ Empty state: No records → 200 OK with empty array
3. ✅ Ordering: Most recent first (verify game_date DESC)

**GET /api/v2/game_results?format=csv**:
1. ✅ Success with data: Returns CSV with headers → 200 OK
2. ✅ Empty state: Returns header-only CSV → 200 OK
3. ✅ Format: Verify column order and data formatting
4. ✅ Filename: Verify Content-Disposition header

### Test Markers (pytest)

```python
@pytest.mark.integration
@pytest.mark.contract
def test_record_game_success():
    # Test implementation
    pass
```

---

## Frontend Integration

### TypeScript Service Client

```typescript
// services/gameResultsService.ts

import {
  GameResult,
  RecordGameRequest,
  RecordGameResponse,
  GameHistoryResponse
} from '../types/gameResults';

const API_BASE = 'http://localhost:8000/api/v2';

export const gameResultsService = {
  async recordGame(sessionId: string, gameDate: string): Promise<GameResult> {
    const response = await fetch(`${API_BASE}/game_results`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, game_date: gameDate })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to record game');
    }

    const data: RecordGameResponse = await response.json();
    return data.result;
  },

  async fetchGameHistory(): Promise<GameResult[]> {
    const response = await fetch(`${API_BASE}/game_results`);

    if (!response.ok) {
      throw new Error('Failed to fetch game history');
    }

    const data: GameHistoryResponse = await response.json();
    return data.results;
  },

  async exportCSV(): Promise<void> {
    const response = await fetch(`${API_BASE}/game_results?format=csv`);

    if (!response.ok) {
      throw new Error('Failed to export CSV');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'game_results_extract.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }
};
```

---

## Summary

This contract specification provides:
- ✅ Complete endpoint definitions with request/response schemas
- ✅ Comprehensive error handling for all edge cases
- ✅ Pydantic models for type safety and validation
- ✅ CSV export with specific format requirements
- ✅ OpenAPI/Swagger documentation integration
- ✅ Testing requirements with specific scenarios
- ✅ Frontend integration guidance with TypeScript client

All contracts align with constitution requirements and data model specifications.
