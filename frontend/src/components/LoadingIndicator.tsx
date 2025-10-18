/**
 * Enhanced Loading Indicator Component
 * Provides persistent loading states for LLM recommendations with progress feedback.
 */

import React, { useState, useEffect } from 'react';
import './LoadingIndicator.css';

export interface LoadingIndicatorProps {
  isLoading: boolean;
  message?: string;
  provider?: string;
  showProgress?: boolean;
  showElapsedTime?: boolean;
  estimatedDuration?: number; // in milliseconds
  onCancel?: () => void;
  className?: string;
}

export interface LoadingState {
  elapsedTime: number;
  progress: number;
  phase: 'initializing' | 'processing' | 'validating' | 'finalizing';
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  isLoading,
  message = 'Generating recommendation...',
  provider,
  showProgress = true,
  showElapsedTime = true,
  estimatedDuration = 5000,
  onCancel,
  className = ''
}) => {
  const [loadingState, setLoadingState] = useState<LoadingState>({
    elapsedTime: 0,
    progress: 0,
    phase: 'initializing'
  });

  useEffect(() => {
    if (!isLoading) {
      setLoadingState({
        elapsedTime: 0,
        progress: 0,
        phase: 'initializing'
      });
      return;
    }

    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progressPercent = Math.min((elapsed / estimatedDuration) * 100, 95);
      
      let phase: LoadingState['phase'] = 'initializing';
      if (progressPercent > 20) phase = 'processing';
      if (progressPercent > 70) phase = 'validating';
      if (progressPercent > 90) phase = 'finalizing';

      setLoadingState({
        elapsedTime: elapsed,
        progress: progressPercent,
        phase
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isLoading, estimatedDuration]);

  const formatElapsedTime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    
    if (minutes > 0) {
      return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`;
    }
    return `${seconds}s`;
  };

  const getPhaseMessage = (phase: LoadingState['phase'], provider?: string): string => {
    const providerName = provider ? ` (${provider})` : '';
    
    switch (phase) {
      case 'initializing':
        return `Initializing${providerName}...`;
      case 'processing':
        return `Processing with ${provider || 'AI'}...`;
      case 'validating':
        return 'Validating response...';
      case 'finalizing':
        return 'Finalizing recommendation...';
      default:
        return message;
    }
  };

  const getProviderIcon = (provider?: string): string => {
    switch (provider?.toLowerCase()) {
      case 'openai':
        return '🤖';
      case 'ollama':
        return '🦙';
      case 'simple':
        return '⚡';
      default:
        return '🧠';
    }
  };

  if (!isLoading) {
    return null;
  }

  return (
    <div className={`loading-indicator ${className}`} role="status" aria-live="polite">
      <div className="loading-content">
        {/* Main spinner */}
        <div className="spinner-container">
          <div className="spinner" aria-hidden="true">
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
          </div>
          <span className="provider-icon" aria-hidden="true">
            {getProviderIcon(provider)}
          </span>
        </div>

        {/* Loading message */}
        <div className="loading-message">
          <h3 className="primary-message">{message}</h3>
          <p className="phase-message">
            {getPhaseMessage(loadingState.phase, provider)}
          </p>
        </div>

        {/* Progress bar */}
        {showProgress && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${loadingState.progress}%` }}
                aria-valuenow={loadingState.progress}
                aria-valuemin={0}
                aria-valuemax={100}
                role="progressbar"
              />
            </div>
            <span className="progress-text">
              {Math.round(loadingState.progress)}%
            </span>
          </div>
        )}

        {/* Elapsed time */}
        {showElapsedTime && (
          <div className="elapsed-time">
            Elapsed: {formatElapsedTime(loadingState.elapsedTime)}
          </div>
        )}

        {/* Cancel button */}
        {onCancel && (
          <button 
            className="cancel-button"
            onClick={onCancel}
            type="button"
            aria-label="Cancel recommendation generation"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Loading dots animation */}
      <div className="loading-dots" aria-hidden="true">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
};

export default LoadingIndicator;