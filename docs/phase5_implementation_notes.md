Phase 5 Implementation Notes

This file contains implementation-level details, DDL, exact API examples, and other technical guidance for engineers implementing the Phase 5 feature set. These notes are intended to be kept separate from the high-level functional specification.

1) Database Table (Postgres example)

Suggested SQL (Postgres dialect):

```sql
CREATE TABLE game_results (
    result_id   SERIAL PRIMARY KEY,
    puzzle_id   TEXT NOT NULL,
    game_date   TIMESTAMPTZ NOT NULL,
    puzzle_solved BOOLEAN NOT NULL,
    count_groups_found INTEGER NOT NULL,
    count_mistakes INTEGER NOT NULL,
    total_guesses INTEGER NOT NULL,
    llm_provider_name TEXT NULL,
    llm_model_name TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (puzzle_id, game_date)
);
```

Notes:
- `result_id` is an autoincrementing integer primary key (Postgres `SERIAL` shown).
- `game_date` is stored as a timezone-aware timestamp (`TIMESTAMPTZ`).
- `llm_provider_name` and `llm_model_name` are nullable.
- Uniqueness enforced by `(puzzle_id, game_date)` as required by the high-level spec.

2) API Examples (exact request/response samples)

- POST `/api/v2/game_results` — Record a completed game result (create).
  - Required request fields: `session_id` (string), `game_date` (ISO 8601 timestamp with timezone).
  - The server will validate `session_id` points to a completed session and will ignore any client-supplied numeric counts.

Example request (JSON):
```json
{
  "session_id": "session-0a1b2c3d",
  "game_date": "2025-12-24T15:30:00-08:00"
}
```

Success response (HTTP 201 Created):
```json
{
  "status": "created",
  "result": {
    "result_id": 123,
    "puzzle_id": "3b5d5c3712955042212316173ccf37be8001a8f5",
    "game_date": "2025-12-24T15:30:00-08:00",
    "puzzle_solved": true,
    "count_groups_found": 4,
    "count_mistakes": 1,
    "total_guesses": 5,
    "llm_provider_name": "openai",
    "llm_model_name": "gpt-4"
  }
}
```

Duplicate / Conflict response (HTTP 409 Conflict):
```json
{
  "status": "conflict",
  "code": "duplicate_record",
  "message": "A game result for this puzzle and game_date already exists. No new record was created."
}
```

- GET `/api/v2/game_results` — Retrieve game results (list). Returns rows ordered by `game_date` descending.
  - Response format (HTTP 200 OK):
```json
{
  "status": "ok",
  "results": [ /* array of persisted rows, most recent first */ ]
}
```

3) CSV Export

- Endpoint: GET `/api/v2/game_results?export=csv` (implementation may vary) or a dedicated route to return CSV. The server will produce a CSV with a header row and all rows.
- Default filename (Content-Disposition): `game_results_extract.csv`.

Exact column order (must match exporter):
```
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name
```

Example CSV content:
```csv
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name
123,3b5d5c3712955042212316173ccf37be8001a8f5,2025-12-24T15:30:00-08:00,true,4,1,5,openai,gpt-4
125,3b5d5c3712955042212316173ccf37be8001a8f5,2025-12-25T09:10:00-08:00,false,2,4,6,ollama,llama2
```

When sending the CSV, set:
```
Content-Disposition: attachment; filename="game_results_extract.csv"
Content-Type: text/csv
```

4) Puzzle ID hashing (exact deterministic algorithm)

To produce `puzzle_id` deterministically from the 16 puzzle words:

- For each word in the 16-word list: trim leading/trailing whitespace and lowercase.
- Preserve duplicate words.
- Sort the normalized words lexicographically using the runtime's default string sort (e.g., Python's `sorted()` which sorts by Unicode codepoint).
- Join the sorted words with a single comma `,` between items to produce a canonical string.
- Compute the SHA1 hash of the canonical string and use the hex digest as the `puzzle_id`.

Example (Python-like pseudocode):
```python
norm = [w.strip().lower() for w in words]
norm_sorted = sorted(norm)
canonical = ",".join(norm_sorted)
import hashlib
pid = hashlib.sha1(canonical.encode("utf-8")).hexdigest()
```

5) RecommendationService implementation note

When `get_recommendation()` creates/saves the `session.last_recommendation` and the authoritative response, ensure the session also records:

```python
session.llm_provider_name = authoritative_request.llm_provider.llm_type
session.llm_model_name = authoritative_request.llm_provider.model_name
```

These exact attribute names are implementation-specific — the high-level spec requires that the session persist which provider and model were used for the recommendation.

6) Additional implementation guidance

- Validation: The POST handler must verify `session.is_finished == true` before persisting a `game_results` row. If not finished, return HTTP 400 Bad Request with an explanatory message.
- Duplicate handling: If `puzzle_id` + `game_date` already exists, return HTTP 409 Conflict and do not create or update the existing row.
- Source of truth: All numeric counts and the `puzzle_solved` flag must be read from the server-side `PuzzleSession` object; ignore client-supplied counts.

7) Example error handling and messages

- 201 Created — created successfully (see success response above).
- 400 Bad Request — invalid session_id or session not in completed state.
- 409 Conflict — duplicate record.

End of implementation notes.
