/**
 * Tests for the main App component.
 * Tests the root application structure and routing.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import App from '../../src/App';
import { apiService } from '../../src/services/api';

// Mock child components
jest.mock('../../src/components/FileUpload', () => {
  return function MockFileUpload({ onFileUpload, isLoading, error }: any) {
    return (
      <div data-testid="file-upload">
        <button onClick={() => onFileUpload('test content')}>Upload File</button>
        {isLoading && <div>Loading...</div>}
        {error && <div>{error}</div>}
      </div>
    );
  };
});

jest.mock('../../src/components/ImagePuzzleSetup', () => {
  return {
    ImagePuzzleSetup: function MockImagePuzzleSetup({ onImageSetup, onError }: any) {
      return (
        <div data-testid="image-puzzle-setup">
          <button onClick={() => onImageSetup(['word1', 'word2', 'word3', 'word4'], 'session-123')}>
            Setup from Image
          </button>
          <button onClick={() => onError('Image error')}>Trigger Error</button>
        </div>
      );
    }
  };
});

jest.mock('../../src/components/EnhancedPuzzleInterface', () => {
  return function MockEnhancedPuzzleInterface({
    onRecordResponse,
    onProviderChange,
    gameStatus,
    words,
    correctCount,
    mistakeCount
  }: any) {
    return (
      <div data-testid="enhanced-puzzle-interface">
        <div>Game Status: {gameStatus}</div>
        <div>Words: {words.join(', ')}</div>
        <div>Correct: {correctCount}</div>
        <div>Mistakes: {mistakeCount}</div>
        <button onClick={() => onRecordResponse('correct', 'blue', ['word1', 'word2'])}>
          Record Correct
        </button>
        <button onClick={() => onRecordResponse('incorrect', 'red', ['word3', 'word4'])}>
          Record Incorrect
        </button>
        <button onClick={() => onRecordResponse('one-away', 'yellow', ['word5', 'word6'])}>
          Record One Away
        </button>
        <button onClick={() => onProviderChange({ type: 'openai', name: 'OpenAI' })}>
          Change Provider
        </button>
      </div>
    );
  };
});

jest.mock('../../src/pages/GameHistoryPage', () => {
  return function MockGameHistoryPage() {
    return <div data-testid="game-history-page">Game History</div>;
  };
});

jest.mock('../../src/services/api');

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders the main application title', () => {
    render(<App />);

    const titleElement = screen.getByRole('heading', { level: 1 });
    expect(titleElement).toHaveTextContent(/NYT Connections Puzzle Assistant/i);
    expect(titleElement).toBeInTheDocument();
  });

  test('renders centered layout structure', () => {
    render(<App />);

    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
    expect(main).toHaveClass('App-main');
  });

  test('renders navigation sidebar component', () => {
    render(<App />);

    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toBeInTheDocument();
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
  });

  test('applies correct CSS styling for grid layout', () => {
    render(<App />);

    const title = screen.getByRole('heading', { level: 1 });
    const main = document.querySelector('.App-main');
    const sidebar = document.querySelector('.sidebar');

    expect(title).toBeInTheDocument();
    expect(main).toBeInTheDocument();
    expect(main).toHaveClass('App-main');
    expect(sidebar).toBeInTheDocument();
    expect(sidebar).toHaveClass('sidebar');
  });

  test('renders without crashing', () => {
    expect(() => render(<App />)).not.toThrow();
  });

  test('has proper semantic structure', () => {
    render(<App />);

    const mainElement = screen.getByRole('main');
    expect(mainElement).toBeInTheDocument();

    const headingElement = screen.getByRole('heading', { level: 1 });
    expect(headingElement).toBeInTheDocument();
    expect(headingElement).toHaveTextContent(/NYT Connections Puzzle Assistant/i);
  });

  test('contains all required UI components in initial state', () => {
    render(<App />);

    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
    expect(screen.getByText('From File')).toBeInTheDocument();
    expect(screen.getByText('Select action in Left Side Bar')).toBeInTheDocument();
  });

  test('maintains consistent theme and styling', () => {
    render(<App />);
    const appRoot = document.querySelector('.App');
    expect(appRoot).toBeInTheDocument();
    expect(appRoot).toHaveClass('App');
  });

  test('navigates to file upload view when from-file action is triggered', () => {
    const { container } = render(<App />);

    // Simulate navigation action by clicking on From File button
    const fromFileButton = screen.getByText('From File');
    fireEvent.click(fromFileButton);

    // Should render FileUpload component
    expect(screen.getByTestId('file-upload')).toBeInTheDocument();
  });

  test('navigates to image setup view when from-image action is triggered', () => {
    render(<App />);

    const fromImageButton = screen.getByText('From Image');
    fireEvent.click(fromImageButton);

    expect(screen.getByTestId('image-puzzle-setup')).toBeInTheDocument();
  });

  test('navigates to game history view when view-past-games action is triggered', () => {
    render(<App />);

    // First expand the Game History menu
    const gameHistoryButton = screen.getByText('Game History');
    fireEvent.click(gameHistoryButton);

    // Then click on View Past Games
    const viewPastGamesButton = screen.getByText('View Past Games');
    fireEvent.click(viewPastGamesButton);

    expect(screen.getByTestId('game-history-page')).toBeInTheDocument();
  });

  test('handles file upload successfully and transitions to puzzle view', async () => {
    (apiService.setupPuzzle as jest.Mock).mockResolvedValueOnce({
      session_id: 'test-session-123',
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 0,
      game_status: 'active'
    });

    render(<App />);

    // Navigate to file upload
    const fromFileButton = screen.getByText('From File');
    fireEvent.click(fromFileButton);

    // Trigger file upload
    const uploadButton = screen.getByText('Upload File');
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(apiService.setupPuzzle).toHaveBeenCalledWith('test content');
    });

    await waitFor(() => {
      expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
    });

    expect(screen.getByText(/Game Status: active/)).toBeInTheDocument();
  });

  test('handles file upload error', async () => {
    (apiService.setupPuzzle as jest.Mock).mockRejectedValueOnce(
      new Error('Failed to setup puzzle')
    );

    render(<App />);

    const fromFileButton = screen.getByText('From File');
    fireEvent.click(fromFileButton);

    const uploadButton = screen.getByText('Upload File');
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to setup puzzle')).toBeInTheDocument();
    });
  });

  test('handles image setup successfully', () => {
    render(<App />);

    const fromImageButton = screen.getByText('From Image');
    fireEvent.click(fromImageButton);

    const setupButton = screen.getByText('Setup from Image');
    fireEvent.click(setupButton);

    expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
    expect(screen.getByText(/Game Status: active/)).toBeInTheDocument();
  });

  test('handles image error', () => {
    render(<App />);

    const fromImageButton = screen.getByText('From Image');
    fireEvent.click(fromImageButton);

    const errorButton = screen.getByText('Trigger Error');
    fireEvent.click(errorButton);

    // The error is set in puzzle state but stays on the same view
    expect(screen.getByTestId('image-puzzle-setup')).toBeInTheDocument();
  });

  test('records correct response and updates state', async () => {
    (apiService.setupPuzzle as jest.Mock).mockResolvedValueOnce({
      session_id: 'test-session-123',
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 0,
      game_status: 'active'
    });

    (apiService.recordResponse as jest.Mock).mockResolvedValueOnce({
      remaining_words: ['word3', 'word4'],
      correct_count: 1,
      mistake_count: 0,
      game_status: 'active'
    });

    render(<App />);

    // Setup puzzle
    fireEvent.click(screen.getByText('From File'));
    fireEvent.click(screen.getByText('Upload File'));

    await waitFor(() => {
      expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
    });

    // Record correct response
    const recordButton = screen.getByText('Record Correct');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(apiService.recordResponse).toHaveBeenCalledWith('correct', 'blue', ['word1', 'word2']);
    });

    await waitFor(() => {
      expect(screen.getByText(/Correct: 1/)).toBeInTheDocument();
    });
  });

  test('records incorrect response and updates state', async () => {
    (apiService.setupPuzzle as jest.Mock).mockResolvedValueOnce({
      session_id: 'test-session-123',
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 0,
      game_status: 'active'
    });

    (apiService.recordResponse as jest.Mock).mockResolvedValueOnce({
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 1,
      game_status: 'active'
    });

    render(<App />);

    fireEvent.click(screen.getByText('From File'));
    fireEvent.click(screen.getByText('Upload File'));

    await waitFor(() => {
      expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
    });

    const recordButton = screen.getByText('Record Incorrect');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(apiService.recordResponse).toHaveBeenCalledWith('incorrect', 'red', ['word3', 'word4']);
    });

    await waitFor(() => {
      expect(screen.getByText(/Mistakes: 1/)).toBeInTheDocument();
    });
  });

  test('records one-away response', async () => {
    (apiService.setupPuzzle as jest.Mock).mockResolvedValueOnce({
      session_id: 'test-session-123',
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 0,
      game_status: 'active'
    });

    (apiService.recordResponse as jest.Mock).mockResolvedValueOnce({
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 0,
      game_status: 'active'
    });

    render(<App />);

    fireEvent.click(screen.getByText('From File'));
    fireEvent.click(screen.getByText('Upload File'));

    await waitFor(() => {
      expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
    });

    const recordButton = screen.getByText('Record One Away');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(apiService.recordResponse).toHaveBeenCalledWith('one-away', 'yellow', ['word5', 'word6']);
    });
  });

  test('transitions to puzzle-complete view when game is won', async () => {
    (apiService.setupPuzzle as jest.Mock).mockResolvedValueOnce({
      session_id: 'test-session-123',
      remaining_words: ['word1', 'word2'],
      correct_count: 3,
      mistake_count: 0,
      game_status: 'active'
    });

    (apiService.recordResponse as jest.Mock).mockResolvedValueOnce({
      remaining_words: [],
      correct_count: 4,
      mistake_count: 0,
      game_status: 'won'
    });

    render(<App />);

    fireEvent.click(screen.getByText('From File'));
    fireEvent.click(screen.getByText('Upload File'));

    await waitFor(() => {
      expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Record Correct'));

    await waitFor(() => {
      expect(screen.getByText(/Game Status: won/)).toBeInTheDocument();
    });
  });

  test('transitions to puzzle-complete view when game is lost', async () => {
    (apiService.setupPuzzle as jest.Mock).mockResolvedValueOnce({
      session_id: 'test-session-123',
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 3,
      game_status: 'active'
    });

    (apiService.recordResponse as jest.Mock).mockResolvedValueOnce({
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 4,
      game_status: 'lost'
    });

    render(<App />);

    fireEvent.click(screen.getByText('From File'));
    fireEvent.click(screen.getByText('Upload File'));

    await waitFor(() => {
      expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Record Incorrect'));

    await waitFor(() => {
      expect(screen.getByText(/Game Status: lost/)).toBeInTheDocument();
    });
  });

  test('handles record response error', async () => {
    (apiService.setupPuzzle as jest.Mock).mockResolvedValueOnce({
      session_id: 'test-session-123',
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 0,
      game_status: 'active'
    });

    (apiService.recordResponse as jest.Mock).mockRejectedValueOnce(
      new Error('Failed to record response')
    );

    render(<App />);

    fireEvent.click(screen.getByText('From File'));
    fireEvent.click(screen.getByText('Upload File'));

    await waitFor(() => {
      expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Record Correct'));

    // Error should be handled but component stays visible
    await waitFor(() => {
      expect(apiService.recordResponse).toHaveBeenCalled();
    });
  });

  test('handles LLM provider change', async () => {
    (apiService.setupPuzzle as jest.Mock).mockResolvedValueOnce({
      session_id: 'test-session-123',
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 0,
      game_status: 'active'
    });

    render(<App />);

    fireEvent.click(screen.getByText('From File'));
    fireEvent.click(screen.getByText('Upload File'));

    await waitFor(() => {
      expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
    });

    const changeProviderButton = screen.getByText('Change Provider');
    fireEvent.click(changeProviderButton);

    // Provider change should be handled (no visual change to test, but ensures handler is called)
    expect(screen.getByTestId('enhanced-puzzle-interface')).toBeInTheDocument();
  });
});