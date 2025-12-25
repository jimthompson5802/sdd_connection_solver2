phase5 db support

### User Interface Changes (functional)

### End of game summary page

Add a button labeled `Record Game` to the existing Game Summary page (end-of-game view). The button triggers a server-side action that records a completed game into persistent game history. All other visible elements on the Game Summary page remain unchanged.

Visually, the `Record Game` button should be placed alongside the existing summary information so users can clearly associate it with the finished game state.

Example of revised Game Summary Page
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

Add a top-level navigation item `Game History` below the existing `Start New Game` item. `Game History` is collapsible and contains a single entry `View Past Games`. The `Game History` node is collapsed by default.

Example of revised left navigation side bar
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

Selecting `View Past Games` loads a table of recorded games from the backend (`GET /api/v2/game_results`). The table displays the recorded rows and must be scrollable horizontally and vertically if content exceeds the main content area.

Provide a button labeled `Export CSV` associated with the table. When clicked, the application downloads a server-produced CSV extract of the stored game results. The default filename visible to users should be `game_results_extract.csv` (the server will return an appropriate attachment response).

Table columns (user-visible names):
- `result_id`, `puzzle_id`, `game_date` (ISO 8601), `puzzle_solved`, `count_groups_found`, `count_mistakes`, `total_guesses`, `llm_provider_name`, `llm_model_name`.

Example new View Past Game web page
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


## Session Manager (functional behavior)

When a puzzle session is created and played, the server-side session manager adds these new attributes:
- `puzzle_id`: a deterministic identifier derived from the session's 16 puzzle words. This identifier is used to group identical puzzles across sessions.
- `llm_provider_name`: the name of the LLM provider used for a recommendation; initially empty and set when a recommendation is generated.
- `llm_model_name`: the model name used for recommendations; initially empty and set when a recommendation is generated.

No changes in the existing puzzle session attributes.


## RecommendationService (functional behavior)

When a recommendation is generated and saved to the session, the session must also record which provider and model were used. The session fields `llm_provider_name` and `llm_model_name` must be populated so they can be persisted with a recorded game result.


## Database backend — functional contract

The backend exposes the following endpoints for game history:
- POST `/api/v2/game_results` — Record a completed game result. The server locates the authoritative `PuzzleSession` by `session_id` and persists a `game_results` row using values from the server-side session. The server ignores any client-supplied numeric counts.
- GET `/api/v2/game_results` — Retrieve recorded game results. Returns stored rows ordered by `game_date` (most recent first).

Persisted fields (names only):
- `result_id` (autogenerated identifier)
- `puzzle_id`
- `game_date` (ISO 8601 timestamp with timezone)
- `puzzle_solved` (boolean)
- `count_groups_found` (integer)
- `count_mistakes` (integer)
- `total_guesses` (integer)
- `llm_provider_name` (nullable)
- `llm_model_name` (nullable)
- `created_at` (server timestamp)

Uniqueness and duplicates:
- The server enforces uniqueness of recorded results by the tuple (`puzzle_id`, `game_date`). If a POST would create a row with the same (`puzzle_id`, `game_date`) as an existing row, the server must return HTTP 409 Conflict and must not create or update the existing row.

Validation rules:
- Only sessions that are finished may be recorded. The server must validate that the referenced `session_id` corresponds to a completed session (e.g., `session.is_finished == true`) before persisting; otherwise return HTTP 400 Bad Request.
- All persisted numeric counts and the `puzzle_solved` flag are read from the server's `PuzzleSession` object; the client-supplied counts are ignored.

Retrieval and CSV export:
- `GET /api/v2/game_results` returns the list of persisted rows ordered by `game_date` descending. Filtering and pagination are out of scope for this phase.
- The `Export CSV` action triggers a server-generated CSV download containing all rows and a header. The default filename presented to users is `game_results_extract.csv`.

Error handling (functional):
- Successful creation: HTTP 201 Created. Payload should indicate success and include the persisted row.
- Duplicate/conflict: HTTP 409 Conflict with an explanatory message indicating the record already exists.
- Validation failures: HTTP 400 Bad Request with details explaining the validation failure.

## Confirmed functional decisions (summary)
- Server is the single source of truth for counts and solved state.
- Duplicate detection is based on (`puzzle_id`, `game_date`).
- Partial or interrupted games must not be recorded.
- The application is single-user for recorded data visibility in this phase.
