import React, { useRef, useEffect, useState } from 'react';

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
  gameStatus?: 'active' | 'waiting' | 'won' | 'lost';
}

/**
 * Reusable GameSummary component that shows counters and previous responses.
 * This is intended to be used both during active play and when a win/lose
 * status message is shown so the player can see final stats.
 */
const GameSummary: React.FC<Props> = ({ correctCount, mistakeCount, wordsRemaining, previousResponses, gameStatus }) => {
  const expanded = gameStatus && (gameStatus === 'won' || gameStatus === 'lost');
  const containerRef = useRef<HTMLDivElement | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);
  const [maxHeightPx, setMaxHeightPx] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (!expanded) {
      setMaxHeightPx(undefined);
      return;
    }

    // Measure the inner responses-list height and set an inline maxHeight so
    // the list expands to its full content but is capped to a viewport fraction.
    const listEl = listRef.current;
    if (!listEl) return;

    // Use requestAnimationFrame to ensure layout is stable
    const id = requestAnimationFrame(() => {
      const contentHeight = listEl.scrollHeight;
      const viewportCap = Math.floor(window.innerHeight * 0.8); // 80% of viewport
      const finalHeight = Math.min(contentHeight + 32, viewportCap); // add padding buffer
      setMaxHeightPx(`${finalHeight}px`);
    });

    return () => cancelAnimationFrame(id);
  }, [expanded, previousResponses]);

  // Respect reduced-motion preference: if user prefers reduced motion, don't animate
  const prefersReducedMotion = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <div className="game-summary" aria-live={expanded ? 'polite' : undefined}>
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

      <div
        ref={containerRef}
        className={`previous-responses ${expanded ? 'expanded' : ''}`}
        aria-label="Previous responses"
        tabIndex={0}
        style={expanded && maxHeightPx ? { maxHeight: maxHeightPx, transition: prefersReducedMotion ? 'none' : 'max-height 300ms ease' } : undefined}
      >
        <h4>Previous Responses</h4>
        <div ref={listRef} className="responses-list">
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
