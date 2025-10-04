/**
 * PuzzleInterface component - main interface for interacting with the puzzle.
 * Displays current state, recommendations, and handles user interactions.
 */

import React, { useEffect, useState } from 'react';
import { PuzzleInterfaceProps } from '../types/puzzle';

const PuzzleInterface: React.FC<PuzzleInterfaceProps> = ({
  words,
  recommendation,
  recommendationConnection,
  correctCount,
  mistakeCount,
  gameStatus,
  isLoading,
  error,
  onGetRecommendation,
  onRecordResponse,
  previousResponses,
}) => {
  const handleGetRecommendation = () => {
    if (!isLoading && gameStatus === 'active') {
      onGetRecommendation();
    }
  };

  const handleResponseClick = (type: 'correct' | 'incorrect' | 'one-away', color?: string) => {
    if (!isLoading && gameStatus === 'active') {
      // If this is a correct response with a color, immediately disable that color button
      // so the UI reflects the selection (FR-014). The actual recording is handled by the
      // parent via onRecordResponse.
      if (type === 'correct' && color) {
        setDisabledColors(prev => new Set(prev).add(color));
      }

      onRecordResponse(type, color);
    }
  };

  // Track which color buttons have been disabled by the user (after selecting that color)
  const [disabledColors, setDisabledColors] = useState<Set<string>>(new Set());

  // When a new puzzle is started (gameStatus goes back to 'waiting') reset the disabled colors
  // so buttons are re-enabled and return to their original color.
  useEffect(() => {
    if (gameStatus === 'waiting') {
      setDisabledColors(new Set());
    }
  }, [gameStatus]);

  const renderGameStatus = () => {
    switch (gameStatus) {
      case 'won':
        return <div className="game-status won">🎉 Congratulations! You solved the puzzle!</div>;
      case 'lost':
        return <div className="game-status lost">Game Over - Maximum mistakes reached</div>;
      case 'waiting':
        return <div className="game-status waiting">Upload a CSV file to start</div>;
      default:
        return null;
    }
  };

  const renderWordGrid = () => {
    if (words.length === 0) return null;

    return (
      <div className="word-grid">
        <h3>Remaining Words ({words.length})</h3>
        <div className="words-container">
          {words.map((word, index) => (
            <span key={index} className="word-item">
              {word}
            </span>
          ))}
        </div>
      </div>
    );
  };

  const renderRecommendation = () => {
    if (recommendation.length === 0) return null;

    return (
      <div className="recommendation-section">
        <h3>Current Recommendation</h3>
        <div className="recommendation-words">
          {recommendation.map((word, index) => (
            <span key={index} className="recommended-word">
              {word}
            </span>
          ))}
        </div>
        {recommendationConnection && (
          <p className="recommendation-connection">
            <strong>Connection:</strong> {recommendationConnection}
          </p>
        )}
      </div>
    );
  };

  const renderResponseButtons = () => {
    if (gameStatus !== 'active' || recommendation.length === 0) return null;

    return (
      <div className="response-buttons">
        <h4>How was this recommendation?</h4>
        <div className="button-group">
          <button
            onClick={() => handleResponseClick('correct', 'Yellow')}
            disabled={isLoading || disabledColors.has('Yellow')}
            className={`response-button correct yellow ${disabledColors.has('Yellow') ? 'gray-button' : ''}`}
          >
            Correct (Yellow)
          </button>
          <button
            onClick={() => handleResponseClick('correct', 'Green')}
            disabled={isLoading || disabledColors.has('Green')}
            className={`response-button correct green ${disabledColors.has('Green') ? 'gray-button' : ''}`}
          >
            Correct (Green)
          </button>
          <button
            onClick={() => handleResponseClick('correct', 'Blue')}
            disabled={isLoading || disabledColors.has('Blue')}
            className={`response-button correct blue ${disabledColors.has('Blue') ? 'gray-button' : ''}`}
          >
            Correct (Blue)
          </button>
          <button
            onClick={() => handleResponseClick('correct', 'Purple')}
            disabled={isLoading || disabledColors.has('Purple')}
            className={`response-button correct purple ${disabledColors.has('Purple') ? 'gray-button' : ''}`}
          >
            Correct (Purple)
          </button>
        </div>
        <div className="button-group">
          <button
            onClick={() => handleResponseClick('incorrect')}
            disabled={isLoading}
            className="response-button incorrect"
          >
            Incorrect
          </button>
          <button
            onClick={() => handleResponseClick('one-away')}
            disabled={isLoading}
            className="response-button one-away"
          >
            One Away
          </button>
        </div>
      </div>
    );
  };

  const renderStats = () => {
    return (
      <div className="game-stats">
        <div className="stat-item">
          <span className="stat-label">Correct Groups:</span>
          <span className="stat-value">{correctCount}/4</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Mistakes:</span>
          <span className="stat-value">{mistakeCount}/4</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Words Remaining:</span>
          <span className="stat-value">{words.length}</span>
        </div>
      </div>
    );
  };

  const renderPreviousResponses = () => {
    // Show the history panel for any non-waiting game state so it persists after responses
    if (gameStatus === 'waiting') return null;

    return (
      <div className="previous-responses">
        <h4>Previous Guesses</h4>
        <div className="previous-list">
          {previousResponses && previousResponses.length > 0 ? (
            previousResponses.map((resp, idx) => (
              <div key={idx} className="previous-item">
                <div className={`response-badge ${resp.type} ${resp.color ? resp.color.toLowerCase() : ''}`}></div>
                <div className="response-words">{resp.words.join(', ')}</div>
                <div className="response-meta">{new Date(resp.timestamp).toLocaleTimeString()}</div>
              </div>
            ))
          ) : (
            <div className="previous-item empty">
              <div className="response-words">No previous guesses yet</div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="puzzle-interface">
      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {renderGameStatus()}

      {gameStatus === 'active' && (
        <>
          {renderStats()}
          {renderWordGrid()}
          
          <div className="recommendation-controls">
            <button
              onClick={handleGetRecommendation}
              disabled={isLoading}
              className="primary-button get-recommendation"
            >
              {isLoading ? 'Getting Recommendation...' : 'Get Recommendation'}
            </button>
          </div>

          {renderRecommendation()}
          {renderResponseButtons()}
          {renderPreviousResponses()}
        </>
      )}

      {isLoading && (
        <div className="loading-indicator">
          <span>Loading...</span>
        </div>
      )}
    </div>
  );
};

export default PuzzleInterface;