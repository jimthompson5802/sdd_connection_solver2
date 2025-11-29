# UI Domain — Deep Dive

## Overview

The UI is a TypeScript React application (Create React App). Components live under `frontend/src/components/` and are implemented as functional components using TypeScript (`.tsx`). Styling often uses component-scoped `.css` files colocated with components (e.g., `RecommendationDisplay.css`).

## Key files

- `frontend/src/components/PuzzleInterface.tsx` — main puzzle interaction UI.
- `frontend/src/components/RecommendationDisplay.tsx` — displays LLM recommendations.
- `frontend/src/components/EnhancedPuzzleInterface.tsx` — richer interactions.

## Patterns and conventions

- Components are typed with TypeScript and exported as plain React functional components.
- Tests use React Testing Library with files such as `frontend/src/App.test.tsx` and `frontend/src/FullApplicationFlow.test.tsx`.
- Styling: simple `.css` files per component (no global CSS framework evident).

## Example usage (exact path references)

- `frontend/src/services/llm-api.ts` abstracts network calls to the backend recommendation endpoints.

## Implementation guidance

- New UI components should be added under `frontend/src/components/` with a `.tsx` file and an optional accompanying `.css` and `*.test.tsx` test file.
- Prefer passing typed props and keep business logic in services or hooks, not in the top-level component.

---
