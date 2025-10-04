# Feature Specification: NYT Connections Puzzle Assistant Web Application

**Feature Branch**: `001-nyt-connections-puzzle`  
**Created**: 2025-09-28  
**Status**: Draft  
**Input**: User description: "NYT Connections Puzzle Assistant Web Application - Develop a web application that assists users in solving the New York Times Connections Puzzle. The application will leverage a Large Language Model (LLM) to generate recommendations for grouping words and tracks invalid guesses to enhance the solving experience. For this first phase we will focus only the web UI and user interactions."

---

## User Scenarios & Testing

### Primary User Story
A puzzle enthusiast visits the web application to get assistance solving a New York Times Connections puzzle. They upload their puzzle file containing 16 words, receive AI-powered recommendations for grouping four words together, and track their progress as they work through the puzzle by recording correct groups and mistakes until they either solve all four groups or reach the maximum number of allowed errors.

### Acceptance Scenarios
1. Given the application is loaded, when the user uploads a puzzle file and confirms setup, then the system validates the file, initializes a new puzzle session with exactly 16 unique words, displays those words in the "Remaining Words" area, clears any prior history, and resets all counters and state to the initial active state.
2. Given a valid active puzzle, when the user requests a recommendation, then the system presents a recommended group of 4 words together with a human-readable rationale or hint explaining why those words may belong together.
3. Given a recommendation is presented, when the user marks it as correct and selects one of the connection colors (Yellow / Green / Blue / Purple), then that color is recorded for the found group, the chosen color option becomes disabled for future use, the words that belong to that found group are removed from the remaining words list, and the correct groups counter increments.
4. Given a recommendation is presented, when the user marks it as incorrect, then the mistake counter increments, the attempt is captured in the previous-guesses/history panel with an incorrect indicator, and the session state updates to reflect the failed attempt.
5. Given a recommendation is presented, when the user marks it as "one-away", then the attempt is recorded with a "one-away" indicator and (where available) a rationale/hint, the mistake counter increments, and the attempt appears in the previous-guesses/history panel with the appropriate visual indicator.
6. Given the user has recorded 4 correct groups, when the correct groups count reaches 4, then the system transitions the game state to success and displays a prominent success message to the user.
7. Given the user has recorded 4 mistakes, when the mistake count reaches 4, then the system transitions the game state to failure, displays a prominent failure message, and prevents further recommendation/response interactions until a new puzzle is set up.
8. Given invalid user actions (for example, requesting a recommendation with fewer than 4 words remaining, responding when no recommendation is active, or uploading an invalid file), when the action is attempted, then the system displays a clear, user-friendly error message describing the problem and prevents the invalid state transition.

### Edge Cases
- System displays error message and prevents setup when puzzle file is empty or invalid CSV format
- System displays error message "Not enough words remaining" when fewer than 4 words available for recommendation
- System displays error message "No recommendation to respond to" when response buttons clicked without active recommendation

## Clarifications

### Session 2025-09-28
- Q: What file format should the puzzle file use for uploading the 16 words? → A: CSV file with all words in a single row
- Q: What should happen when the user clicks "Next Recommendation" but there are fewer than 4 remaining words? → A: Display error message "Not enough words remaining"
- Q: What should happen when the user uploads an invalid or empty CSV file? → A: Display error message and prevent setup
- Q: What should happen if the user clicks response buttons when no recommendation is currently displayed? → A: Display error message "No recommendation to respond to"
- Q: What performance target should the system meet for generating recommendations when "Next Recommendation" is clicked? → A: No specific time requirement

## Requirements

### Functional Requirements
- **FR-001**: The system MUST present a clear web UI that allows users to start a new puzzle, view words remaining, request recommendations, and respond to recommendations.
- **FR-002**: The system MUST accept a CSV puzzle file and validate it contains exactly 16 non-empty, unique words; invalid files must be rejected with a clear error message before creating a puzzle session.
- **FR-003**: The system MUST initialize and expose puzzle state after a successful setup: remaining words (16 at start), counters (correct groups = 0, mistakes = 0), an empty recommendation, and a cleared previous-attempts history.
- **FR-004**: The system MUST provide a user action to request a recommendation; the recommendation MUST be a group of exactly 4 words plus a human-readable rationale or hint explaining the suggested grouping.
- **FR-005**: If fewer than 4 words remain, the system MUST refuse to produce a new recommendation and surface a user-facing error indicating there are not enough words remaining.
- **FR-006**: When a recommendation is presented, the system MUST allow the user to mark it as correct, incorrect, or one-away; marking a recommendation as correct MUST require the user to select one of the connection colors (Yellow, Green, Blue, Purple).
- **FR-007**: When a recommendation is marked correct and assigned a color, the system MUST record the successful group, remove those words from the remaining words set, increment the correct-groups counter, and persist the attempt in the previous-attempts history with a success indicator and the chosen color.
- **FR-008**: When a recommendation is marked incorrect or one-away, the system MUST record the attempt in the previous-attempts history with the appropriate indicator (incorrect or one-away), increment the mistakes counter, and keep remaining words unchanged.
- **FR-009**: The system MUST treat a "one-away" result as a mistake for game progression while preserving the special one-away indicator in history and (when available) an explanatory rationale.
- **FR-010**: The system MUST disable or otherwise prevent reuse of a connection color after the player assigns it to a found group (so each color maps to at most one found group during a session).
- **FR-011**: The system MUST present counters and status information to the user: number of correct groups found (out of 4), number of mistakes made (out of 4), and number of words remaining.
- **FR-012**: When the correct-groups counter reaches 4, the system MUST transition the game state to success and present a success message; when the mistakes counter reaches 4, the system MUST transition the game state to failure and prevent further recommendation/response actions until a new puzzle is started.
- **FR-013**: The system MUST display a persistent history of previous attempts (timestamped) including attempt words, result (correct/incorrect/one-away), chosen color if any, and any available rationale/hint.
- **FR-014**: The system MUST validate and surface user-facing errors for invalid actions such as: responding when no active recommendation exists, uploading an empty or malformed file, or requesting a recommendation when insufficient words remain.
- **FR-015**: The system MUST preserve puzzle state for the duration of the user's session (in-memory for the current prototype) including remaining words, attempts history, last recommendation, counters, and game status.
- **FR-016**: The system SHOULD provide a brief hint or explanation alongside generated recommendations to help users understand the suggested grouping (this can be a heuristic hint rather than a full ML explanation for the initial release).

### Key Entities
- Puzzle Session / Puzzle State: The complete state for a single puzzle attempt. Includes the initial word set (16 words), the current list of remaining words, the list of placeholder or discovered groups, the attempts history, counters (correct groups found, mistakes made), the last issued recommendation, timestamps, and the current game status (waiting/active/won/lost).

- Word Group: A logical grouping of exactly 4 words that represent a single connection in the puzzle. A Word Group includes a human-readable connection rationale/hint, an optional assigned connection color when marked correct, and a found/not-found status.

- Recommendation: A suggested Word Group presented to the user for evaluation. A Recommendation contains the 4 proposed words plus a short rationale or hint that explains why those words may belong together.

- User Attempt / Previous Response: A recorded user action applied to a recommendation (or ad-hoc guess). Each attempt records the 4 words involved, the result (correct, incorrect, one-away), an optional chosen color (for correct), a timestamp, an indicator whether it was produced from a recommendation, and any optional rationale/hint text attached to the attempt.

- Connection Color: A user-visible label that the player assigns to a found group (Yellow, Green, Blue, Purple). Each color represents one of the four solution slots and is disabled after assignment for the current puzzle session.

- Validation/Error: Structured user-facing validation outcomes (for example: "File must contain exactly 16 words", "All words must be unique", "Not enough words remaining", "No recommendation to respond to"). These are surfaced to the user and prevent invalid state transitions.

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous  
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
