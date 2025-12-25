# Feature Specification: Game History and Persistent Storage

**Feature Branch**: `005-game-history`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "Add database support for recording and viewing game history with persistent storage"

## Clarifications

### Session 2025-12-24

- Q: How should the deterministic puzzle_id be generated from the 16 puzzle words? → A: Normalize words (trim whitespace, lowercase), sort lexicographically, join with commas, compute UUID v5 (SHA-1 based hash)
- Q: What precision should game_date timestamps have? → A: ISO 8601 format with timezone, canonicalized to UTC before storage for consistency
- Q: How should the system handle rapid duplicate clicks on "Record Game"? → A: Button should be disabled during the recording operation to prevent multiple submissions
- Q: What feedback should users see when recording succeeds or fails? → A: Success: Brief confirmation message with "Game recorded successfully". Failure: Error message explaining the specific issue (duplicate, incomplete session, network error)
- Q: Where should CSV generation occur? → A: Server-side generation via GET /api/v2/game_results endpoint (with query parameter or dedicated route) to ensure data consistency and reduce client processing

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record Completed Game (Priority: P1)

A user completes a puzzle game (win or lose) and wants to save the result for future reference. After viewing the game summary page showing their performance, they click a "Record Game" button to permanently store the game result.

**Why this priority**: This is the core value proposition - without the ability to record games, there is no game history feature. This creates the foundation for all other functionality.

**Independent Test**: Can be fully tested by playing a complete game, clicking "Record Game" on the summary page, and verifying the game was saved (via backend API or database query). Delivers immediate value by preserving game records.

**Acceptance Scenarios**:

1. **Given** a user has completed a puzzle game (all groups found or maximum mistakes reached), **When** they view the game summary page, **Then** they see a "Record Game" button alongside the game statistics
2. **Given** a user clicks the "Record Game" button, **When** the game has not been previously recorded, **Then** the system saves the game result with all statistics (groups found, mistakes, guesses, puzzle ID, date, LLM provider/model) and displays a success confirmation
3. **Given** a user clicks the "Record Game" button, **When** the same puzzle game has already been recorded on the same date, **Then** the system displays an error message indicating the game was already recorded and does not create a duplicate record
4. **Given** a user attempts to record a game, **When** the puzzle session is incomplete or not finished, **Then** the system displays an error message and does not save the result

---

### User Story 2 - View Game History (Priority: P2)

A user wants to review their past game performance across multiple puzzle sessions. They navigate to the game history section and view a table showing all recorded games with key statistics like puzzle ID, date, success status, groups found, mistakes made, and which LLM was used.

**Why this priority**: Viewing history provides value for the recorded data and enables users to track their progress and performance patterns over time. This is the primary retrieval mechanism for stored games.

**Independent Test**: Can be tested by recording several games (manually or via seeded data), navigating to "Game History" > "View Past Games", and verifying all recorded games appear in a scrollable table with correct data. Delivers value by making historical data accessible.

**Acceptance Scenarios**:

1. **Given** a user navigates to the left sidebar, **When** they look at the navigation menu, **Then** they see a collapsible "Game History" section below "Start New Game" (collapsed by default)
2. **Given** a user expands the "Game History" section, **When** they click on "View Past Games", **Then** the system displays a table with all recorded game results showing: result_id, puzzle_id, game_date (ISO 8601), puzzle_solved, count_groups_found, count_mistakes, total_guesses, llm_provider_name, and llm_model_name
3. **Given** the game history table contains many records, **When** the content exceeds the viewport, **Then** the table is scrollable both horizontally and vertically
4. **Given** a user views the game history table, **When** records are displayed, **Then** they are ordered by game_date with most recent games appearing first
5. **Given** no games have been recorded, **When** a user views the game history page, **Then** they see an empty table or appropriate message indicating no records exist

---

### User Story 3 - Export Game History (Priority: P3)

A user wants to analyze their game history outside the application or keep a backup of their data. They click an "Export CSV" button on the game history page, which downloads all recorded games in CSV format with a standard filename.

**Why this priority**: Export functionality adds convenience and data portability but is not essential for the core recording/viewing workflow. Users can still achieve their primary goals without it.

**Independent Test**: Can be tested by viewing the game history page with recorded games, clicking "Export CSV", and verifying a CSV file downloads with all game records and proper formatting. Delivers value by enabling external analysis and data backup.

**Acceptance Scenarios**:

1. **Given** a user is viewing the game history table, **When** they look below the table, **Then** they see an "Export CSV" button
2. **Given** a user clicks the "Export CSV" button, **When** game records exist in the database, **Then** the system downloads a CSV file containing all recorded games with a header row and all data columns
3. **Given** the CSV download is triggered, **When** the file is saved, **Then** the default filename is "game_results_extract.csv"
4. **Given** a user clicks "Export CSV", **When** no game records exist, **Then** the system downloads a CSV with only the header row or displays an appropriate message

---

### Edge Cases

- **Incomplete game recording**: System validates session.is_finished == true (which requires session.game_complete == true, meaning either game_won == true OR mistakes_made >= max_mistakes) before persisting; returns HTTP 400 Bad Request with error message if session is not completed
- **Network connectivity loss**: Frontend displays appropriate error message; user can retry recording once connectivity is restored; no partial records are created
- **Same puzzle played multiple times same day**: System enforces uniqueness on (puzzle_id, game_date); second attempt returns HTTP 409 Conflict indicating record already exists
- **Missing LLM information**: LLM provider and model fields are nullable; games completed without recommendations will have empty/null values for these fields
- **Large game history (hundreds/thousands of records)**: Performance target supports up to 100 records without degradation; pagination and filtering are explicitly out of scope for this phase
- **Rapid duplicate clicks on "Record Game"**: "Record Game" button is disabled during the recording operation to prevent multiple concurrent submissions
- **Game summary for incomplete/abandoned game**: "Record Game" button behavior is determined by session completion state; system validates before allowing recording

## Requirements *(mandatory)*

### Functional Requirements

#### User Interface Requirements

- **FR-001**: System MUST add a "Record Game" button to the game summary page (end-of-game view) that is visible after any completed game
- **FR-001a**: System MUST disable the "Record Game" button during the recording operation to prevent duplicate submissions
- **FR-001b**: System MUST display a success confirmation message "Game recorded successfully" when recording completes
- **FR-001c**: System MUST display specific error messages for failure cases:
  - Duplicate record (HTTP 409): "This game has already been recorded for this date."
  - Incomplete session (HTTP 400): "Cannot record incomplete game. Please finish the puzzle first."
  - Network error: "Failed to record game. Please check your connection and try again."
- **FR-002**: System MUST add a collapsible "Game History" section to the left navigation sidebar below "Start New Game", collapsed by default
- **FR-003**: System MUST provide a "View Past Games" option within the "Game History" navigation section
- **FR-004**: System MUST display a scrollable table of recorded games when "View Past Games" is selected, with both horizontal and vertical scrolling when content exceeds viewport
- **FR-004a**: System MUST display an appropriate message when no games have been recorded (empty state)
- **FR-005**: System MUST display an "Export CSV" button associated with the game history table
- **FR-006**: System MUST present downloaded CSV files with the default filename "game_results_extract.csv"

#### Session Management Requirements

- **FR-007**: System MUST generate a deterministic puzzle_id for each puzzle session by normalizing the 16 puzzle words (trim whitespace, lowercase), sorting them lexicographically, joining with commas, and computing SHA1 hash of the resulting string
- **FR-008**: System MUST track llm_provider_name for each session, initially empty and set when a recommendation is generated
- **FR-009**: System MUST track llm_model_name for each session, initially empty and set when a recommendation is generated
- **FR-010**: System MUST maintain all existing puzzle session attributes without modification

#### Recommendation Service Requirements

- **FR-011**: System MUST populate llm_provider_name in the session when a recommendation is generated
- **FR-012**: System MUST populate llm_model_name in the session when a recommendation is generated

#### Data Persistence Requirements

- **FR-013**: System MUST persist game results with these fields: result_id (autogenerated), puzzle_id, game_date (ISO 8601 with timezone, MUST be canonicalized to UTC before storage per constitution v2.2.0), puzzle_solved (boolean, stored as TEXT "true"/"false" per Phase 5 pattern), count_groups_found, count_mistakes, total_guesses, llm_provider_name (nullable), llm_model_name (nullable), created_at (server timestamp in UTC)
- **FR-014**: System MUST enforce uniqueness of recorded results by the tuple (puzzle_id, game_date)
- **FR-015**: System MUST reject duplicate game records (same puzzle_id and game_date) with HTTP 409 Conflict status
- **FR-016**: System MUST derive all numeric counts and puzzle_solved flag from the server's PuzzleSession object, ignoring any client-supplied values
- **FR-017**: System MUST validate that only completed/finished sessions can be recorded (session.is_finished == true)
- **FR-018**: System MUST reject attempts to record incomplete sessions with HTTP 400 Bad Request status

#### API Endpoint Requirements

- **FR-019**: System MUST provide POST /api/v2/game_results endpoint to record completed game results, accepting session_id and game_date
- **FR-020**: System MUST provide GET /api/v2/game_results endpoint to retrieve recorded game results
- **FR-020a**: System MUST provide CSV export functionality via the GET endpoint (query parameter or dedicated route) with server-side generation
- **FR-021**: System MUST return game results ordered by game_date descending (most recent first)
- **FR-022**: System MUST return HTTP 201 Created with the persisted row upon successful game recording
- **FR-023**: System MUST return HTTP 409 Conflict with explanatory message for duplicate record attempts
- **FR-024**: System MUST return HTTP 400 Bad Request with details for validation failures
- **FR-025**: System MUST generate CSV export containing all recorded games with header row and all data columns in the order: result_id, puzzle_id, game_date, puzzle_solved, count_groups_found, count_mistakes, total_guesses, llm_provider_name, llm_model_name

### Key Entities

- **Game Result**: Represents a single completed puzzle game session with performance metrics. Attributes include: unique identifier (result_id), puzzle identifier (SHA1 hash of sorted normalized words), game completion date/time (ISO 8601 with timezone, stored as UTC), success status (boolean), number of groups found (0-4), number of mistakes made (0-4), total guesses, LLM provider name used (if any, nullable), LLM model name used (if any, nullable), and record creation timestamp. Uniqueness enforced by (puzzle_id, game_date) tuple.

- **Puzzle Session**: Existing entity enhanced with new attributes - puzzle_id (deterministic SHA1 hash identifier based on sorted normalized 16 words), llm_provider_name (tracks which LLM provider was used), llm_model_name (tracks specific model used), is_finished flag (indicates session completion). Relationships: one session can generate zero or one game result record

- **Puzzle Identifier**: Deterministic SHA1 hash identifier derived from normalizing (trim, lowercase) the 16 puzzle words, sorting them lexicographically, and joining with commas. Used to group identical puzzles across different sessions and enforce uniqueness constraints with game_date

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully record a completed game in under 5 seconds after clicking the "Record Game" button
- **SC-002**: System correctly prevents duplicate game records, showing appropriate error messages when users attempt to record the same puzzle on the same date
- **SC-003**: Users can view their complete game history with all records visible and correctly sorted by most recent date first
- **SC-004**: Game history table displays correctly and remains usable with up to 100 recorded games without performance degradation
- **SC-005**: Users can successfully export their game history to CSV format with all data intact and properly formatted
- **SC-006**: 100% of completed games capture LLM provider and model information when recommendations were used
- **SC-007**: System correctly validates game completion status, rejecting 100% of incomplete game recording attempts with clear error messages
- **SC-008**: All recorded game statistics (groups found, mistakes, guesses, solved status) exactly match the server-side session state with zero discrepancies
