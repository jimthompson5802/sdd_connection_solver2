# Feature Specification: Image-Based Puzzle Setup

**Feature Branch**: `004-image-puzzle-setup`  
**Created**: December 13, 2025  
**Status**: Draft  
**Input**: User description: "screenshot puzzle setup - update the left side bar navigation with the following: Add a navigation item called 'From Image' below 'From File' navigation item within the 'Start New Game' Navigation item. When 'From Image' navigation item is clicked, display interface for pasting puzzle image, selecting provider/model, and setting up puzzle. Allow user to paste 4x4 grid image from clipboard. Use LLM with structured output to extract 16 words from image. Return word list in same format as file-based setup."

## Clarifications

### Session 2025-12-13

- Q: The spec states that when an image is pasted, a "preview" is displayed. However, the implementation approach for handling the paste area visual state is ambiguous. → A: Empty placeholder with icon/text prompt ("Paste image here")
- Q: The spec mentions that LLM vision models need to extract words from a 4x4 grid, but doesn't specify the expected word order in the returned list. → A: Left-to-right, top-to-bottom (reading order: row 1 left→right, row 2 left→right, etc.)
- Q: The spec assumes LLM vision models can extract text from grids, but doesn't clarify what happens when a provider/model lacks vision capabilities (e.g., text-only models). → A: Attempt extraction and fail gracefully - return HTTP 400 "Model does not support vision" when LLM call fails

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access Image-Based Puzzle Setup (Priority: P1)

When a user wants to create a puzzle from a screenshot or image of a 4x4 word grid, they should be able to select "From Image" in the sidebar navigation and see an interface for pasting the image and configuring the puzzle extraction.

**Why this priority**: This is the core entry point for the new feature. Without this navigation and interface, users cannot access the image-based puzzle setup capability at all. It establishes the foundation for all subsequent interactions.

**Independent Test**: Can be fully tested by clicking "From Image" in the sidebar and verifying that the main content area displays the image paste area, provider/model dropdowns, and Setup Puzzle button. No backend interaction required.

**Acceptance Scenarios**:

1. **Given** the application is loaded, **When** the user views the left sidebar, **Then** "From Image" appears below "From File" under the expanded "Start New Game" menu
2. **Given** the user clicks "From Image", **When** the main content area updates, **Then** an image paste area with placeholder text and icon prompt, "Provider Type" dropdown, "Model Type" dropdown, and "Setup Puzzle" button are displayed
3. **Given** the image setup interface is displayed, **When** the user views the layout, **Then** the components are arranged vertically matching the specified ASCII diagram layout
4. **Given** the image paste area is displayed with no image pasted, **When** the user views it, **Then** placeholder text ("Paste image here") and keyboard shortcut hint (⌘V/Ctrl+V) are visible

---

### User Story 2 - Paste and Preview Puzzle Image (Priority: P2)

When a user has copied a 4x4 word grid image to their clipboard, they should be able to paste it into the designated area using keyboard shortcuts and see a preview of the pasted image before proceeding with puzzle setup.

**Why this priority**: Image input is essential for the feature but depends on having the interface from User Story 1. This enables users to provide the puzzle data that will be extracted by the LLM.

**Independent Test**: Can be tested by navigating to "From Image", pasting an image using CMD/CTRL+V, and verifying the image appears in the paste area. Does not require LLM extraction to validate the paste functionality works.

**Acceptance Scenarios**:

1. **Given** the image setup interface is displayed, **When** the user presses CMD+V (Mac) or CTRL+V (Windows/Linux) with an image on the clipboard, **Then** the pasted image appears in the designated paste area
2. **Given** an image has been pasted, **When** the user views the paste area, **Then** the image is displayed as a preview showing the 4x4 word grid
3. **Given** the user attempts to paste content that is not an image, **When** the paste occurs, **Then** a clear error message indicates "Please paste a valid image"

---

### User Story 3 - Configure LLM Provider and Model (Priority: P2)

When a user is preparing to extract words from a pasted puzzle image, they should be able to select their preferred LLM provider and specific model using dropdown lists, with the same options available as during puzzle solving.

**Why this priority**: Provider/model configuration is required for the extraction process but is a straightforward UI interaction that doesn't depend on the image being pasted. This allows flexible workflows where users can configure before or after pasting.

**Independent Test**: Can be tested by navigating to "From Image" and verifying the dropdown lists contain valid provider types and model names matching those used in puzzle solving. Selection functionality can be verified without initiating extraction.

**Acceptance Scenarios**:

1. **Given** the image setup interface is displayed, **When** the user clicks the "Provider Type" dropdown, **Then** the same provider options used during puzzle solving are displayed (e.g., OpenAI, Ollama)
2. **Given** a provider type is selected, **When** the user clicks the "Model Type" dropdown, **Then** valid model names for that provider are displayed (e.g., GPT-4, GPT-3.5-turbo for OpenAI)
3. **Given** the user views the dropdowns, **When** no selection has been made, **Then** default values matching existing puzzle solving defaults are pre-selected

---

### User Story 4 - Extract Words from Image and Start Puzzle (Priority: P1)

When a user has pasted a puzzle image and configured the LLM provider/model, they should be able to click "Setup Puzzle" to have the system extract the 16 words from the image and automatically transition to the active puzzle interface.

**Why this priority**: This is the critical integration point that delivers the feature's core value - converting an image into a playable puzzle. It must work reliably for the feature to be useful. This is P1 despite depending on earlier stories because it's the essential end-to-end value delivery.

**Independent Test**: Can be fully tested by pasting a valid 4x4 word grid image, selecting a provider/model, clicking "Setup Puzzle", and verifying that 16 words are extracted and the puzzle interface appears with those words ready to play.

**Acceptance Scenarios**:

1. **Given** an image is pasted and provider/model are selected, **When** the user clicks "Setup Puzzle", **Then** the system calls the backend API with base64-encoded image, MIME type, provider type, and model name
2. **Given** the backend successfully extracts 16 words from the image, **When** the API response is received, **Then** the application transitions to the puzzle-active view displaying the extracted words in the puzzle interface
3. **Given** the puzzle is set up from an image, **When** the puzzle interface loads, **Then** all existing gameplay features (word selection, recommendations, submission) work identically to file-based puzzles
4. **Given** the user clicks "Setup Puzzle" without pasting an image, **When** validation occurs, **Then** an error message displays "Please paste a puzzle image first"

---

### User Story 5 - Handle Image Size and Extraction Errors (Priority: P3)

When a user attempts to set up a puzzle from an image, the system should validate image size constraints and handle extraction errors gracefully, providing clear feedback about what went wrong and how to proceed.

**Why this priority**: Error handling improves user experience but is not required for the happy path to work. This can be implemented after core functionality is proven. Users can work around errors by trying different images or providers.

**Independent Test**: Can be tested independently by attempting to paste images larger than 5MB, images that don't contain a clear 4x4 grid, or by simulating LLM provider failures, then verifying appropriate error messages are displayed.

**Acceptance Scenarios**:

1. **Given** the user attempts to paste an image larger than 5MB, **When** the Setup Puzzle button is clicked, **Then** the system returns HTTP 413 with message "Payload too large" and displays this to the user
2. **Given** the LLM cannot extract exactly 16 words from the pasted image, **When** the extraction completes, **Then** the system returns HTTP 400 with message "Could not extract 16 words" and the user remains on the image setup interface
3. **Given** a model without vision capabilities is selected, **When** the Setup Puzzle button is clicked, **Then** the system returns HTTP 400 with message "Model does not support vision" and the user can select a vision-capable model
4. **Given** the LLM provider encounters a failure during extraction, **When** the error occurs, **Then** the system returns HTTP 500 with message "Internal error: LLM provider failure" and the user can retry with a different provider or image
5. **Given** an error occurs during setup, **When** the error message is displayed, **Then** the pasted image and provider/model selections are preserved so the user can adjust and retry without starting over

---

### Edge Cases

- What happens when the pasted image contains text but not in a clear 4x4 grid format? The LLM extraction will fail to identify exactly 16 words, returning HTTP 400 with "Could not extract 16 words" error message, allowing the user to try a different image.
- How does the system handle images with words that are partially obscured or unclear? The LLM will attempt extraction with its vision capabilities; if successful, the words are returned even if imperfect; if the LLM cannot confidently extract 16 words, it returns the "Could not extract 16 words" error.
- What happens when a user selects a model without vision capabilities (e.g., text-only model)? The backend attempts the extraction, detects the model limitation, and returns HTTP 400 with "Model does not support vision" error message, prompting the user to select a vision-capable model.
- What happens if the user pastes multiple images in succession before clicking Setup Puzzle? Only the most recently pasted image is retained and displayed in the preview area, replacing any previous image.
- How does the system behave if the user switches between "From File" and "From Image" multiple times? Each navigation action clears the previous state - switching to "From Image" shows a fresh interface, and switching to "From File" shows the file upload interface without any image data.
- What happens when the user has an active game and clicks "From Image"? Following existing behavior from "From File", the application immediately switches to the image setup interface without confirmation, abandoning the current game state.
- How does the system handle clipboard paste when no image data is present? The paste operation is ignored with an error message "Please paste a valid image", and the paste area remains empty or shows the previously pasted image if any.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Left sidebar navigation MUST include a new "From Image" menu item positioned directly below the existing "From File" item under "Start New Game"
- **FR-002**: Clicking "From Image" MUST display an interface in the main content area containing an image paste area, "Provider Type" dropdown, "Model Type" dropdown, and "Setup Puzzle" button
- **FR-002a**: Image paste area MUST display placeholder text ("Paste image here") and keyboard shortcut hint (⌘V/Ctrl+V) when no image has been pasted, providing clear visual affordance for the paste action
- **FR-003**: Image paste area MUST support keyboard-based paste operations (CMD+V on Mac, CTRL+V on Windows/Linux) to insert image data from the system clipboard
- **FR-004**: Image paste area MUST NOT support drag-and-drop operations (explicitly out of scope)
- **FR-005**: When an image is pasted, the system MUST display a preview of the pasted image in the designated paste area
- **FR-006**: "Provider Type" dropdown MUST contain the same LLM provider options available during puzzle solving (e.g., OpenAI, Ollama, Simple provider)
- **FR-007**: "Model Type" dropdown MUST contain valid model names for the selected provider, matching those available during puzzle solving
- **FR-008**: Provider and model dropdowns MUST have default values pre-selected matching the defaults used in puzzle solving
- **FR-009**: Clicking "Setup Puzzle" button MUST validate that an image has been pasted and return an error message "Please paste a puzzle image first" if no image is present
- **FR-010**: When "Setup Puzzle" is clicked with a valid image, the system MUST encode the image as base64 content and determine the MIME type (e.g., image/png, image/jpeg)
- **FR-011**: System MUST validate that the image size does not exceed 5MB before sending to the backend
- **FR-012**: If image exceeds 5MB, the system MUST display HTTP 413 error with message "Payload too large" without calling the backend
- **FR-013**: Frontend MUST call backend endpoint `/api/v2/setup_puzzle_from_image` with JSON payload containing `image_base64`, `image_mime`, `provider_type`, and `model_name`
- **FR-014**: Backend endpoint `/api/v2/setup_puzzle_from_image` MUST connect to the specified LLM provider and model
- **FR-015**: Backend MUST invoke the LLM using `with_structured_output()` method to extract exactly 16 words from the image
- **FR-016**: LLM invocation MUST extract words from the 4x4 grid cells in the pasted image
- **FR-016a**: Extracted words MUST be ordered left-to-right, top-to-bottom (reading order): positions [0-3] from row 1, positions [4-7] from row 2, positions [8-11] from row 3, positions [12-15] from row 4
- **FR-017**: Upon successful extraction of 16 words, backend MUST return HTTP 200 with JSON containing `remaining_words` (list of 16 words) and `status: "success"`
- **FR-018**: The word list format returned by image-based setup MUST match the format returned by file-based setup to ensure compatibility with existing puzzle initialization
- **FR-019**: If LLM cannot extract exactly 16 words, backend MUST return HTTP 400 with JSON containing `status: "error"` and `message: "Could not extract 16 words"`
- **FR-019a**: If selected model does not support vision/image analysis capabilities, backend MUST return HTTP 400 with JSON containing `status: "error"` and `message: "Model does not support vision"`
- **FR-020**: If request is missing required fields, backend MUST return HTTP 422 with JSON containing `status: "error"` and `message: "Unprocessable Entity: missing fields"`
- **FR-021**: If LLM provider fails or encounters an error, backend MUST return HTTP 500 with JSON containing `status: "error"` and `message: "Internal error: LLM provider failure"`
- **FR-022**: Upon successful word extraction, the application MUST transition to the puzzle-active view displaying the extracted words
- **FR-023**: Once puzzle is set up from image, all existing puzzle gameplay functionality MUST work identically to file-based puzzles (word selection, recommendations, submission, game completion)
- **FR-024**: System MUST support only single-user, single-session operation (multi-user/multi-session explicitly out of scope)
- **FR-025**: OCR-based text extraction is explicitly out of scope; only LLM vision capabilities with structured output are used

### Key Entities

- **Puzzle Image**: Image data containing a 4x4 grid of words. Key attributes: base64-encoded content, MIME type (image/png, image/jpeg), size in bytes (max 5MB). Represents the user's input for image-based puzzle setup.
- **Image Setup Request**: API request payload sent from frontend to backend. Attributes: base64 image content, image MIME type, LLM provider type, LLM model name. Contains all information needed for backend to perform word extraction.
- **Extracted Word List**: Collection of 16 words extracted by LLM from the puzzle image. Attributes: ordered list of word strings (left-to-right, top-to-bottom from grid), status indicator. Must match the format of word lists from file-based setup for compatibility.
- **LLM Provider Configuration**: User-selected LLM provider and model for image processing. Attributes: provider type string, model name string. Must correspond to valid provider/model combinations available in the application.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can access the image-based puzzle setup interface within 1 click from the initial application state (clicking "From Image" in sidebar)
- **SC-002**: Users can paste a puzzle image from the clipboard and see a preview of that image in under 2 seconds from the paste action
- **SC-003**: System successfully extracts 16 words from a clear 4x4 grid image and initializes a playable puzzle in under 10 seconds from clicking "Setup Puzzle"
- **SC-004**: Word extraction accuracy matches the visible words in the source image for 95% of clear, well-formatted 4x4 grid images
- **SC-005**: All error conditions (oversized image, extraction failure, missing fields, provider failure) return appropriate HTTP status codes and user-friendly error messages within 3 seconds
- **SC-006**: Puzzles created from images behave identically to file-based puzzles, with 100% feature parity for gameplay interactions (selection, recommendations, submission, completion)
- **SC-007**: Image setup interface layout matches the specified ASCII diagram layout, with all components positioned vertically and clearly labeled
- **SC-008**: Users can successfully create and play puzzles from images using any supported LLM provider (OpenAI, Ollama, Simple) with consistent behavior across providers

## Assumptions

- Users have puzzle images readily available on their clipboard (e.g., from screenshots or copying images from websites)
- Puzzle images contain a clearly visible 4x4 grid with one word per cell
- Words in the puzzle images are in English and use standard fonts/formatting that LLMs can recognize
- LLM vision models (particularly GPT-4 Vision or equivalent) have sufficient capability to accurately identify text in grid layouts
- The existing backend LLM provider infrastructure supports models with vision capabilities and structured output
- Image MIME types are limited to common formats: image/png, image/jpeg, image/gif, image/webp
- The 5MB size limit is sufficient for typical puzzle screenshot images while preventing abuse
- Users understand that OCR is not being used; the feature relies on LLM vision capabilities which may have different accuracy characteristics
- Network bandwidth and LLM API latency allow for reasonable response times when sending base64-encoded images
- Existing puzzle setup and gameplay code can accept word lists from any source (file or image) without modification
- The application's session management for single-user operation is sufficient and does not require changes for image-based setup
