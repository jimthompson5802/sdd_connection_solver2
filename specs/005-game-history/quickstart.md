# Quickstart Guide: Game History Feature

**Feature**: Game History and Persistent Storage
**Branch**: `005-game-history`
**Date**: 2025-12-24

## Overview

This guide provides step-by-step instructions for developers to set up, develop, test, and validate the game history feature. Follow these instructions to implement persistent game storage with SQLite backend and React frontend enhancements.

---

## Prerequisites

Ensure your development environment meets these requirements:

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **Git**: Current branch `005-game-history`
- **IDE**: VS Code (recommended) or similar
- **Terminal**: bash/zsh on macOS/Linux

**Verify Prerequisites**:
```bash
python3 --version  # Should be 3.11+
node --version     # Should be 18+
git branch        # Should show 005-game-history
```

---

## Initial Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies (including dev dependencies)
pip install -e ".[dev]"

# Verify installation
python -c "import fastapi, pydantic, sqlite3; print('Backend dependencies OK')"
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Verify installation
npm run type-check  # Should pass with no errors
```

### 3. Database Setup

```bash
# Create database directory (if not exists)
mkdir -p backend/data

# The database file will be created automatically on first run
# Default location: backend/data/connect_puzzle_game.db
```

---

## Development Workflow

### Phase 1: Backend Implementation

#### Step 1: Database Schema and Service

1. **Create database schema file**:
   - File: `backend/src/database/schema.sql`
   - Copy schema from `specs/005-game-history/data-model.md`
   - Includes table definition, indexes, and constraints

2. **Implement database service**:
   - File: `backend/src/services/database_service.py`
   - Methods: `init_db()`, `get_connection()`, `close_connection()`
   - Enable WAL mode and foreign key constraints
   - Singleton pattern for connection management

3. **Test database operations**:
   ```bash
   cd backend
   pytest tests/test_database_service.py -v
   ```

#### Step 2: Enhance PuzzleSession Model

1. **Update models.py**:
   - File: `backend/src/models.py`
   - Add fields: `puzzle_id`, `llm_provider_name`, `llm_model_name`
   - Add method: `generate_puzzle_id()` (UUID v5 logic)
   - Add method: `to_game_result(game_date)` (conversion helper)
   - Add computed properties: `is_finished`, `groups_found_count`, `total_guesses_count`

2. **Test session enhancements**:
   ```bash
   pytest tests/test_models.py::test_puzzle_id_generation -v
   pytest tests/test_models.py::test_to_game_result -v
   ```

#### Step 3: Update RecommendationService

1. **Enhance recommendation service**:
   - File: `backend/src/services/recommendation_service.py`
   - After generating recommendation, capture:
     ```python
     session.llm_provider_name = authoritative_request.llm_provider.llm_type
     session.llm_model_name = authoritative_request.llm_provider.model_name
     ```
   - Ensure provider and model names are captured from the authoritative LLM request

2. **Test LLM info capture**:
   ```bash
   pytest tests/test_recommendation_service.py::test_llm_info_recorded -v --llm_mock
   ```

#### Step 4: Implement GameResultsService

1. **Create game results service**:
   - File: `backend/src/services/game_results_service.py`
   - Method: `record_game(session_id, game_date) -> GameResult`
   - Method: `get_game_history() -> List[GameResult]`
   - Method: `export_csv() -> str` (CSV generation)
   - Handle uniqueness check, validation, error cases

2. **Test service layer**:
   ```bash
   pytest tests/test_game_results_service.py -v
   ```

#### Step 5: Implement API Endpoints

1. **Create API router**:
   - File: `backend/src/api/v2_game_results.py`
   - Endpoint: `POST /api/v2/game_results`
   - Endpoint: `GET /api/v2/game_results`
   - CSV export via query parameter: `?format=csv`
   - Use dependency injection for service layer

2. **Register router in main.py**:
   ```python
   from src.api.v2_game_results import router as game_results_router
   app.include_router(game_results_router)
   ```

3. **Test API endpoints**:
   ```bash
   pytest tests/test_game_results_api.py -v --integration
   ```

#### Step 6: Run Backend Development Server

```bash
cd backend
source .venv/bin/activate
export PYTHONPATH=src
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Verify endpoints**:
- Swagger UI: http://localhost:8000/docs
- Check for `/api/v2/game_results` endpoints

---

### Phase 2: Frontend Implementation

#### Step 1: Create TypeScript Types

1. **Define interfaces**:
   - File: `frontend/src/types/gameResults.ts`
   - Interfaces: `GameResult`, `RecordGameRequest`, `RecordGameResponse`, `GameHistoryResponse`
   - Copy from `specs/005-game-history/contracts/api_contracts.md`

2. **Type-check**:
   ```bash
   cd frontend
   npm run type-check
   ```

#### Step 2: Implement API Service Client

1. **Create service client**:
   - File: `frontend/src/services/gameResultsService.ts`
   - Methods: `recordGame()`, `fetchGameHistory()`, `exportCSV()`
   - Use fetch API with proper error handling
   - Base URL: `http://localhost:8000/api/v2`

2. **Test service (manual)**:
   - Start backend server
   - Create test file to call service methods
   - Verify network requests in browser DevTools

#### Step 3: Enhance GameSummary Component

1. **Add "Record Game" button**:
   - File: `frontend/src/components/GameSummary.tsx`
   - Import `gameResultsService`
   - Add button with onClick handler
   - Implement loading state (disable during POST)
   - Show success/error messages

2. **Update component styles**:
   - File: `frontend/src/components/GameSummary.css` (if needed)
   - Style button consistently with existing UI

3. **Test component**:
   ```bash
   npm test GameSummary.test.tsx
   ```

#### Step 4: Create RecordGameButton Component

1. **Extract button logic** (optional, for reusability):
   - File: `frontend/src/components/RecordGameButton.tsx`
   - Props: `sessionId`, `gameDate`, `onSuccess`, `onError`
   - Handles API call, loading state, error display

2. **Test component**:
   ```bash
   npm test RecordGameButton.test.tsx
   ```

#### Step 5: Update Sidebar Navigation

1. **Add "Game History" section**:
   - File: `frontend/src/components/Sidebar.tsx`
   - Add collapsible section below "Start New Game"
   - Sub-item: "View Past Games" (links to `/game-history`)
   - Default state: collapsed

2. **Test navigation**:
   ```bash
   npm test Sidebar.test.tsx
   ```

#### Step 6: Create GameHistoryView Component

1. **Implement game history table**:
   - File: `frontend/src/components/GameHistoryView.tsx`
   - Fetch data on mount: `useEffect(() => { fetchGameHistory() }, [])`
   - Display scrollable table with columns from spec
   - Handle empty state with message
   - Add "Export CSV" button below table

2. **Style table**:
   - File: `frontend/src/components/GameHistoryView.css`
   - Scrollable table (horizontal + vertical)
   - Responsive design for different screen sizes

3. **Test component**:
   ```bash
   npm test GameHistoryView.test.tsx
   ```

#### Step 7: Add Routing (if needed)

If using React Router, add route for game history:
```typescript
<Route path="/game-history" element={<GameHistoryView />} />
```

#### Step 8: Run Frontend Development Server

```bash
cd frontend
npm start
```

**Verify in browser** (http://localhost:3000):
- Complete a game
- Click "Record Game" button
- Navigate to "Game History" > "View Past Games"
- Verify table displays recorded game
- Click "Export CSV" and verify download

---

## Testing Guide

### Backend Testing

#### Run All Tests
```bash
cd backend
source .venv/bin/activate
pytest tests/ -v --cov=src --cov-report=term-missing
```

#### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/ -v -m "not integration and not contract"

# Integration tests
pytest tests/ -v -m integration

# Contract tests (API)
pytest tests/ -v -m contract

# LLM mock tests
pytest tests/ -v -m llm_mock
```

#### Test Coverage Requirements
- **Minimum**: 80% (enforced in `pyproject.toml`)
- **Target**: 90%+ for new service and API code
- View HTML report: `open backend/htmlcov/index.html`

### Frontend Testing

#### Run All Tests
```bash
cd frontend
npm test -- --coverage --watchAll=false
```

#### Run Specific Test Files
```bash
npm test GameHistoryView.test.tsx
npm test RecordGameButton.test.tsx
npm test Sidebar.test.tsx
```

#### Test Coverage Requirements
- **Target**: 75%+ for new components
- View coverage report in terminal output

### Manual Testing Checklist

**User Story 1: Record Game**
- [ ] Complete a puzzle (win or lose)
- [ ] "Record Game" button appears on summary page
- [ ] Click button → success message appears
- [ ] Try recording same puzzle again → error message appears
- [ ] Button disabled during recording (no double-click)

**User Story 2: View Game History**
- [ ] Navigate to "Game History" in sidebar
- [ ] Click "View Past Games"
- [ ] Table displays with recorded games
- [ ] Most recent game appears first
- [ ] All columns show correct data
- [ ] Table scrolls if many records

**User Story 3: Export CSV**
- [ ] Click "Export CSV" button
- [ ] File downloads with name `game_results_extract.csv`
- [ ] Open CSV in spreadsheet app
- [ ] Verify headers and data format

**Edge Cases**
- [ ] Try recording incomplete game → error message
- [ ] View history with no games → empty state message
- [ ] Export CSV with no games → header-only file
- [ ] Refresh page after recording → data persists
- [ ] Close and reopen app → data persists

---

## Code Quality Checks

### Backend (Python)

```bash
cd backend

# Type checking
mypy src/

# Code formatting (check only)
black --check src/ tests/

# Code formatting (auto-fix)
black src/ tests/

# Run all quality checks
mypy src/ && black --check src/ tests/ && pytest tests/ -v
```

### Frontend (TypeScript)

```bash
cd frontend

# Type checking
npm run type-check

# Linting
npm run lint

# Code formatting (check only)
npm run format -- --check

# Code formatting (auto-fix)
npm run format

# Run all quality checks
npm run type-check && npm run lint && npm test -- --watchAll=false
```

---

## Debugging Tips

### Backend Debugging

**Database Issues**:
```bash
# Check if database file exists
ls -lh backend/data/connect_puzzle_game.db

# Inspect database schema
sqlite3 backend/data/connect_puzzle_game.db ".schema"

# View all records
sqlite3 backend/data/connect_puzzle_game.db "SELECT * FROM game_results;"

# Check indexes
sqlite3 backend/data/connect_puzzle_game.db ".indexes game_results"
```

**API Debugging**:
```bash
# View API logs (uvicorn output)
# Look for error tracebacks and HTTP status codes

# Test endpoint directly with curl
curl -X POST "http://localhost:8000/api/v2/game_results" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-uuid", "game_date": "2025-12-24T15:30:00-08:00"}' \
  -v
```

### Frontend Debugging

**Network Issues**:
- Open browser DevTools (F12)
- Navigate to "Network" tab
- Filter by "Fetch/XHR"
- Check request/response for errors

**Console Errors**:
- Check browser console for JavaScript errors
- Look for CORS issues (should not occur with localhost)
- Verify API base URL is correct

**Component Issues**:
- Use React DevTools extension
- Inspect component state and props
- Check useEffect dependencies

---

## Environment Configuration

### Backend Environment Variables

Create `.env` file in `backend/` directory:
```bash
# Database configuration
DATABASE_PATH=data/connect_puzzle_game.db
ENABLE_PERSISTENCE=true

# API configuration
API_HOST=127.0.0.1
API_PORT=8000

# LLM provider keys (existing)
OPENAI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

### Frontend Environment Variables

Create `.env` file in `frontend/` directory:
```bash
REACT_APP_API_BASE_URL=http://localhost:8000/api/v2
```

---

## Common Issues and Solutions

### Issue: Database locked error
**Solution**: Ensure no other process is accessing the database. Close any SQLite browser tools.

### Issue: CORS errors in frontend
**Solution**: Verify backend is running on localhost:8000. Check FastAPI CORS middleware configuration.

### Issue: Tests failing with "session not found"
**Solution**: Ensure test fixtures create and register sessions in SessionManager before API calls.

### Issue: CSV export shows wrong column order
**Solution**: Verify csv.DictWriter fieldnames match the spec exactly. Check data-model.md for correct order.

### Issue: Duplicate games not prevented
**Solution**: Verify UNIQUE index exists: `sqlite3 backend/data/connect_puzzle_game.db ".indexes game_results"`

---

## Performance Validation

### Load Testing (Optional)

```bash
# Install pytest-benchmark
pip install pytest-benchmark

# Run performance tests
pytest tests/test_game_results_performance.py --benchmark-only
```

**Target Metrics**:
- POST /api/v2/game_results: < 50ms (local SQLite insert)
- GET /api/v2/game_results: < 100ms (up to 100 records)
- CSV export: < 500ms (up to 100 records)

---

## Deployment Checklist

Before merging to main branch:

**Code Quality**
- [ ] All tests passing (backend 80%+ coverage)
- [ ] mypy type checking passes
- [ ] black/prettier formatting applied
- [ ] No console.log or debug prints left in code

**Functionality**
- [ ] All user stories manually tested
- [ ] Edge cases handled with appropriate errors
- [ ] CSV export format validated
- [ ] Database migrations documented (if any)

**Documentation**
- [ ] README updated with game history feature
- [ ] API endpoints documented in OpenAPI/Swagger
- [ ] Database schema documented
- [ ] CSV export format documented

**Performance**
- [ ] Tested with 100+ game records
- [ ] No memory leaks in frontend
- [ ] Database queries optimized (indexes in place)

---

## Next Steps

After completing implementation:

1. **Code Review**: Create PR for `005-game-history` branch
2. **Integration Testing**: Test full flow end-to-end
3. **Documentation**: Update main README with feature description
4. **User Acceptance**: Demo feature to stakeholders
5. **Merge**: Merge to main after approval

---

## Support and Resources

**Documentation References**:
- Feature Spec: `specs/005-game-history/spec.md`
- Data Model: `specs/005-game-history/data-model.md`
- API Contracts: `specs/005-game-history/contracts/api_contracts.md`
- Research: `specs/005-game-history/research.md`

**External Resources**:
- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLite Docs: https://www.sqlite.org/docs.html
- React Docs: https://react.dev/
- TypeScript Docs: https://www.typescriptlang.org/docs/

**Constitution**: `.specify/memory/constitution.md`

---

## Summary

This quickstart guide provides a complete development workflow for the game history feature. Follow the steps in order, run tests frequently, and validate against acceptance scenarios. The feature maintains constitution compliance with local-first architecture, type safety, and comprehensive testing.

Happy coding! 🚀
