# Style Guide — frontend-tests

Unique conventions:

- Use React Testing Library and Jest-like syntax; tests are located under `frontend/src/` and named `*.test.tsx`.
- Full application flow tests exist (`FullApplicationFlow.test.tsx`) for end-to-end scenarios within the CRA test runner.
- Use `jest-fetch-mock` or similar to mock backend calls where appropriate.

File examples: `frontend/src/FullApplicationFlow.test.tsx`, `frontend/src/App.test.tsx`.
