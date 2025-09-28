/**
 * Validation tests for FileUpload component implementation.
 * These tests validate that our actual implementation works correctly.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUpload from './FileUpload';

describe('FileUpload Component - Implementation Validation', () => {
  const mockOnFileUpload = jest.fn();

  beforeEach(() => {
    mockOnFileUpload.mockClear();
  });

  test('renders file upload interface correctly', () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    expect(screen.getByLabelText(/Choose Puzzle File/i)).toBeInTheDocument();
    expect(screen.getByText(/Setup Puzzle/i)).toBeInTheDocument();
  });

  test('setup button is initially disabled', () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const setupButton = screen.getByText(/Setup Puzzle/i);
    expect(setupButton).toBeDisabled();
  });

  test('file input accepts CSV files', () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/Choose Puzzle File/i);
    expect(fileInput).toHaveAttribute('accept', '.csv,text/csv');
  });

  test('file input has correct attributes', () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} />);
    
    const fileInput = screen.getByLabelText(/Choose Puzzle File/i);
    expect(fileInput).toHaveAttribute('type', 'file');
    expect(fileInput).toHaveAttribute('id', 'puzzle-file');
  });

  test('component renders without crashing', () => {
    expect(() => {
      render(<FileUpload onFileUpload={mockOnFileUpload} />);
    }).not.toThrow();
  });

  test('renders with loading state', () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} isLoading={true} />);
    
    const setupButton = screen.getByText(/Setting up.../i);
    expect(setupButton).toBeInTheDocument();
    expect(setupButton).toBeDisabled();
  });

  test('renders with error message', () => {
    render(<FileUpload onFileUpload={mockOnFileUpload} error="Test error message" />);
    
    expect(screen.getByText('Test error message')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });
});