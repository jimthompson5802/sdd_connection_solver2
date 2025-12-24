phase5 db support

## User Interface Changes

### End of game summary page

Add a button called "Record Game" on the "Game Summary" page displayed at the end of the game.

All other existing web elements on the game summary page remain unchanged

```text
+---------------------------------------------------------------------------------------------+
|  Win or lose message                                                                        |
+---------------------------------------------------------------------------------------------+
| Correct Groups: 4/4   Mistakes: 0/4   Words Remaining: 0 | |   Previous Responses         | |
|                                                          | +---------------------------+  | |
|                                                          | | commerce   education      |  | |
|                                                          | | energy     labor          |  | |
|                                                          | |   CORRECT (Blue)          |  | |
|        [Record Game]                                     | +---------------------------+  | |
|                                                          | +---------------------------+  | |
|                                                          | | cook      delivery        |  | |
|                                                          | | go out    leftovers       |  | |
|                                                          | |   CORRECT (Green)         |  | |
|                                                          | +---------------------------+  | |
+---------------------------------------------------------------------------------------------+
```


### Left navigation side bar

On the left navigation side bar add a new top-level navigation item called `Game History` placed below the existing navigation item `Start New Game`. `Game History` is a collapsible list with one entry called `View Past Games`. By default `Game History` is collapsed.

```
+----------------------+
| Start New Game   ▼   |
|----------------------|
|  From File           |
|                      |
|  From Image          |
+----------------------+

+----------------------+
| Game History     ▼   |
|----------------------|
|  View Past Games     |
+----------------------+
```

### View Past Games
When the `View Past Games` navigation item is selected the frontend will call the backend `GET /api/v2/game_results` endpoint to populate a table displayed in the main content area of the web UI. The table should be scrollable both horizontally and vertically if it does not fit in the main content area.

Place a button at the end of the table labeled `Export CSV`. When clicked, the application will download a CSV extract of the server-exported data. The default filename is `game_results_extract.csv`. The backend will set `Content-Disposition: attachment; filename="game_results_extract.csv"` and the browser will handle the download location according to user/browser preferences. (Note: web apps cannot force the OS file explorer location — the browser controls where files are saved.)

```text
+---------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                      Game Results History                                                                               |
+---------------------------------------------------------------------------------------------------------------------------------------------------------+
| result_id | puzzle_id | game_date (ISO 8601) | puzzle_solved | count_groups_found | count_mistakes | total_guesses | llm_provider_name | llm_model_name |
+---------------------------------------------------------------------------------------------------------------------------------------------------------+
|    1      |  abc123   |2025-12-24T15:30:00-08:00 |    True       |         4         |       1         |      7        |     openai        |   gpt-4    |
|    2      |  def456   |2025-12-23T11:05:00-08:00 |    False      |         3         |       4         |      8        |     ollama        |   llama2   |
|   ...     |   ...     |   ...                  |     ...       |        ...        |      ...        |     ...       |      ...          |     ...      |
+---------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                 [Export CSV]                                                                            |
+---------------------------------------------------------------------------------------------------------------------------------------------------------+

```


## Session Manager

When a session is created, the following session attributes are maintained by the backend session manager (server-side):

- `puzzle_id`: computed by normalizing the 16 words (trim whitespace, lowercase, sort lexicographically, join with a comma) and then taking the SHA1 hash of that normalized string. The `puzzle_id` stored is the SHA1 hex digest. See the `puzzle_id` hashing section for deterministic details.
- `llm_provider_name`: name of the LLM provider. Initialized to `None` and updated when a recommendation is generated.
- `llm_model_name`: name of the LLM model used to make a recommendation. Initialized to `None` and updated when a recommendation is generated.


## Database Backend Service

### Endpoints (canonical)
- POST `/api/v2/game_results` — Record a completed game result (create).
- GET `/api/v2/game_results` — Retrieve game results (list).

The backend implements these endpoints for this phase. The POST endpoint requires a `session_id` request field so the server can locate the authoritative `PuzzleSession` and read the counts and solved indicator from it; however, by design we will NOT add a `session_id` column to the `game_results` table for this phase. The server will ignore any client-supplied counts and will populate all persisted fields using the server-side `PuzzleSession` object. (If you want `session_id` stored in the DB later, we can add it in a follow-up.)

### `game_results` table (schema and DDL)
This table stores recorded game results for history and analysis. Suggested SQL (Postgres dialect):

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
- `result_id` is an autoincrementing integer primary key.
- `game_date` is stored as a timezone-aware timestamp (`TIMESTAMPTZ`) and examples use full ISO 8601 timestamps with timezone (e.g., `2025-12-24T15:30:00-08:00`).
- `llm_provider_name` and `llm_model_name` are nullable because sessions may not have those values populated.
- Uniqueness is enforced using `(puzzle_id, game_date)` per existing decisions. Be aware this may be sensitive to the timestamp precision; consider normalizing `game_date` if you want coarser uniqueness (e.g., date-only) in future.


### Retrieve past game results
GET `/api/v2/game_results` returns the stored rows ordered by `game_date` descending (most recent first). Filtering, pagination, and additional sorting are out of scope for this phase; a future enhancement can add `?limit=&offset=&from_date=&to_date=&puzzle_id=` query parameters.


## Confirmed Functional Decisions (clarified)

- **Counts source:** All count fields (`count_groups_found`, `count_mistakes`, `total_guesses`) are taken from the backend `PuzzleSession` object. The backend session object is the single source of truth; any frontend session state is only for convenience.
- **Record uniqueness and duplicate handling:** Determine uniqueness using the tuple (`puzzle_id`, `game_date`) (as implemented in the DB `UNIQUE` constraint). If a new record's `puzzle_id`+`game_date` matches an existing row, do not create or update the row; return HTTP 409 Conflict and an explanatory message to the client.
- **Retrieval default behavior:** `GET /api/v2/game_results` returns all records sorted by `game_date` descending (most recent first).
- **CSV export:** Export CSV will include all rows (server-side export). The backend will produce a CSV with the header row and return it with `Content-Disposition: attachment; filename="game_results_extract.csv"`.
- **Partial/interrupted games:** Partial or interrupted games must not be recorded. The `Record Game` action is only valid when the server-side session state indicates the game is complete (e.g., `session.is_finished == true` and not a partial/interrupted state). The backend must validate the session state before persisting.
- **Visibility / single-user:** This is a single-user application; all recorded data is visible to the application user (no additional access restrictions required at this time).
- **Edit/Delete scope:** Edit and delete operations are out of scope for this phase; the UI will be read-only for recorded `game_results`.
- **Counts semantics:** `total_guesses` is defined as the length of the session's `previous_guesses` list on the server.
- **`puzzle_id` hashing:** Compute the normalized 16-word string by trimming leading/trailing whitespace from each word, lowercasing, sorting lexicographically (use the runtime's default string sort, e.g., Python's `sorted()` which sorts by Unicode codepoint), and joining with a comma; then compute the SHA1 hash and store the hex digest as `puzzle_id`. Preserve duplicates in the list before sorting.


## Error and Conflict Responses

- Successful creation (POST `/api/v2/game_results`): HTTP 201 Created
	```json
	{
		"status": "created",
		"result": { /* persisted row as returned by DB */ }
	}
	```

- Duplicate / Conflict (attempt to record an already-recorded game): HTTP 409 Conflict
	```json
	{
		"status": "conflict",
		"code": "duplicate_record",
		"message": "A game result for this puzzle and game_date already exists. No new record was created."
	}
	```

The client UI should display a warning message with the `message` text returned by the server.


## Example Payloads and CSV Sample (updated notes)

Record Game — Request
- Purpose: Create a `game_results` row for the specified session. Backend reads authoritative counts and solved indicator from the server-side `PuzzleSession` object.
- Required fields: `session_id` (string), `game_date` (ISO 8601 timestamp with timezone). The backend will validate the `session_id` refers to a completed session and will ignore any client-supplied numeric counts.

Example request (JSON):
```json
{
	"session_id": "session-0a1b2c3d",
	"game_date": "2025-12-24T15:30:00-08:00"
}
```

Record Game — Success Response (201 Created)
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

Retrieve Game Results — Request/Response
- Request: HTTP GET to `/api/v2/game_results` (no payload for this phase).
- Response: 200 OK with `results` array ordered by `game_date` descending.

Example response:
```json
{
	"status": "ok",
	"results": [
		{
			"result_id": 125,
			"puzzle_id": "3b5d5c3712955042212316173ccf37be8001a8f5",
			"game_date": "2025-12-25T09:10:00-08:00",
			"puzzle_solved": false,
			"count_groups_found": 3,
			"count_mistakes": 4,
			"total_guesses": 7,
			"llm_provider_name": "ollama",
			"llm_model_name": "llama2"
		},
		{
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
	]
}
```

CSV Export — Exact column order and example
- Filename: `game_results_extract.csv` (default).
- Include header row. Export all rows (server-side export).
- Column order (exact): `result_id`, `puzzle_id`, `game_date`, `puzzle_solved`, `count_groups_found`, `count_mistakes`, `total_guesses`, `llm_provider_name`, `llm_model_name`.

Example CSV content:
```csv
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name
123,3b5d5c3712955042212316173ccf37be8001a8f5,2025-12-24T15:30:00-08:00,true,4,1,5,openai,gpt-4
125,3b5d5c3712955042212316173ccf37be8001a8f5,2025-12-25T09:10:00-08:00,false,2,4,6,ollama,llama2
```

Notes
- `puzzle_id` is a SHA1 hex digest of the normalized 16-word string (normalization: trim, lowercase, runtime lexicographic sort, join with comma). Preserve duplicates prior to sorting.
- `total_guesses` is defined as the length of the session's `previous_guesses` list.
