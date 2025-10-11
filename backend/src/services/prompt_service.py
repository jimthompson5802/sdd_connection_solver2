"""
Prompt template service for generating LLM prompts with context injection.
Creates specialized prompts for connection puzzle recommendations.
"""

from typing import List, Dict, Any
from src.llm_models.guess_attempt import GuessAttempt
from src.llm_models.recommendation_request import RecommendationRequest


class PromptTemplateService:
    """Service for generating LLM prompts with puzzle context."""

    def __init__(self):
        self.base_prompt = self._load_base_prompt()
        self.examples = self._load_examples()

    def _load_base_prompt(self) -> str:
        """Load the base prompt template for connection puzzles."""
        return (
            "You are an expert at solving New York Times Connections puzzles. "
            "Your task is to find groups of 4 words that share a common connection.\n\n"
            "RULES:\n"
            "- Find exactly 4 words that belong together\n"
            "- The connection should be specific and clear\n"
            "- Avoid obvious or generic connections\n"
            "- Consider wordplay, categories, and subtle relationships\n"
            "- Use ONLY words from the AVAILABLE WORDS list below\n"
            "- Do NOT invent, modify, or reformat words; return each word exactly as listed in AVAILABLE WORDS\n\n"
            "PUZZLE CONTEXT:\n"
            "{context}\n\n"
            "AVAILABLE WORDS:\n"
            "{remaining_words}\n\n"
            "{previous_guesses_section}\n\n"
            "IMPORTANT VALIDATION:\n"
            "- Your answer is INVALID if any selected word is not present in AVAILABLE WORDS\n\n"
            "OUTPUT FORMAT (JSON ONLY):\n"
            "Return a single JSON object and nothing else with the following keys:\n\n"
            '- "recommendations": a JSON array of exactly four words (strings) chosen from AVAILABLE WORDS\n'
            '- "connection": a short connection phrase (brief — keep it under 6 words)\n'
            '- "explanation": a short paragraph explaining why the recommended_words belong together\n\n'
            "Example valid JSON:\n"
            "{{\n"
            '  "recommendations": ["BASS", "FLOUNDER", "SALMON", "TROUT"],\n'
            '  "connection": "Types of fish",\n'
            '  "explanation": "All are common fish species found in fresh or salt water."\n'
            "}}\n\n"
            "Please provide only the JSON object that matches the schema above. "
            "Do not include any additional commentary or text"
        )

    def _load_examples(self) -> List[Dict[str, str]]:
        """Load example connections for few-shot learning."""
        return [
            {
                "words": "BASS, FLOUNDER, SALMON, TROUT",
                "connection": "Types of fish",
                "explanation": "All are common fish species",
            },
            {
                "words": "PIANO, GUITAR, VIOLIN, DRUMS",
                "connection": "Musical instruments",
                "explanation": "All are instruments used to make music",
            },
            {
                "words": "RED, BLUE, GREEN, YELLOW",
                "connection": "Primary and secondary colors",
                "explanation": "Basic colors in the color wheel",
            },
        ]

    def generate_recommendation_prompt(self, request: RecommendationRequest) -> str:
        """Generate a prompt for word recommendations.

        Args:
            request: RecommendationRequest with puzzle context.

        Returns:
            Formatted prompt string for the LLM.
        """
        # Format remaining words
        words_text = ", ".join(request.remaining_words)

        # Add previous guesses section if any exist
        previous_section = self._format_previous_guesses(request.previous_guesses)

        # Add puzzle context if provided
        context = request.puzzle_context or "Standard NYT Connections puzzle with 16 words forming 4 groups of 4."

        # Format the complete prompt using simple replace to avoid conflicts with literal braces
        prompt = (
            self.base_prompt.replace("{context}", context)
            .replace("{remaining_words}", words_text)
            .replace("{previous_guesses_section}", previous_section)
        )

        return prompt

    def _format_previous_guesses(self, guesses: List[GuessAttempt]) -> str:
        """Format previous guesses for inclusion in prompt.

        Args:
            guesses: List of previous guess attempts.

        Returns:
            Formatted string describing previous guesses.
        """
        if not guesses:
            return ""

        section = "\nPREVIOUS GUESSES:\n"
        for i, guess in enumerate(guesses, 1):
            words_str = ", ".join(guess.words)
            outcome_text = guess.outcome.value.replace("_", " ").title()

            section += f"{i}. {words_str} - {outcome_text}"

            if guess.actual_connection:
                section += f" (Actual: {guess.actual_connection})"

            section += "\n"

        section += "\nAvoid repeating these unsuccessful combinations.\n"
        return section

    def generate_explanation_prompt(self, words: List[str], connection: str) -> str:
        """Generate a prompt for explaining a connection.

        Args:
            words: List of 4 words in the connection.
            connection: The connection theme.

        Returns:
            Prompt for generating a detailed explanation.
        """
        words_text = ", ".join(words)

        prompt = f"""Explain why these 4 words belong together in a New York Times Connections puzzle:

WORDS: {words_text}
CONNECTION: {connection}

Provide a clear, concise explanation (1-2 sentences) that would help a player \
understand the connection. Focus on what specifically links these words together."""

        return prompt

    def generate_validation_prompt(self, words: List[str]) -> str:
        """Generate a prompt for validating a potential connection.

        Args:
            words: List of 4 words to validate.

        Returns:
            Prompt for assessing connection strength.
        """
        words_text = ", ".join(words)

        prompt = f"""Evaluate if these 4 words form a valid connection for a New York Times Connections puzzle:

WORDS: {words_text}

Rate the connection strength from 1-10 and explain:
1. What connects these words?
2. Is the connection specific enough?
3. Would this be a valid NYT Connections group?

Provide your rating and brief reasoning."""

        return prompt

    def add_provider_specific_instructions(self, base_prompt: str, provider_type: str) -> str:
        """Add provider-specific instructions to the prompt.

        Args:
            base_prompt: The base prompt text.
            provider_type: Type of LLM provider (simple, ollama, openai).

        Returns:
            Enhanced prompt with provider-specific instructions.
        """
        if provider_type == "simple":
            # Simple provider gets basic instructions
            return base_prompt + "\n\nKeep your response simple and direct."

        elif provider_type == "ollama":
            # Ollama gets more detailed reasoning instructions
            return (
                base_prompt
                + "\n\nThink step by step and provide clear reasoning for your choice."
                + "\nEnsure all four words come exclusively from the AVAILABLE WORDS list above."
                + "\nReturn your answer as a single JSON object using the keys: "
                + "recommended_words, connection, explanation."
            )

        elif provider_type == "openai":
            # OpenAI gets sophisticated analysis instructions
            return (
                base_prompt
                + "\n\nUse your advanced reasoning capabilities to find "
                + "subtle connections and provide insightful explanations."
                + "\nAll four output words must come exclusively from the AVAILABLE WORDS list above."
                + " If any word is not in that list, revise your selection."
                + "\nReturn your answer as a single JSON object using the keys: "
                + "recommended_words, connection, explanation."
            )

        return base_prompt

    def get_template_metadata(self) -> Dict[str, Any]:
        """Get metadata about the prompt templates.

        Returns:
            Dictionary with template information.
        """
        return {
            "base_prompt_length": len(self.base_prompt),
            "examples_count": len(self.examples),
            "supported_providers": ["simple", "ollama", "openai"],
            "template_version": "1.0",
        }
