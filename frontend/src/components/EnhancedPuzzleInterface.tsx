/**
 * Enhanced PuzzleInterface component with LLM provider integration.
 * Provides comprehensive puzzle interaction with AI-powered recommendations.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { LLMProvider } from '../types/llm-provider';
import { RecommendationResponse, GenerateRecommendationRequest } from '../types/recommendation';
import { PuzzleInterfaceProps } from '../types/puzzle';

import LLMProviderInput from './LLMProviderInput';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import RecommendationDisplay from './RecommendationDisplay';
import { llmApiService } from '../services/llm-api';
import './EnhancedPuzzleInterface.css';

/**
 * Enhanced PuzzleInterface Props that extend the base interface
 */
interface EnhancedPuzzleInterfaceProps extends PuzzleInterfaceProps {
  /** Current LLM provider configuration */
  llmProvider?: LLMProvider | null;
  /** Callback when LLM provider is changed */
  onProviderChange?: (provider: LLMProvider | null) => void;
  /** Whether to show LLM provider controls */
  showProviderControls?: boolean;
  /** Custom puzzle context for recommendations */
  puzzleContext?: string;
  /** Previous guess attempts for context */
  previousGuesses?: Array<{
    words: string[];
    outcome: "correct" | "incorrect" | "one-away";
    actual_connection?: string;
    timestamp: string;
  }>;
  /** Optional override for LLM recommendation (testing) */
  llmRecommendationOverride?: RecommendationResponse | null;
}

const EnhancedPuzzleInterface: React.FC<EnhancedPuzzleInterfaceProps> = ({
  words,
  recommendation,
  recommendationConnection,
  correctCount,
  mistakeCount,
  gameStatus,
  isLoading,
  error,
  onRecordResponse,
  previousResponses,
  llmProvider,
  onProviderChange,
  showProviderControls = true,
  puzzleContext,
  previousGuesses = [],
  llmRecommendationOverride = null,
}) => {
  const [llmRecommendation, setLlmRecommendation] = useState<RecommendationResponse | null>(null);
  const [llmLoading, setLlmLoading] = useState(false);
  const [llmError, setLlmError] = useState<string | null>(null);
  const [currentProvider, setCurrentProvider] = useState<LLMProvider | null>(
    llmProvider || { provider_type: 'simple', model_name: null }
  );
  const [disabledColors, setDisabledColors] = useState<Set<string>>(new Set());
  const [recordingResponse, setRecordingResponse] = useState(false);

  // Reset state when game status changes
  useEffect(() => {
    if (gameStatus === 'waiting') {
      setDisabledColors(new Set());
      setLlmRecommendation(null);
      setLlmError(null);
    }
  }, [gameStatus]);

  // Handle provider changes
  const handleProviderChange = useCallback((provider: LLMProvider | null) => {
    setCurrentProvider(provider);
    if (onProviderChange) {
      onProviderChange(provider);
    }
    // Clear previous recommendation when provider changes
    setLlmRecommendation(null);
    setLlmError(null);
  }, [onProviderChange]);

  // Notify parent of the default provider on mount if none was passed in
  useEffect(() => {
    if (!llmProvider && currentProvider && onProviderChange) {
      onProviderChange(currentProvider);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Get LLM recommendation
  const handleGetLlmRecommendation = useCallback(async () => {
    if (llmLoading || gameStatus !== 'active') {
      return;
    }

    if (!currentProvider) {
      // Prompt user to choose a provider before making a request
      setLlmError('Please select an AI provider before requesting a recommendation.');
      return;
    }

    setLlmLoading(true);
    setLlmError(null);

    try {
      const request: GenerateRecommendationRequest = {
        llm_provider: currentProvider,
        remaining_words: words,
        previous_guesses: previousGuesses,
        puzzle_context: puzzleContext
      };

      const response = await llmApiService.generateRecommendation(request);
      setLlmRecommendation(response);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get LLM recommendation';
      setLlmError(errorMessage);
      setLlmRecommendation(null);
    } finally {
      setLlmLoading(false);
    }
  }, [currentProvider, words, previousGuesses, puzzleContext, llmLoading, gameStatus]);

  // traditional recommendation removed

  // Handle response recording
  const handleResponseClick = useCallback(async (
    type: 'correct' | 'incorrect' | 'one-away',
    color?: string,
    attemptWords?: string[]
  ) => {
    if (isLoading || gameStatus !== 'active' || recordingResponse) return;

    setRecordingResponse(true);
    try {
      // Await the parent's record response so we can only disable UI on success
      // Pass the provided attemptWords (LLM or traditional) so backend can record the correct group
      await onRecordResponse(type, color, attemptWords);

      // Only mark the color disabled after a successful API call
      if (type === 'correct' && color) {
        setDisabledColors(prev => new Set(prev).add(color));
      }
    } catch (err) {
      // Parent will typically surface the error via props; no local change to disabledColors
      // Optionally, we could set a local error state here if desired
    } finally {
      setRecordingResponse(false);
    }
  }, [isLoading, gameStatus, onRecordResponse, recordingResponse]);

  // Handle LLM recommendation acceptance
  const handleAcceptLlmRecommendation = useCallback((words: string[]) => {
    // For now, we'll just show the traditional recommendation interface
    // In a full implementation, this would submit the guess directly
    console.log('Accepting LLM recommendation:', words);
    // You could trigger the traditional recommendation system with these words
    // or implement direct guess submission here
  }, []);

  // Handle LLM recommendation rejection
  const handleRejectLlmRecommendation = useCallback((words: string[]) => {
    console.log('Rejecting LLM recommendation:', words);
    // Clear the current recommendation to allow getting a new one
    setLlmRecommendation(null);
  }, []);

  // Retry LLM recommendation on error
  const handleRetryLlmRecommendation = useCallback(() => {
    handleGetLlmRecommendation();
  }, [handleGetLlmRecommendation]);

  // Clear LLM error
  const handleClearLlmError = useCallback(() => {
    setLlmError(null);
  }, []);

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

  const renderStats = () => {
    if (gameStatus !== 'active') return null;

    return (
      <div className="puzzle-stats">
        <div className="stat-item">
          <span className="stat-label">Groups Found:</span>
          <span className="stat-value">{correctCount}/4</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Mistakes:</span>
          <span className="stat-value">{mistakeCount}/4</span>
        </div>
      </div>
    );
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

  // traditional recommendation display removed

  const renderResponseButtons = (useLlm: boolean = false) => {
    // Only render when game is active
    if (gameStatus !== 'active') return null;

    // Determine which recommendation to check: LLM or traditional
    const effectiveLlmRecommendation = llmRecommendationOverride ?? llmRecommendation;
    if (useLlm) {
      if (!effectiveLlmRecommendation) return null;
    } else {
      if (recommendation.length === 0) return null;
    }

    return (
      <div className="response-buttons">
        <h4>How was this recommendation?</h4>
        <div className="button-group">
          <button
            onClick={() => handleResponseClick('correct', 'Yellow', useLlm ? (llmRecommendationOverride ?? llmRecommendation)?.recommended_words : recommendation)}
            disabled={isLoading || disabledColors.has('Yellow')}
            className={`response-button correct yellow ${disabledColors.has('Yellow') ? 'gray-button' : ''}`}
          >
            Correct (Yellow)
          </button>
          <button
            onClick={() => handleResponseClick('correct', 'Green', useLlm ? (llmRecommendationOverride ?? llmRecommendation)?.recommended_words : recommendation)}
            disabled={isLoading || disabledColors.has('Green')}
            className={`response-button correct green ${disabledColors.has('Green') ? 'gray-button' : ''}`}
          >
            Correct (Green)
          </button>
          <button
            onClick={() => handleResponseClick('correct', 'Blue', useLlm ? (llmRecommendationOverride ?? llmRecommendation)?.recommended_words : recommendation)}
            disabled={isLoading || disabledColors.has('Blue')}
            className={`response-button correct blue ${disabledColors.has('Blue') ? 'gray-button' : ''}`}
          >
            Correct (Blue)
          </button>
          <button
            onClick={() => handleResponseClick('correct', 'Purple', useLlm ? (llmRecommendationOverride ?? llmRecommendation)?.recommended_words : recommendation)}
            disabled={isLoading || disabledColors.has('Purple')}
            className={`response-button correct purple ${disabledColors.has('Purple') ? 'gray-button' : ''}`}
          >
            Correct (Purple)
          </button>
        </div>
        <div className="button-group">
          <button
            onClick={() => handleResponseClick('incorrect', undefined, useLlm ? (llmRecommendationOverride ?? llmRecommendation)?.recommended_words : recommendation)}
            disabled={isLoading}
            className="response-button incorrect"
          >
            Incorrect
          </button>
          <button
            onClick={() => handleResponseClick('one-away', undefined, useLlm ? (llmRecommendationOverride ?? llmRecommendation)?.recommended_words : recommendation)}
            disabled={isLoading}
            className="response-button one-away"
          >
            One Away
          </button>
        </div>
      </div>
    );
  };

  const renderPreviousResponses = () => {
    if (!previousResponses || previousResponses.length === 0) return null;

    return (
      <div className="previous-responses">
        <h4>Previous Responses</h4>
        <div className="responses-list">
          {previousResponses.map((response, index) => (
            <div key={index} className={`response-item ${response.type}`}>
              <div className="response-words">
                {response.words.map((word, wordIndex) => (
                  <span key={wordIndex} className="response-word">
                    {word}
                  </span>
                ))}
              </div>
              <span className={`response-outcome ${response.type}`}>
                {response.type.replace('-', ' ').toUpperCase()}
                {response.color && ` (${response.color})`}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="enhanced-puzzle-interface">
      {error && (
        <ErrorMessage
          message={error}
          type="error"
          showRetry={true}
          onRetry={() => window.location.reload()}
          showDismiss={true}
          onDismiss={() => {}}
        />
      )}

      {renderGameStatus()}

      {gameStatus === 'active' && (
        <>
          {renderStats()}
          {renderWordGrid()}

          {showProviderControls && (
            <div className="llm-provider-section">
              <h3>AI Assistant</h3>
              <LLMProviderInput
                value={currentProvider || { provider_type: 'simple', model_name: null }}
                onChange={handleProviderChange}
                disabled={llmLoading}
              />
              
              <div className="llm-controls">
                <button
                  onClick={handleGetLlmRecommendation}
                  disabled={llmLoading}
                  className="primary-button get-llm-recommendation"
                >
                  Get AI Recommendation
                </button>
              </div>

              {llmLoading && (
                <LoadingIndicator
                  isLoading={true}
                  provider={currentProvider?.provider_type}
                  message="Analyzing puzzle and generating recommendations..."
                  showElapsedTime={true}
                  onCancel={() => setLlmLoading(false)}
                />
              )}

              {llmError && (
                <ErrorMessage
                  message={llmError}
                  type="error"
                  showRetry={true}
                  onRetry={handleRetryLlmRecommendation}
                  showDismiss={true}
                  onDismiss={handleClearLlmError}
                  provider={currentProvider?.provider_type}
                />
              )}

              {llmRecommendation && (
                <RecommendationDisplay
                  recommendation={llmRecommendation}
                  isLoading={false}
                  provider={currentProvider}
                  onAcceptRecommendation={handleAcceptLlmRecommendation}
                  onRejectRecommendation={handleRejectLlmRecommendation}
                  showProviderInfo={true}
                  showMetadata={true}
                />
              )}
              {/* Render response buttons for LLM recommendation below the LLM display */}
              {renderResponseButtons(true)}
            </div>
          )}

          {/* traditional recommendation section removed per branch remove-traditional-recommendation-section */}

          {renderPreviousResponses()}
        </>
      )}

      {isLoading && (
        <LoadingIndicator
          isLoading={true}
          message="Processing traditional recommendation..."
        />
      )}
    </div>
  );
};

export default EnhancedPuzzleInterface;