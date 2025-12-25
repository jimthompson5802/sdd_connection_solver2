"""
API endpoints for game results recording and retrieval (v2).

This module provides endpoints for:
- POST /api/v2/game_results - Record a completed game
- GET /api/v2/game_results - Retrieve game history
- GET /api/v2/game_results?format=csv - Export game history as CSV
"""

import logging
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
import io
import csv

from ..models import SessionManager
from ..database.game_results_repository import GameResultsRepository
from ..game_result import GameResult


# Configure logger
logger = logging.getLogger(__name__)

# Create router for v2 API endpoints
router = APIRouter(prefix="/api/v2", tags=["v2-game-results"])


# ============================================================================
# Pydantic Models (T015, T016)
# ============================================================================

class RecordGameRequest(BaseModel):
    """
    T015: Request model for recording a completed game.

    Attributes:
        session_id: UUID of the puzzle session to record
        game_date: ISO 8601 timestamp with timezone when game was completed
    """
    session_id: str = Field(..., description="Session UUID to record")
    game_date: datetime = Field(..., description="Game completion timestamp with timezone")

    @validator('game_date')
    def validate_game_date(cls, v):
        """Ensure game_date has timezone information"""
        if v.tzinfo is None:
            raise ValueError("game_date must include timezone information")
        return v


class GameResultData(BaseModel):
    """Game result data for response"""
    result_id: int
    puzzle_id: str
    game_date: str
    puzzle_solved: bool
    count_groups_found: int
    count_mistakes: int
    total_guesses: int
    llm_provider_name: Optional[str]
    llm_model_name: Optional[str]


class GameResultResponse(BaseModel):
    """
    T016: Response model for game result operations.

    Attributes:
        status: Operation status (created, ok, conflict)
        result: Game result data (optional for some responses)
        code: Error code for conflict/error cases
        message: Human-readable message
    """
    status: str = Field(..., description="Response status")
    result: Optional[GameResultData] = Field(None, description="Game result data")
    code: Optional[str] = Field(None, description="Error code")
    message: Optional[str] = Field(None, description="Status message")


class GameHistoryResponse(BaseModel):
    """Response model for game history list"""
    status: str = Field(default="ok", description="Response status")
    results: List[GameResultData] = Field(default_factory=list, description="List of game results")


# ============================================================================
# Dependencies
# ============================================================================

def get_session_manager() -> SessionManager:
    """Dependency to get SessionManager instance"""
    from ..main import session_manager
    return session_manager


def get_repository() -> GameResultsRepository:
    """Dependency to get GameResultsRepository instance"""
    return GameResultsRepository()


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/game_results", response_model=GameResultResponse, status_code=201)
async def record_game_result(
    request_data: RecordGameRequest,
    session_manager: SessionManager = Depends(get_session_manager),
    repository: GameResultsRepository = Depends(get_repository),
) -> GameResultResponse:
    """
    T017-T020: Record a completed puzzle game to persistent storage.

    This endpoint validates the session, checks for duplicates, and records
    the game result to the database.

    Args:
        request_data: Record game request with session_id and game_date
        session_manager: Session manager dependency
        repository: Game results repository dependency

    Returns:
        GameResultResponse with status and result data

    Raises:
        HTTPException 400: Session not completed
        HTTPException 404: Session not found
        HTTPException 409: Duplicate record (same puzzle_id + game_date)
        HTTPException 500: Database error
    """
    try:
        # T019: Session validation - check if session exists (404)
        session = session_manager.get_session(request_data.session_id)
        if session is None:
            logger.warning(f"Session not found: {request_data.session_id}")
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        # T019: Session completion validation (400)
        if not session.is_finished:
            logger.warning(f"Attempted to record incomplete session: {request_data.session_id}")
            raise HTTPException(
                status_code=400,
                detail="Session must be completed before recording"
            )

        # Convert session to game result data
        game_result_data = session.to_game_result(request_data.game_date)

        # T018: Duplicate detection - check if record already exists (409)
        if repository.check_duplicate(
            game_result_data["puzzle_id"],
            game_result_data["game_date"]
        ):
            logger.info(
                f"Duplicate game result detected: puzzle_id={game_result_data['puzzle_id']}, "
                f"game_date={game_result_data['game_date']}"
            )
            raise HTTPException(
                status_code=409,
                detail={
                    "status": "conflict",
                    "code": "duplicate_record",
                    "message": "A game result for this puzzle and game_date already exists. No new record was created."
                }
            )

        # T017: Insert game result into database
        result_id = repository.insert(game_result_data)

        logger.info(
            f"Game result recorded successfully: result_id={result_id}, "
            f"session_id={request_data.session_id}"
        )

        # Build response with created result
        return GameResultResponse(
            status="created",
            result=GameResultData(
                result_id=result_id,
                puzzle_id=game_result_data["puzzle_id"],
                game_date=game_result_data["game_date"],
                puzzle_solved=(game_result_data["puzzle_solved"] == "true"),
                count_groups_found=game_result_data["count_groups_found"],
                count_mistakes=game_result_data["count_mistakes"],
                total_guesses=game_result_data["total_guesses"],
                llm_provider_name=game_result_data.get("llm_provider_name"),
                llm_model_name=game_result_data.get("llm_model_name"),
            )
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except sqlite3.IntegrityError as e:
        # T020: Handle database constraint violations
        logger.error(f"Database integrity error: {str(e)}")
        if "UNIQUE constraint" in str(e):
            raise HTTPException(
                status_code=409,
                detail={
                    "status": "conflict",
                    "code": "duplicate_record",
                    "message": "A game result for this puzzle and game_date already exists."
                }
            )
        raise HTTPException(
            status_code=500,
            detail="Database integrity error"
        )

    except Exception as e:
        # T020: Handle unexpected errors
        logger.error(f"Failed to record game result: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to record game"
        )


@router.get("/game_results", response_model=GameHistoryResponse)
async def get_game_results(
    format: Optional[str] = Query(None, description="Export format (e.g., 'csv')"),
    repository: GameResultsRepository = Depends(get_repository),
):
    """
    Retrieve all game results or export as CSV.

    Args:
        format: Optional export format ('csv' for CSV export)
        repository: Game results repository dependency

    Returns:
        GameHistoryResponse with results list or CSV file

    Raises:
        HTTPException 500: Database error
    """
    try:
        # Retrieve all game results ordered by date (most recent first)
        results = repository.get_all(order_by="game_date DESC")

        # If CSV export requested, return CSV file
        if format == "csv":
            return _export_csv(results)

        # Convert to response format
        result_data = [
            GameResultData(
                result_id=result.result_id,
                puzzle_id=result.puzzle_id,
                game_date=result.game_date,
                puzzle_solved=result.puzzle_solved,
                count_groups_found=result.count_groups_found,
                count_mistakes=result.count_mistakes,
                total_guesses=result.total_guesses,
                llm_provider_name=result.llm_provider_name,
                llm_model_name=result.llm_model_name,
            )
            for result in results
        ]

        logger.info(f"Retrieved {len(results)} game results")

        return GameHistoryResponse(
            status="ok",
            results=result_data
        )

    except Exception as e:
        logger.error(f"Failed to retrieve game history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve game history"
        )


def _export_csv(results: List[GameResult]) -> StreamingResponse:
    """
    Export game results as CSV file.

    Args:
        results: List of GameResult objects

    Returns:
        StreamingResponse with CSV content
    """
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "result_id",
        "puzzle_id",
        "game_date",
        "puzzle_solved",
        "count_groups_found",
        "count_mistakes",
        "total_guesses",
        "llm_provider_name",
        "llm_model_name"
    ])

    # Write data rows
    for result in results:
        writer.writerow([
            result.result_id,
            result.puzzle_id,
            result.game_date,
            "true" if result.puzzle_solved else "false",
            result.count_groups_found,
            result.count_mistakes,
            result.total_guesses,
            result.llm_provider_name or "",
            result.llm_model_name or ""
        ])

    # Get CSV content
    output.seek(0)
    csv_content = output.getvalue()

    # Return as streaming response
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=game_results_extract.csv"
        }
    )
