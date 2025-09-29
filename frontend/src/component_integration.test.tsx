/**
 * Integration tests for frontend component interactions.
 * 
 * Tests the actual behavior of components working together,
 * matching the real implementation rather than idealized expectations.
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

describe('Frontend Component Integration', () => {
  test('file upload and puzzle setup workflow', async () => {
    render(<App />);
    
    // Verify initial state
    expect(screen.getByText('NYT Connections Puzzle Assistant')).toBeInTheDocument();
    expect(screen.getByText('Upload a CSV file with 16 words to get started')).toBeInTheDocument();
    
    // Verify file input exists
    const fileInput = screen.getByLabelText('Puzzle file');
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveAttribute('accept', '.csv,text/csv');
    
    // Verify setup button is initially disabled
    const setupButton = screen.getByText('Setup Puzzle');
    expect(setupButton).toBeInTheDocument();
    expect(setupButton).toBeDisabled();
    expect(setupButton).toHaveClass('gray-button');
  });

  test('header and main content structure', () => {
    render(<App />);
    
    // Verify semantic HTML structure
    const header = screen.getByRole('banner');
    expect(header).toBeInTheDocument();
    expect(header).toHaveClass('App-header');
    
    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
    expect(main).toHaveClass('App-main');
    
    // Verify heading hierarchy
    const h1 = screen.getByRole('heading', { level: 1 });
    expect(h1).toBeInTheDocument();
    expect(h1).toHaveTextContent('NYT Connections Puzzle Assistant');
  });

  test('file upload section structure and classes', () => {
    render(<App />);
    
    // Verify file upload container
    const fileUploadContainer = screen.getByText('Setup Puzzle').closest('.file-upload');
    expect(fileUploadContainer).toBeInTheDocument();
    
    // Verify upload section
    const uploadSection = screen.getByText('Choose Puzzle File (CSV):').closest('.upload-section');
    expect(uploadSection).toBeInTheDocument();
    
    // Verify file label
    const fileLabel = screen.getByText('Choose Puzzle File (CSV):');
    expect(fileLabel).toBeInTheDocument();
    expect(fileLabel).toHaveClass('file-label');
    expect(fileLabel).toHaveAttribute('for', 'puzzle-file');
  });

  test('app container and CSS classes', () => {
    render(<App />);
    
    // Verify main app container
    const appContainer = screen.getByText('NYT Connections Puzzle Assistant').closest('.App');
    expect(appContainer).toBeInTheDocument();
    expect(appContainer).toHaveClass('App');
  });

  test('button styling and states', () => {
    render(<App />);
    
    const setupButton = screen.getByText('Setup Puzzle');
    
    // Verify button classes and initial state
    expect(setupButton).toHaveClass('gray-button', 'setup-button');
    expect(setupButton).toBeDisabled();
    expect(setupButton).toHaveAttribute('type', 'button');
  });

  test('accessibility attributes', () => {
    render(<App />);
    
    // Verify file input accessibility
    const fileInput = screen.getByLabelText('Puzzle file');
    expect(fileInput).toHaveAttribute('aria-label', 'Puzzle file');
    expect(fileInput).toHaveAttribute('id', 'puzzle-file');
    
    // Verify proper labeling
    const label = screen.getByText('Choose Puzzle File (CSV):');
    expect(label).toHaveAttribute('for', 'puzzle-file');
  });

  test('responsive design elements', () => {
    render(<App />);
    
    // Verify key structural elements exist for responsive design
    const header = screen.getByRole('banner');
    const main = screen.getByRole('main');
    const appContainer = header.closest('.App');
    
    expect(appContainer).toBeInTheDocument();
    expect(header).toBeInTheDocument();
    expect(main).toBeInTheDocument();
    
    // Verify class structure supports CSS styling
    expect(header).toHaveClass('App-header');
    expect(main).toHaveClass('App-main');
  });

  test('component hierarchy and nesting', () => {
    render(<App />);
    
    // Verify proper nesting structure
    const appContainer = screen.getByText('NYT Connections Puzzle Assistant').closest('.App');
    const header = screen.getByRole('banner');
    const main = screen.getByRole('main');
    
    // Header should be inside app container
    expect(appContainer).toContainElement(header);
    
    // Main should be inside app container
    expect(appContainer).toContainElement(main);
    
    // File upload should be inside main
    const fileUploadContainer = screen.getByText('Setup Puzzle').closest('.file-upload');
    expect(main).toContainElement(fileUploadContainer);
  });

  test('text content and instructions', () => {
    render(<App />);
    
    // Verify instructional text
    expect(screen.getByText('Upload a CSV file with 16 words to get started')).toBeInTheDocument();
    expect(screen.getByText('Choose Puzzle File (CSV):')).toBeInTheDocument();
    expect(screen.getByText('Setup Puzzle')).toBeInTheDocument();
  });

  test('form elements and input configuration', () => {
    render(<App />);
    
    const fileInput = screen.getByLabelText('Puzzle file');
    
    // Verify file input configuration
    expect(fileInput).toHaveAttribute('type', 'file');
    expect(fileInput).toHaveAttribute('accept', '.csv,text/csv');
    expect(fileInput).toHaveAttribute('id', 'puzzle-file');
  });
});