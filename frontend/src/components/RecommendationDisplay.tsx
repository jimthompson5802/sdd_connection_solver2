import React from 'react';
import { RecommendationResponse } from '../types/recommendation';
import { LLMProvider } from '../types/llm-provider';
import './RecommendationDisplay.css';

/**
 * Props for the RecommendationDisplay component
 */
export interface RecommendationDisplayProps {
  /** The recommendation response from the API */
  recommendation: RecommendationResponse | null;
  /** Whether recommendations are currently loading */
  isLoading?: boolean;
  /** Error message if recommendation failed */
  error?: string;
  /** Current LLM provider information */
  provider?: LLMProvider | null;
  /** Callback when user accepts a recommendation */
  /** Callback when user applies an alternative suggestion */
  onApplyAlternative?: (words: string[]) => void;
  /** Whether to show provider information */
  showProviderInfo?: boolean;
  /** Whether to show recommendation metadata */
  showMetadata?: boolean;
  /** Custom CSS class name */
  className?: string;
}

/**
 * RecommendationDisplay Component
 * 
 * Displays AI-generated puzzle recommendations with user interaction options.
 * Shows recommendation details, confidence levels, and provider information.
 */
export const RecommendationDisplay: React.FC<RecommendationDisplayProps> = ({
  recommendation,
  isLoading = false,
  error,
  provider,
  onApplyAlternative,
  showProviderInfo = true,
  showMetadata = true,
  className = ''
}) => {
  // Confidence removed — UI no longer shows or computes confidence levels.

  const formatDuration = (milliseconds: number) => {
    const seconds = milliseconds / 1000;
    if (seconds < 1) return `${milliseconds}ms`;
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(1)}s`;
  };

  const getProviderDisplayName = (provider: LLMProvider) => {
    switch (provider.provider_type) {
      case 'simple':
        return 'Simple Provider';
      case 'ollama':
        return 'Ollama';
      case 'openai':
        return 'OpenAI';
      default:
        return provider.provider_type;
    }
  };

  // Handle provider_used which can be a string or object depending on backend/test mocks
  const getProviderUsedLabel = (prov: RecommendationResponse['provider_used']) => {
    if (!prov) return '';
    if (typeof prov === 'string') return prov;
    // prov is LLMProvider
    const name = getProviderDisplayName(prov);
    return prov.model_name ? `${name} (${prov.model_name})` : name;
  };

  // Primary accept/reject actions removed from this component.

  const componentClasses = [
    'recommendation-display',
    className
  ].filter(Boolean).join(' ');

  if (isLoading) {
    return (
      <div className={`${componentClasses} recommendation-display--loading`}>
        <div className="recommendation-display__loading">
          <div className="loading-spinner" aria-hidden="true">🤔</div>
          <p>Analyzing puzzle and generating recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${componentClasses} recommendation-display--error`}>
        <div className="recommendation-display__error">
          <span className="error-icon" aria-hidden="true">❌</span>
          <p>Failed to generate recommendations: {error}</p>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className={`${componentClasses} recommendation-display--empty`}>
        <div className="recommendation-display__empty">
          <span className="empty-icon" aria-hidden="true">💡</span>
          <p>No recommendations available. Submit a puzzle to get AI assistance!</p>
        </div>
      </div>
    );
  }

  return (
    <div className={componentClasses}>
      {showProviderInfo && provider && (
        <div className="recommendation-display__provider">
          <div className="provider-info">
            <span className="provider-icon" aria-hidden="true">🤖</span>
            <span className="provider-name">{getProviderDisplayName(provider)}</span>
            {provider.model_name && (
              <span className="provider-model">({provider.model_name})</span>
            )}
          </div>
        </div>
      )}

      <div className="recommendation-display__content">
        <div className="recommendation-display__header">
          <h3 className="recommendation-title">AI Recommendation</h3>
          {showMetadata && recommendation.generation_time_ms && (
            <div className="recommendation-metadata">
              <span className="metadata-item">
                ⏱️ {formatDuration(recommendation.generation_time_ms)}
              </span>
              <span className="metadata-item">
                🤖 {getProviderUsedLabel(recommendation.provider_used)}
              </span>
            </div>
          )}
        </div>

        <div className="recommendation-display__main">
          <div className="recommendation-primary">
            <div className="recommendation-words">
              {recommendation.recommended_words.map((word, index) => (
                <span key={index} className="recommendation-word">
                  {word}
                </span>
              ))}
            </div>
            
            {/* Confidence display removed */}
          </div>

          <div className="recommendation-explanation">
            <h4 className="explanation-title">Connection Explanation</h4>
            <p className="explanation-text">{recommendation.connection_explanation}</p>
          </div>

          {/* Primary actions removed: these buttons were intentionally removed
              to simplify the UI. Alternatives can still be applied via the
              alternative suggestions below. */}
        </div>

        {recommendation.alternative_suggestions && recommendation.alternative_suggestions.length > 0 && (
          <div className="recommendation-display__alternatives">
            <h4 className="alternatives-title">Alternative Suggestions</h4>
            <div className="alternatives-list">
              {recommendation.alternative_suggestions.map((alternative, index) => (
                <div key={index} className="alternative-suggestion">
                  <div className="alternative-words">
                    {alternative.map((word, wordIndex) => (
                      <span key={wordIndex} className="alternative-word">
                        {word}
                      </span>
                    ))}
                  </div>
                  <button
                    className="alternative-action"
                    onClick={() => onApplyAlternative && onApplyAlternative(alternative)}
                    disabled={!onApplyAlternative}
                    title="Use this alternative"
                  >
                    Try This
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {recommendation.puzzle_state && (
          <div className="recommendation-display__puzzle-state">
            <h4 className="puzzle-state-title">Puzzle State</h4>
            <div className="puzzle-state-info">
              <div className="state-item">
                <strong>Remaining Words:</strong> {recommendation.puzzle_state.remaining_words.length}
              </div>
              <div className="state-item">
                <strong>Groups Found:</strong> {recommendation.puzzle_state.completed_groups.length}
              </div>
              <div className="state-item">
                <strong>Mistakes:</strong> {recommendation.puzzle_state.total_mistakes}/{recommendation.puzzle_state.max_mistakes}
              </div>
              <div className="state-item">
                <strong>Status:</strong> 
                <span className={`game-status game-status--${recommendation.puzzle_state.game_status}`}>
                  {recommendation.puzzle_state.game_status}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationDisplay;