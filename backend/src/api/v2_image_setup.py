"""
Image-based puzzle setup API endpoint.

Provides POST /api/v2/setup_puzzle_from_image endpoint for extracting words
from 4x4 puzzle grid images using LLM vision capabilities.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Any

from ..models import ImageSetupRequest, ImageSetupResponse
from ..services.image_word_extractor import ImageWordExtractor
from ..models import session_manager

# Create router for image setup endpoints
router = APIRouter(prefix="/api/v2", tags=["image-setup"])

# Dependency for image word extractor service
def get_image_extractor() -> ImageWordExtractor:
    """Dependency injection for ImageWordExtractor service."""
    return ImageWordExtractor()


@router.post(
    "/setup_puzzle_from_image",
    response_model=ImageSetupResponse,
    summary="Setup puzzle from image",
    description="Extract 16 words from a 4x4 grid image using LLM vision capabilities and create a new puzzle session"
)
async def setup_puzzle_from_image(
    request: ImageSetupRequest,
    extractor: ImageWordExtractor = Depends(get_image_extractor)
) -> ImageSetupResponse:
    """
    Setup a new puzzle from an uploaded image.

    This endpoint:
    1. Validates the image setup request (size, format, provider)
    2. Uses LLM vision models to extract 16 words from the 4x4 grid
    3. Creates a new puzzle session with the extracted words
    4. Returns the words for puzzle gameplay

    Args:
        request: Image setup request with base64 image and LLM provider details
        extractor: Injected ImageWordExtractor service

    Returns:
        ImageSetupResponse: Success response with extracted words or error details

    Raises:
        HTTPException:
            - 400: Bad request (extraction failure, wrong word count)
            - 413: Payload too large (image exceeds size limit)
            - 422: Unprocessable entity (validation errors)
            - 500: Internal server error (provider failures)
    """
    try:
        # Extract words from image using LLM vision
        extracted_words = await extractor.extract_words(request)

        # Create new puzzle session with extracted words
        session = session_manager.create_session(extracted_words)

        # Return successful response
        return ImageSetupResponse(
            remaining_words=extracted_words,
            status="success",
            session_id=session.session_id
        )

    except ValueError as e:
        # Handle validation and extraction errors (400 Bad Request)
        error_message = str(e)
        if "size exceeds" in error_message.lower():
            # Handle oversized image as 413 Payload Too Large
            raise HTTPException(
                status_code=413,
                detail=error_message
            )
        else:
            # Other validation errors as 400 Bad Request
            raise HTTPException(
                status_code=400,
                detail=error_message
            )

    except RuntimeError as e:
        # Handle provider capability/availability errors (500 Internal Server Error)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except Exception as e:
        # Handle unexpected provider/system errors (500 Internal Server Error)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )