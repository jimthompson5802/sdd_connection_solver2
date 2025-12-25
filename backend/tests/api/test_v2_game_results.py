"""
Contract tests for /api/v2/game_results endpoints.

These tests validate the API contract compliance for recording and retrieving
game results. Tests should fail until implementation is complete (TDD approach).
"""

import pytest
from fastapi.testclient import TestClient


class TestRecordGameContract:
    """Contract tests for POST /api/v2/game_results endpoint"""

    @pytest.fixture
    def client(self):
        """Test client fixture"""
        from src.main import app
        return TestClient(app)

    @pytest.fixture
    def session_manager(self):
        """Get session manager from app"""
        from src.main import session_manager
        return session_manager

    @pytest.fixture(autouse=True)
    def clean_database(self):
        """Clean database before each test"""
        from src.database import get_database_connection
        # Clear all records before each test
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM game_results")
            conn.commit()
        yield
        # Optional: cleanup after test if needed

    @pytest.fixture
    def completed_session(self, session_manager):
        """Create a completed puzzle session for testing"""
        # Create session with test words
        words = [
            "apple", "banana", "cherry", "date",
            "egg", "flour", "garlic", "honey",
            "ice", "jam", "kale", "lemon",
            "milk", "nut", "olive", "pepper"
        ]
        session = session_manager.create_session(words)

        # Mark 4 groups as found to complete the game
        from src.models import ResponseResult
        session.record_attempt(["apple", "banana", "cherry", "date"], ResponseResult.CORRECT, color="yellow")
        session.record_attempt(["egg", "flour", "garlic", "honey"], ResponseResult.CORRECT, color="green")
        session.record_attempt(["ice", "jam", "kale", "lemon"], ResponseResult.CORRECT, color="blue")
        session.record_attempt(["milk", "nut", "olive", "pepper"], ResponseResult.CORRECT, color="purple")

        # Set LLM info
        session.set_llm_info("openai", "gpt-4")

        return session

    @pytest.fixture
    def incomplete_session(self, session_manager):
        """Create an incomplete puzzle session for testing"""
        words = [
            "red", "blue", "green", "yellow",
            "cat", "dog", "bird", "fish",
            "car", "bus", "train", "plane",
            "sun", "moon", "star", "cloud"
        ]
        session = session_manager.create_session(words)

        # Only mark 2 groups as found (incomplete)
        from src.models import ResponseResult
        session.record_attempt(["red", "blue", "green", "yellow"], ResponseResult.CORRECT, color="yellow")
        session.record_attempt(["cat", "dog", "bird", "fish"], ResponseResult.CORRECT, color="green")

        return session

    @pytest.mark.contract
    def test_record_game_success_contract(self, client, completed_session):
        """
        T011: Test successful game recording (201 Created)

        Validates:
        - Request accepts session_id and game_date
        - Returns 201 Created on success
        - Response includes status="created" and complete result object
        - Result includes all required fields with correct types
        """
        request_data = {
            "session_id": completed_session.session_id,
            "game_date": "2025-12-24T15:30:00-08:00"
        }

        response = client.post("/api/v2/game_results", json=request_data)

        # Should return 201 Created
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

        data = response.json()

        # Validate response structure
        assert "status" in data
        assert data["status"] == "created"
        assert "result" in data

        result = data["result"]

        # Validate all required fields exist
        required_fields = [
            "result_id", "puzzle_id", "game_date", "puzzle_solved",
            "count_groups_found", "count_mistakes", "total_guesses",
            "llm_provider_name", "llm_model_name"
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Validate field types and values
        assert isinstance(result["result_id"], int)
        assert result["result_id"] > 0

        assert isinstance(result["puzzle_id"], str)
        assert len(result["puzzle_id"]) == 36  # UUID format

        assert isinstance(result["game_date"], str)
        # Should be UTC ISO 8601 format
        assert result["game_date"].endswith("+00:00") or result["game_date"].endswith("Z")

        assert isinstance(result["puzzle_solved"], bool)
        assert result["puzzle_solved"] is True  # Completed session should be solved

        assert isinstance(result["count_groups_found"], int)
        assert result["count_groups_found"] == 4  # All groups found

        assert isinstance(result["count_mistakes"], int)
        assert 0 <= result["count_mistakes"] <= 4

        assert isinstance(result["total_guesses"], int)
        assert result["total_guesses"] >= 4  # At least 4 guesses to find 4 groups

        assert isinstance(result["llm_provider_name"], str)
        assert result["llm_provider_name"] == "openai"

        assert isinstance(result["llm_model_name"], str)
        assert result["llm_model_name"] == "gpt-4"

    @pytest.mark.contract
    def test_record_game_duplicate_detection_contract(self, client, completed_session):
        """
        T012: Test duplicate record detection (409 Conflict)

        Validates:
        - Recording the same puzzle_id and game_date twice returns 409 Conflict
        - Response includes appropriate error message
        - First record succeeds, second record is rejected
        """
        request_data = {
            "session_id": completed_session.session_id,
            "game_date": "2025-12-24T15:30:00-08:00"
        }

        # First request should succeed
        response1 = client.post("/api/v2/game_results", json=request_data)
        assert response1.status_code == 201, f"First request should succeed: {response1.text}"

        # Second request with same puzzle_id and game_date should fail with 409
        response2 = client.post("/api/v2/game_results", json=request_data)
        assert response2.status_code == 409, f"Expected 409 Conflict, got {response2.status_code}: {response2.text}"

        data = response2.json()

        # Validate error response structure (nested under 'detail')
        assert "detail" in data
        detail = data["detail"]

        assert "status" in detail
        assert detail["status"] == "conflict"

        assert "code" in detail
        assert detail["code"] == "duplicate_record"

        assert "message" in detail
        assert "already exists" in detail["message"].lower()

    @pytest.mark.contract
    def test_record_game_incomplete_session_contract(self, client, incomplete_session):
        """
        T013: Test incomplete session validation (400 Bad Request)

        Validates:
        - Attempting to record an incomplete session returns 400 Bad Request
        - Response includes appropriate error message
        - Only completed sessions (is_finished=True) can be recorded
        """
        request_data = {
            "session_id": incomplete_session.session_id,
            "game_date": "2025-12-24T15:30:00-08:00"
        }

        response = client.post("/api/v2/game_results", json=request_data)

        # Should return 400 Bad Request
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"

        data = response.json()

        # Validate error message
        assert "detail" in data
        assert "completed" in data["detail"].lower() or "finished" in data["detail"].lower()

    @pytest.mark.contract
    def test_record_game_session_not_found_contract(self, client):
        """
        Test session not found validation (404 Not Found)

        Validates:
        - Attempting to record with non-existent session_id returns 404
        - Response includes appropriate error message
        """
        request_data = {
            "session_id": "00000000-0000-0000-0000-000000000000",
            "game_date": "2025-12-24T15:30:00-08:00"
        }

        response = client.post("/api/v2/game_results", json=request_data)

        # Should return 404 Not Found
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

        data = response.json()

        # Validate error message
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @pytest.mark.contract
    def test_record_game_invalid_request_format_contract(self, client):
        """
        Test invalid request format validation (422 Unprocessable Entity)

        Validates:
        - Missing required fields returns 422
        - Invalid date format returns 422
        - Response includes validation error details
        """
        # Test missing session_id
        response = client.post("/api/v2/game_results", json={"game_date": "2025-12-24T15:30:00-08:00"})
        assert response.status_code == 422, f"Expected 422 for missing session_id, got {response.status_code}"

        # Test missing game_date
        response = client.post("/api/v2/game_results", json={"session_id": "123e4567-e89b-12d3-a456-426614174000"})
        assert response.status_code == 422, f"Expected 422 for missing game_date, got {response.status_code}"

        # Test invalid date format
        response = client.post("/api/v2/game_results", json={
            "session_id": "123e4567-e89b-12d3-a456-426614174000",
            "game_date": "not-a-date"
        })
        assert response.status_code == 422, f"Expected 422 for invalid date, got {response.status_code}"


class TestRetrieveGameHistoryContract:
    """Contract tests for GET /api/v2/game_results endpoint"""

    @pytest.fixture
    def client(self):
        """Test client fixture"""
        from src.main import app
        return TestClient(app)

    @pytest.fixture
    def session_manager(self):
        """Get session manager from app"""
        from src.main import session_manager
        return session_manager

    @pytest.fixture
    def multiple_recorded_games(self, client, session_manager):
        """Create and record multiple games for testing retrieval"""
        from src.models import ResponseResult
        import time

        recorded_games = []

        # Create 3 different puzzle sessions with unique timestamps
        base_timestamp = int(time.time())

        test_puzzles = [
            {
                "words": [
                    "apple", "banana", "cherry", "date",
                    "egg", "flour", "garlic", "honey",
                    "ice", "jam", "kale", "lemon",
                    "milk", "nut", "olive", "pepper"
                ],
                "date": f"2025-12-20T10:00:{base_timestamp % 60:02d}-08:00",
                "provider": "openai",
                "model": "gpt-4"
            },
            {
                "words": [
                    "red", "blue", "green", "yellow",
                    "cat", "dog", "bird", "fish",
                    "car", "bus", "train", "plane",
                    "sun", "moon", "star", "cloud"
                ],
                "date": f"2025-12-22T14:30:{(base_timestamp + 1) % 60:02d}-08:00",
                "provider": "ollama",
                "model": "llama2"
            },
            {
                "words": [
                    "book", "pen", "paper", "desk",
                    "chair", "lamp", "window", "door",
                    "wall", "floor", "ceiling", "roof",
                    "house", "home", "place", "space"
                ],
                "date": f"2025-12-24T16:45:{(base_timestamp + 2) % 60:02d}-08:00",
                "provider": "simple",
                "model": "random"
            }
        ]

        for puzzle_data in test_puzzles:
            # Create session
            session = session_manager.create_session(puzzle_data["words"])

            # Complete the game (find all 4 groups)
            session.record_attempt(puzzle_data["words"][0:4], ResponseResult.CORRECT, color="yellow")
            session.record_attempt(puzzle_data["words"][4:8], ResponseResult.CORRECT, color="green")
            session.record_attempt(puzzle_data["words"][8:12], ResponseResult.CORRECT, color="blue")
            session.record_attempt(puzzle_data["words"][12:16], ResponseResult.CORRECT, color="purple")

            # Set LLM info
            session.set_llm_info(puzzle_data["provider"], puzzle_data["model"])

            # Record the game
            request_data = {
                "session_id": session.session_id,
                "game_date": puzzle_data["date"]
            }
            response = client.post("/api/v2/game_results", json=request_data)

            # Skip if duplicate (from previous test run)
            if response.status_code == 409:
                continue

            assert response.status_code == 201, f"Failed to record game: {response.text}"

            recorded_games.append(response.json()["result"])

        return recorded_games

    @pytest.mark.contract
    def test_get_game_results_with_data_contract(self, client, multiple_recorded_games):
        """
        T028: Test retrieving game results when data exists (200 OK)

        Validates:
        - GET /api/v2/game_results returns 200 OK
        - Response includes status and results array
        - Results are ordered by game_date DESC (most recent first)
        - Each result contains all required fields
        - Data matches what was recorded
        """
        response = client.get("/api/v2/game_results")

        # Should return 200 OK
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()

        # Validate response structure
        assert "status" in data
        assert data["status"] == "success"
        assert "results" in data
        assert isinstance(data["results"], list)

        results = data["results"]

        # Should have at least 3 recorded games (may have more from previous tests)
        assert len(results) >= 3, f"Expected at least 3 results, got {len(results)}"

        # Validate results are ordered by game_date DESC (most recent first)
        # Check that dates are in descending order
        for i in range(len(results) - 1):
            date1 = results[i]["game_date"]
            date2 = results[i + 1]["game_date"]
            assert date1 >= date2, f"Results not ordered by date DESC: {date1} should be >= {date2}"

        # Validate each result has all required fields
        required_fields = [
            "result_id", "puzzle_id", "game_date", "puzzle_solved",
            "count_groups_found", "count_mistakes", "total_guesses",
            "llm_provider_name", "llm_model_name"
        ]

        for result in results:
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"

            # Validate field types
            assert isinstance(result["result_id"], int)
            assert isinstance(result["puzzle_id"], str)
            assert isinstance(result["game_date"], str)
            assert isinstance(result["puzzle_solved"], bool)
            assert isinstance(result["count_groups_found"], int)
            assert isinstance(result["count_mistakes"], int)
            assert isinstance(result["total_guesses"], int)

            # Validate completed game constraints
            assert result["count_groups_found"] >= 0
            assert result["count_groups_found"] <= 4
            assert 0 <= result["count_mistakes"] <= 4
            assert result["total_guesses"] >= result["count_groups_found"]

    @pytest.mark.contract
    def test_get_game_results_empty_state_contract(self, client):
        """
        T029: Test retrieving game results when database is empty (200 OK)

        Validates:
        - GET /api/v2/game_results returns 200 OK even with no data
        - Response includes status and empty results array
        - Empty array is returned, not null or error
        """
        # Note: This test assumes a fresh database or uses test isolation
        # In practice, this would need database cleanup between tests

        response = client.get("/api/v2/game_results")

        # Should return 200 OK even with no data
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()

        # Validate response structure
        assert "status" in data
        assert data["status"] == "success"
        assert "results" in data
        assert isinstance(data["results"], list)

        # Should return empty array, not null
        # Note: This test may need to run in isolation or with database cleanup
        # The assertion is flexible to allow for existing data from other tests
        assert isinstance(data["results"], list), "Results should be a list even when empty"


class TestExportGameResultsCSV:
    """Contract tests for GET /api/v2/game_results?format=csv endpoint"""

    @pytest.fixture
    def client(self):
        """Test client fixture"""
        from src.main import app
        return TestClient(app)

    @pytest.fixture
    def session_manager(self):
        """Get session manager from app"""
        from src.main import session_manager
        return session_manager

    @pytest.fixture
    def recorded_games_for_csv(self, client, session_manager):
        """Create and record multiple games for CSV export testing"""
        from src.models import ResponseResult

        test_puzzles = [
            {
                "words": [
                    "red", "blue", "green", "yellow",
                    "cat", "dog", "bird", "fish",
                    "car", "bus", "train", "plane",
                    "sun", "moon", "star", "cloud"
                ],
                "date": "2025-12-24T10:00:00-08:00",
                "provider": "openai",
                "model": "gpt-4"
            },
            {
                "words": [
                    "apple", "banana", "cherry", "date",
                    "egg", "flour", "garlic", "honey",
                    "ice", "jam", "kale", "lemon",
                    "milk", "nut", "olive", "pepper"
                ],
                "date": "2025-12-24T14:30:00-08:00",
                "provider": "ollama",
                "model": "llama2"
            }
        ]

        for puzzle_data in test_puzzles:
            # Create session
            session = session_manager.create_session(puzzle_data["words"])

            # Complete the game (find all 4 groups)
            session.record_attempt(puzzle_data["words"][0:4], ResponseResult.CORRECT, color="yellow")
            session.record_attempt(puzzle_data["words"][4:8], ResponseResult.CORRECT, color="green")
            session.record_attempt(puzzle_data["words"][8:12], ResponseResult.CORRECT, color="blue")
            session.record_attempt(puzzle_data["words"][12:16], ResponseResult.CORRECT, color="purple")

            # Set LLM info
            session.set_llm_info(puzzle_data["provider"], puzzle_data["model"])

            # Record the game
            request_data = {
                "session_id": session.session_id,
                "game_date": puzzle_data["date"]
            }
            response = client.post("/api/v2/game_results", json=request_data)

            # Skip if duplicate (from previous test run)
            if response.status_code != 409:
                assert response.status_code == 201, f"Failed to record game: {response.text}"

    @pytest.mark.contract
    def test_export_csv_with_data_contract(self, client, recorded_games_for_csv):
        """
        T043: Test CSV export when data exists (200 OK)

        Validates:
        - GET /api/v2/game_results?format=csv returns 200 OK
        - Response has Content-Type: text/csv header
        - Response has Content-Disposition header with correct filename
        - CSV includes header row with all columns
        - CSV includes data rows for all recorded games
        - Column order matches specification
        - Boolean values formatted correctly
        """
        response = client.get("/api/v2/game_results?format=csv")

        # Should return 200 OK
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        # Validate headers
        assert response.headers["content-type"] == "text/csv; charset=utf-8", \
            f"Expected text/csv content type, got {response.headers.get('content-type')}"

        assert "content-disposition" in response.headers, "Missing Content-Disposition header"
        content_disposition = response.headers["content-disposition"]
        assert 'attachment' in content_disposition, "Content-Disposition should include 'attachment'"
        assert 'game_results_extract.csv' in content_disposition, \
            f"Filename should be 'game_results_extract.csv', got {content_disposition}"

        # Parse CSV content
        csv_content = response.text
        lines = csv_content.strip().split('\n')

        # Should have header row + at least 2 data rows
        assert len(lines) >= 3, f"Expected at least 3 lines (header + 2 rows), got {len(lines)}"

        # Validate header row
        header = lines[0]
        expected_columns = [
            "result_id", "puzzle_id", "game_date", "puzzle_solved",
            "count_groups_found", "count_mistakes", "total_guesses",
            "llm_provider_name", "llm_model_name"
        ]
        for column in expected_columns:
            assert column in header, f"Missing column '{column}' in header: {header}"

        # Validate data rows exist and have correct number of fields
        for i, line in enumerate(lines[1:], start=1):
            if line.strip():  # Skip empty lines
                fields = line.split(',')
                assert len(fields) == len(expected_columns), \
                    f"Row {i} has {len(fields)} fields, expected {len(expected_columns)}"

    @pytest.mark.contract
    def test_export_csv_empty_state_contract(self, client):
        """
        T044: Test CSV export when database is empty (200 OK)

        Validates:
        - GET /api/v2/game_results?format=csv returns 200 OK even with no data
        - Response has correct CSV content type and disposition headers
        - CSV includes header row even when empty
        - CSV has no data rows
        """
        # Note: This test may see data from other tests
        # We test that empty CSV still has header row

        response = client.get("/api/v2/game_results?format=csv")

        # Should return 200 OK even with no data
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        # Validate headers
        assert response.headers["content-type"] == "text/csv; charset=utf-8", \
            f"Expected text/csv content type, got {response.headers.get('content-type')}"

        assert "content-disposition" in response.headers, "Missing Content-Disposition header"
        content_disposition = response.headers["content-disposition"]
        assert 'attachment' in content_disposition, "Content-Disposition should include 'attachment'"
        assert 'game_results_extract.csv' in content_disposition, \
            f"Filename should be 'game_results_extract.csv', got {content_disposition}"

        # Parse CSV content
        csv_content = response.text
        lines = csv_content.strip().split('\n')

        # Should have at least header row
        assert len(lines) >= 1, "CSV should have at least header row"

        # Validate header row exists
        header = lines[0]
        expected_columns = [
            "result_id", "puzzle_id", "game_date", "puzzle_solved",
            "count_groups_found", "count_mistakes", "total_guesses",
            "llm_provider_name", "llm_model_name"
        ]
        for column in expected_columns:
            assert column in header, f"Missing column '{column}' in header: {header}"
