"""
Image Word Extractor Service

This service handles LLM-based word extraction from 4x4 puzzle grid images.
Uses the existing LLM provider factory pattern for provider-agnostic processing.
"""

from typing import List
from langchain_core.messages import HumanMessage
from ..models import ExtractedWords, ImageSetupRequest
from .llm_provider_factory import LLMProviderFactory


class ImageWordExtractor:
    """Service for extracting words from puzzle grid images using LLM vision models."""

    def __init__(self) -> None:
        """Initialize the image word extractor service."""
        pass

    async def extract_words(self, request: ImageSetupRequest) -> List[str]:
        """
        Extract 16 items (cell contents) from a 4x4 puzzle grid image using LLM vision capabilities.
        Each cell may contain single or multi-word phrases.

        Args:
            request: Image setup request containing base64 image and LLM provider details

        Returns:
            List[str]: 16 items (cell contents) extracted from the image in reading order,
                      where each item is the complete text from one grid cell

        Raises:
            ValueError: If extraction fails or doesn't return exactly 16 items
            RuntimeError: If LLM provider doesn't support vision capabilities
        """
        try:
            # 1. Create LLM provider using existing factory pattern
            from ..llm_models.llm_provider import LLMProvider

            provider_model = LLMProvider(
                provider_type=request.provider_type,
                model_name=request.model_name
            )

            factory = LLMProviderFactory()
            provider = factory.create_provider(provider_model)

            # 2. Check for vision capability (with_structured_output support)
            if not hasattr(provider.llm, 'with_structured_output') or provider.llm.with_structured_output is None:
                raise RuntimeError(f"LLM does not support 'with_structured_output()' method required for vision tasks")

            # 3. Construct vision prompt with 4-strategy approach
            vision_prompt = self._construct_vision_prompt()

            # 4. Prepare message content with base64 image
            message_content = [
                {
                    "type": "text",
                    "text": vision_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{request.image_mime};base64,{request.image_base64}"
                    }
                }
            ]

            # Wrap in HumanMessage for proper LangChain format
            message = HumanMessage(content=message_content)

            # 5. Invoke with_structured_output for word extraction
            structured_llm = provider.llm.with_structured_output(ExtractedWords)
            result = structured_llm.invoke([message])

            # 6. Validate response
            if not result:
                raise ValueError("No words extracted from image")

            # 7. Check if LLM detected a valid grid
            if not result.grid_detected:
                raise ValueError(
                    "No valid 4x4 word grid detected in image. "
                    "Please ensure the image contains a visible puzzle grid with text."
                )

            # 8. Validate word count
            if len(result.words) != 16:
                raise ValueError(f"Expected 16 words, got {len(result.words)}")

            # 9. Normalize words to lowercase (consistent with file-based setup)
            normalized_words = [word.lower().strip() for word in result.words]

            # 10. Validate word quality to detect error messages
            self._validate_extracted_words(normalized_words)

            return normalized_words

        except ValueError as e:
            # Re-raise validation errors with context
            error_msg = str(e)
            if any(phrase in error_msg for phrase in [
                "No valid 4x4 word grid detected",
                "LLM returned error message",
                "too short",
                "appears to be sentences",
                "Too many repeated words"
            ]):
                # This is our content validation failure
                raise ValueError(f"Unable to extract puzzle from image: {error_msg}")
            else:
                # This is a count or other validation error
                raise
        except RuntimeError:
            # Re-raise capability errors as-is
            raise
        except Exception as e:
            # Convert all other errors to ValueError for unified error handling
            raise ValueError(f"LLM unable to extract puzzle words: {str(e)}") from e

    def _validate_extracted_words(self, words: List[str]) -> None:
        """
        Validate that extracted items are valid puzzle cell contents, not error messages.

        Args:
            words: List of 16 extracted items (cell contents) to validate

        Raises:
            ValueError: If items appear to be an error message or invalid puzzle content
        """
        # Check 1: Detect common error/refusal patterns
        error_indicators = {
            'cannot', 'unable', 'error', 'sorry', 'please', 'apologize',
            'fail', 'failed', 'invalid', 'missing', 'not', 'no'
        }

        # Count how many error indicator words appear
        error_word_count = sum(1 for word in words if word.lower() in error_indicators)

        # If more than 3 error indicators, likely an error message
        if error_word_count >= 3:
            raise ValueError(
                "LLM returned error message instead of puzzle words. "
                "Image may not contain a valid 4x4 word grid."
            )

        # Check 2: Ensure words have reasonable lengths for puzzle words
        # Puzzle words are typically 3-15 characters
        too_short = sum(1 for word in words if len(word) < 2)
        if too_short > 4:  # Allow a few short words (like "TO", "OF")
            raise ValueError(
                "Extracted words are too short to be valid puzzle words. "
                "Image may not contain readable text."
            )

        # Check 3: Detect sentence-like patterns (words ending with punctuation)
        punctuated = sum(1 for word in words if word and word.rstrip() and word.rstrip()[-1] in '.!?,;:')
        if punctuated >= 2:
            raise ValueError(
                "Extracted content appears to be sentences, not puzzle words. "
                "Image may not contain a 4x4 word grid."
            )

        # Check 4: Ensure sufficient unique words (avoid repeated error messages)
        unique_words = len(set(w.lower() for w in words))
        if unique_words < 12:  # At least 12 of 16 should be unique
            raise ValueError(
                "Too many repeated words detected. "
                "Image may not contain a valid puzzle grid."
            )

    def _construct_vision_prompt(self) -> str:
        """
        Construct comprehensive vision prompt using 4-strategy approach.

        Returns:
            str: Complete prompt for LLM vision model
        """
        return '''Your task is to extract the TEXT CONTENT from each of the 16 cells in a 4x4 puzzle grid image.

**CRITICAL: Grid Detection**
Before extracting content, you MUST determine if this image contains a visible 4x4 grid of TEXT.
- Set grid_detected = True ONLY if you can see a clear 4x4 grid layout with readable text
- Set grid_detected = False if:
  * The image shows objects, scenes, or photos without text
  * There is no visible grid structure
  * Text is not arranged in a 4x4 grid pattern
  * You cannot clearly read text in the image

**If grid_detected = False**: You must still provide 16 placeholder values (use "INVALID" repeated), but the grid_detected flag will cause the request to be rejected.

**If grid_detected = True**: Extract cell contents using these strategies:

**STRATEGY 1 - Grid Layout Verification:**
Verify you can see a 4x4 grid with text arranged in rows and columns. The grid should be clearly visible with text in each cell.

**STRATEGY 2 - Cell Content Extraction (Reading Order):**
Extract the COMPLETE text from each cell exactly as it appears, reading left-to-right, top-to-bottom:
- Row 1: cells at positions 1, 2, 3, 4
- Row 2: cells at positions 5, 6, 7, 8
- Row 3: cells at positions 9, 10, 11, 12
- Row 4: cells at positions 13, 14, 15, 16

**IMPORTANT**: Each cell may contain ONE or MORE words. Extract ALL words from each cell as a SINGLE STRING.

**STRATEGY 3 - Expected Content Format:**
This is typically a New York Times Connections puzzle:
- Each cell contains a phrase or concept (e.g., "GRAND PIANO", "SWIFT", "EIFFEL TOWER")
- May be single words OR multi-word phrases
- Common patterns: compound nouns, proper nouns, brand names, phrases
- Extract EXACTLY what you see - keep all words within a cell together
- Do NOT split multi-word phrases into separate entries
- Preserve spacing between words within a cell
- No numbers or symbols typically appear

**EXAMPLES of correct extraction:**
- Cell shows "GRAND PIANO" → extract as "GRAND PIANO" (not "GRAND" and "PIANO" separately)
- Cell shows "SWIFT" → extract as "SWIFT"
- Cell shows "EIFFEL TOWER" → extract as "EIFFEL TOWER" (not "EIFFEL" and "TOWER" separately)

**STRATEGY 4 - Quality Check:**
- You must extract exactly 16 items (one per grid cell)
- Each item should be the complete text from one cell
- Items must be EXTRACTED from visible text, not generated based on image content
- If you're inventing content based on what you see in the image (not reading text), set grid_detected = False

**Confidence Levels:**
- high: Clear, readable 4x4 grid with all cell contents easily visible
- medium: Grid structure visible but some cell contents unclear
- low: Uncertain if this is a puzzle grid or if cell contents are correct

Return the 16 cell contents in exact reading order (left-to-right, top-to-bottom).'''
