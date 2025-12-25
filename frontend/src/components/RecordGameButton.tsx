/**
 * T022, T025-T027: RecordGameButton Component
 *
 * Button for recording a completed game to persistent storage.
 * Handles:
 * - Disabled state during submission (T022, T027)
 * - Success confirmation messages (T025)
 * - Error message handling for duplicate, incomplete, and network errors (T026)
 */

import React, { useState } from 'react';
import { gameResultsService } from '../services/gameResultsService';
import './RecordGameButton.css';

interface Props {
  sessionId: string;
  isFinished: boolean;
  onRecordSuccess?: () => void;
}

type RecordStatus = 'idle' | 'recording' | 'success' | 'error';

const RecordGameButton: React.FC<Props> = ({ sessionId, isFinished, onRecordSuccess }) => {
  const [status, setStatus] = useState<RecordStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [isDisabled, setIsDisabled] = useState(false);

  // Don't render button if game is not finished
  if (!isFinished) {
    return null;
  }

  const handleRecordGame = async () => {
    // T027: Disable button during API call
    setIsDisabled(true);
    setStatus('recording');
    setErrorMessage('');

    try {
      // Call API to record game
      await gameResultsService.recordGame(sessionId);

      // T025: Success confirmation
      setStatus('success');

      // Keep button disabled after success (cannot record same game twice)
      // setIsDisabled remains true

      // Notify parent component of success
      if (onRecordSuccess) {
        onRecordSuccess();
      }

    } catch (error) {
      // T026: Error message handling
      setStatus('error');

      const errorMsg = error instanceof Error ? error.message : 'Unknown error occurred';

      // Classify error types for user-friendly messages
      if (errorMsg.toLowerCase().includes('already exists') ||
          errorMsg.toLowerCase().includes('duplicate')) {
        setErrorMessage('This game has already been recorded for today.');
        // Keep button disabled for duplicate (no point retrying)
        setIsDisabled(true);
      } else if (errorMsg.toLowerCase().includes('must be completed') ||
                 errorMsg.toLowerCase().includes('not finished')) {
        setErrorMessage('Game must be completed before recording.');
        setIsDisabled(true);
      } else if (errorMsg.toLowerCase().includes('not found')) {
        setErrorMessage('Session not found. Please try again.');
        setIsDisabled(false); // Allow retry
      } else if (errorMsg.toLowerCase().includes('network')) {
        setErrorMessage('Network error. Please check your connection and try again.');
        setIsDisabled(false); // Allow retry for network errors
      } else {
        setErrorMessage('Failed to record game. Please try again.');
        setIsDisabled(false); // Allow retry for unknown errors
      }
    }
  };

  return (
    <div className="record-game-container">
      <button
        className="record-game-button"
        onClick={handleRecordGame}
        disabled={isDisabled}
        aria-busy={status === 'recording'}
      >
        {status === 'recording' ? 'Recording...' : 'Record Game'}
      </button>

      {/* T025: Success message */}
      {status === 'success' && (
        <div className="record-message success" role="status" aria-live="polite">
          ✓ Game recorded successfully!
        </div>
      )}

      {/* T026: Error messages */}
      {status === 'error' && errorMessage && (
        <div className="record-message error" role="alert" aria-live="assertive">
          ✗ {errorMessage}
        </div>
      )}
    </div>
  );
};

export default RecordGameButton;
