/**
 * Integration tests for frontend component interactions.
 * 
 * Tests the actual behavior of components working together,
 * matching the real implementation rather than idealized expectations.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

describe('Frontend Component Integration', () => {
  test('file upload and puzzle setup workflow', async () => {
    render(<App />);
    
    // Verify initial state - welcome message instead of file upload
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByText('Select action in Left Side Bar')).toBeInTheDocument();
    
    // Click "From File" to navigate to file upload
    fireEvent.click(screen.getByText('From File'));
    
    // Now verify file input exists
    const fileInput = screen.getByLabelText(/choose puzzle file/i);
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveAttribute('accept', '.csv,text/csv');
    
    // Verify setup button is initially disabled
    const setupButton = screen.getByText(/setup puzzle/i);
    expect(setupButton).toBeInTheDocument();
    expect(setupButton).toBeDisabled();
    expect(setupButton).toHaveClass('gray-button');
  });

  test('header and main content structure', () => {
    render(<App />);
    
    // Verify semantic HTML structure
    const header = screen.getByRole('banner');
    expect(header).toBeInTheDocument();
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
    
    // Click "From File" to navigate to file upload
    fireEvent.click(screen.getByText('From File'));
    
    // Verify file upload container
    const fileUploadContainer = screen.getByText(/setup puzzle/i).closest('.file-upload');
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
    
    // Click "From File" to navigate to file upload
    fireEvent.click(screen.getByText('From File'));
    
    const setupButton = screen.getByText(/setup puzzle/i);
    
    // Verify button classes and initial state
    expect(setupButton).toHaveClass('gray-button', 'setup-button');
    expect(setupButton).toBeDisabled();
    expect(setupButton).toHaveAttribute('type', 'button');
  });

  test('accessibility attributes', () => {
    render(<App />);
    
    // Click "From File" to navigate to file upload
    fireEvent.click(screen.getByText('From File'));
    
    // Verify file input accessibility
    const fileInput = screen.getByLabelText(/puzzle file/i);
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
    
    // Verify class structure supports CSS styling: App-header class is on the header element
    const headerElement = screen.getByRole('banner');
    expect(headerElement).toHaveClass('App-header');
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
    
    // Initially main contains welcome message
    expect(main).toContainElement(screen.getByText('Select action in Left Side Bar'));
    
    // Click "From File" to navigate to file upload
    fireEvent.click(screen.getByText('From File'));
    
    // File upload should be inside main after navigation
    const fileUploadContainer = screen.getByText(/setup puzzle/i).closest('.file-upload') as HTMLElement;
    expect(main).toContainElement(fileUploadContainer);
  });

  test('text content and instructions', () => {
    render(<App />);
    
    // Verify initial state text and navigation
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByText('Select action in Left Side Bar')).toBeInTheDocument();
    expect(screen.getByText('From File')).toBeInTheDocument();
    
    // Click "From File" to navigate to file upload
    fireEvent.click(screen.getByText('From File'));
    
    // Verify file upload text and controls appear after navigation
    expect(screen.getByText('Choose Puzzle File (CSV):')).toBeInTheDocument();
    expect(screen.getByText(/setup puzzle/i)).toBeInTheDocument();
  });

  test('form elements and input configuration', () => {
    render(<App />);
    
    // Click "From File" to navigate to file upload
    fireEvent.click(screen.getByText('From File'));
    
    const fileInput = screen.getByLabelText(/puzzle file/i);
    
    // Verify file input configuration
    expect(fileInput).toHaveAttribute('type', 'file');
    expect(fileInput).toHaveAttribute('accept', '.csv,text/csv');
    expect(fileInput).toHaveAttribute('id', 'puzzle-file');
  });
});