/**
 * T050, T053: Export CSV Button Component
 *
 * Button component for exporting game history as CSV file.
 * Features:
 * - Disabled state during export operation
 * - Success/error message handling
 * - Proper filename handling via service
 */
import React, { useState } from 'react';
import { gameResultsService } from '../services/gameResultsService';
import './ExportCSVButton.css';

const ExportCSVButton: React.FC = () => {
  const [isExporting, setIsExporting] = useState(false);
  const [message, setMessage] = useState<{
    type: 'success' | 'error' | null;
    text: string;
  }>({ type: null, text: '' });

  /**
   * T053: Handle export CSV button click
   * Triggers download with proper filename handling
   */
  const handleExport = async () => {
    // Clear previous messages
    setMessage({ type: null, text: '' });

    // Disable button during export
    setIsExporting(true);

    try {
      // T051: Call service method to export and download CSV
      await gameResultsService.exportGameResultsCSV();

      // Show success message
      setMessage({
        type: 'success',
        text: 'Game history exported successfully!',
      });

      // Clear success message after 3 seconds
      setTimeout(() => {
        setMessage({ type: null, text: '' });
      }, 3000);

    } catch (error) {
      // Show error message
      const errorMessage = error instanceof Error
        ? error.message
        : 'Failed to export game history';

      setMessage({
        type: 'error',
        text: errorMessage,
      });

      // Clear error message after 5 seconds
      setTimeout(() => {
        setMessage({ type: null, text: '' });
      }, 5000);

    } finally {
      // Re-enable button
      setIsExporting(false);
    }
  };

  return (
    <div className="export-csv-button-container">
      <button
        className="export-csv-button"
        onClick={handleExport}
        disabled={isExporting}
        aria-label="Export CSV"
      >
        {isExporting ? 'Exporting...' : 'Export CSV'}
      </button>

      {message.type && (
        <div className={`export-message export-message-${message.type}`}>
          {message.text}
        </div>
      )}
    </div>
  );
};

export default ExportCSVButton;
