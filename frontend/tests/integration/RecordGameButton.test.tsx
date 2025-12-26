/**
 * T014: Integration test for record game button interaction
 *
 * Tests the complete user flow for recording a completed game:
 * - Button visibility on completed game
 * - Button interaction and API call
 * - Success/error message handling
 * - Button disabled state during submission
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// This test will fail until RecordGameButton component is implemented
describe('RecordGameButton Integration', () => {
  beforeEach(() => {
    // Mock fetch API
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('renders record button for completed game', () => {
    // Mock completed session data
    const completedSession = {
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
      isFinished: true,
      isWon: true,
      groupsFound: 4,
      mistakesMade: 1,
      totalGuesses: 5
    };

    // This will fail until RecordGameButton component exists
    const RecordGameButton = require('../../src/components/RecordGameButton').default;

    render(<RecordGameButton sessionData={completedSession} />);

    // Button should be visible
    expect(screen.getByRole('button', { name: /record game/i })).toBeInTheDocument();
  });

  test('successfully records game when button clicked', async () => {
    const completedSession = {
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
      isFinished: true,
      isWon: true,
      groupsFound: 4,
      mistakesMade: 1,
      totalGuesses: 5
    };

    // Mock successful API response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => ({
        status: 'created',
        result: {
          result_id: 1,
          puzzle_id: 'abc123',
          game_date: '2025-12-24T15:30:00+00:00',
          puzzle_solved: true,
          count_groups_found: 4,
          count_mistakes: 1,
          total_guesses: 5,
          llm_provider_name: 'openai',
          llm_model_name: 'gpt-4'
        }
      })
    });

    const RecordGameButton = require('../../src/components/RecordGameButton').default;

    render(<RecordGameButton sessionData={completedSession} />);

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should call API
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v2/game_results',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: expect.stringContaining(completedSession.sessionId)
        })
      );
    });

    // Should show success message
    await waitFor(() => {
      expect(screen.getByText(/game recorded successfully/i)).toBeInTheDocument();
    });
  });

  test('disables button during API call to prevent duplicates', async () => {
    const completedSession = {
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
      isFinished: true,
      isWon: true,
      groupsFound: 4,
      mistakesMade: 1,
      totalGuesses: 5
    };

    // Mock delayed API response
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      new Promise(resolve =>
        setTimeout(() => resolve({
          ok: true,
          status: 201,
          json: async () => ({
            status: 'created',
            result: {}
          })
        }), 100)
      )
    );

    const RecordGameButton = require('../../src/components/RecordGameButton').default;

    render(<RecordGameButton sessionData={completedSession} />);

    const button = screen.getByRole('button', { name: /record game/i });

    // Button should be enabled initially
    expect(button).not.toBeDisabled();

    // Click button
    fireEvent.click(button);

    // Button should be disabled during API call
    expect(button).toBeDisabled();

    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText(/game recorded successfully/i)).toBeInTheDocument();
    });

    // Button should remain disabled after success (cannot record same game twice on same date)
    expect(button).toBeDisabled();
  });

  test('shows error message for duplicate game', async () => {
    const completedSession = {
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
      isFinished: true,
      isWon: true,
      groupsFound: 4,
      mistakesMade: 1,
      totalGuesses: 5
    };

    // Mock 409 Conflict response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 409,
      json: async () => ({
        status: 'conflict',
        code: 'duplicate_record',
        message: 'A game result for this puzzle and game_date already exists.'
      })
    });

    const RecordGameButton = require('../../src/components/RecordGameButton').default;

    render(<RecordGameButton sessionData={completedSession} />);

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should show duplicate error message
    await waitFor(() => {
      expect(screen.getByText(/already exists/i)).toBeInTheDocument();
    });
  });

  test('shows error message for incomplete session', async () => {
    const incompleteSession = {
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
      isFinished: false,
      isWon: false,
      groupsFound: 2,
      mistakesMade: 1,
      totalGuesses: 3
    };

    // Mock 400 Bad Request response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({
        detail: 'Session must be completed before recording'
      })
    });

    const RecordGameButton = require('../../src/components/RecordGameButton').default;

    render(<RecordGameButton sessionData={incompleteSession} />);

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should show incomplete session error
    await waitFor(() => {
      expect(screen.getByText(/must be completed/i)).toBeInTheDocument();
    });
  });

  test('shows error message for network failure', async () => {
    const completedSession = {
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
      isFinished: true,
      isWon: true,
      groupsFound: 4,
      mistakesMade: 1,
      totalGuesses: 5
    };

    // Mock network error
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    const RecordGameButton = require('../../src/components/RecordGameButton').default;

    render(<RecordGameButton sessionData={completedSession} />);

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should show network error message
    await waitFor(() => {
      expect(screen.getByText(/failed to record game|network error/i)).toBeInTheDocument();
    });

    // Button should be re-enabled after network error so user can retry
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });

  test('does not render button for incomplete game', () => {
    const incompleteSession = {
      sessionId: '123e4567-e89b-12d3-a456-426614174000',
      isFinished: false,
      isWon: false,
      groupsFound: 2,
      mistakesMade: 1,
      totalGuesses: 3
    };

    const RecordGameButton = require('../../src/components/RecordGameButton').default;

    render(<RecordGameButton sessionData={incompleteSession} />);

    // Button should not be visible for incomplete games
    expect(screen.queryByRole('button', { name: /record game/i })).not.toBeInTheDocument();
  });
});
