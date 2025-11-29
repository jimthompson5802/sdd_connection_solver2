# Style Guide — frontend-components

Unique conventions:

- Components are TypeScript `.tsx` files under `frontend/src/components/`.
- Styling is done with component-scoped `.css` files next to components (e.g., `RecommendationDisplay.css`).
- Tests use React Testing Library; create `*.test.tsx` files adjacent to the components for integration-like behaviors.
- Keep side-effectful code and API calls in `frontend/src/services/*` rather than in component bodies.

File examples: `frontend/src/components/PuzzleInterface.tsx`, `frontend/src/components/RecommendationDisplay.tsx`.
