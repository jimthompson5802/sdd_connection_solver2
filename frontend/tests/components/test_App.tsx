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
    const titleElement = screen.getByText(/NYT Connection Solver Virtual Assistant/i);
    expect(titleElement).toBeInTheDocument();
  });

  test('renders centered layout structure', () => {
    render(<App />);
    
    // Verify centered layout per functional requirements
    const appContainer = screen.getByTestId('app-container');
    expect(appContainer).toBeInTheDocument();
    expect(appContainer).toHaveClass('centered-layout');
  });

  test('renders main puzzle interface component', () => {
    render(<App />);
    
    // Verify PuzzleInterface component is rendered
    const puzzleInterface = screen.getByTestId('puzzle-interface');
    expect(puzzleInterface).toBeInTheDocument();
  });

  test('applies correct CSS styling for centered layout', () => {
    render(<App />);
    
    const appContainer = screen.getByTestId('app-container');
    
    // Check that styling is applied (this will need actual CSS to pass)
    expect(appContainer).toHaveStyle({
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
    });
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
    expect(headingElement).toHaveTextContent(/NYT Connection Solver Virtual Assistant/i);
  });

  test('contains all required UI components', () => {
    render(<App />);
    
    // Verify all major components are present per functional requirements
    expect(screen.getByTestId('puzzle-interface')).toBeInTheDocument();
    
    // These components should be rendered within PuzzleInterface
    // but we test their presence in the overall app structure
    expect(screen.getByText(/puzzle file/i)).toBeInTheDocument();
    expect(screen.getByText(/setup puzzle/i)).toBeInTheDocument();
  });

  test('maintains consistent theme and styling', () => {
    render(<App />);
    
    const appContainer = screen.getByTestId('app-container');
    
    // Verify consistent styling approach
    expect(appContainer).toHaveClass('app');
    expect(appContainer).toHaveClass('centered-layout');
  });
});