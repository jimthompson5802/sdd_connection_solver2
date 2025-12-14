/**
 * Comprehensive tests for RecommendationDisplay component.
 * Tests recommendation display, loading states, error handling, provider info, and metadata.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { RecommendationDisplay, RecommendationDisplayProps } from './RecommendationDisplay';
import { RecommendationResponse } from '../types/recommendation';
import { LLMProvider } from '../types/llm-provider';

describe('RecommendationDisplay Component', () => {
  const mockProvider: LLMProvider = {
    provider_type: 'openai',
    model_name: 'gpt-4o-mini',
  };

  const mockRecommendation: RecommendationResponse = {
    recommended_words: ['word1', 'word2', 'word3', 'word4'],
    connection_explanation: 'These words are all related to testing',
    provider_used: mockProvider,
    generation_time_ms: 1500,
  };

  const defaultProps: RecommendationDisplayProps = {
    recommendation: null,
  };

  describe('Empty State', () => {
    test('renders empty state when no recommendation', () => {
      render(<RecommendationDisplay {...defaultProps} />);

      expect(screen.getByText(/No recommendations available/)).toBeInTheDocument();
      expect(screen.getByText('💡')).toBeInTheDocument();
    });

    test('shows message prompting user to submit puzzle', () => {
      render(<RecommendationDisplay {...defaultProps} />);

      expect(screen.getByText(/Submit a puzzle to get AI assistance/)).toBeInTheDocument();
    });

    test('applies empty state CSS class', () => {
      const { container } = render(<RecommendationDisplay {...defaultProps} />);

      expect(container.querySelector('.recommendation-display--empty')).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    test('renders loading state when isLoading is true', () => {
      render(<RecommendationDisplay {...defaultProps} isLoading={true} />);

      expect(screen.getByText(/Analyzing puzzle and generating recommendations/)).toBeInTheDocument();
      expect(screen.getByText('🤔')).toBeInTheDocument();
    });

    test('applies loading state CSS class', () => {
      const { container } = render(<RecommendationDisplay {...defaultProps} isLoading={true} />);

      expect(container.querySelector('.recommendation-display--loading')).toBeInTheDocument();
    });

    test('loading spinner has aria-hidden attribute', () => {
      const { container } = render(<RecommendationDisplay {...defaultProps} isLoading={true} />);

      const spinner = container.querySelector('.loading-spinner');
      expect(spinner).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Error State', () => {
    test('renders error state when error prop is provided', () => {
      render(<RecommendationDisplay {...defaultProps} error="Connection failed" />);

      expect(screen.getByText(/Failed to generate recommendations: Connection failed/)).toBeInTheDocument();
      expect(screen.getByText('❌')).toBeInTheDocument();
    });

    test('applies error state CSS class', () => {
      const { container } = render(<RecommendationDisplay {...defaultProps} error="Error message" />);

      expect(container.querySelector('.recommendation-display--error')).toBeInTheDocument();
    });

    test('error icon has aria-hidden attribute', () => {
      const { container } = render(<RecommendationDisplay {...defaultProps} error="Error" />);

      const icon = container.querySelector('.error-icon');
      expect(icon).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Recommendation Display', () => {
    test('renders recommendation with words', () => {
      render(<RecommendationDisplay recommendation={mockRecommendation} />);

      expect(screen.getByText('word1')).toBeInTheDocument();
      expect(screen.getByText('word2')).toBeInTheDocument();
      expect(screen.getByText('word3')).toBeInTheDocument();
      expect(screen.getByText('word4')).toBeInTheDocument();
    });

    test('renders connection explanation', () => {
      render(<RecommendationDisplay recommendation={mockRecommendation} />);

      expect(screen.getByText('Connection Explanation')).toBeInTheDocument();
      expect(screen.getByText('These words are all related to testing')).toBeInTheDocument();
    });

    test('displays AI Recommendation title', () => {
      render(<RecommendationDisplay recommendation={mockRecommendation} />);

      expect(screen.getByText('AI Recommendation')).toBeInTheDocument();
    });
  });

  describe('Provider Information', () => {
    test('shows provider info when showProviderInfo is true and provider is provided', () => {
      render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          provider={mockProvider}
          showProviderInfo={true}
        />
      );

      expect(screen.getByText('OpenAI')).toBeInTheDocument();
      expect(screen.getByText('(gpt-4o-mini)')).toBeInTheDocument();
      expect(screen.getByText('🤖')).toBeInTheDocument();
    });

    test('hides provider info when showProviderInfo is false', () => {
      render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          provider={mockProvider}
          showProviderInfo={false}
        />
      );

      expect(screen.queryByText('OpenAI')).not.toBeInTheDocument();
    });

    test('hides provider info when provider is null', () => {
      render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          provider={null}
          showProviderInfo={true}
        />
      );

      expect(screen.queryByText('OpenAI')).not.toBeInTheDocument();
    });

    test('displays simple provider correctly', () => {
      const simpleProvider: LLMProvider = {
        provider_type: 'simple',
        model_name: null,
      };

      render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          provider={simpleProvider}
          showProviderInfo={true}
        />
      );

      expect(screen.getByText('Simple Provider')).toBeInTheDocument();
      // Simple provider doesn't show model name in parentheses
      const providerSection = screen.getByText('Simple Provider').closest('.recommendation-display__provider');
      expect(providerSection?.textContent).not.toMatch(/\(.+\)/);
    });

    test('displays ollama provider correctly', () => {
      const ollamaProvider: LLMProvider = {
        provider_type: 'ollama',
        model_name: 'qwen2.5:32b',
      };

      render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          provider={ollamaProvider}
          showProviderInfo={true}
        />
      );

      expect(screen.getByText('Ollama')).toBeInTheDocument();
      expect(screen.getByText('(qwen2.5:32b)')).toBeInTheDocument();
    });

    test('provider icon has aria-hidden attribute', () => {
      const { container } = render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          provider={mockProvider}
          showProviderInfo={true}
        />
      );

      const icon = container.querySelector('.provider-icon');
      expect(icon).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Metadata Display', () => {
    test('shows generation time when showMetadata is true', () => {
      render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          showMetadata={true}
        />
      );

      expect(screen.getByText(/⏱️/)).toBeInTheDocument();
      expect(screen.getByText(/1.5s/)).toBeInTheDocument();
    });

    test('hides metadata when showMetadata is false', () => {
      render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          showMetadata={false}
        />
      );

      expect(screen.queryByText(/⏱️/)).not.toBeInTheDocument();
    });

    test('does not show metadata when generation_time_ms is null', () => {
      const recWithoutTime: RecommendationResponse = {
        ...mockRecommendation,
        generation_time_ms: null,
      };

      render(
        <RecommendationDisplay
          recommendation={recWithoutTime}
          showMetadata={true}
        />
      );

      expect(screen.queryByText(/⏱️/)).not.toBeInTheDocument();
    });

    test('shows provider used in metadata', () => {
      render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          showMetadata={true}
        />
      );

      expect(screen.getByText(/🤖/)).toBeInTheDocument();
      expect(screen.getByText(/OpenAI \(gpt-4o-mini\)/)).toBeInTheDocument();
    });

    test('handles string provider_used', () => {
      const recWithStringProvider: RecommendationResponse = {
        ...mockRecommendation,
        provider_used: 'simple',
      };

      render(
        <RecommendationDisplay
          recommendation={recWithStringProvider}
          showMetadata={true}
        />
      );

      expect(screen.getByText(/simple/)).toBeInTheDocument();
    });
  });

  describe('Duration Formatting', () => {
    test('formats milliseconds correctly (< 1s)', () => {
      const rec: RecommendationResponse = {
        ...mockRecommendation,
        generation_time_ms: 500,
      };

      render(<RecommendationDisplay recommendation={rec} showMetadata={true} />);

      expect(screen.getByText(/500ms/)).toBeInTheDocument();
    });

    test('formats seconds correctly (1s - 60s)', () => {
      const rec: RecommendationResponse = {
        ...mockRecommendation,
        generation_time_ms: 5500,
      };

      render(<RecommendationDisplay recommendation={rec} showMetadata={true} />);

      expect(screen.getByText(/5.5s/)).toBeInTheDocument();
    });

    test('formats minutes and seconds correctly (>= 60s)', () => {
      const rec: RecommendationResponse = {
        ...mockRecommendation,
        generation_time_ms: 125000, // 2m 5s
      };

      render(<RecommendationDisplay recommendation={rec} showMetadata={true} />);

      expect(screen.getByText(/2m 5.0s/)).toBeInTheDocument();
    });
  });

  describe('Alternative Suggestions', () => {
    test('displays alternative suggestions when available', () => {
      const recWithAlternatives: RecommendationResponse = {
        ...mockRecommendation,
        alternative_suggestions: [
          ['alt1', 'alt2', 'alt3', 'alt4'],
          ['alt5', 'alt6', 'alt7', 'alt8'],
        ],
      };

      render(<RecommendationDisplay recommendation={recWithAlternatives} />);

      expect(screen.getByText('Alternative Suggestions')).toBeInTheDocument();
      expect(screen.getByText('alt1')).toBeInTheDocument();
      expect(screen.getByText('alt5')).toBeInTheDocument();
    });

    test('shows Try This button for each alternative', () => {
      const recWithAlternatives: RecommendationResponse = {
        ...mockRecommendation,
        alternative_suggestions: [
          ['alt1', 'alt2', 'alt3', 'alt4'],
          ['alt5', 'alt6', 'alt7', 'alt8'],
        ],
      };

      render(<RecommendationDisplay recommendation={recWithAlternatives} />);

      const buttons = screen.getAllByText('Try This');
      expect(buttons).toHaveLength(2);
    });

    test('calls onApplyAlternative when button clicked', () => {
      const onApplyAlternative = jest.fn();
      const alternatives = [['alt1', 'alt2', 'alt3', 'alt4']];
      const recWithAlternatives: RecommendationResponse = {
        ...mockRecommendation,
        alternative_suggestions: alternatives,
      };

      render(
        <RecommendationDisplay
          recommendation={recWithAlternatives}
          onApplyAlternative={onApplyAlternative}
        />
      );

      fireEvent.click(screen.getByText('Try This'));

      expect(onApplyAlternative).toHaveBeenCalledWith(alternatives[0]);
    });

    test('disables button when onApplyAlternative not provided', () => {
      const recWithAlternatives: RecommendationResponse = {
        ...mockRecommendation,
        alternative_suggestions: [['alt1', 'alt2', 'alt3', 'alt4']],
      };

      render(<RecommendationDisplay recommendation={recWithAlternatives} />);

      const button = screen.getByText('Try This');
      expect(button).toBeDisabled();
    });

    test('does not show alternatives section when array is empty', () => {
      const rec: RecommendationResponse = {
        ...mockRecommendation,
        alternative_suggestions: [],
      };

      render(<RecommendationDisplay recommendation={rec} />);

      expect(screen.queryByText('Alternative Suggestions')).not.toBeInTheDocument();
    });

    test('does not show alternatives section when not provided', () => {
      render(<RecommendationDisplay recommendation={mockRecommendation} />);

      expect(screen.queryByText('Alternative Suggestions')).not.toBeInTheDocument();
    });
  });

  describe('Puzzle State Display', () => {
    test('displays puzzle state when provided', () => {
      const recWithState: RecommendationResponse = {
        ...mockRecommendation,
        puzzle_state: {
          remaining_words: ['word5', 'word6', 'word7', 'word8'],
          completed_groups: [
            {
              words: ['w1', 'w2', 'w3', 'w4'],
              connection: 'Test',
              difficulty_level: 'straightforward',
            },
          ],
          total_mistakes: 1,
          max_mistakes: 4,
          game_status: 'active',
        },
      };

      render(<RecommendationDisplay recommendation={recWithState} />);

      expect(screen.getByText('Puzzle State')).toBeInTheDocument();
      expect(screen.getByText(/Remaining Words:/)).toBeInTheDocument();
      // Use more specific query to avoid matching numbers in other places
      const puzzleStateSection = screen.getByText('Puzzle State').parentElement!;
      expect(puzzleStateSection.textContent).toContain('4');
      expect(screen.getByText(/Groups Found:/)).toBeInTheDocument();
      expect(puzzleStateSection.textContent).toContain('1');
      expect(screen.getByText(/Mistakes:/)).toBeInTheDocument();
      expect(screen.getByText(/1\/4/)).toBeInTheDocument();
      expect(screen.getByText(/Status:/)).toBeInTheDocument();
      expect(screen.getByText('active')).toBeInTheDocument();
    });

    test('does not show puzzle state when not provided', () => {
      render(<RecommendationDisplay recommendation={mockRecommendation} />);

      expect(screen.queryByText('Puzzle State')).not.toBeInTheDocument();
    });

    test('applies correct game status CSS class', () => {
      const recWithState: RecommendationResponse = {
        ...mockRecommendation,
        puzzle_state: {
          remaining_words: [],
          completed_groups: [],
          total_mistakes: 0,
          max_mistakes: 4,
          game_status: 'won',
        },
      };

      const { container } = render(<RecommendationDisplay recommendation={recWithState} />);

      expect(container.querySelector('.game-status--won')).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    test('applies custom className', () => {
      const { container } = render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          className="custom-recommendation"
        />
      );

      expect(container.querySelector('.custom-recommendation')).toBeInTheDocument();
    });

    test('combines custom className with base class', () => {
      const { container } = render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          className="custom-class"
        />
      );

      const element = container.querySelector('.recommendation-display.custom-class');
      expect(element).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('handles recommendation with no words', () => {
      const emptyRec: RecommendationResponse = {
        ...mockRecommendation,
        recommended_words: [],
      };

      render(<RecommendationDisplay recommendation={emptyRec} />);

      expect(screen.getByText('AI Recommendation')).toBeInTheDocument();
    });

    test('handles very long connection explanation', () => {
      const longExplanation = 'A'.repeat(500);
      const rec: RecommendationResponse = {
        ...mockRecommendation,
        connection_explanation: longExplanation,
      };

      render(<RecommendationDisplay recommendation={rec} />);

      expect(screen.getByText(longExplanation)).toBeInTheDocument();
    });

    test('handles provider_used as empty string', () => {
      const rec: RecommendationResponse = {
        ...mockRecommendation,
        provider_used: '',
      };

      render(<RecommendationDisplay recommendation={rec} showMetadata={true} />);

      // Should still render without crashing
      expect(screen.getByText('AI Recommendation')).toBeInTheDocument();
    });

    test('handles zero generation time', () => {
      const rec: RecommendationResponse = {
        ...mockRecommendation,
        generation_time_ms: 0,
      };

      render(<RecommendationDisplay recommendation={rec} showMetadata={true} />);

      // When generation_time_ms is 0 (falsy), metadata section won't render per component logic
      expect(screen.queryByText(/⏱️/)).not.toBeInTheDocument();
    });
  });

  describe('Integration Scenarios', () => {
    test('renders complete recommendation with all features', () => {
      const fullRec: RecommendationResponse = {
        recommended_words: ['test1', 'test2', 'test3', 'test4'],
        connection_explanation: 'All testing related',
        provider_used: mockProvider,
        generation_time_ms: 2500,
        alternative_suggestions: [
          ['alt1', 'alt2', 'alt3', 'alt4'],
        ],
        puzzle_state: {
          remaining_words: ['word5', 'word6'],
          completed_groups: [],
          total_mistakes: 0,
          max_mistakes: 4,
          game_status: 'active',
        },
      };

      const onApplyAlternative = jest.fn();

      render(
        <RecommendationDisplay
          recommendation={fullRec}
          provider={mockProvider}
          showProviderInfo={true}
          showMetadata={true}
          onApplyAlternative={onApplyAlternative}
          className="full-recommendation"
        />
      );

      expect(screen.getByText('test1')).toBeInTheDocument();
      expect(screen.getByText('All testing related')).toBeInTheDocument();
      expect(screen.getByText('OpenAI')).toBeInTheDocument();
      expect(screen.getByText(/2.5s/)).toBeInTheDocument();
      expect(screen.getByText('Alternative Suggestions')).toBeInTheDocument();
      expect(screen.getByText('Puzzle State')).toBeInTheDocument();
    });

    test('loading state takes precedence over other states', () => {
      render(
        <RecommendationDisplay
          recommendation={mockRecommendation}
          isLoading={true}
          error="Some error"
        />
      );

      expect(screen.getByText(/Analyzing puzzle/)).toBeInTheDocument();
      expect(screen.queryByText('Some error')).not.toBeInTheDocument();
    });

    test('error state takes precedence over empty state', () => {
      render(
        <RecommendationDisplay
          recommendation={null}
          error="Connection error"
        />
      );

      expect(screen.getByText(/Connection error/)).toBeInTheDocument();
      expect(screen.queryByText(/No recommendations available/)).not.toBeInTheDocument();
    });
  });
});
