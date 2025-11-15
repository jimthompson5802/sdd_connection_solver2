import React from 'react';

interface PreviousResponse {
  words: string[];
  type?: string;
  color?: string;
  timestamp?: string | Date;
}

interface Props {
  correctCount: number;
  mistakeCount: number;
  wordsRemaining: number;
  previousResponses: PreviousResponse[];
}

/**
 * Reusable GameSummary component that shows counters and previous responses.
 * This is intended to be used both during active play and when a win/lose
 * status message is shown so the player can see final stats.
 */
const GameSummary: React.FC<Props> = ({ correctCount, mistakeCount, wordsRemaining, previousResponses }) => {
  return (
    <div className="game-summary">
      <div className="puzzle-stats summary-stats">
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
          <span className="stat-value">{wordsRemaining}</span>
        </div>
      </div>

      <div className="previous-responses">
        <h4>Previous Responses</h4>
        <div className="responses-list">
          {previousResponses && previousResponses.length > 0 ? (
            previousResponses.map((resp, idx) => (
              <div key={idx} className={`response-item ${resp.type || ''}`}>
                <div className="response-words">
                  {resp.words.map((w, i) => (
                    <span key={i} className="response-word">{w}</span>
                  ))}
                </div>
                <span className={`response-outcome ${resp.type || ''}`}>
                  {(resp.type || '').toUpperCase()}{resp.color ? ` (${resp.color})` : ''}
                </span>
              </div>
            ))
          ) : (
            <div className="response-item empty">
              <div className="response-words">No previous responses</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameSummary;
