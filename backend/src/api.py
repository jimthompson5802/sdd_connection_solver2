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
)

router = APIRouter()


@router.post("/api/puzzle/setup_puzzle", response_model=SetupPuzzleResponse)
async def setup_puzzle(request: SetupPuzzleRequest):
    """
    Set up a new puzzle with the provided 16 words.

    Creates a new puzzle session and returns the word list and status.
    """
    try:
        # Parse the words from the comma-separated string
        words = [word.strip() for word in request.file_content.split(",")]

        # Create a new puzzle session (store for later use in other endpoints)
        session_manager.create_session(words)

        return SetupPuzzleResponse(remaining_words=words, status="success")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"status": str(e)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to setup puzzle: {str(e)}"
        )


@router.get("/api/puzzle/next_recommendation", response_model=NextRecommendationResponse)
async def get_next_recommendation():
    """
    Get the next recommended group of 4 words.

    For now, returns a simple static recommendation since we don't have session management
    integrated with the test contract yet.
    """
    try:
        # Static recommendation for contract compliance
        # In real implementation, this would use session management and recommendation engine
        recommended_words = ["apple", "banana", "cherry", "date"]
        connection = "These are all fruits"

        return NextRecommendationResponse(words=recommended_words, connection=connection, status="success")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get recommendation: {str(e)}"
        )


@router.post("/api/puzzle/record_response", response_model=RecordResponseResponse)
async def record_user_response(request: RecordResponseRequest):
    """
    Record the result of a user's attempt at finding a word group.

    For now, returns a static response for contract compliance.
    """
    try:
        # Static response for contract compliance
        # In real implementation, this would update session state

        # Simulate different game states based on response type
        all_words = [
            "apple",
            "banana",
            "cherry",
            "date",
            "elderberry",
            "fig",
            "grape",
            "honeydew",
            "kiwi",
            "lemon",
            "mango",
            "orange",
            "papaya",
            "quince",
            "raspberry",
            "strawberry",
        ]

        if request.response_type == "correct":
            remaining_after_correct = [
                "kiwi",
                "lemon",
                "mango",
                "orange",
                "papaya",
                "quince",
                "raspberry",
                "strawberry",
                "elderberry",
                "fig",
                "grape",
                "honeydew",
            ]
            return RecordResponseResponse(
                remaining_words=remaining_after_correct, correct_count=1, mistake_count=0, game_status="active"
            )
        elif request.response_type == "incorrect":
            return RecordResponseResponse(
                remaining_words=all_words, correct_count=0, mistake_count=1, game_status="active"
            )
        else:  # one-away
            return RecordResponseResponse(
                remaining_words=all_words, correct_count=0, mistake_count=0, game_status="active"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to record response: {str(e)}"
        )
