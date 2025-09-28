/**
 * Tests for the FileUpload component.
 * Tests file upload functionality and CSV validation.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import FileUpload from '../../src/components/FileUpload';

describe('FileUpload Component', () => {
  const mockOnFileUpload = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders file input with correct attributes', () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveAttribute('type', 'file');
    expect(fileInput).toHaveAttribute('accept', '.csv,text/csv');
  });

  test('renders setup puzzle button with correct styling', () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const setupButton = screen.getByRole('button', { name: /setup puzzle/i });
    expect(setupButton).toBeInTheDocument();
    expect(setupButton).toHaveClass('gray-button');
    expect(setupButton).toBeDisabled(); // Initially disabled until file selected
  });

  test('enables setup button when valid file is selected', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    const setupButton = screen.getByRole('button', { name: /setup puzzle/i });
    
    // Create valid CSV file with 16 words
    const validFile = new File([
      'apple,banana,cherry,date,elderberry,fig,grape,honeydew,kiwi,lemon,mango,orange,papaya,quince,raspberry,strawberry'
    ], 'puzzle.csv', { type: 'text/csv' });
    
    await userEvent.upload(fileInput, validFile);
    
    expect(setupButton).toBeEnabled();
  });

  test('calls onFileUpload when setup button is clicked with valid file', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    const setupButton = screen.getByRole('button', { name: /setup puzzle/i });
    
    const validFile = new File([
      'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16'
    ], 'puzzle.csv', { type: 'text/csv' });
    
    await userEvent.upload(fileInput, validFile);
    fireEvent.click(setupButton);
    
    await waitFor(() => {
      expect(mockOnFileUpload).toHaveBeenCalledWith(
        'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16'
      );
    });
  });

  test('validates CSV format and shows error for invalid files', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    
    // Test empty file
    const emptyFile = new File([''], 'empty.csv', { type: 'text/csv' });
    await userEvent.upload(fileInput, emptyFile);
    
    expect(screen.getByText(/file cannot be empty/i)).toBeInTheDocument();
    
    // Test file with wrong number of words
    const wrongWordsFile = new File(['word1,word2,word3'], 'wrong.csv', { type: 'text/csv' });
    await userEvent.upload(fileInput, wrongWordsFile);
    
    expect(screen.getByText(/file must contain exactly 16 words/i)).toBeInTheDocument();
  });

  test('validates CSV content for duplicate words', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    
    // File with duplicate words
    const duplicateFile = new File([
      'word1,word2,word1,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16'
    ], 'duplicate.csv', { type: 'text/csv' });
    
    await userEvent.upload(fileInput, duplicateFile);
    
    expect(screen.getByText(/all words must be unique/i)).toBeInTheDocument();
  });

  test('validates file type and shows error for non-CSV files', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    
    const textFile = new File(['some text content'], 'file.txt', { type: 'text/plain' });
    await userEvent.upload(fileInput, textFile);
    
    expect(screen.getByText(/please select a csv file/i)).toBeInTheDocument();
  });

  test('handles malformed CSV content gracefully', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    
    // Test various malformed CSV cases
    const malformedCases = [
      'word1,word2,,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16', // Empty field
      'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,', // Trailing comma
      ',word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16', // Leading comma
    ];
    
    for (const content of malformedCases) {
      const malformedFile = new File([content], 'malformed.csv', { type: 'text/csv' });
      await userEvent.upload(fileInput, malformedFile);
      
      expect(screen.getByText(/invalid csv format/i)).toBeInTheDocument();
    }
  });

  test('resets error state when valid file is selected after error', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    
    // First upload invalid file
    const invalidFile = new File(['word1,word2'], 'invalid.csv', { type: 'text/csv' });
    await userEvent.upload(fileInput, invalidFile);
    
    expect(screen.getByText(/file must contain exactly 16 words/i)).toBeInTheDocument();
    
    // Then upload valid file
    const validFile = new File([
      'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16'
    ], 'valid.csv', { type: 'text/csv' });
    await userEvent.upload(fileInput, validFile);
    
    expect(screen.queryByText(/file must contain exactly 16 words/i)).not.toBeInTheDocument();
  });

  test('displays file name when valid file is selected', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    
    const validFile = new File([
      'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16'
    ], 'my-puzzle.csv', { type: 'text/csv' });
    
    await userEvent.upload(fileInput, validFile);
    
    expect(screen.getByText(/my-puzzle\.csv/i)).toBeInTheDocument();
  });

  test('provides accessible error messages', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    
    const invalidFile = new File(['invalid'], 'invalid.csv', { type: 'text/csv' });
    await userEvent.upload(fileInput, invalidFile);
    
    const errorMessage = screen.getByRole('alert');
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage).toHaveTextContent(/file must contain exactly 16 words/i);
  });

  test('handles large file sizes appropriately', async () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    
    // Create a large file with valid 16 words but lots of extra content
    const largeContent = 'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16' + 'x'.repeat(10000);
    const largeFile = new File([largeContent], 'large.csv', { type: 'text/csv' });
    
    await userEvent.upload(fileInput, largeFile);
    
    // Should handle gracefully - either accept if first 16 words are valid or show appropriate error
    expect(fileInput.files).toHaveLength(1);
  });
});