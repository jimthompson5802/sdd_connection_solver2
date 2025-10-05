# Feature Specification: LLM Provider Integration for Connection Puzzle Solver

**Feature Branch**: `002-in-phase-2`  
**Created**: October 5, 2025  
**Status**: Draft  
**Input**: User description: "In phase 2 we will extend the backend services to support integratation with various LLM providers. The goal is to create a flexible and modular system that can easily switch between different LLM providers based on configuration."

## Execution Flow (main)
```
1. Parse user description from Input
   → Identified: LLM integration, flexible provider switching
2. Extract key concepts from description
   → Actors: Users solving puzzles, LLM providers
   → Actions: Select provider, generate recommendations, switch providers
   → Data: Provider configuration, puzzle words, recommendations
   → Constraints: Specific connection types, no previous guesses
3. For each unclear aspect:
   → All requirements clarified in detailed user input
4. Fill User Scenarios & Testing section
   → Clear user flow for provider selection and recommendation generation
5. Generate Functional Requirements
   → All requirements testable and specific
6. Identify Key Entities
   → LLM Provider, Recommendation, Puzzle State
7. Run Review Checklist
   → No implementation details included
   → Focus on user value and business needs
8. Return: SUCCESS (spec ready for planning)
```

---

## User Scenarios & Testing

### Primary User Story
A user solving a connection puzzle wants to choose between a simple algorithm or AI-powered recommendations to help them find groups of connected words. They can select their preferred LLM provider and model, then receive intelligent suggestions that avoid repeating previous guesses and focus on specific, meaningful connections.

### Acceptance Scenarios
1. **Given** a puzzle with remaining words, **When** user selects "simple" provider and clicks "Next Recommendation", **Then** system returns first 4 words from remaining list
2. **Given** a puzzle with remaining words, **When** user selects "ollama:llama2" provider and clicks "Next Recommendation", **Then** system generates AI-powered recommendation with 4 connected words and explanation
3. **Given** previous incorrect guesses exist, **When** user requests LLM recommendation, **Then** system excludes all previously guessed words from new recommendation
4. **Given** user enters invalid provider format, **When** user attempts to get recommendation, **Then** system displays clear error message about valid formats

### Edge Cases
- What happens when LLM provider is unavailable or returns error?
- How does system handle when fewer than 4 words remain?
- What occurs if LLM returns invalid word selections (words not in remaining list)?
- How does system respond when LLM fails to provide specific connection reasoning?

## Requirements

### Functional Requirements
- **FR-001**: System MUST provide text input field labeled "LLM Provider" on web interface above file chooser
- **FR-001a**: System MUST reset LLM Provider selection to default value at start of each new session
- **FR-001b**: System MUST set default LLM Provider value to "simple" when user first visits application
- **FR-002**: System MUST accept "simple" as valid LLM provider value to use existing Phase 1 algorithm
- **FR-003**: System MUST accept "<llm_provider>:<llm_model>" format where llm_provider is "ollama" or "openai"
- **FR-003a**: System MUST obtain LLM provider credentials from backend environment variables only
- **FR-004**: System MUST route recommendations to appropriate provider based on LLM Provider selection
- **FR-005**: System MUST generate prompts for LLM that include remaining puzzle words, previous guesses, and guess outcomes
- **FR-006**: System MUST ensure LLM prompts request specific connections (e.g., "words are fishes") not general ones (e.g., "all words are verbs")
- **FR-007**: System MUST validate that LLM recommendations contain exactly 4 words from remaining puzzle words
- **FR-007a**: System MUST display error message when LLM returns invalid word count or words not in remaining list
- **FR-008**: System MUST exclude all previously guessed words from new recommendations
- **FR-009**: System MUST handle LLM provider errors gracefully with user-friendly error messages
- **FR-009a**: System MUST display persistent loading indicator while waiting for LLM response without timeout
- **FR-010**: System MUST maintain backward compatibility with existing Phase 1 simple recommendation functionality

### Key Entities
- **LLM Provider**: Represents external AI service configuration including provider type (ollama, openai) and specific model identifier
- **Recommendation Request**: Contains puzzle state, remaining words, previous guesses with outcomes, and selected provider configuration
- **Recommendation Response**: Contains 4 recommended words, connection explanation, and confidence indicators
- **Puzzle State**: Tracks remaining words, previous guesses, guess outcomes (correct, incorrect, one-away), and current recommendation context

---

## Clarifications

### Session 2025-10-05
- Q: When an LLM provider takes too long to respond or becomes unresponsive, what should happen to the user experience? → A: Show loading indicator indefinitely until response received
- Q: Where should the user's LLM provider selection be persisted between sessions? → A: Session memory only (resets each visit)
- Q: What should be the default value in the "LLM Provider" text field when a user first visits the application? → A: "simple" (existing Phase 1 algorithm)
- Q: When an LLM returns a response that doesn't contain exactly 4 valid words from the remaining puzzle words, what should the system do? → A: Show error message and ask user to try again
- Q: For LLM providers that require API keys or authentication (like OpenAI), how should the system handle credentials? → A: Use environment variables on backend only

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
- [ ] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [ ] User description parsed
- [ ] Key concepts extracted
- [ ] Ambiguities marked
- [ ] User scenarios defined
- [ ] Requirements generated
- [ ] Entities identified
- [ ] Review checklist passed

---
