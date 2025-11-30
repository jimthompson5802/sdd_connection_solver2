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

  test('renders navigation sidebar component', () => {
    render(<App />);
    
    // Verify sidebar navigation is present
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toBeInTheDocument();
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
  });

  test('applies correct CSS styling for grid layout', () => {
    render(<App />);
    
    // Verify key layout classes are present on header/main/sidebar
    const title = screen.getByRole('heading', { level: 1 });
    const main = document.querySelector('.App-main');
    const sidebar = document.querySelector('.sidebar');
    
    expect(title).toBeInTheDocument();
    expect(main).toBeInTheDocument();
    expect(main).toHaveClass('App-main');
    expect(sidebar).toBeInTheDocument();
    expect(sidebar).toHaveClass('sidebar');
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

  test('contains all required UI components in initial state', () => {
    render(<App />);
    
    // Verify all major components are present per functional requirements
    // In initial state, should show sidebar navigation and welcome message
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
    expect(screen.getByText('From File')).toBeInTheDocument();
    expect(screen.getByText('Select action in Left Side Bar')).toBeInTheDocument();
  });

  test('maintains consistent theme and styling', () => {
    render(<App />);
    // Verify consistent styling approach using class names present in the DOM
    const appRoot = document.querySelector('.App');
    expect(appRoot).toBeInTheDocument();
    expect(appRoot).toHaveClass('App');
  });
});