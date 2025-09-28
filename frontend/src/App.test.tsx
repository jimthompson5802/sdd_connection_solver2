import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App Component Integration', () => {
  test('renders main application header', () => {
    render(<App />);
    const headerElement = screen.getByText(/NYT Connections Puzzle Assistant/i);
    expect(headerElement).toBeInTheDocument();
  });

  test('renders file upload interface', () => {
    render(<App />);
    const fileInput = screen.getByLabelText(/Choose Puzzle File/i);
    expect(fileInput).toBeInTheDocument();
  });

  test('renders setup button', () => {
    render(<App />);
    const setupButton = screen.getByText(/Setup Puzzle/i);
    expect(setupButton).toBeInTheDocument();
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

  test('setup button is initially disabled', () => {
    render(<App />);
    const setupButton = screen.getByText(/Setup Puzzle/i);
    expect(setupButton).toBeDisabled();
  });
});
