/**
 * T023: Game Results Service
 *
 * API client service for game history operations.
 * Handles recording completed games and retrieving game history.
 */

/**
 * Request payload for recording a completed game
 */
export interface RecordGameRequest {
  session_id: string;
  game_date: string; // ISO 8601 with timezone
}

/**
 * Game result data structure
 */
export interface GameResultData {
  result_id: number;
  puzzle_id: string;
  game_date: string;
  puzzle_solved: boolean;
  count_groups_found: number;
  count_mistakes: number;
  total_guesses: number;
  llm_provider_name: string | null;
  llm_model_name: string | null;
}

/**
 * Response from recording a game
 */
export interface RecordGameResponse {
  status: 'created' | 'conflict';
  result?: GameResultData;
  code?: string;
  message?: string;
}

/**
 * Response from retrieving game history
 */
export interface GameHistoryResponse {
  status: string;
  results: GameResultData[];
}

/**
 * Error response structure
 */
export interface GameResultError {
  detail: string | {
    status?: string;
    code?: string;
    message?: string;
  };
}

class GameResultsService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  /**
   * Record a completed game to persistent storage.
   *
   * @param sessionId - UUID of the completed puzzle session
   * @param gameDate - ISO 8601 timestamp with timezone (defaults to current time)
   * @returns Promise with the recorded game result
   * @throws Error with details about validation, duplicate, or server errors
   */
  async recordGame(
    sessionId: string,
    gameDate?: string
  ): Promise<RecordGameResponse> {
    // Default to current time if not provided
    const timestamp = gameDate || new Date().toISOString();

    const request: RecordGameRequest = {
      session_id: sessionId,
      game_date: timestamp,
    };

    try {
      const response = await fetch(`${this.baseUrl}/api/v2/game_results`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      const data = await response.json();

      // Handle success (201 Created)
      if (response.status === 201) {
        return data as RecordGameResponse;
      }

      // Handle conflict (409 Duplicate)
      if (response.status === 409) {
        const errorData = data as GameResultError;
        const errorDetail = typeof errorData.detail === 'object'
          ? errorData.detail.message || 'Duplicate game record'
          : errorData.detail;
        throw new Error(errorDetail);
      }

      // Handle bad request (400 Incomplete session)
      if (response.status === 400) {
        const errorData = data as GameResultError;
        const errorDetail = typeof errorData.detail === 'string'
          ? errorData.detail
          : 'Session must be completed before recording';
        throw new Error(errorDetail);
      }

      // Handle not found (404 Session not found)
      if (response.status === 404) {
        throw new Error('Session not found');
      }

      // Handle validation errors (422)
      if (response.status === 422) {
        throw new Error('Invalid request format');
      }

      // Handle server errors (500+)
      if (response.status >= 500) {
        throw new Error('Server error while recording game');
      }

      // Handle other unexpected errors
      throw new Error(`Unexpected response: ${response.status}`);

    } catch (error) {
      // Re-throw if already an Error
      if (error instanceof Error) {
        throw error;
      }
      // Wrap network errors
      throw new Error(`Network error: ${String(error)}`);
    }
  }

  /**
   * Retrieve all recorded game results.
   *
   * @returns Promise with list of game results ordered by date (most recent first)
   * @throws Error if retrieval fails
   */
  async getGameResults(): Promise<GameHistoryResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v2/game_results`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to retrieve game history: ${response.status}`);
      }

      return await response.json();

    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error(`Network error: ${String(error)}`);
    }
  }

  /**
   * Export game results as CSV file.
   *
   * Triggers browser download of CSV file.
   *
   * @returns Promise that resolves when download is triggered
   * @throws Error if export fails
   */
  async exportGameResultsCSV(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v2/game_results?format=csv`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`Failed to export CSV: ${response.status}`);
      }

      // Get CSV content
      const blob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'game_results_extract.csv';

      // Trigger download
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error(`Network error: ${String(error)}`);
    }
  }
}

// Export singleton instance
export const gameResultsService = new GameResultsService();

// Export class for testing
export default GameResultsService;
