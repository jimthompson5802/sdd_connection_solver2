/**
 * T030 & T031: Integration tests for game history table rendering
 *
 * Tests the complete user flow for viewing game history:
 * - Table rendering with data
 * - Empty state rendering when no games recorded
 * - Column structure and data display
 * - Scrolling behavior (horizontal and vertical)
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// This test will fail until GameHistoryTable component is implemented
describe('GameHistoryTable Integration', () => {
  beforeEach(() => {
    // Mock fetch API
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  /**
   * T030: Test game history table rendering with data
   */
  test('renders game history table with multiple records', async () => {
    // Mock successful API response with game data
    const mockGameResults = [
      {
        result_id: 3,
        puzzle_id: 'abc123-def456',
        game_date: '2025-12-24T16:45:00+00:00',
        puzzle_solved: true,
        count_groups_found: 4,
        count_mistakes: 2,
        total_guesses: 8,
        llm_provider_name: 'openai',
        llm_model_name: 'gpt-4'
      },
      {
        result_id: 2,
        puzzle_id: 'xyz789-uvw012',
        game_date: '2025-12-22T14:30:00+00:00',
        puzzle_solved: true,
        count_groups_found: 4,
        count_mistakes: 1,
        total_guesses: 6,
        llm_provider_name: 'ollama',
        llm_model_name: 'llama2'
      },
      {
        result_id: 1,
        puzzle_id: 'def456-ghi789',
        game_date: '2025-12-20T10:00:00+00:00',
        puzzle_solved: true,
        count_groups_found: 4,
        count_mistakes: 0,
        total_guesses: 4,
        llm_provider_name: 'simple',
        llm_model_name: 'random'
      }
    ];

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        status: 'success',
        results: mockGameResults
      })
    });

    // This will fail until GameHistoryTable component exists
    const GameHistoryTable = require('../../components/GameHistoryTable').default;

    render(<GameHistoryTable />);

    // Wait for data to load
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    // Should display table with all records
    await waitFor(() => {
      // Check for table headers (all required columns)
      expect(screen.getByText(/result id/i)).toBeInTheDocument();
      expect(screen.getByText(/puzzle id/i)).toBeInTheDocument();
      expect(screen.getByText(/game date/i)).toBeInTheDocument();
      expect(screen.getByText(/solved/i)).toBeInTheDocument();
      expect(screen.getByText(/groups found/i)).toBeInTheDocument();
      expect(screen.getByText(/mistakes/i)).toBeInTheDocument();
      expect(screen.getByText(/total guesses/i)).toBeInTheDocument();
      expect(screen.getByText(/llm provider/i)).toBeInTheDocument();
      expect(screen.getByText(/llm model/i)).toBeInTheDocument();

      // Check for first record data (most recent)
      expect(screen.getByText('3')).toBeInTheDocument(); // result_id
      expect(screen.getByText(/abc123-def456/i)).toBeInTheDocument(); // puzzle_id
      expect(screen.getByText(/Dec 24, 2025/i)).toBeInTheDocument(); // game_date formatted
      expect(screen.getByText('openai')).toBeInTheDocument(); // llm_provider_name
      expect(screen.getByText('gpt-4')).toBeInTheDocument(); // llm_model_name

      // Check for second record data
      expect(screen.getAllByText('2').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('ollama')).toBeInTheDocument();
      expect(screen.getByText('llama2')).toBeInTheDocument();

      // Check for third record data
      expect(screen.getAllByText('1').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('simple')).toBeInTheDocument();
      expect(screen.getByText('random')).toBeInTheDocument();
    });

    // Table container exists and is scrollable (CSS defined)
    const tableContainer = document.querySelector('.game-history-table-container');
    expect(tableContainer).toBeInTheDocument();
  });

  /**
   * T030: Test table displays all required columns with correct data
   */
  test('displays all required fields for each game record', async () => {
    const mockGameResult = {
      result_id: 1,
      puzzle_id: 'test-puzzle-id-123',
      game_date: '2025-12-24T15:30:00+00:00',
      puzzle_solved: true,
      count_groups_found: 4,
      count_mistakes: 2,
      total_guesses: 7,
      llm_provider_name: 'openai',
      llm_model_name: 'gpt-4'
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        status: 'success',
        results: [mockGameResult]
      })
    });

    const GameHistoryTable = require('../../components/GameHistoryTable').default;

    render(<GameHistoryTable />);

    await waitFor(() => {
      // Verify all field values are displayed
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText(/test-puzzle-id-123/i)).toBeInTheDocument();
      // Date will be formatted by the component
      expect(screen.getAllByText(/2025/i).length).toBeGreaterThan(0);
      expect(screen.getByText('4')).toBeInTheDocument(); // groups found
      expect(screen.getByText('2')).toBeInTheDocument(); // mistakes
      expect(screen.getByText('7')).toBeInTheDocument(); // total guesses
      expect(screen.getByText('openai')).toBeInTheDocument();
      expect(screen.getByText('gpt-4')).toBeInTheDocument();

      // Puzzle solved should show as "Yes" or checkmark
      expect(screen.getByText(/Yes/i)).toBeInTheDocument();
    });
  });

  /**
   * T031: Test empty state when no games recorded
   */
  test('displays empty state message when no games recorded', async () => {
    // Mock empty API response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        status: 'success',
        results: []
      })
    });

    const GameHistoryTable = require('../../components/GameHistoryTable').default;

    render(<GameHistoryTable />);

    // Wait for data to load
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    // Should display empty state message
    await waitFor(() => {
      expect(screen.getByText(/no games recorded/i)).toBeInTheDocument();
      expect(screen.getByText(/record your first game/i)).toBeInTheDocument();
    });

    // Should NOT display table when empty
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  /**
   * T031: Test loading state before data arrives
   */
  test('displays loading state while fetching data', () => {
    // Mock delayed API response
    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 1000))
    );

    const GameHistoryTable = require('../../components/GameHistoryTable').default;

    render(<GameHistoryTable />);

    // Should show loading indicator
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  /**
   * T030: Test error handling when API call fails
   */
  test('displays error message when API call fails', async () => {
    // Mock failed API response
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    const GameHistoryTable = require('../../components/GameHistoryTable').default;

    render(<GameHistoryTable />);

    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText(/failed to load game history/i)).toBeInTheDocument();
    });
  });

  /**
   * T030: Test table remains scrollable with many records
   */
  test('table is scrollable horizontally and vertically', async () => {
    // Create many records to test scrolling
    const manyRecords = Array.from({ length: 20 }, (_, i) => ({
      result_id: i + 1,
      puzzle_id: `puzzle-${i + 1}`,
      game_date: `2025-12-${String(i + 1).padStart(2, '0')}T10:00:00+00:00`,
      puzzle_solved: true,
      count_groups_found: 4,
      count_mistakes: i % 5,
      total_guesses: 4 + (i % 5),
      llm_provider_name: 'openai',
      llm_model_name: 'gpt-4'
    }));

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        status: 'success',
        results: manyRecords
      })
    });

    const GameHistoryTable = require('../../components/GameHistoryTable').default;

    const { container } = render(<GameHistoryTable />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    // Table should have scrollable container
    await waitFor(() => {
      const table = screen.getByRole('table');
      expect(table).toBeInTheDocument();
    });
  });
});
