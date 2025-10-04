/**
 * Tests for the PuzzleInterface component.
 * Tests the main puzzle interaction interface and state management.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import PuzzleInterface from '../../src/components/PuzzleInterface';

// Mock the API service
jest.mock('../../src/services/apiService', () => ({
  setupPuzzle: jest.fn(),
  getNextRecommendation: jest.fn(),
  recordResponse: jest.fn(),
}));

describe('PuzzleInterface Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
  });

  test('renders all required UI elements per functional requirements', () => {
    render(<PuzzleInterface />);
    
    // FR-002: File picker input with placeholder "Puzzle File" and gray "Setup Puzzle" button
    const fileInput = screen.getByLabelText(/puzzle file/i);
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveAttribute('type', 'file');
    
    const setupButton = screen.getByRole('button', { name: /setup puzzle/i });
    expect(setupButton).toBeInTheDocument();
    expect(setupButton).toHaveClass('gray-button');
    
    // FR-003: Remaining puzzle words in 3-line text area with green "Next Recommendation" button
    const remainingWordsArea = screen.getByLabelText(/remaining puzzle words/i);
    expect(remainingWordsArea).toBeInTheDocument();
    expect(remainingWordsArea).toHaveAttribute('rows', '3');
    
    const nextRecButton = screen.getByRole('button', { name: /next recommendation/i });
    expect(nextRecButton).toBeInTheDocument();
    expect(nextRecButton).toHaveClass('green-button');
    
    // FR-004: Recommended group and connection text areas
    const recommendedGroup = screen.getByLabelText(/recommended group/i);
    expect(recommendedGroup).toBeInTheDocument();
    
    const groupConnection = screen.getByLabelText(/group connection/i);
    expect(groupConnection).toBeInTheDocument();
    
    // FR-005: Counters for correct groups and mistakes
    const correctCounter = screen.getByText(/count correct groups/i);
    expect(correctCounter).toBeInTheDocument();
    
    const mistakeCounter = screen.getByText(/count mistakes/i);
    expect(mistakeCounter).toBeInTheDocument();
  });

  test('renders color-coded response buttons per FR-006', () => {
    render(<PuzzleInterface />);
    
    // FR-006: Color-coded response buttons (Yellow, Green, Blue, Purple)
    const yellowButton = screen.getByRole('button', { name: /yellow/i });
    expect(yellowButton).toBeInTheDocument();
    expect(yellowButton).toHaveClass('yellow-button');
    
    const greenButton = screen.getByRole('button', { name: /green/i });
    expect(greenButton).toBeInTheDocument();
    expect(greenButton).toHaveClass('green-button');
    
    const blueButton = screen.getByRole('button', { name: /blue/i });
    expect(blueButton).toBeInTheDocument();
    expect(blueButton).toHaveClass('blue-button');
    
    const purpleButton = screen.getByRole('button', { name: /purple/i });
    expect(purpleButton).toBeInTheDocument();
    expect(purpleButton).toHaveClass('purple-button');
    
    // FR-007: "Incorrect" (red) and "One-away" (orange) response buttons
    const incorrectButton = screen.getByRole('button', { name: /incorrect/i });
    expect(incorrectButton).toBeInTheDocument();
    expect(incorrectButton).toHaveClass('red-button');
    
    const oneAwayButton = screen.getByRole('button', { name: /one-away/i });
    expect(oneAwayButton).toBeInTheDocument();
    expect(oneAwayButton).toHaveClass('orange-button');
  });

  test('renders previous guesses display per FR-008', () => {
    render(<PuzzleInterface />);
    
    // FR-008: Track and display previous guesses with color coding
    const previousGuesses = screen.getByLabelText(/previous guesses/i);
    expect(previousGuesses).toBeInTheDocument();
  });

  test('handles file upload and puzzle setup per FR-009', async () => {
    const mockSetupPuzzle = require('../../src/services/apiService').setupPuzzle;
    mockSetupPuzzle.mockResolvedValue({
      remaining_words: ['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8', 'word9', 'word10', 'word11', 'word12', 'word13', 'word14', 'word15', 'word16'],
      status: 'success'
    });

    render(<PuzzleInterface />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    const setupButton = screen.getByRole('button', { name: /setup puzzle/i });
    
    // Create a mock file
    const file = new File(['word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16'], 'puzzle.csv', {
      type: 'text/csv',
    });
    
    // Upload file and setup puzzle
    await userEvent.upload(fileInput, file);
    fireEvent.click(setupButton);
    
    // Wait for API call and UI update
    await waitFor(() => {
      expect(mockSetupPuzzle).toHaveBeenCalledWith(expect.any(String));
    });
    
    // Verify remaining words are displayed
    const remainingWordsArea = screen.getByLabelText(/remaining puzzle words/i);
    expect(remainingWordsArea).toHaveValue(expect.stringContaining('word1'));
  });

  test('handles recommendations per FR-010', async () => {
    const mockGetNextRecommendation = require('../../src/services/apiService').getNextRecommendation;
    mockGetNextRecommendation.mockResolvedValue({
      words: ['word1', 'word2', 'word3', 'word4'],
      connection: 'group of related words',
      status: 'success'
    });

    render(<PuzzleInterface />);
    
    const nextRecButton = screen.getByRole('button', { name: /next recommendation/i });
    fireEvent.click(nextRecButton);
    
    await waitFor(() => {
      expect(mockGetNextRecommendation).toHaveBeenCalled();
    });
    
    // Verify recommendation display
    const recommendedGroup = screen.getByLabelText(/recommended group/i);
    expect(recommendedGroup).toHaveValue(expect.stringContaining('word1'));
    
    const groupConnection = screen.getByLabelText(/group connection/i);
    expect(groupConnection).toHaveValue('group of related words');
  });

  test('handles correct responses per FR-011 and FR-014', async () => {
    const mockRecordResponse = require('../../src/services/apiService').recordResponse;
    mockRecordResponse.mockResolvedValue({
      remaining_words: ['word5', 'word6', 'word7', 'word8', 'word9', 'word10', 'word11', 'word12'],
      correct_count: 1,
      mistake_count: 0,
      game_status: 'active'
    });

    render(<PuzzleInterface />);
    
    const yellowButton = screen.getByRole('button', { name: /yellow/i });
    fireEvent.click(yellowButton);
    
    await waitFor(() => {
      expect(mockRecordResponse).toHaveBeenCalledWith('correct', 'Yellow');
    });
    
    // FR-014: Button should be disabled and gray after being clicked
    expect(yellowButton).toBeDisabled();
    expect(yellowButton).toHaveClass('gray-button');
    
    // FR-011: Correct counter should increment
    const correctCounter = screen.getByText(/count correct groups: 1/i);
    expect(correctCounter).toBeInTheDocument();
  });

  test('handles win condition per FR-015', async () => {
    const mockRecordResponse = require('../../src/services/apiService').recordResponse;
    mockRecordResponse.mockResolvedValue({
      remaining_words: [],
      correct_count: 4,
      mistake_count: 0,
      game_status: 'won'
    });

    render(<PuzzleInterface />);
    
    const yellowButton = screen.getByRole('button', { name: /yellow/i });
    fireEvent.click(yellowButton);
    
    await waitFor(() => {
      expect(screen.getByText(/successfully solved the puzzle/i)).toBeInTheDocument();
    });
  });

  test('handles loss condition per FR-016', async () => {
    const mockRecordResponse = require('../../src/services/apiService').recordResponse;
    mockRecordResponse.mockResolvedValue({
      remaining_words: ['word1', 'word2', 'word3', 'word4'],
      correct_count: 0,
      mistake_count: 4,
      game_status: 'lost'
    });

    render(<PuzzleInterface />);
    
    const incorrectButton = screen.getByRole('button', { name: /incorrect/i });
    fireEvent.click(incorrectButton);
    
    await waitFor(() => {
      expect(screen.getByText(/unable to solve puzzle/i)).toBeInTheDocument();
    });
    
    // All buttons except Setup Puzzle should be disabled
    const colorButtons = screen.getAllByRole('button').filter(btn => 
      !btn.textContent?.includes('Setup Puzzle')
    );
    colorButtons.forEach(button => {
      expect(button).toBeDisabled();
    });
  });

  test('handles error conditions per FR-018', async () => {
    const mockRecordResponse = require('../../src/services/apiService').recordResponse;
    mockRecordResponse.mockRejectedValue(new Error('No recommendation to respond to'));

    render(<PuzzleInterface />);
    
    const yellowButton = screen.getByRole('button', { name: /yellow/i });
    fireEvent.click(yellowButton);
    
    await waitFor(() => {
      expect(screen.getByText(/no recommendation to respond to/i)).toBeInTheDocument();
    });
  });

  test('resets disabled/gray state for color buttons when a new puzzle is started', async () => {
    const mockRecordResponse = require('../../src/services/apiService').recordResponse;
    mockRecordResponse.mockResolvedValue({
      remaining_words: ['word5', 'word6', 'word7', 'word8'],
      correct_count: 1,
      mistake_count: 0,
      game_status: 'active'
    });

    const { rerender } = render(
      <PuzzleInterface
        words={['w1','w2','w3','w4','w5']}
        recommendation={['w1','w2','w3','w4']}
        recommendationConnection={'conn'}
        correctCount={0}
        mistakeCount={0}
        gameStatus={'active'}
        isLoading={false}
        error={null}
        onGetRecommendation={jest.fn()}
        onRecordResponse={jest.fn()}
        previousResponses={[]}
      />
    );

    const yellowButton = screen.getByRole('button', { name: /yellow/i });
    // click to disable and gray it
    fireEvent.click(yellowButton);

    await waitFor(() => {
      expect(yellowButton).toBeDisabled();
      expect(yellowButton).toHaveClass('gray-button');
    });

    // Simulate starting a new puzzle: component will be re-rendered with gameStatus 'waiting'
    rerender(
      <PuzzleInterface
        words={[]}
        recommendation={['w1','w2','w3','w4']}
        recommendationConnection={''}
        correctCount={0}
        mistakeCount={0}
        gameStatus={'waiting'}
        isLoading={false}
        error={null}
        onGetRecommendation={jest.fn()}
        onRecordResponse={jest.fn()}
        previousResponses={[]}
      />
    );

    // Then simulate setting up a new active puzzle (gameStatus -> active) so buttons reappear
    rerender(
      <PuzzleInterface
        words={['w1','w2','w3','w4','w5']}
        recommendation={['w1','w2','w3','w4']}
        recommendationConnection={'conn'}
        correctCount={0}
        mistakeCount={0}
        gameStatus={'active'}
        isLoading={false}
        error={null}
        onGetRecommendation={jest.fn()}
        onRecordResponse={jest.fn()}
        previousResponses={[]}
      />
    );

    const yellowButtonAfter = screen.getByRole('button', { name: /yellow/i });
    // After a new puzzle start the button should be enabled and no longer gray
    expect(yellowButtonAfter).not.toBeDisabled();
    expect(yellowButtonAfter).not.toHaveClass('gray-button');
  });
});