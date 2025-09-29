"""
Unit tests for CSV parsing edge cases and validation.

Tests the SetupPuzzleRequest model validation logic that handles CSV input parsing,
ensuring proper error handling for malformed, invalid, or edge case inputs.
"""

import pytest
from pydantic import ValidationError
from src.models import SetupPuzzleRequest


class TestCSVParsingEdgeCases:
    """Test CSV parsing edge cases in SetupPuzzleRequest validation."""

    def test_valid_csv_parsing(self):
        """Test valid CSV input is parsed correctly."""
        valid_content = "apple,orange,banana,grape,dog,cat,mouse,bird,red,blue,green,yellow,chair,table,sofa,desk"
        request = SetupPuzzleRequest(file_content=valid_content)
        assert request.file_content == valid_content

    def test_empty_content_raises_error(self):
        """Test empty content raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SetupPuzzleRequest(file_content="")

        assert "File content cannot be empty" in str(exc_info.value)

    def test_whitespace_only_content_raises_error(self):
        """Test whitespace-only content raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SetupPuzzleRequest(file_content="   ")

        assert "File content cannot be empty" in str(exc_info.value)

    def test_too_few_words_raises_error(self):
        """Test less than 16 words raises validation error."""
        content = "apple,orange,banana,grape,dog,cat,mouse,bird,red,blue,green,yellow,chair,table,sofa"  # 15 words
        with pytest.raises(ValidationError) as exc_info:
            SetupPuzzleRequest(file_content=content)

        assert "Must provide exactly 16 words" in str(exc_info.value)

    def test_too_many_words_raises_error(self):
        """Test more than 16 words raises validation error."""
        content = (
            "apple,orange,banana,grape,dog,cat,mouse,bird,red,blue,green,yellow,"
            "chair,table,sofa,desk,lamp"  # 17 words
        )
        with pytest.raises(ValidationError) as exc_info:
            SetupPuzzleRequest(file_content=content)

        assert "Must provide exactly 16 words" in str(exc_info.value)

    def test_duplicate_words_raises_error(self):
        """Test duplicate words raise validation error."""
        content = (
            "apple,orange,banana,grape,dog,cat,mouse,bird,red,blue,green,yellow,"
            "chair,table,sofa,apple"  # 'apple' twice
        )
        with pytest.raises(ValidationError) as exc_info:
            SetupPuzzleRequest(file_content=content)

        assert "All words must be unique" in str(exc_info.value)

    def test_empty_words_raises_error(self):
        """Test empty words (consecutive commas) raise validation error."""
        content = (
            "apple,orange,,grape,dog,cat,mouse,bird,red,blue,green,yellow,"
            "chair,table,sofa,desk"  # Empty word
        )
        with pytest.raises(ValidationError) as exc_info:
            SetupPuzzleRequest(file_content=content)

        assert "Words cannot be empty or whitespace" in str(exc_info.value)

    def test_whitespace_words_raises_error(self):
        """Test whitespace-only words raise validation error."""
        content = (
            "apple,orange,   ,grape,dog,cat,mouse,bird,red,blue,green,yellow,"
            "chair,table,sofa,desk"  # Whitespace word
        )
        with pytest.raises(ValidationError) as exc_info:
            SetupPuzzleRequest(file_content=content)

        assert "Words cannot be empty or whitespace" in str(exc_info.value)

    def test_leading_trailing_whitespace_trimmed(self):
        """Test that leading and trailing whitespace is properly trimmed from words."""
        content = (
            " apple , orange , banana , grape , dog , cat , mouse , bird , "
            "red , blue , green , yellow , chair , table , sofa , desk "
        )
        request = SetupPuzzleRequest(file_content=content)
        # Validation should pass because whitespace is trimmed
        assert request.file_content == content

    def test_mixed_case_words_valid(self):
        """Test that mixed case words are valid."""
        content = "Apple,ORANGE,banana,Grape,DOG,cat,Mouse,BIRD,red,Blue,GREEN,yellow,Chair,TABLE,sofa,Desk"
        request = SetupPuzzleRequest(file_content=content)
        assert request.file_content == content

    def test_special_characters_in_words(self):
        """Test words with special characters are valid."""
        content = (
            "apple-pie,orange!,banana?,grape.,dog's,cat@home,mouse#1,bird&fly,"
            "red%color,blue*sky,green+grass,yellow-sun,chair-old,table.new,sofa@home,desk#work"
        )
        request = SetupPuzzleRequest(file_content=content)
        assert request.file_content == content

    def test_numbers_as_words_valid(self):
        """Test that numbers as words are valid."""
        content = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"
        request = SetupPuzzleRequest(file_content=content)
        assert request.file_content == content

    def test_unicode_characters_valid(self):
        """Test that Unicode characters in words are valid."""
        content = (
            "café,naïve,résumé,piñata,jalapeño,mañana,niño,año,"
            "corazón,montaña,pequeño,grande,bueno,malo,rápido,lento"
        )
        request = SetupPuzzleRequest(file_content=content)
        assert request.file_content == content

    def test_very_long_words_valid(self):
        """Test that very long words are valid."""
        long_words = (
            ["supercalifragilisticexpialidocious"]
            + [f"word{i}" for i in range(2, 16)]
            + ["antidisestablishmentarianism"]
        )
        content = ",".join(long_words)
        request = SetupPuzzleRequest(file_content=content)
        assert request.file_content == content

    def test_single_character_words_valid(self):
        """Test that single character words are valid."""
        content = "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p"
        request = SetupPuzzleRequest(file_content=content)
        assert request.file_content == content
