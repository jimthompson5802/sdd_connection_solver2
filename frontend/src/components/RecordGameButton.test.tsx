/**
 * Tests for RecordGameButton Component
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
import RecordGameButton from './RecordGameButton';
import { gameResultsService } from '../services/gameResultsService';

// Mock the gameResultsService
jest.mock('../services/gameResultsService');

describe('RecordGameButton', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('does not render button when game is not finished', () => {
    const { container } = render(
      <RecordGameButton sessionId="test-session-id" isFinished={false} />
    );

    expect(container.firstChild).toBeNull();
  });

  test('renders record button for completed game', () => {
    render(
      <RecordGameButton sessionId="test-session-id" isFinished={true} />
    );

    expect(screen.getByRole('button', { name: /record game/i })).toBeInTheDocument();
  });

  test('successfully records game when button clicked', async () => {
    (gameResultsService.recordGame as jest.Mock).mockResolvedValueOnce(undefined);

    const onRecordSuccess = jest.fn();

    render(
      <RecordGameButton
        sessionId="test-session-id"
        isFinished={true}
        onRecordSuccess={onRecordSuccess}
      />
    );

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should show recording state
    expect(await screen.findByText(/recording\.\.\./i)).toBeInTheDocument();

    // Should call the service
    await waitFor(() => {
      expect(gameResultsService.recordGame).toHaveBeenCalledWith('test-session-id');
    });

    // Should show success message
    expect(await screen.findByText(/game recorded successfully/i)).toBeInTheDocument();

    // Should call success callback
    expect(onRecordSuccess).toHaveBeenCalled();

    // Button should remain disabled after success
    expect(button).toBeDisabled();
  });

  test('disables button during API call to prevent duplicates', async () => {
    let resolvePromise: () => void;
    const promise = new Promise<void>((resolve) => {
      resolvePromise = resolve;
    });

    (gameResultsService.recordGame as jest.Mock).mockReturnValueOnce(promise);

    render(
      <RecordGameButton sessionId="test-session-id" isFinished={true} />
    );

    const button = screen.getByRole('button', { name: /record game/i });

    // Button should be enabled initially
    expect(button).not.toBeDisabled();

    // Click button
    fireEvent.click(button);

    // Button should be disabled during API call
    expect(button).toBeDisabled();

    // Resolve the promise
    resolvePromise!();

    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText(/game recorded successfully/i)).toBeInTheDocument();
    });

    // Button should remain disabled after success
    expect(button).toBeDisabled();
  });

  test('shows error message for duplicate game', async () => {
    (gameResultsService.recordGame as jest.Mock).mockRejectedValueOnce(
      new Error('Game already exists for this date')
    );

    render(
      <RecordGameButton sessionId="test-session-id" isFinished={true} />
    );

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should show duplicate error message
    expect(await screen.findByText(/already been recorded/i)).toBeInTheDocument();

    // Button should remain disabled for duplicate
    expect(button).toBeDisabled();
  });

  test('shows error message for incomplete session', async () => {
    (gameResultsService.recordGame as jest.Mock).mockRejectedValueOnce(
      new Error('Game must be completed before recording')
    );

    render(
      <RecordGameButton sessionId="test-session-id" isFinished={true} />
    );

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should show error message
    expect(await screen.findByText(/must be completed/i)).toBeInTheDocument();

    // Button should remain disabled
    expect(button).toBeDisabled();
  });

  test('shows error message and allows retry for network errors', async () => {
    (gameResultsService.recordGame as jest.Mock).mockRejectedValueOnce(
      new Error('Network error occurred')
    );

    render(
      <RecordGameButton sessionId="test-session-id" isFinished={true} />
    );

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should show network error message
    expect(await screen.findByText(/network error/i)).toBeInTheDocument();

    // Button should be enabled for retry
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });

  test('shows error message for session not found', async () => {
    (gameResultsService.recordGame as jest.Mock).mockRejectedValueOnce(
      new Error('Session not found')
    );

    render(
      <RecordGameButton sessionId="test-session-id" isFinished={true} />
    );

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should show not found error message
    expect(await screen.findByText(/not found/i)).toBeInTheDocument();

    // Button should be enabled for retry
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });

  test('shows generic error message for unknown errors', async () => {
    (gameResultsService.recordGame as jest.Mock).mockRejectedValueOnce(
      new Error('Some unknown error')
    );

    render(
      <RecordGameButton sessionId="test-session-id" isFinished={true} />
    );

    const button = screen.getByRole('button', { name: /record game/i });

    // Click button
    fireEvent.click(button);

    // Should show generic error message
    expect(await screen.findByText(/failed to record game/i)).toBeInTheDocument();

    // Button should be enabled for retry
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });
});
