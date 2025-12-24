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


### left navigation side bar

On the left navigagion side bar add a new top level navigation item called "Game History" that is "below the existing navigtation item "Start New Game".  "Game History" is a collapsible list with one entry called "View Past Games".  By default "Game History" is collapsed.

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
When the `View Past Game` navigation item is selected the frontend calls a backend service called `retrieve_game_results` to populate a table that is displayed in the main content area of the web ui as shown in this ascii diagram.  the table should be scrollable both horizontally and vertifcally if the table does not fit in the main content area.

Place a button at the end of the table called `Export CSV`.   When this button is clicked the application will create downloadable CSV extract of the displayed data.  The default name for this export is "game_results_extract.csv".  The file explorer will be displayed with the default location for the download is the "Downloads" folder.  However the user should be allowed to change this location.

```
+-----------------------------------------------------------------------------------------------------------------------------------------------+
|                                                      Game Results History                                                                     |
+-----------------------------------------------------------------------------------------------------------------------------------------------+
| result_id | puzzle_id | game_date  | puzzle_solved | count_groups_found | count_mistakes | total_guesses | llm_provider_name | llm_model_name |
+-----------------------------------------------------------------------------------------------------------------------------------------------+
|    1      |  abc123   |2025-12-24  |    True       |         4         |       1         |      7        |     openai        |   gpt-4        |
|    2      |  def456   |2025-12-23  |    False      |         3         |       4         |      8        |     ollama        |   llama2       |
|   ...     |   ...     |   ...      |     ...       |        ...        |      ...        |     ...       |      ...          |     ...        |
+-----------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                 [Export CSV]                                                                  |
+-----------------------------------------------------------------------------------------------------------------------------------------------+

```


## Session Manager

When a session is created, add the following attributes:

 * `puzzle_id` is computed by normalizing the 16 words (trim whitespace, lowercase, sort lexicographically, join with a comma) and then taking the SHA1 hash of that normalized string. The `puzzle_id` stored is the SHA1 hex digest.
 * `llm_provider_name` is the name of the llm_provider.  Initialized to None.  This is updated when a recommendation is generated.
 * `llm_model_name` is the name of the llm model used to make a recommendation.  Initialized to None.  This is updated when a recommendation is generated.




## Database Backend Service

### record_game_status endpoint
Add a backend service with endpoint `/api/v2/record_game_results`.  This service will record the status of the game into a database table called `game_results` that can be used for viewing history of games and support future data analysis.

### `game_results` table
This table will contain the following columns:

|column name|Description|
|-----------|-----------|
|result_id|Primary key for the record.  Integer value.|
|puzzle_id|Puzzle id from the session class. SHA1 hex digest computed from the normalized 16-word list (trim, lowercase, sort, join).|
|game_date|date the game was played.  Format: YYYY-MM-DD.|
|puzzle_solved| True or False.  Indicator whether the puzzle was solved or not.  Boolean.|
|count_groups_found|Number of correct groups found.  Integer.|
|count_mistakes|Number of incorrect groups.  Integer.|
|total_guesses|total number of guesses. Integer.|
|llm_provider_name|Name of the last LLM Provider used.  String.|
|llm_model_name|Name of the last LLM model used. string.|


### Retrieve past game results
add a backend service with endpoint `/api/v2/retrieve_game_results` that will return the entire contents of the `game_results`


## Confirmed Functional Decisions

- **Counts source:** All count fields (`count_groups_found`, `count_mistakes`, `total_guesses`) are taken from the backend `PuzzleSession` object. The backend session object is the single source of truth; any frontend session state is only for convenience.
- **Record uniqueness and duplicate handling:** Determine uniqueness using the tuple (`puzzle_id`, `game_date`). If a new record's `puzzle_id`+`game_date` does not match an existing record, create a new `game_results` row. If it matches an existing record, do not record and display a warning message to the user (no automatic update or overwrite).
- **Retrieval default behavior:** `retrieve_game_results` returns all records sorted by `game_date` descending (most recent first). Filtering, pagination, and additional sorting are out of scope for now.
- **CSV export:** Export CSV will include all rows (not only the visible subset). Keep the default filename `game_results_extract.csv`. The CSV includes a header row.
- **Partial/interrupted games:** Partial or interrupted games must not be recorded. The `Record Game` action is only valid when the session indicates a completed game.
- **Visibility / single-user:** This is a single-user application; all recorded data is visible to the application user (no additional access restrictions required at this time).
- **Edit/Delete scope:** Edit and delete operations are out of scope for this phase; the UI will be read-only for recorded `game_results`.
- **Counts semantics:** All counts are taken from the `PuzzleSession` object. `total_guesses` is defined as the length of the session's "previous guesses" list.
- **`puzzle_id` hashing:** Compute the normalized 16-word string by trimming leading/trailing whitespace from each word, lowercasing, sorting lexicographically, and joining with a comma; then compute the SHA1 hash and store the hex digest as `puzzle_id`.

## Remaining Open Functional Items

- None at this moment; core functional decisions for recording and retrieving game results have been specified. Future items (pagination, edit/delete, advanced filtering) can be added when moving beyond this phase.

## Example Payloads and CSV Sample

The following examples are technology-agnostic and illustrate the exact fields, formats, and a sample `puzzle_id` value (SHA1 hex digest of the normalized 16-word string).

Record Game — Request
- Purpose: Create a `game_results` row for the specified session. Backend reads authoritative counts and solved indicator from the `PuzzleSession` object.
- Required fields: `session_id` (string), `game_date` (ISO 8601 timestamp with local timezone).

Example request (JSON):
```
{
	"session_id": "session-0a1b2c3d",
	"game_date": "2025-12-24T15:30:00-08:00"
}
```

Record Game — Success Response (201 Created)
```
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

Record Game — Duplicate / Warning Response (409 Conflict)
```
{
	"status": "warning",
	"code": "duplicate_record",
	"message": "A game result for this puzzle and game_date already exists. No new record was created."
}
```

Retrieve Game Results — Request/Response
- Request: HTTP GET to `/api/v2/retrieve_game_results` (no payload for this phase).
- Response: 200 OK with `results` array ordered by `game_date` descending.

Example response:
```
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
- Include header row. Export all rows.
- Column order (exact): `result_id`, `puzzle_id`, `game_date`, `puzzle_solved`, `count_groups_found`, `count_mistakes`, `total_guesses`, `llm_provider_name`, `llm_model_name`.

Example CSV content:
```
result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name
123,3b5d5c3712955042212316173ccf37be8001a8f5,2025-12-24T15:30:00-08:00,true,4,1,5,openai,gpt-4
125,3b5d5c3712955042212316173ccf37be8001a8f5,2025-12-25T09:10:00-08:00,false,2,4,5,ollama,llama2
```

Notes
- `puzzle_id` in examples above is a SHA1 hex digest of the normalized 16-word string (normalization: trim, lowercase, lexicographic sort, join with comma).
- `total_guesses` is defined as the length of the session's `previous guesses` list.
