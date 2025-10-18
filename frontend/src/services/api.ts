/**
 * API client service for communicating with the NYT Connections Puzzle backend.
 * Handles HTTP requests, error handling, and response parsing.
 */

import {
  SetupPuzzleRequest,
  SetupPuzzleResponse,
  NextRecommendationResponse,
  RecordResponseRequest,
  RecordResponseResponse,
  PuzzleError,
} from '../types/puzzle';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  /**
   * Set up a new puzzle with the provided CSV content.
   */
  async setupPuzzle(fileContent: string): Promise<SetupPuzzleResponse> {
    this.validateInput(fileContent, 'File content cannot be empty');

    // Normalize CSV content words to lowercase before sending so backend sees canonical form
    const normalized = fileContent
      .split(',')
      .map(w => w.trim().toLowerCase())
      .join(',');

    const request: SetupPuzzleRequest = {
      file_content: normalized,
    };

    try {
      const response = await fetch(`${this.baseUrl}/api/puzzle/setup_puzzle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new PuzzleError(
          `Failed to setup puzzle: ${response.status} ${response.statusText}`,
          response.status
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof PuzzleError) {
        throw error;
      }
      throw new PuzzleError(`Network error: ${(error as Error).message}`);
    }
  }

  /**
   * Get the next recommendation for word grouping.
   */
  async getNextRecommendation(): Promise<NextRecommendationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/puzzle/next_recommendation`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new PuzzleError(
          `Failed to get recommendation: ${response.status} ${response.statusText}`,
          response.status
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof PuzzleError) {
        throw error;
      }
      throw new PuzzleError(`Network error: ${(error as Error).message}`);
    }
  }

  /**
   * Record the user's response to a recommendation.
   */
  async recordResponse(
    responseType: 'correct' | 'incorrect' | 'one-away',
    color?: string,
    attemptWords?: string[],
    sessionId?: string
  ): Promise<RecordResponseResponse> {
    this.validateResponseType(responseType);
    
    if (responseType === 'correct' && !color) {
      throw new PuzzleError('Color is required for correct responses');
    }

    if (color && !['Yellow', 'Green', 'Blue', 'Purple'].includes(color)) {
      throw new PuzzleError('Color must be one of: Yellow, Green, Blue, Purple');
    }

    // Ensure attemptWords are lowercased when provided
    const normalizedAttempt = attemptWords ? attemptWords.map(w => w.trim().toLowerCase()) : undefined;

    const request: RecordResponseRequest = {
      response_type: responseType,
      ...(color && { color: color as 'Yellow' | 'Green' | 'Blue' | 'Purple' }),
      ...(normalizedAttempt && { attempt_words: normalizedAttempt }),
      ...(sessionId && { session_id: sessionId }),
    };

    try {
      const response = await fetch(`${this.baseUrl}/api/puzzle/record_response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new PuzzleError(
          `Failed to record response: ${response.status} ${response.statusText}`,
          response.status
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof PuzzleError) {
        throw error;
      }
      throw new PuzzleError(`Network error: ${(error as Error).message}`);
    }
  }

  /**
   * Health check endpoint to verify API connectivity.
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new PuzzleError(
          `Health check failed: ${response.status} ${response.statusText}`,
          response.status
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof PuzzleError) {
        throw error;
      }
      throw new PuzzleError(`Network error: ${(error as Error).message}`);
    }
  }

  /**
   * Validate input parameters.
   */
  private validateInput(value: string, errorMessage: string): void {
    if (!value || !value.trim()) {
      throw new PuzzleError(errorMessage);
    }
  }

  /**
   * Validate response type parameter.
   */
  private validateResponseType(responseType: string): void {
    const validTypes = ['correct', 'incorrect', 'one-away'];
    if (!validTypes.includes(responseType)) {
      throw new PuzzleError(`Response type must be one of: ${validTypes.join(', ')}`);
    }
  }

  /**
   * Parse CSV content and validate it has exactly 16 words.
   */
  static parseAndValidateCSV(content: string): string[] {
    if (!content || !content.trim()) {
      throw new PuzzleError('File cannot be empty');
    }

    const words = content.split(',').map(word => word.trim()).filter(word => word);
    
    if (words.length !== 16) {
      throw new PuzzleError('File must contain exactly 16 words');
    }

    if (new Set(words).size !== 16) {
      throw new PuzzleError('All words must be unique');
    }

    return words;
  }

  /**
   * Validate file content before sending to API.
   */
  static validateFileContent(content: string): void {
    ApiService.parseAndValidateCSV(content);
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export class for testing
export { ApiService };

// Named exports for individual functions
export const {
  setupPuzzle,
  getNextRecommendation,
  recordResponse,
  healthCheck,
} = apiService;