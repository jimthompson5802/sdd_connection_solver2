/**
 * T035, T040, T041: GameHistoryTable Component
 *
 * Displays game history in a scrollable table with all required fields.
 * Shows empty state when no games recorded.
 */
import React, { useEffect, useState } from 'react';
import { gameResultsService, GameResultData } from '../services/gameResultsService';
import './GameHistoryTable.css';

interface GameHistoryTableProps {
  // No props needed - component fetches its own data
}

const GameHistoryTable: React.FC<GameHistoryTableProps> = () => {
  const [results, setResults] = useState<GameResultData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadGameHistory();
  }, []);

  const loadGameHistory = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await gameResultsService.getGameResults();
      setResults(response.results);
    } catch (err) {
      setError('Failed to load game history');
      console.error('Error loading game history:', err);
    } finally {
      setLoading(false);
    }
  };

  // Loading state (check first)
  if (loading) {
    return (
      <div className="game-history-loading">
        <p>Loading game history...</p>
      </div>
    );
  }

  // Error state (check before empty state)
  if (error) {
    return (
      <div className="game-history-error">
        <p>{error}</p>
        <button onClick={loadGameHistory}>Retry</button>
      </div>
    );
  }

  // T041: Empty state (check after error)
  if (results.length === 0) {
    return (
      <div className="game-history-empty">
        <h3>No Games Recorded</h3>
        <p>Complete a puzzle game and click "Record Game" to record your first game.</p>
      </div>
    );
  }

  // Format date for display
  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
      });
    } catch {
      return dateStr;
    }
  };

  // T035, T040: Table with horizontal and vertical scrolling
  return (
    <div className="game-history-container">
      <div className="game-history-header">
        <h2>Game History</h2>
        <p className="game-history-count">
          {results.length} {results.length === 1 ? 'game' : 'games'} recorded
        </p>
      </div>

      <div className="game-history-table-container">
        <table className="game-history-table">
          <thead>
            <tr>
              <th>Result ID</th>
              <th>Puzzle ID</th>
              <th>Game Date</th>
              <th>Solved</th>
              <th>Groups Found</th>
              <th>Mistakes</th>
              <th>Total Guesses</th>
              <th>LLM Provider</th>
              <th>LLM Model</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result) => (
              <tr key={result.result_id}>
                <td>{result.result_id}</td>
                <td className="puzzle-id-cell" title={result.puzzle_id}>
                  {result.puzzle_id}
                </td>
                <td className="date-cell">{formatDate(result.game_date)}</td>
                <td className={result.puzzle_solved ? 'solved-yes' : 'solved-no'}>
                  {result.puzzle_solved ? '✓ Yes' : '✗ No'}
                </td>
                <td className="count-cell">{result.count_groups_found}</td>
                <td className="count-cell">{result.count_mistakes}</td>
                <td className="count-cell">{result.total_guesses}</td>
                <td className="provider-cell">
                  {result.llm_provider_name || '-'}
                </td>
                <td className="model-cell">
                  {result.llm_model_name || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default GameHistoryTable;
