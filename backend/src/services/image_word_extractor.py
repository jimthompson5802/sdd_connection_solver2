"""
Image Word Extractor Service

This service handles LLM-based word extraction from 4x4 puzzle grid images.
Uses the existing LLM provider factory pattern for provider-agnostic processing.
"""

from typing import List
from ..models import ExtractedWords, ImageSetupRequest
from .llm_provider_factory import LLMProviderFactory


class ImageWordExtractor:
    """Service for extracting words from puzzle grid images using LLM vision models."""
    
    def __init__(self) -> None:
        """Initialize the image word extractor service."""
        pass
    
    async def extract_words(self, request: ImageSetupRequest) -> List[str]:
        """
        Extract 16 words from a 4x4 puzzle grid image using LLM vision capabilities.
        
        Args:
            request: Image setup request containing base64 image and LLM provider details
            
        Returns:
            List[str]: 16 words extracted from the image in reading order
            
        Raises:
            ValueError: If extraction fails or doesn't return exactly 16 words
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
            
            # 5. Invoke with_structured_output for word extraction
            structured_llm = provider.llm.with_structured_output(ExtractedWords)
            result = structured_llm.invoke(message_content)
            
            # 6. Validate response
            if not result:
                raise ValueError("No words extracted from image")
                
            if len(result.words) != 16:
                raise ValueError(f"Expected 16 words, got {len(result.words)}")
            
            # 7. Normalize words to lowercase (consistent with file-based setup)
            normalized_words = [word.lower().strip() for word in result.words]
            
            return normalized_words
            
        except (ValueError, RuntimeError):
            # Re-raise validation and capability errors as-is
            raise
        except Exception as e:
            # Convert all other errors to ValueError for unified error handling
            raise ValueError(f"LLM unable to extract puzzle words: {str(e)}") from e
    
    def _construct_vision_prompt(self) -> str:
        """
        Construct comprehensive vision prompt using 4-strategy approach.
        
        Returns:
            str: Complete prompt for LLM vision model
        """
        return '''Extract all 16 words from this 4x4 puzzle grid image. Read words in order: top row left to right, second row left to right, third row left to right, bottom row left to right.

**STRATEGY 1 - Basic Extraction:**
Look for a 4x4 grid of words arranged in rows and columns. Extract each word exactly as it appears.

**STRATEGY 2 - Grid Positioning:**
- Row 1: positions 1, 2, 3, 4
- Row 2: positions 5, 6, 7, 8  
- Row 3: positions 9, 10, 11, 12
- Row 4: positions 13, 14, 15, 16

**STRATEGY 3 - Expected Format:**
This is likely a New York Times Connections puzzle with 16 words that form 4 groups of 4 related words each. Words are typically:
- Common nouns, verbs, adjectives
- May include proper nouns, brand names
- Usually single words, occasionally hyphenated
- No numbers or symbols

**STRATEGY 4 - Validation:**
Ensure you return exactly 16 distinct words. Double-check reading order is consistent (left-to-right, top-to-bottom).

Return the words in the exact order they appear in the grid (reading order).'''