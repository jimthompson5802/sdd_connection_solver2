/**
 * PuzzleInterface component - main interface for interacting with the puzzle.
 * Displays current state, recommendations, and handles user interactions.
 */

import React from 'react';
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
}) => {
  const handleGetRecommendation = () => {
    if (!isLoading && gameStatus === 'active') {
      onGetRecommendation();
    }
  };

  const handleResponseClick = (type: 'correct' | 'incorrect' | 'one-away', color?: string) => {
    if (!isLoading && gameStatus === 'active') {
      onRecordResponse(type, color);
    }
  };

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
            disabled={isLoading}
            className="response-button correct yellow"
          >
            Correct (Yellow)
          </button>
          <button
            onClick={() => handleResponseClick('correct', 'Green')}
            disabled={isLoading}
            className="response-button correct green"
          >
            Correct (Green)
          </button>
          <button
            onClick={() => handleResponseClick('correct', 'Blue')}
            disabled={isLoading}
            className="response-button correct blue"
          >
            Correct (Blue)
          </button>
          <button
            onClick={() => handleResponseClick('correct', 'Purple')}
            disabled={isLoading}
            className="response-button correct purple"
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