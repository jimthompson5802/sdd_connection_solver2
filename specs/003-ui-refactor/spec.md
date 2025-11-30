# Feature Specification: UI Refactor - Persistent Navigation Layout

**Feature Branch**: `003-ui-refactor`  
**Created**: November 29, 2025  
**Status**: Draft  
**Input**: User description: "refactor the web UI to contain the following: Title contains NYT Connections Puzzle Assistant. This should be visible at all times throughout the game. Left Side Bar contains the following list: Start New Game, From File. When the page is first opened, the Main Area contains Select action in Left Side Bar. If the user clicks on From File, do the existing puzzle setup using csv file. The Main Area will be used by the assistant to interact with the user. Ensure no changes in the behavior of all web ui components (e.g., buttons and text area). At the end of the game the current Game Summary and game success or failed message should be displayed in the Main Area in the same relative positions. No changes in backend functionality."

## Clarifications

### Session 2025-11-29

- Q: What should the sidebar width behavior be to balance readability with space efficiency? → A: Minimum width with constraint (min width to ensure readability, max percentage of viewport to prevent excessive space consumption)
- Q: When user clicks "From File" during an active game, should there be a confirmation step to prevent accidental progress loss? → A: No confirmation - immediately show file upload (matches current behavior, maintains behavioral consistency)
- Q: Should the title use fixed/sticky positioning to stay at viewport top when scrolling, or static positioning at document top? → A: Static position - title at document top, visible unless user scrolls (simpler, less intrusive)
- Q: Should "Start New Game" be clickable (performing an action), non-clickable (category label only), or expandable/collapsible? → A: Expandable/collapsible - clicking toggles visibility of sub-items
- Q: What should the initial state of the "Start New Game" expandable section be when the application first loads? → A: Expanded by default

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Initial Application Launch (Priority: P1)

When a user opens the application for the first time or returns to it, they should see a clear, organized interface with persistent navigation that guides them to start a new game.

**Why this priority**: This is the entry point for all users. Without a clear initial state, users won't know how to begin using the application. This establishes the foundational layout pattern that all other interactions build upon.

**Independent Test**: Can be fully tested by opening the application in a browser and verifying that the title, sidebar, and main area appear with the expected content and layout. Delivers immediate value by providing clear navigation and context.

**Acceptance Scenarios**:

1. **Given** the user opens the application URL, **When** the page loads, **Then** the title "NYT Connections Puzzle Assistant" is visible at the top of the page
2. **Given** the user opens the application URL, **When** the page loads, **Then** the left sidebar displays "Start New Game" expanded with the sub-item "From File" visible
3. **Given** the user opens the application URL, **When** the page loads, **Then** the main area displays the message "Select action in Left Side Bar"

---

### User Story 2 - Start New Game from File (Priority: P2)

When a user wants to begin a new puzzle, they should be able to select "From File" in the sidebar and upload a CSV file containing the puzzle data, with the interface transitioning smoothly to display the puzzle in the main area.

**Why this priority**: This is the primary method to initialize a game. It must work seamlessly to enable the core application functionality. Without this, users cannot play puzzles.

**Independent Test**: Can be tested by clicking "From File" in the sidebar and uploading a valid CSV puzzle file, then verifying the puzzle interface appears in the main area with all expected controls and data.

**Acceptance Scenarios**:

1. **Given** the application is in its initial state, **When** the user clicks "From File" in the sidebar, **Then** a file upload interface appears in the main area
2. **Given** the file upload interface is displayed, **When** the user selects and uploads a valid CSV puzzle file, **Then** the puzzle interface replaces the upload interface in the main area
3. **Given** the puzzle interface is displayed, **When** the user interacts with it, **Then** all existing functionality (word selection, recommendations, response recording) works identically to the current implementation
4. **Given** the puzzle interface is displayed, **When** viewing the layout, **Then** the title and sidebar remain visible and in their original positions

---

### User Story 3 - Persistent Navigation During Gameplay (Priority: P2)

During active gameplay, users should have continuous access to navigation options while the puzzle interface occupies the main area, allowing them to restart or navigate without losing context.

**Why this priority**: Users need the ability to start a new game or navigate during gameplay. The persistent sidebar provides this without requiring them to complete or abandon the current game through awkward UI patterns.

**Independent Test**: Can be tested by starting a puzzle and verifying that the sidebar remains accessible throughout gameplay, and that the title stays visible during all interactions.

**Acceptance Scenarios**:

1. **Given** a puzzle is active in the main area, **When** the user views the interface, **Then** the sidebar remains visible and accessible with all navigation options
2. **Given** a puzzle is active, **When** the user clicks "From File" in the sidebar, **Then** the file upload interface appears, allowing them to start a new game
3. **Given** the puzzle interface is displaying recommendations or results, **When** the user looks at the layout, **Then** the sidebar does not overlap or obscure the main content area

---

### User Story 4 - End Game Display (Priority: P3)

When a game concludes (either won or lost), the success/failure message and game summary should display in the main area in their familiar positions, maintaining visual consistency with the current implementation.

**Why this priority**: End-game feedback is important for user satisfaction and provides closure to the game session. While critical for a complete experience, it depends on the prior stories being functional.

**Independent Test**: Can be tested by completing a puzzle (winning or losing) and verifying that the game summary and status message appear in the main area at the same relative positions as in the current implementation.

**Acceptance Scenarios**:

1. **Given** a user has won the puzzle, **When** the final correct group is submitted, **Then** the success message "🎉 Congratulations! You solved the puzzle!" displays in the main area
2. **Given** a user has lost the puzzle, **When** the maximum mistakes are reached, **Then** the failure message "Game Over - Maximum mistakes reached" displays in the main area
3. **Given** the game has concluded, **When** viewing the main area, **Then** the Game Summary component displays at the same relative position as in the current implementation
4. **Given** the game has concluded, **When** viewing the interface, **Then** the title and sidebar remain visible in their expected positions

---

### Edge Cases

- What happens when a user clicks "From File" while a game is already active? The application immediately replaces the game with the file upload interface without confirmation, matching current behavior and maintaining consistency with existing user expectations.
- How does the layout respond to different screen sizes and resolutions? (Responsive design considerations)
- What happens if the sidebar navigation items are numerous enough to require scrolling? (Currently only 2 items, but future-proofing)
- How does the layout handle very long game summaries or previous response lists at the end of the game? (GameSummary component already has scroll handling)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Application MUST display a persistent title "NYT Connections Puzzle Assistant" at the top of the page in a static position, visible in the initial viewport across all application states
- **FR-002**: Application MUST provide a left sidebar containing navigation options organized as a hierarchical list
- **FR-002a**: Left sidebar MUST have a minimum width to ensure navigation text readability, constrained to a maximum percentage of the viewport to prevent excessive screen space consumption
- **FR-003**: Left sidebar MUST include a "Start New Game" section with a sub-item "From File"
- **FR-003a**: "Start New Game" navigation item MUST be expandable/collapsible, with clicking the item toggling the visibility of its sub-items
- **FR-003b**: "Start New Game" section MUST be expanded by default when the application first loads, showing the "From File" sub-item
- **FR-004**: Main content area MUST display context-appropriate content based on user actions and application state
- **FR-005**: Main content area MUST display the message "Select action in Left Side Bar" when the application is in its initial waiting state
- **FR-006**: Application MUST transition from the initial state to the file upload interface when the user selects "From File" in the sidebar
- **FR-007**: Application MUST transition from the file upload interface to the puzzle interface when a valid CSV file is successfully uploaded
- **FR-008**: Puzzle interface MUST maintain all existing functionality including word display, selection, recommendation retrieval, and response recording
- **FR-009**: All existing UI components (buttons, text areas, word selection, color buttons, recommendation display) MUST retain their current behavior without modification
- **FR-010**: Game completion screens MUST display the success message ("🎉 Congratulations! You solved the puzzle!") or failure message ("Game Over - Maximum mistakes reached") in the same relative position within the main area as in the current implementation
- **FR-011**: Game completion screens MUST display the GameSummary component (correct count, mistake count, words remaining, previous responses) in the same relative position within the main area as in the current implementation
- **FR-012**: Title and sidebar MUST remain visible and accessible during all game states (waiting, active, won, lost)
- **FR-013**: Backend API and services MUST remain unchanged with no modifications to endpoints, request/response formats, or business logic

### Key Entities

- **Layout Structure**: Contains three persistent regions: title bar (top), sidebar (left), and main content area (center/right). The title and sidebar remain constant while main area content changes based on application state.
- **Application State**: Determines main area content. States include: waiting (initial/no game), file-upload (selecting puzzle), active (playing game), won (successfully completed), lost (maximum mistakes reached).
- **Navigation Actions**: User-initiated commands from the sidebar that trigger state transitions and main area content updates. Currently includes "From File" action under "Start New Game".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can see the application title "NYT Connections Puzzle Assistant" at the top of the page in the initial viewport, regardless of application state
- **SC-002**: Users can access sidebar navigation options within 0 clicks from any application state (always visible)
- **SC-003**: Users can start a new game by selecting "From File" and uploading a CSV file, with the puzzle interface appearing in the main area within 2 seconds of file upload completion
- **SC-004**: All existing puzzle gameplay functions (word selection, getting recommendations, submitting responses, viewing game summary) work identically to the current implementation with 100% behavioral consistency
- **SC-005**: Game completion displays (win/loss messages and game summary) appear in the same visual positions as the current implementation, maintaining user familiarity
- **SC-006**: Layout transitions between states (waiting → file upload → active game → completed) occur smoothly without content jumping or layout shifts
- **SC-007**: Zero backend changes are required (0 API modifications, 0 service updates, 0 database changes)

## Assumptions

- The current `App.tsx` component manages application state and coordinates between file upload and puzzle interface components
- The existing `FileUpload` component handles CSV file selection and upload
- The existing `EnhancedPuzzleInterface` component handles all puzzle gameplay interactions
- The existing `GameSummary` component displays end-game statistics and previous responses
- The application currently uses a conditional rendering pattern where only one main component (FileUpload or EnhancedPuzzleInterface) is visible at a time
- Users are familiar with the current layout and expect game summary and status messages to appear in consistent positions
- The application is a single-page application (SPA) with no server-side routing
- The layout should be implemented using standard CSS layout techniques (flexbox/grid) without introducing new UI frameworks
- The sidebar navigation will remain simple with minimal items (currently only "Start New Game" → "From File")
- Responsive design is a consideration but not the primary focus of this refactor (desktop-first approach is acceptable)

## Out of Scope

- Adding new gameplay features or modifying puzzle mechanics
- Implementing additional navigation options beyond "From File" (e.g., "From URL", "Random Puzzle")
- Adding authentication or user account management
- Implementing puzzle history or saved games functionality
- Changing backend API structure or functionality
- Adding new LLM providers or modifying LLM integration logic
- Implementing mobile-specific layouts or touch optimizations
- Adding accessibility features beyond maintaining existing ARIA attributes
- Implementing dark mode or theme customization
- Adding animations or transitions beyond smooth content updates
- Modifying the GameSummary component's internal layout or functionality
