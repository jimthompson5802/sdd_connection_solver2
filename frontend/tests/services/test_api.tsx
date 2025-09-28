/**
 * Tests for the API service module.
 * Tests HTTP communication with the backend API.
 */

import { setupPuzzle, getNextRecommendation, recordResponse } from '../../src/services/api';

// Mock fetch globally
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('API Service', () => {
  const mockApiUrl = 'http://localhost:8000';
  
  beforeEach(() => {
    jest.clearAllMocks();
    process.env.REACT_APP_API_URL = mockApiUrl;
  });

  afterEach(() => {
    delete process.env.REACT_APP_API_URL;
  });

  describe('setupPuzzle', () => {
    const mockWords = 'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16';

    test('makes POST request to setup-puzzle endpoint with correct data', async () => {
      const mockResponse = { session_id: 'test-session-123' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await setupPuzzle(mockWords);

      expect(mockFetch).toHaveBeenCalledWith(`${mockApiUrl}/setup-puzzle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ words: mockWords }),
      });
      expect(result).toEqual(mockResponse);
    });

    test('throws error when API request fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      } as Response);

      await expect(setupPuzzle(mockWords)).rejects.toThrow('Failed to setup puzzle: 500 Internal Server Error');
    });

    test('throws error when network request fails', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(setupPuzzle(mockWords)).rejects.toThrow('Network error');
    });

    test('handles JSON parsing errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      } as Response);

      await expect(setupPuzzle(mockWords)).rejects.toThrow('Invalid JSON');
    });

    test('validates input parameter', async () => {
      await expect(setupPuzzle('')).rejects.toThrow('Words parameter cannot be empty');
      await expect(setupPuzzle('   ')).rejects.toThrow('Words parameter cannot be empty');
    });
  });

  describe('getNextRecommendation', () => {
    const mockSessionId = 'test-session-123';

    test('makes POST request to next-recommendation endpoint with correct data', async () => {
      const mockResponse = { 
        words: ['word1', 'word2', 'word3', 'word4'],
        confidence: 0.85
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await getNextRecommendation(mockSessionId);

      expect(mockFetch).toHaveBeenCalledWith(`${mockApiUrl}/next-recommendation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: mockSessionId }),
      });
      expect(result).toEqual(mockResponse);
    });

    test('throws error when API request fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      } as Response);

      await expect(getNextRecommendation(mockSessionId)).rejects.toThrow('Failed to get recommendation: 404 Not Found');
    });

    test('throws error when network request fails', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Connection timeout'));

      await expect(getNextRecommendation(mockSessionId)).rejects.toThrow('Connection timeout');
    });

    test('validates session ID parameter', async () => {
      await expect(getNextRecommendation('')).rejects.toThrow('Session ID cannot be empty');
      await expect(getNextRecommendation('   ')).rejects.toThrow('Session ID cannot be empty');
    });

    test('handles response with no recommendations available', async () => {
      const mockResponse = { 
        words: [],
        confidence: 0.0,
        message: 'No more recommendations available'
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await getNextRecommendation(mockSessionId);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('recordResponse', () => {
    const mockSessionId = 'test-session-123';
    const mockWords = ['word1', 'word2', 'word3', 'word4'];
    const mockResult = 'correct';

    test('makes POST request to record-response endpoint with correct data', async () => {
      const mockResponse = { 
        status: 'recorded',
        remaining_groups: 3
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await recordResponse(mockSessionId, mockWords, mockResult);

      expect(mockFetch).toHaveBeenCalledWith(`${mockApiUrl}/record-response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          session_id: mockSessionId,
          words: mockWords,
          result: mockResult
        }),
      });
      expect(result).toEqual(mockResponse);
    });

    test('throws error when API request fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
      } as Response);

      await expect(recordResponse(mockSessionId, mockWords, mockResult)).rejects.toThrow('Failed to record response: 400 Bad Request');
    });

    test('throws error when network request fails', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Request timeout'));

      await expect(recordResponse(mockSessionId, mockWords, mockResult)).rejects.toThrow('Request timeout');
    });

    test('validates all parameters', async () => {
      await expect(recordResponse('', mockWords, mockResult)).rejects.toThrow('Session ID cannot be empty');
      await expect(recordResponse(mockSessionId, [], mockResult)).rejects.toThrow('Words array cannot be empty');
      await expect(recordResponse(mockSessionId, mockWords, '')).rejects.toThrow('Result cannot be empty');
    });

    test('validates words array content', async () => {
      await expect(recordResponse(mockSessionId, ['', 'word2', 'word3', 'word4'], mockResult))
        .rejects.toThrow('Words array cannot contain empty strings');
      
      await expect(recordResponse(mockSessionId, ['word1'], mockResult))
        .rejects.toThrow('Words array must contain exactly 4 words');
      
      await expect(recordResponse(mockSessionId, ['word1', 'word2', 'word3', 'word4', 'word5'], mockResult))
        .rejects.toThrow('Words array must contain exactly 4 words');
    });

    test('validates result parameter values', async () => {
      await expect(recordResponse(mockSessionId, mockWords, 'invalid'))
        .rejects.toThrow('Result must be one of: correct, incorrect, one-away');
    });

    test('handles different valid result values', async () => {
      const mockResponse = { status: 'recorded', remaining_groups: 2 };
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const validResults = ['correct', 'incorrect', 'one-away'];
      
      for (const result of validResults) {
        await recordResponse(mockSessionId, mockWords, result);
        expect(mockFetch).toHaveBeenCalledWith(
          expect.any(String),
          expect.objectContaining({
            body: JSON.stringify({
              session_id: mockSessionId,
              words: mockWords,
              result: result
            })
          })
        );
      }
    });
  });

  describe('API URL configuration', () => {
    test('uses environment variable for API URL', async () => {
      process.env.REACT_APP_API_URL = 'https://custom-api.example.com';
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ session_id: 'test' }),
      } as Response);

      await setupPuzzle('word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16');

      expect(mockFetch).toHaveBeenCalledWith(
        'https://custom-api.example.com/setup-puzzle',
        expect.any(Object)
      );
    });

    test('falls back to default URL when environment variable is not set', async () => {
      delete process.env.REACT_APP_API_URL;
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ session_id: 'test' }),
      } as Response);

      await setupPuzzle('word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/setup-puzzle',
        expect.any(Object)
      );
    });
  });

  describe('Error handling and resilience', () => {
    test('handles malformed JSON responses gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new SyntaxError('Unexpected token in JSON');
        },
      } as Response);

      await expect(setupPuzzle('words')).rejects.toThrow('Unexpected token in JSON');
    });

    test('handles HTTP status codes appropriately', async () => {
      const statusCodes = [400, 401, 403, 404, 422, 500, 502, 503];
      
      for (const status of statusCodes) {
        mockFetch.mockResolvedValueOnce({
          ok: false,
          status,
          statusText: `Status ${status}`,
        } as Response);

        await expect(setupPuzzle('words')).rejects.toThrow(`Failed to setup puzzle: ${status} Status ${status}`);
      }
    });

    test('handles network timeouts and connection errors', async () => {
      const networkErrors = [
        new Error('Network timeout'),
        new Error('Connection refused'),
        new Error('DNS resolution failed'),
        new TypeError('Failed to fetch')
      ];

      for (const error of networkErrors) {
        mockFetch.mockRejectedValueOnce(error);
        await expect(setupPuzzle('words')).rejects.toThrow(error.message);
      }
    });
  });
});