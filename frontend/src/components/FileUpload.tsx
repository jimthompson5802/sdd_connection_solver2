/**
 * FileUpload component for uploading CSV puzzle files.
 * Handles file selection, validation, and CSV parsing.
 */

import React, { useState, useRef, ChangeEvent } from 'react';
import { FileUploadProps, PuzzleError } from '../types/puzzle';
import { ApiService } from '../services/api';

const FileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  isLoading = false,
  error = null,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isValidFile, setIsValidFile] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setValidationError(null);
    setSelectedFile(null);
    setIsValidFile(false);

    if (!file) {
      return;
    }

    // Validate file type
    if (!file.type.includes('csv') && !file.name.toLowerCase().endsWith('.csv')) {
      setValidationError('Please select a CSV file');
      return;
    }

    // Read and validate file content
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        
        // Validate CSV content
        ApiService.validateFileContent(content);
        
        // If validation passes, set the file as valid
        setSelectedFile(file);
        setIsValidFile(true);
        setValidationError(null);
      } catch (err) {
        if (err instanceof PuzzleError) {
          setValidationError(err.message);
        } else {
          setValidationError('Invalid CSV format');
        }
        setSelectedFile(null);
        setIsValidFile(false);
      }
    };

    reader.onerror = () => {
      setValidationError('Error reading file');
      setSelectedFile(null);
      setIsValidFile(false);
    };

    reader.readAsText(file);
  };

  const handleSetupPuzzle = () => {
    if (!selectedFile || !isValidFile) {
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      onFileUpload(content);
    };
    reader.readAsText(selectedFile);
  };

  const resetFile = () => {
    setSelectedFile(null);
    setValidationError(null);
    setIsValidFile(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="file-upload">
      <div className="upload-section">
        <label htmlFor="puzzle-file" className="file-label">
          Choose Puzzle File (CSV):
        </label>
        <input
          ref={fileInputRef}
          id="puzzle-file"
          type="file"
          accept=".csv,text/csv"
          onChange={handleFileSelect}
          disabled={isLoading}
          aria-label="Puzzle file"
        />
      </div>

      {selectedFile && (
        <div className="file-info">
          <span className="file-name">{selectedFile.name}</span>
          <button 
            type="button" 
            onClick={resetFile}
            className="reset-button"
            disabled={isLoading}
          >
            ×
          </button>
        </div>
      )}

      {(validationError || error) && (
        <div className="error-message" role="alert">
          {validationError || error}
        </div>
      )}

      <button
        type="button"
        onClick={handleSetupPuzzle}
        disabled={!isValidFile || isLoading}
        className="gray-button setup-button"
      >
        {isLoading ? 'Setting up...' : 'Setup Puzzle'}
      </button>
    </div>
  );
};

export default FileUpload;