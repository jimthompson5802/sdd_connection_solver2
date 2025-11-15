import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import EnhancedPuzzleInterface from '../../../frontend/src/components/EnhancedPuzzleInterface';
import PuzzleInterface from '../../../frontend/src/components/PuzzleInterface';

// Mock minimal props used by the components
const baseProps: any = {
  words: ['ONE', 'TWO', 'THREE'],
  recommendation: [],
  recommendationConnection: '',
  correctCount: 2,
  mistakeCount: 1,
  gameStatus: 'won' as const,
  isLoading: false,
  error: null,
  onRecordResponse: jest.fn(),
  previousResponses: [
    { words: ['ONE','TWO','THREE','FOUR'], type: 'correct', color: 'Yellow', timestamp: new Date() },
    { words: ['ALPHA','BETA'], type: 'incorrect', timestamp: new Date() }
  ],
};

describe('GameSummary integration', () => {
  test('EnhancedPuzzleInterface shows summary on win', () => {
    render(<EnhancedPuzzleInterface {...baseProps} llmProvider={null} onProviderChange={jest.fn()} />);

    // Win message should be visible
    expect(screen.getByText(/congratulations/i)).toBeInTheDocument();

    // Counters from GameSummary
    expect(screen.getByText(/Correct Groups:/i)).toBeInTheDocument();
    expect(screen.getByText(/Mistakes:/i)).toBeInTheDocument();

    // Previous Responses heading and at least one response word
    const heading = screen.getByText(/Previous Responses/i);
    expect(heading).toBeInTheDocument();
    expect(screen.getByText('ONE')).toBeInTheDocument();
    // The list should be expanded when the game is won
    const container = heading.closest('.previous-responses');
    expect(container).toBeTruthy();
    expect(container?.classList.contains('expanded')).toBe(true);
  });

  test('PuzzleInterface shows summary on lost', () => {
    const lostProps = { ...baseProps, gameStatus: 'lost' as const };
    render(<PuzzleInterface {...lostProps} />);

    // Lost message should be visible
    expect(screen.getByText(/Game Over/i)).toBeInTheDocument();

    // Counters present
    expect(screen.getByText(/Correct Groups:/i)).toBeInTheDocument();
    expect(screen.getByText(/Mistakes:/i)).toBeInTheDocument();

    // Previous responses visible and expanded
    const heading = screen.getByText(/Previous Responses/i);
    expect(heading).toBeInTheDocument();
    expect(screen.getByText('ALPHA')).toBeInTheDocument();
    const container = heading.closest('.previous-responses');
    expect(container).toBeTruthy();
    expect(container?.classList.contains('expanded')).toBe(true);
  });
});
