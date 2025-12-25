/**
 * T045: Integration test for export CSV button interaction
 *
 * Tests the complete user flow for exporting game history as CSV:
 * - Button visibility on game history page
 * - Button interaction and API call
 * - CSV download trigger
 * - Error message handling
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// This test will fail until ExportCSVButton component is implemented
describe('ExportCSVButton Integration', () => {
  beforeEach(() => {
    // Mock fetch API
    global.fetch = jest.fn();
    
    // Mock URL.createObjectURL
    global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = jest.fn();
    
    // Mock document.createElement and click
    const mockLink = {
      href: '',
      download: '',
      click: jest.fn(),
      remove: jest.fn(),
    };
    jest.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('renders export CSV button', () => {
    // This will fail until ExportCSVButton component exists
    const ExportCSVButton = require('../../src/components/ExportCSVButton').default;

    render(<ExportCSVButton />);

    // Button should be visible
    expect(screen.getByRole('button', { name: /export csv/i })).toBeInTheDocument();
  });

  test('successfully exports CSV when button clicked', async () => {
    // Mock successful CSV response
    const mockCSVContent = `result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name
1,abc123,2025-12-24T15:30:00+00:00,true,4,1,5,openai,gpt-4
2,def456,2025-12-24T16:45:00+00:00,false,3,4,10,ollama,llama2`;

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: {
        get: (name: string) => {
          if (name === 'content-type') return 'text/csv; charset=utf-8';
          if (name === 'content-disposition') return 'attachment; filename="game_results_extract.csv"';
          return null;
        }
      },
      text: async () => mockCSVContent
    });

    const ExportCSVButton = require('../../src/components/ExportCSVButton').default;

    render(<ExportCSVButton />);

    const button = screen.getByRole('button', { name: /export csv/i });

    // Click button
    fireEvent.click(button);

    // Should call API with correct format parameter
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v2/game_results?format=csv',
        expect.objectContaining({
          method: 'GET'
        })
      );
    });

    // Should create blob URL and trigger download
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });

    // Should click the download link
    await waitFor(() => {
      const mockLink = (document.createElement as jest.Mock).mock.results[0].value;
      expect(mockLink.click).toHaveBeenCalled();
    });
  });

  test('button is disabled during export', async () => {
    // Mock delayed CSV response
    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        status: 200,
        headers: {
          get: (name: string) => {
            if (name === 'content-type') return 'text/csv; charset=utf-8';
            if (name === 'content-disposition') return 'attachment; filename="game_results_extract.csv"';
            return null;
          }
        },
        text: async () => 'result_id,puzzle_id\n1,abc123'
      }), 100))
    );

    const ExportCSVButton = require('../../src/components/ExportCSVButton').default;

    render(<ExportCSVButton />);

    const button = screen.getByRole('button', { name: /export csv/i });

    // Button should be enabled initially
    expect(button).not.toBeDisabled();

    // Click button
    fireEvent.click(button);

    // Button should be disabled during export
    await waitFor(() => {
      expect(button).toBeDisabled();
    });

    // Wait for export to complete
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    }, { timeout: 200 });
  });

  test('displays error message when export fails', async () => {
    // Mock failed API response
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    const ExportCSVButton = require('../../src/components/ExportCSVButton').default;

    render(<ExportCSVButton />);

    const button = screen.getByRole('button', { name: /export csv/i });

    // Click button
    fireEvent.click(button);

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/failed to export/i)).toBeInTheDocument();
    });

    // Button should be re-enabled after error
    expect(button).not.toBeDisabled();
  });

  test('displays error message when API returns non-200', async () => {
    // Mock failed API response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: async () => 'Internal Server Error'
    });

    const ExportCSVButton = require('../../src/components/ExportCSVButton').default;

    render(<ExportCSVButton />);

    const button = screen.getByRole('button', { name: /export csv/i });

    // Click button
    fireEvent.click(button);

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/failed to export/i)).toBeInTheDocument();
    });

    // Button should be re-enabled after error
    expect(button).not.toBeDisabled();
  });

  test('handles empty CSV response', async () => {
    // Mock empty CSV response (only header)
    const mockCSVContent = `result_id,puzzle_id,game_date,puzzle_solved,count_groups_found,count_mistakes,total_guesses,llm_provider_name,llm_model_name`;

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: {
        get: (name: string) => {
          if (name === 'content-type') return 'text/csv; charset=utf-8';
          if (name === 'content-disposition') return 'attachment; filename="game_results_extract.csv"';
          return null;
        }
      },
      text: async () => mockCSVContent
    });

    const ExportCSVButton = require('../../src/components/ExportCSVButton').default;

    render(<ExportCSVButton />);

    const button = screen.getByRole('button', { name: /export csv/i });

    // Click button
    fireEvent.click(button);

    // Should still trigger download even with empty data
    await waitFor(() => {
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });

    await waitFor(() => {
      const mockLink = (document.createElement as jest.Mock).mock.results[0].value;
      expect(mockLink.click).toHaveBeenCalled();
    });
  });

  test('uses correct filename for download', async () => {
    const mockCSVContent = `result_id,puzzle_id\n1,abc123`;

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: {
        get: (name: string) => {
          if (name === 'content-type') return 'text/csv; charset=utf-8';
          if (name === 'content-disposition') return 'attachment; filename="game_results_extract.csv"';
          return null;
        }
      },
      text: async () => mockCSVContent
    });

    const ExportCSVButton = require('../../src/components/ExportCSVButton').default;

    render(<ExportCSVButton />);

    const button = screen.getByRole('button', { name: /export csv/i });

    // Click button
    fireEvent.click(button);

    // Should set correct filename on download link
    await waitFor(() => {
      const mockLink = (document.createElement as jest.Mock).mock.results[0].value;
      expect(mockLink.download).toBe('game_results_extract.csv');
    });
  });
});
