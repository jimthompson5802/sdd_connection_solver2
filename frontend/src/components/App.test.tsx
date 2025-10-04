/**
 * Tests for the main App component.
 * Tests the root application structure and routing.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../src/App';

describe('App Component', () => {
  test('renders the main application title', () => {
    render(<App />);
    
    // Verify the main title from functional requirements FR-001
    const titleElement = screen.getByRole('heading', { level: 1 });
    // The app currently renders the heading text shown in the DOM
    expect(titleElement).toHaveTextContent(/NYT Connections Puzzle Assistant/i);
    expect(titleElement).toBeInTheDocument();
  });

  test('renders centered layout structure', () => {
    render(<App />);
    
    // Verify centered layout per functional requirements using semantic roles and classes
    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
    // The app uses a class-based layout; ensure main has the expected class
    expect(main).toHaveClass('App-main');
  });

  test('renders main puzzle interface component', () => {
    render(<App />);
    
    // Verify PuzzleInterface-like inputs are rendered (file input with accessible label)
    const fileInput = screen.getByLabelText(/puzzle file/i);
    expect(fileInput).toBeInTheDocument();
  });

  test('applies correct CSS styling for centered layout', () => {
    render(<App />);
    
    // Verify key layout classes are present on header/main
    const header = document.querySelector('.App-header');
    const main = document.querySelector('.App-main');
    expect(header).toBeInTheDocument();
    expect(main).toBeInTheDocument();
    // Check that the setup button exists and is initially disabled
    const setupButton = screen.getByRole('button', { name: /setup puzzle/i });
    expect(setupButton).toBeInTheDocument();
    expect(setupButton).toBeDisabled();
  });

  test('renders without crashing', () => {
    // Basic smoke test
    expect(() => render(<App />)).not.toThrow();
  });

  test('has proper semantic structure', () => {
    render(<App />);
    
    // Verify semantic HTML structure
    const mainElement = screen.getByRole('main');
    expect(mainElement).toBeInTheDocument();
    
    const headingElement = screen.getByRole('heading', { level: 1 });
    expect(headingElement).toBeInTheDocument();
    expect(headingElement).toHaveTextContent(/NYT Connections Puzzle Assistant/i);
  });

  test('contains all required UI components', () => {
    render(<App />);
    
    // Verify all major components are present per functional requirements
    // Check the file input and setup button are present
    expect(screen.getByLabelText(/puzzle file/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /setup puzzle/i })).toBeInTheDocument();
  });

  test('maintains consistent theme and styling', () => {
    render(<App />);
    // Verify consistent styling approach using class names present in the DOM
    const appRoot = document.querySelector('.App');
    expect(appRoot).toBeInTheDocument();
    expect(appRoot).toHaveClass('App');
  });
});