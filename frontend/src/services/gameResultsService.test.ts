/**
 * Tests for gameResultsService
 */
import GameResultsService, { gameResultsService, RecordGameResponse, GameHistoryResponse } from './gameResultsService';

describe('GameResultsService', () => {
  let service: GameResultsService;

  beforeEach(() => {
    service = new GameResultsService();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('recordGame', () => {
    test('successfully records a game with default date', async () => {
      const mockResponse: RecordGameResponse = {
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
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 201,
        json: async () => mockResponse
      });

      const result = await service.recordGame('test-session-id');

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v2/game_results'),
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: expect.stringContaining('test-session-id')
        })
      );
    });

    test('successfully records a game with custom date', async () => {
      const mockResponse: RecordGameResponse = {
        status: 'created',
        result: {
          result_id: 1,
          puzzle_id: 'abc123',
          game_date: '2025-12-20T10:00:00+00:00',
          puzzle_solved: true,
          count_groups_found: 4,
          count_mistakes: 0,
          total_guesses: 4,
          llm_provider_name: 'openai',
          llm_model_name: 'gpt-4'
        }
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 201,
        json: async () => mockResponse
      });

      const customDate = '2025-12-20T10:00:00+00:00';
      const result = await service.recordGame('test-session-id', customDate);

      expect(result).toEqual(mockResponse);
      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.game_date).toBe(customDate);
    });

    test('throws error for duplicate game (409)', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 409,
        json: async () => ({
          detail: {
            status: 'conflict',
            code: 'duplicate_record',
            message: 'Game already exists for this date'
          }
        })
      });

      await expect(service.recordGame('test-session-id')).rejects.toThrow(
        'Game already exists for this date'
      );
    });

    test('throws error for duplicate game with string detail', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 409,
        json: async () => ({
          detail: 'Duplicate game record'
        })
      });

      await expect(service.recordGame('test-session-id')).rejects.toThrow(
        'Duplicate game record'
      );
    });

    test('throws error for incomplete session (400)', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 400,
        json: async () => ({
          detail: 'Session must be completed before recording'
        })
      });

      await expect(service.recordGame('test-session-id')).rejects.toThrow(
        'Session must be completed before recording'
      );
    });

    test('throws error for session not found (404)', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 404,
        json: async () => ({})
      });

      await expect(service.recordGame('test-session-id')).rejects.toThrow(
        'Session not found'
      );
    });

    test('throws error for validation error (422)', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 422,
        json: async () => ({})
      });

      await expect(service.recordGame('test-session-id')).rejects.toThrow(
        'Invalid request format'
      );
    });

    test('throws error for server error (500)', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 500,
        json: async () => ({})
      });

      await expect(service.recordGame('test-session-id')).rejects.toThrow(
        'Server error while recording game'
      );
    });

    test('throws error for unexpected status code', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 418,
        json: async () => ({})
      });

      await expect(service.recordGame('test-session-id')).rejects.toThrow(
        'Unexpected response: 418'
      );
    });

    test('throws network error when fetch fails', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network failure'));

      await expect(service.recordGame('test-session-id')).rejects.toThrow(
        'Network failure'
      );
    });

    test('wraps non-Error rejections', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce('string error');

      await expect(service.recordGame('test-session-id')).rejects.toThrow(
        'Network error: string error'
      );
    });
  });

  describe('getGameResults', () => {
    test('successfully retrieves game results', async () => {
      const mockResponse: GameHistoryResponse = {
        status: 'success',
        results: [
          {
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
        ]
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await service.getGameResults();

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v2/game_results'),
        expect.objectContaining({
          method: 'GET'
        })
      );
    });

    test('throws error when response is not ok', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500
      });

      await expect(service.getGameResults()).rejects.toThrow(
        'Failed to retrieve game history: 500'
      );
    });

    test('throws network error when fetch fails', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network failure'));

      await expect(service.getGameResults()).rejects.toThrow('Network failure');
    });

    test('wraps non-Error rejections', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce('string error');

      await expect(service.getGameResults()).rejects.toThrow(
        'Network error: string error'
      );
    });
  });

  describe('exportGameResultsCSV', () => {
    let createElementSpy: jest.SpyInstance;
    let appendChildSpy: jest.SpyInstance;
    let removeChildSpy: jest.SpyInstance;
    let mockLink: any;

    beforeEach(() => {
      // Mock document methods
      mockLink = {
        href: '',
        download: '',
        click: jest.fn()
      };

      createElementSpy = jest.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
      appendChildSpy = jest.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any);
      removeChildSpy = jest.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any);

      // Mock URL methods
      (window.URL as any).createObjectURL = jest.fn().mockReturnValue('blob:mock-url');
      (window.URL as any).revokeObjectURL = jest.fn();
    });

    afterEach(() => {
      createElementSpy.mockRestore();
      appendChildSpy.mockRestore();
      removeChildSpy.mockRestore();
    });

    test('successfully exports CSV file', async () => {
      const mockBlob = new Blob(['csv,data'], { type: 'text/csv' });

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        blob: async () => mockBlob
      });

      await service.exportGameResultsCSV();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v2/game_results?format=csv'),
        expect.objectContaining({
          method: 'GET'
        })
      );

      expect(window.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
      expect(createElementSpy).toHaveBeenCalledWith('a');
      expect(appendChildSpy).toHaveBeenCalled();
      expect(removeChildSpy).toHaveBeenCalled();
      expect(window.URL.revokeObjectURL).toHaveBeenCalled();
    });

    test('throws error when response is not ok', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500
      });

      await expect(service.exportGameResultsCSV()).rejects.toThrow(
        'Failed to export CSV: 500'
      );
    });

    test('throws network error when fetch fails', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network failure'));

      await expect(service.exportGameResultsCSV()).rejects.toThrow('Network failure');
    });

    test('wraps non-Error rejections', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce('string error');

      await expect(service.exportGameResultsCSV()).rejects.toThrow(
        'Network error: string error'
      );
    });
  });

  describe('singleton instance', () => {
    test('exports a singleton instance', () => {
      expect(gameResultsService).toBeInstanceOf(GameResultsService);
    });
  });
});
