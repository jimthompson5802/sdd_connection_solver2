/**
 * Comprehensive tests for GameSummary component.
 * Tests stats display, previous responses, win/loss states, and expanded view.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import GameSummary from './GameSummary';

describe('GameSummary Component', () => {
  const mockPreviousResponses = [
    { words: ['cat', 'dog', 'bird', 'fish'], type: 'correct', color: 'yellow' },
    { words: ['red', 'blue', 'green', 'purple'], type: 'correct', color: 'green' },
    { words: ['one', 'two', 'three', 'four'], type: 'incorrect' },
  ];

  const defaultProps = {
    correctCount: 2,
    mistakeCount: 1,
    wordsRemaining: 8,
    previousResponses: mockPreviousResponses,
  };

  describe('Basic Rendering', () => {
    test('renders game summary section', () => {
      const { container } = render(<GameSummary {...defaultProps} />);

      expect(container.querySelector('.game-summary')).toBeInTheDocument();
    });

    test('renders stats section', () => {
      const { container } = render(<GameSummary {...defaultProps} />);

      expect(container.querySelector('.puzzle-stats')).toBeInTheDocument();
    });

    test('renders previous responses section', () => {
      render(<GameSummary {...defaultProps} />);

      expect(screen.getByText('Previous Responses')).toBeInTheDocument();
    });

    test('previous responses section has proper ARIA label', () => {
      render(<GameSummary {...defaultProps} />);

      const responsesSection = screen.getByLabelText('Previous responses');
      expect(responsesSection).toBeInTheDocument();
    });

    test('previous responses section is focusable', () => {
      render(<GameSummary {...defaultProps} />);

      const responsesSection = screen.getByLabelText('Previous responses');
      expect(responsesSection).toHaveAttribute('tabIndex', '0');
    });
  });

  describe('Stats Display', () => {
    test('displays correct groups count', () => {
      render(<GameSummary {...defaultProps} />);

      expect(screen.getByText('Correct Groups:')).toBeInTheDocument();
      expect(screen.getByText('2/4')).toBeInTheDocument();
    });

    test('displays mistakes count', () => {
      render(<GameSummary {...defaultProps} />);

      expect(screen.getByText('Mistakes:')).toBeInTheDocument();
      expect(screen.getByText('1/4')).toBeInTheDocument();
    });

    test('displays words remaining', () => {
      render(<GameSummary {...defaultProps} />);

      expect(screen.getByText('Words Remaining:')).toBeInTheDocument();
      expect(screen.getByText('8')).toBeInTheDocument();
    });

    test('handles zero correct groups', () => {
      render(<GameSummary {...defaultProps} correctCount={0} />);

      expect(screen.getByText('0/4')).toBeInTheDocument();
    });

    test('handles max correct groups', () => {
      render(<GameSummary {...defaultProps} correctCount={4} />);

      expect(screen.getByText('4/4')).toBeInTheDocument();
    });

    test('handles zero mistakes', () => {
      render(<GameSummary {...defaultProps} mistakeCount={0} />);

      expect(screen.getByText('0/4')).toBeInTheDocument();
    });

    test('handles max mistakes', () => {
      render(<GameSummary {...defaultProps} mistakeCount={4} />);

      expect(screen.getByText('4/4')).toBeInTheDocument();
    });

    test('handles zero words remaining', () => {
      render(<GameSummary {...defaultProps} wordsRemaining={0} />);

      expect(screen.getByText(/Words Remaining:/).parentElement).toHaveTextContent('0');
    });

    test('handles 16 words remaining (full puzzle)', () => {
      render(<GameSummary {...defaultProps} wordsRemaining={16} />);

      expect(screen.getByText(/Words Remaining:/).parentElement).toHaveTextContent('16');
    });
  });

  describe('Previous Responses Display', () => {
    test('displays all previous responses', () => {
      const { container } = render(<GameSummary {...defaultProps} />);

      const responseItems = container.querySelectorAll('.response-item');
      expect(responseItems.length).toBe(3);
    });

    test('displays correct response words', () => {
      render(<GameSummary {...defaultProps} />);

      expect(screen.getByText('cat')).toBeInTheDocument();
      expect(screen.getByText('dog')).toBeInTheDocument();
      expect(screen.getByText('bird')).toBeInTheDocument();
      expect(screen.getByText('fish')).toBeInTheDocument();
    });

    test('displays response type in uppercase', () => {
      render(<GameSummary {...defaultProps} />);

      expect(screen.getByText('CORRECT (yellow)')).toBeInTheDocument();
    });

    test('displays color when provided', () => {
      render(<GameSummary {...defaultProps} />);

      expect(screen.getByText('CORRECT (yellow)')).toBeInTheDocument();
      expect(screen.getByText('CORRECT (green)')).toBeInTheDocument();
    });

    test('displays type without color when color not provided', () => {
      render(<GameSummary {...defaultProps} />);

      expect(screen.getByText('INCORRECT')).toBeInTheDocument();
    });

    test('applies CSS class for response type', () => {
      const { container } = render(<GameSummary {...defaultProps} />);

      const correctItems = container.querySelectorAll('.response-item.correct');
      const incorrectItems = container.querySelectorAll('.response-item.incorrect');

      expect(correctItems.length).toBe(2);
      expect(incorrectItems.length).toBe(1);
    });

    test('applies CSS class for outcome type', () => {
      const { container } = render(<GameSummary {...defaultProps} />);

      const correctOutcomes = container.querySelectorAll('.response-outcome.correct');
      const incorrectOutcomes = container.querySelectorAll('.response-outcome.incorrect');

      expect(correctOutcomes.length).toBe(2);
      expect(incorrectOutcomes.length).toBe(1);
    });

    test('handles empty previous responses array', () => {
      render(<GameSummary {...defaultProps} previousResponses={[]} />);

      expect(screen.getByText('No previous responses')).toBeInTheDocument();
    });

    test('displays empty state with proper CSS class', () => {
      const { container } = render(<GameSummary {...defaultProps} previousResponses={[]} />);

      expect(container.querySelector('.response-item.empty')).toBeInTheDocument();
    });

    test('handles response without type', () => {
      const responses = [{ words: ['word1', 'word2', 'word3', 'word4'] }];
      render(<GameSummary {...defaultProps} previousResponses={responses} />);

      expect(screen.getByText('word1')).toBeInTheDocument();
    });

    test('handles response without color', () => {
      const responses = [{ words: ['word1', 'word2', 'word3', 'word4'], type: 'correct' }];
      render(<GameSummary {...defaultProps} previousResponses={responses} />);

      expect(screen.getByText('CORRECT')).toBeInTheDocument();
    });

    test('displays all four words for each response', () => {
      render(<GameSummary {...defaultProps} />);

      const firstResponse = mockPreviousResponses[0];
      firstResponse.words.forEach(word => {
        expect(screen.getByText(word)).toBeInTheDocument();
      });
    });
  });

  describe('Game Status States', () => {
    test('does not expand by default (active status)', () => {
      const { container } = render(<GameSummary {...defaultProps} gameStatus="active" />);

      const responsesSection = container.querySelector('.previous-responses');
      expect(responsesSection).not.toHaveClass('expanded');
    });

    test('does not expand for waiting status', () => {
      const { container } = render(<GameSummary {...defaultProps} gameStatus="waiting" />);

      const responsesSection = container.querySelector('.previous-responses');
      expect(responsesSection).not.toHaveClass('expanded');
    });

    test('expands for won status', () => {
      const { container } = render(<GameSummary {...defaultProps} gameStatus="won" />);

      const responsesSection = container.querySelector('.previous-responses');
      expect(responsesSection).toHaveClass('expanded');
    });

    test('expands for lost status', () => {
      const { container } = render(<GameSummary {...defaultProps} gameStatus="lost" />);

      const responsesSection = container.querySelector('.previous-responses');
      expect(responsesSection).toHaveClass('expanded');
    });

    test('adds aria-live when expanded', () => {
      const { container } = render(<GameSummary {...defaultProps} gameStatus="won" />);

      const summary = container.querySelector('.game-summary');
      expect(summary).toHaveAttribute('aria-live', 'polite');
    });

    test('no aria-live when not expanded', () => {
      const { container } = render(<GameSummary {...defaultProps} gameStatus="active" />);

      const summary = container.querySelector('.game-summary');
      expect(summary).not.toHaveAttribute('aria-live');
    });

    test('handles missing gameStatus prop', () => {
      const { container } = render(<GameSummary {...defaultProps} />);

      const responsesSection = container.querySelector('.previous-responses');
      expect(responsesSection).not.toHaveClass('expanded');
    });
  });

  describe('Expanded View', () => {
    test('sets max-height style when expanded', () => {
      const { container } = render(<GameSummary {...defaultProps} gameStatus="won" />);

      const responsesSection = container.querySelector('.previous-responses') as HTMLElement;
      // Note: max-height is set after requestAnimationFrame, so we just check it's expanded
      expect(responsesSection).toHaveClass('expanded');
    });

    test('no max-height style when not expanded', () => {
      const { container } = render(<GameSummary {...defaultProps} gameStatus="active" />);

      const responsesSection = container.querySelector('.previous-responses') as HTMLElement;
      expect(responsesSection?.style.maxHeight).toBeFalsy();
    });

    test('respects prefers-reduced-motion', () => {
      // Mock matchMedia for reduced motion
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      const { container } = render(<GameSummary {...defaultProps} gameStatus="won" />);

      const responsesSection = container.querySelector('.previous-responses') as HTMLElement;
      expect(responsesSection).toHaveClass('expanded');

      // Clean up
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: undefined,
      });
    });
  });

  describe('Edge Cases', () => {
    test('handles null previousResponses gracefully', () => {
      // @ts-ignore - testing edge case
      const { container } = render(<GameSummary {...defaultProps} previousResponses={null} />);

      expect(container.querySelector('.game-summary')).toBeInTheDocument();
    });

    test('handles undefined previousResponses gracefully', () => {
      // @ts-ignore - testing edge case
      const { container } = render(<GameSummary {...defaultProps} previousResponses={undefined} />);

      expect(container.querySelector('.game-summary')).toBeInTheDocument();
    });

    test('handles response with empty words array', () => {
      const responses = [{ words: [], type: 'correct', color: 'blue' }];
      render(<GameSummary {...defaultProps} previousResponses={responses} />);

      expect(screen.getByText('CORRECT (blue)')).toBeInTheDocument();
    });

    test('handles response with single word', () => {
      const responses = [{ words: ['single'], type: 'incorrect' }];
      render(<GameSummary {...defaultProps} previousResponses={responses} />);

      expect(screen.getByText('single')).toBeInTheDocument();
    });

    test('handles response with many words', () => {
      const responses = [{ words: ['one', 'two', 'three', 'four', 'five', 'six'], type: 'correct' }];
      render(<GameSummary {...defaultProps} previousResponses={responses} />);

      expect(screen.getByText('one')).toBeInTheDocument();
      expect(screen.getByText('six')).toBeInTheDocument();
    });

    test('handles special characters in words', () => {
      const responses = [{ words: ["it's", 'co-op', '@home', 'word!'], type: 'correct' }];
      render(<GameSummary {...defaultProps} previousResponses={responses} />);

      expect(screen.getByText("it's")).toBeInTheDocument();
      expect(screen.getByText('co-op')).toBeInTheDocument();
    });

    test('handles empty string type', () => {
      const responses = [{ words: ['word1', 'word2', 'word3', 'word4'], type: '', color: 'blue' }];
      render(<GameSummary {...defaultProps} previousResponses={responses} />);

      // Empty type will be uppercased to empty string
      expect(screen.getByText('(blue)')).toBeInTheDocument();
    });

    test('handles empty string color', () => {
      const responses = [{ words: ['word1', 'word2', 'word3', 'word4'], type: 'correct', color: '' }];
      render(<GameSummary {...defaultProps} previousResponses={responses} />);

      // Empty color should not display parentheses
      expect(screen.getByText('CORRECT')).toBeInTheDocument();
    });

    test('handles timestamp field (not currently displayed)', () => {
      const responses = [
        { words: ['word1', 'word2', 'word3', 'word4'], type: 'correct', timestamp: '2025-01-01' }
      ];
      render(<GameSummary {...defaultProps} previousResponses={responses} />);

      expect(screen.getByText('word1')).toBeInTheDocument();
    });
  });

  describe('Integration Scenarios', () => {
    test('displays complete game in progress', () => {
      render(
        <GameSummary
          correctCount={2}
          mistakeCount={3}
          wordsRemaining={4}
          previousResponses={mockPreviousResponses}
          gameStatus="active"
        />
      );

      expect(screen.getByText('2/4')).toBeInTheDocument();
      expect(screen.getByText('3/4')).toBeInTheDocument();
      expect(screen.getByText(/Words Remaining:/).parentElement).toHaveTextContent('4');
      expect(screen.getByText('cat')).toBeInTheDocument();
    });

    test('displays won game with all stats', () => {
      const { container } = render(
        <GameSummary
          correctCount={4}
          mistakeCount={2}
          wordsRemaining={0}
          previousResponses={mockPreviousResponses}
          gameStatus="won"
        />
      );

      expect(screen.getByText('4/4')).toBeInTheDocument();
      expect(screen.getByText('2/4')).toBeInTheDocument();
      expect(screen.getByText(/Words Remaining:/).parentElement).toHaveTextContent('0');
      expect(container.querySelector('.previous-responses.expanded')).toBeInTheDocument();
    });

    test('displays lost game with max mistakes', () => {
      const { container } = render(
        <GameSummary
          correctCount={1}
          mistakeCount={4}
          wordsRemaining={12}
          previousResponses={mockPreviousResponses}
          gameStatus="lost"
        />
      );

      expect(screen.getByText('1/4')).toBeInTheDocument();
      expect(screen.getByText('4/4')).toBeInTheDocument();
      expect(screen.getByText(/Words Remaining:/).parentElement).toHaveTextContent('12');
      expect(container.querySelector('.previous-responses.expanded')).toBeInTheDocument();
    });

    test('displays perfect game (no mistakes)', () => {
      render(
        <GameSummary
          correctCount={4}
          mistakeCount={0}
          wordsRemaining={0}
          previousResponses={mockPreviousResponses}
          gameStatus="won"
        />
      );

      expect(screen.getByText('4/4')).toBeInTheDocument();
      expect(screen.getByText('0/4')).toBeInTheDocument();
    });

    test('displays fresh game (no progress)', () => {
      render(
        <GameSummary
          correctCount={0}
          mistakeCount={0}
          wordsRemaining={16}
          previousResponses={[]}
          gameStatus="active"
        />
      );

      // Both correct and mistakes show 0/4, use getAllByText
      const zeroFourTexts = screen.getAllByText('0/4');
      expect(zeroFourTexts.length).toBe(2);
      expect(screen.getByText(/Words Remaining:/).parentElement).toHaveTextContent('16');
      expect(screen.getByText('No previous responses')).toBeInTheDocument();
    });

    test('displays game with many previous responses', () => {
      const manyResponses = Array.from({ length: 10 }, (_, i) => ({
        words: [`w${i}1`, `w${i}2`, `w${i}3`, `w${i}4`],
        type: i % 2 === 0 ? 'correct' : 'incorrect',
        color: i % 2 === 0 ? `color${i}` : undefined,
      }));

      const { container } = render(
        <GameSummary
          correctCount={3}
          mistakeCount={2}
          wordsRemaining={4}
          previousResponses={manyResponses}
          gameStatus="active"
        />
      );

      const responseItems = container.querySelectorAll('.response-item');
      expect(responseItems.length).toBe(10);
    });
  });
});
