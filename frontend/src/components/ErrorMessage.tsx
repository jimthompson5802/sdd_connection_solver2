import React from 'react';
import './ErrorMessage.css';

/**
 * Props for the ErrorMessage component
 */
export interface ErrorMessageProps {
  /** The error message to display */
  message: string;
  /** Optional error type for styling */
  type?: 'error' | 'warning' | 'validation' | 'network';
  /** Whether to show retry button */
  showRetry?: boolean;
  /** Callback for retry action */
  onRetry?: () => void;
  /** Whether to show dismiss button */
  showDismiss?: boolean;
  /** Callback for dismiss action */
  onDismiss?: () => void;
  /** Additional details to show in expandable section */
  details?: string;
  /** Error code for technical support */
  errorCode?: string;
  /** Whether the error is dismissible */
  dismissible?: boolean;
  /** Custom CSS class name */
  className?: string;
  /** Provider name that caused the error */
  provider?: string;
}

/**
 * ErrorMessage Component
 * 
 * Displays error messages with appropriate styling and actions.
 * Supports different error types, retry functionality, and expandable details.
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  type = 'error',
  showRetry = false,
  onRetry,
  showDismiss = false,
  onDismiss,
  details,
  errorCode,
  dismissible = true,
  className = '',
  provider
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  const getErrorIcon = () => {
    switch (type) {
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'validation':
        return '🔧';
      case 'network':
        return '🌐';
      default:
        return '❌';
    }
  };

  const getErrorTitle = () => {
    switch (type) {
      case 'error':
        return 'Error';
      case 'warning':
        return 'Warning';
      case 'validation':
        return 'Validation Error';
      case 'network':
        return 'Connection Error';
      default:
        return 'Error';
    }
  };

  const getProviderDisplayName = (providerName?: string) => {
    if (!providerName) return '';
    
    switch (providerName.toLowerCase()) {
      case 'simple':
        return 'Simple Provider';
      case 'ollama':
        return 'Ollama';
      case 'openai':
        return 'OpenAI';
      default:
        return providerName;
    }
  };

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    }
  };

  const handleDismiss = () => {
    if (onDismiss) {
      onDismiss();
    }
  };

  const toggleDetails = () => {
    setIsExpanded(!isExpanded);
  };

  const errorClasses = [
    'error-message',
    `error-message--${type}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={errorClasses} role="alert" aria-live="assertive">
      <div className="error-message__header">
        <div className="error-message__icon-title">
          <span className="error-message__icon" aria-hidden="true">
            {getErrorIcon()}
          </span>
          <div className="error-message__title-section">
            <h3 className="error-message__title">
              {getErrorTitle()}
              {provider && (
                <span className="error-message__provider">
                  {` - ${getProviderDisplayName(provider)}`}
                </span>
              )}
            </h3>
            {errorCode && (
              <span className="error-message__code">
                Error Code: {errorCode}
              </span>
            )}
          </div>
        </div>
        
        {dismissible && (
          <button
            className="error-message__dismiss"
            onClick={handleDismiss}
            aria-label="Dismiss error message"
            type="button"
          >
            ×
          </button>
        )}
      </div>

      <div className="error-message__content">
        <p className="error-message__text">{message}</p>

        {details && (
          <div className="error-message__details-section">
            <button
              className="error-message__details-toggle"
              onClick={toggleDetails}
              aria-expanded={isExpanded}
              aria-controls="error-details"
              type="button"
            >
              {isExpanded ? '▼' : '▶'} {isExpanded ? 'Hide' : 'Show'} Details
            </button>
            
            {isExpanded && (
              <div 
                id="error-details"
                className="error-message__details"
                role="region"
                aria-label="Error details"
              >
                <pre className="error-message__details-text">{details}</pre>
              </div>
            )}
          </div>
        )}

        <div className="error-message__actions">
          {showRetry && (
            <button
              className="error-message__action error-message__action--retry"
              onClick={handleRetry}
              type="button"
            >
              🔄 Retry
            </button>
          )}
          
          {showDismiss && (
            <button
              className="error-message__action error-message__action--dismiss"
              onClick={handleDismiss}
              type="button"
            >
              Dismiss
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;