/**
 * Comprehensive tests for API Service implementation.
 * Tests all methods, error handling, and edge cases to achieve 80%+ coverage.
 */

import { ApiService, apiService } from './api';
import { PuzzleError } from '../types/puzzle';

// Mock fetch globally
global.fetch = jest.fn();

describe('ApiService - Comprehensive Tests', () => {
  const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('setupPuzzle', () => {
    test('successfully sets up puzzle with valid CSV', async () => {
      const mockResponse = {
        status: 'success',
        remaining_words: ['word1', 'word2', 'word3'],
        correct_count: 0,
        mistake_count: 0,
        game_status: 'active' as const,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.setupPuzzle('word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/puzzle/setup_puzzle',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: expect.stringContaining('file_content'),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    test('normalizes words to lowercase', async () => {
      const mockResponse = {
        status: 'success',
        remaining_words: ['word1'],
        correct_count: 0,
        mistake_count: 0,
        game_status: 'active' as const,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      await apiService.setupPuzzle('WORD1,Word2,WORD3,word4,WORD5,word6,WORD7,word8,WORD9,word10,WORD11,word12,WORD13,word14,WORD15,word16');

      const callBody = JSON.parse(mockFetch.mock.calls[0][1]?.body as string);
      expect(callBody.file_content).toBe('word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16');
    });

    test('throws PuzzleError when content is empty', async () => {
      await expect(apiService.setupPuzzle('')).rejects.toThrow(PuzzleError);
      await expect(apiService.setupPuzzle('   ')).rejects.toThrow('File content cannot be empty');
    });

    test('throws PuzzleError on HTTP error response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
      } as Response);

      await expect(
        apiService.setupPuzzle('word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16')
      ).rejects.toThrow('Failed to setup puzzle: 400 Bad Request');
    });

    test('throws PuzzleError on network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network failure'));

      await expect(
        apiService.setupPuzzle('word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16')
      ).rejects.toThrow('Network error: Network failure');
    });
  });

  describe('getNextRecommendation', () => {
    test('successfully gets recommendation', async () => {
      const mockResponse = {
        recommendation: ['word1', 'word2', 'word3', 'word4'],
        connection: 'test connection',
        remaining_words: ['word5', 'word6'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.getNextRecommendation();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/puzzle/next_recommendation',
        expect.objectContaining({
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        })
      );
      expect(result).toEqual(mockResponse);
    });

    test('throws PuzzleError on 404 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      } as Response);

      await expect(apiService.getNextRecommendation()).rejects.toThrow(
        'Failed to get recommendation: 404 Not Found'
      );
    });

    test('throws PuzzleError on 500 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      } as Response);

      await expect(apiService.getNextRecommendation()).rejects.toThrow(
        'Failed to get recommendation: 500 Internal Server Error'
      );
    });

    test('throws PuzzleError on network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Connection refused'));

      await expect(apiService.getNextRecommendation()).rejects.toThrow(
        'Network error: Connection refused'
      );
    });
  });

  describe('recordResponse', () => {
    test('successfully records correct response with color', async () => {
      const mockResponse = {
        remaining_words: ['word1', 'word2'],
        correct_count: 1,
        mistake_count: 0,
        game_status: 'active' as const,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.recordResponse('correct', 'Yellow');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/puzzle/record_response',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );

      const callBody = JSON.parse(mockFetch.mock.calls[0][1]?.body as string);
      expect(callBody.response_type).toBe('correct');
      expect(callBody.color).toBe('Yellow');
      expect(result).toEqual(mockResponse);
    });

    test('successfully records incorrect response', async () => {
      const mockResponse = {
        remaining_words: ['word1', 'word2', 'word3'],
        correct_count: 0,
        mistake_count: 1,
        game_status: 'active' as const,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.recordResponse('incorrect');

      const callBody = JSON.parse(mockFetch.mock.calls[0][1]?.body as string);
      expect(callBody.response_type).toBe('incorrect');
      expect(callBody.color).toBeUndefined();
      expect(result).toEqual(mockResponse);
    });

    test('successfully records one-away response', async () => {
      const mockResponse = {
        remaining_words: ['word1', 'word2', 'word3'],
        correct_count: 0,
        mistake_count: 1,
        game_status: 'active' as const,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      await apiService.recordResponse('one-away');

      const callBody = JSON.parse(mockFetch.mock.calls[0][1]?.body as string);
      expect(callBody.response_type).toBe('one-away');
    });

    test('normalizes attempt words to lowercase', async () => {
      const mockResponse = {
        remaining_words: ['word5'],
        correct_count: 1,
        mistake_count: 0,
        game_status: 'active' as const,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      await apiService.recordResponse('correct', 'Green', ['WORD1', 'Word2', 'WORD3', 'word4']);

      const callBody = JSON.parse(mockFetch.mock.calls[0][1]?.body as string);
      expect(callBody.attempt_words).toEqual(['word1', 'word2', 'word3', 'word4']);
    });

    test('includes session ID when provided', async () => {
      const mockResponse = {
        remaining_words: ['word1'],
        correct_count: 1,
        mistake_count: 0,
        game_status: 'active' as const,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      await apiService.recordResponse('correct', 'Blue', undefined, 'session-123');

      const callBody = JSON.parse(mockFetch.mock.calls[0][1]?.body as string);
      expect(callBody.session_id).toBe('session-123');
    });

    test('throws error when correct response missing color', async () => {
      await expect(apiService.recordResponse('correct')).rejects.toThrow(
        'Color is required for correct responses'
      );
    });

    test('throws error for invalid color', async () => {
      await expect(apiService.recordResponse('correct', 'Red')).rejects.toThrow(
        'Color must be one of: Yellow, Green, Blue, Purple'
      );
    });

    test('validates all accepted colors', async () => {
      const mockResponse = {
        remaining_words: [],
        correct_count: 4,
        mistake_count: 0,
        game_status: 'won' as const,
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      // Test all valid colors
      await apiService.recordResponse('correct', 'Yellow');
      await apiService.recordResponse('correct', 'Green');
      await apiService.recordResponse('correct', 'Blue');
      await apiService.recordResponse('correct', 'Purple');

      expect(mockFetch).toHaveBeenCalledTimes(4);
    });

    test('throws error for invalid response type', async () => {
      await expect(
        apiService.recordResponse('invalid' as any, 'Yellow')
      ).rejects.toThrow('Response type must be one of: correct, incorrect, one-away');
    });

    test('throws PuzzleError on HTTP error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
      } as Response);

      await expect(apiService.recordResponse('incorrect')).rejects.toThrow(
        'Failed to record response: 400 Bad Request'
      );
    });

    test('throws PuzzleError on network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Timeout'));

      await expect(apiService.recordResponse('incorrect')).rejects.toThrow(
        'Network error: Timeout'
      );
    });
  });

  describe('setupPuzzleFromImage', () => {
    const validRequest = {
      image_base64: 'base64encodedimage',
      image_mime: 'image/png',
      provider_type: 'openai',
      model_name: 'gpt-4-vision-preview',
    };

    test('successfully sets up puzzle from image', async () => {
      const mockResponse = {
        status: 'success',
        remaining_words: ['word1', 'word2', 'word3'],
        extracted_words: ['word1', 'word2', 'word3'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.setupPuzzleFromImage(validRequest);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v2/setup_puzzle_from_image',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
      expect(result).toEqual(mockResponse);
    });

    test('throws error when image_base64 is empty', async () => {
      await expect(
        apiService.setupPuzzleFromImage({ ...validRequest, image_base64: '' })
      ).rejects.toThrow('Image data cannot be empty');
    });

    test('throws error when image_mime is empty', async () => {
      await expect(
        apiService.setupPuzzleFromImage({ ...validRequest, image_mime: '' })
      ).rejects.toThrow('Image MIME type cannot be empty');
    });

    test('throws error when provider_type is empty', async () => {
      await expect(
        apiService.setupPuzzleFromImage({ ...validRequest, provider_type: '' })
      ).rejects.toThrow('Provider type cannot be empty');
    });

    test('throws error when model_name is empty', async () => {
      await expect(
        apiService.setupPuzzleFromImage({ ...validRequest, model_name: '' })
      ).rejects.toThrow('Model name cannot be empty');
    });

    test('throws PuzzleError on 413 (payload too large)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 413,
        statusText: 'Payload Too Large',
      } as Response);

      await expect(apiService.setupPuzzleFromImage(validRequest)).rejects.toThrow(
        'Failed to setup puzzle from image: 413 Payload Too Large'
      );
    });

    test('throws PuzzleError on 422 (validation error)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
      } as Response);

      await expect(apiService.setupPuzzleFromImage(validRequest)).rejects.toThrow(
        'Failed to setup puzzle from image: 422 Unprocessable Entity'
      );
    });

    test('throws PuzzleError on network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Connection timeout'));

      await expect(apiService.setupPuzzleFromImage(validRequest)).rejects.toThrow(
        'Network error: Connection timeout'
      );
    });
  });

  describe('healthCheck', () => {
    test('successfully performs health check', async () => {
      const mockResponse = {
        status: 'healthy',
        service: 'nyt-connections-api',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiService.healthCheck();

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/health', {
        method: 'GET',
      });
      expect(result).toEqual(mockResponse);
    });

    test('throws PuzzleError when health check fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
      } as Response);

      await expect(apiService.healthCheck()).rejects.toThrow(
        'Health check failed: 503 Service Unavailable'
      );
    });

    test('throws PuzzleError on network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network unreachable'));

      await expect(apiService.healthCheck()).rejects.toThrow(
        'Network error: Network unreachable'
      );
    });
  });

  describe('parseAndValidateCSV', () => {
    test('validates correct CSV with 16 words', () => {
      const validCSV =
        'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16';

      const result = ApiService.parseAndValidateCSV(validCSV);
      expect(result).toHaveLength(16);
      expect(result[0]).toBe('word1');
      expect(result[15]).toBe('word16');
    });

    test('trims whitespace from words', () => {
      const csvWithSpaces =
        ' word1 , word2, word3 ,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16';

      const result = ApiService.parseAndValidateCSV(csvWithSpaces);
      expect(result[0]).toBe('word1');
      expect(result[1]).toBe('word2');
      expect(result[2]).toBe('word3');
    });

    test('throws error for empty content', () => {
      expect(() => ApiService.parseAndValidateCSV('')).toThrow('File cannot be empty');
      expect(() => ApiService.parseAndValidateCSV('   ')).toThrow('File cannot be empty');
    });

    test('throws error for wrong number of words', () => {
      const tooFewWords = 'word1,word2,word3';
      const tooManyWords =
        'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16,word17';

      expect(() => ApiService.parseAndValidateCSV(tooFewWords)).toThrow(
        'File must contain exactly 16 words'
      );
      expect(() => ApiService.parseAndValidateCSV(tooManyWords)).toThrow(
        'File must contain exactly 16 words'
      );
    });

    test('throws error for duplicate words', () => {
      const duplicates =
        'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word1';

      expect(() => ApiService.parseAndValidateCSV(duplicates)).toThrow(
        'All words must be unique'
      );
    });

    test('counts valid words after filtering empty ones', () => {
      const withEmptyWords =
        'word1,word2,,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16';

      // This CSV has 16 non-empty words, so it should pass validation
      const result = ApiService.parseAndValidateCSV(withEmptyWords);
      expect(result).toHaveLength(16);
      expect(result).not.toContain('');
    });
  });

  describe('validateFileContent', () => {
    test('validates correct file content', () => {
      const validCSV =
        'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16';

      expect(() => ApiService.validateFileContent(validCSV)).not.toThrow();
    });

    test('throws error for invalid content', () => {
      const invalidCSV = 'word1,word2,word3';

      expect(() => ApiService.validateFileContent(invalidCSV)).toThrow(
        'File must contain exactly 16 words'
      );
    });
  });

  describe('PuzzleError class', () => {
    test('creates error with message', () => {
      const error = new PuzzleError('Test error message');
      expect(error.message).toBe('Test error message');
      expect(error.name).toBe('PuzzleError');
    });

    test('creates error with status code', () => {
      const error = new PuzzleError('Test error', 404);
      expect(error.message).toBe('Test error');
      expect(error.status).toBe(404);
    });

    test('is instance of Error', () => {
      const error = new PuzzleError('Test');
      expect(error).toBeInstanceOf(Error);
    });
  });

  describe('ApiService constructor', () => {
    test('uses default base URL when env var not set', () => {
      const service = new ApiService();
      expect(service['baseUrl']).toBe('http://localhost:8000');
    });

    test('uses environment variable for base URL when set', () => {
      const originalEnv = process.env.REACT_APP_API_URL;
      process.env.REACT_APP_API_URL = 'https://api.example.com';

      const service = new ApiService();
      expect(service['baseUrl']).toBe('https://api.example.com');

      // Restore original value
      process.env.REACT_APP_API_URL = originalEnv;
    });
  });

  describe('Named exports', () => {
    test('exports singleton methods', () => {
      expect(typeof apiService.setupPuzzle).toBe('function');
      expect(typeof apiService.getNextRecommendation).toBe('function');
      expect(typeof apiService.recordResponse).toBe('function');
      expect(typeof apiService.setupPuzzleFromImage).toBe('function');
      expect(typeof apiService.healthCheck).toBe('function');
    });
  });
});
