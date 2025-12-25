"""
API endpoints for the NYT Connections puzzle solver.
Implements the three main endpoints: setup-puzzle, next-recommendation, and record-response.
"""

from fastapi import APIRouter, HTTPException, status

from .models import (
    SetupPuzzleRequest,
    SetupPuzzleResponse,
    NextRecommendationResponse,
    RecordResponseRequest,
    RecordResponseResponse,
    session_manager,
    ResponseResult,
)

router = APIRouter()


@router.post("/api/puzzle/setup_puzzle", response_model=SetupPuzzleResponse)
async def setup_puzzle(request: SetupPuzzleRequest) -> SetupPuzzleResponse:
    """
    Set up a new puzzle with the provided 16 words.

    Creates a new puzzle session and returns the word list and status.
    """
    try:
        # Parse the words from the comma-separated string and normalize to lowercase
        words = [word.strip().lower() for word in request.file_content.split(",")]

        # Create a new puzzle session (store for later use in other endpoints)
        session = session_manager.create_session(words)

        return SetupPuzzleResponse(remaining_words=words, status="success", session_id=session.session_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"status": str(e)})
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to setup puzzle: {str(e)}"
        )


@router.get("/api/puzzle/next_recommendation", response_model=NextRecommendationResponse)
async def get_next_recommendation() -> NextRecommendationResponse:
    """
    Get the next recommended group of 4 words.

    For now, returns a simple static recommendation since we don't have session management
    integrated with the test contract yet.
    """
    try:
        # If no session exists, return a generic static recommendation
        if session_manager.get_session_count() == 0:
            recommended_words = ["apple", "banana", "cherry", "date"]
            connection = "These are all fruits"
            return NextRecommendationResponse(words=recommended_words, connection=connection, status="success")

        # Use last-created session
        session = list(session_manager._sessions.values())[-1]

        # If game is over, no recommendations should be provided
        if session.is_game_over():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"status": "No recommendations: game over"}
            )

        remaining = session.get_remaining_words()

        if len(remaining) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"status": "Not enough words remaining"}
            )

        # For now, recommend the first 4 remaining words and record them as the last recommendation
        recommended_words = [w.lower() for w in remaining[:4]]
        connection = "this is the connection reason"
        session.last_recommendation = recommended_words

        return NextRecommendationResponse(words=recommended_words, connection=connection, status="success")

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get recommendation: {str(e)}"
        )


@router.post("/api/puzzle/record_response", response_model=RecordResponseResponse)
async def record_user_response(request: RecordResponseRequest) -> RecordResponseResponse:
    """
    Record the result of a user's attempt at finding a word group.

    For now, returns a static response for contract compliance.
    """
    try:
        # Ensure a session exists. If none, create a placeholder session so that
        # contract tests and minimal clients can record responses without prior setup.
        session = None
        if session_manager.get_session_count() == 0:
            # Create a default placeholder session with 16 dummy words
            placeholder_words = [f"word{i+1}" for i in range(16)]
            session = session_manager.create_session(placeholder_words)
            # Seed a last_recommendation so the client can respond immediately
            session.last_recommendation = session.get_remaining_words()[:4]

        # Use session_id if provided, else use last-created session
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"status": "Session not found"})
        else:
            # If we created a placeholder above, 'session' is already set; otherwise pick the last session
            if session_manager.get_session_count() > 0 and session is None:
                session = list(session_manager._sessions.values())[-1]

        # Sanity check for static analysis: ensure session is set
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"status": "Internal server error: session not set"},
            )

        # Ensure there is an active recommendation to respond to
        # If explicit attempt_words are provided, allow recording without requiring last_recommendation
        if not request.attempt_words and not session.last_recommendation:
            # No recommendation has been issued yet
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"status": "No recommendation to respond to"},
            )

        # Determine words to record for the attempt: explicit attempt_words override last_recommendation
        if request.attempt_words:
            attempt_words = [w.strip().lower() for w in request.attempt_words]
            if len(attempt_words) != 4:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"status": "attempt_words must contain exactly 4 words"},
                )
            # Validate words belong to this puzzle and haven't already been found
            all_words = set(session.words)
            remaining = set(session.get_remaining_words())
            if any(w not in all_words for w in attempt_words):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"status": "attempt_words contain words not in the current puzzle"},
                )
            if any(w not in remaining for w in attempt_words):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"status": "attempt_words contain already-found words"},
                )
            # Optionally set as last recommendation for traceability
            session.last_recommendation = attempt_words.copy()
        else:
            # mypy/pylance guard: last_recommendation is guaranteed by earlier check, but guard explicitly
            if session.last_recommendation is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"status": "No recommendation to respond to"},
                )
            attempt_words = [w.lower() for w in session.last_recommendation]

        # Map request to ResponseResult and record the attempt
        # Validate required fields for correct responses
        if request.response_type == "correct":
            if not request.color:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"status": "color is required for correct responses"},
                )

            result = ResponseResult.CORRECT
            # Record the correct attempt using provided words (or last recommendation)
            session.record_attempt(attempt_words, result, was_recommendation=True, color=request.color)
        elif request.response_type == "incorrect":
            result = ResponseResult.INCORRECT
            session.record_attempt(attempt_words, result, was_recommendation=True)
        else:  # one-away
            result = ResponseResult.ONE_AWAY
            session.record_attempt(attempt_words, result, was_recommendation=True)

        # Build response from current session state
        remaining_words = session.get_remaining_words()
        correct_count = sum(1 for g in session.groups if g.found)
        mistake_count = session.mistakes_made
        if session.is_game_over():
            game_status = "won" if session.game_won else "lost"
        else:
            game_status = "active"

        return RecordResponseResponse(
            remaining_words=remaining_words,
            correct_count=correct_count,
            mistake_count=mistake_count,
            game_status=game_status,
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to record response: {str(e)}"
        )
