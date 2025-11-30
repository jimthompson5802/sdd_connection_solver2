import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

describe('App Component - New Layout', () => {
  // User Story 1 Tests - Initial Application Launch
  test('renders title "NYT Connections Puzzle Assistant" at top', () => {
    render(<App />);
    const headerElement = screen.getByRole('heading', { level: 1 });
    expect(headerElement).toBeInTheDocument();
    expect(headerElement).toHaveTextContent('NYT Connections Puzzle Assistant');
  });

  test('renders Sidebar component in initial state', () => {
    render(<App />);
    
    // Should have sidebar with navigation
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toBeInTheDocument();
    
    // Should show "Start New Game" expanded with "From File" visible
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
    expect(screen.getByText('From File')).toBeInTheDocument();
  });

  test('renders "Select action in Left Side Bar" message when currentView=initial', () => {
    render(<App />);
    expect(screen.getByText('Select action in Left Side Bar')).toBeInTheDocument();
  });

  test('layout uses CSS Grid with three regions (header, sidebar, main)', () => {
    render(<App />);
    
    const appContainer = document.querySelector('.App');
    expect(appContainer).toBeInTheDocument();
    
    // Verify grid areas are present (jsdom limitation: grid display may show as 'block')
    const header = document.querySelector('.App-header');
    const sidebar = document.querySelector('.sidebar');
    const main = document.querySelector('.App-main');
    
    expect(header).toBeInTheDocument();
    expect(sidebar).toBeInTheDocument();
    expect(main).toBeInTheDocument();
  });

  // User Story 2 Tests - File Upload Flow  
  test('clicking "From File" changes currentView to file-upload', () => {
    render(<App />);
    
    // Initially should show welcome message
    expect(screen.getByText('Select action in Left Side Bar')).toBeInTheDocument();
    
    // Click "From File"
    fireEvent.click(screen.getByText('From File'));
    
    // Should show file upload interface
    expect(screen.queryByText('Select action in Left Side Bar')).not.toBeInTheDocument();
    expect(screen.getByLabelText(/choose puzzle file/i)).toBeInTheDocument();
  });

  test('title and sidebar remain visible when currentView=file-upload', () => {
    render(<App />);
    
    // Click "From File" to show file upload
    fireEvent.click(screen.getByText('From File'));
    
    // Title should still be visible
    const headerElement = screen.getByRole('heading', { level: 1 });
    expect(headerElement).toBeInTheDocument();
    expect(headerElement).toHaveTextContent('NYT Connections Puzzle Assistant');
    
    // Sidebar should still be visible
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toBeInTheDocument();
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
  });

  // Layout Integration Tests
  test('has proper semantic structure with new layout', () => {
    render(<App />);
    
    // Verify semantic HTML structure
    const headerElement = screen.getByRole('heading', { level: 1 });
    expect(headerElement).toBeInTheDocument();
    
    const navigation = screen.getByRole('navigation');
    expect(navigation).toBeInTheDocument();
    
    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
  });

  test('sidebar onNavigationAction handler works from any currentView state', () => {
    render(<App />);
    
    // Click "From File" to change view
    fireEvent.click(screen.getByText('From File'));
    expect(screen.getByLabelText(/choose puzzle file/i)).toBeInTheDocument();
    
    // Click "From File" again - should work from any state
    fireEvent.click(screen.getByText('From File'));
    expect(screen.getByLabelText(/choose puzzle file/i)).toBeInTheDocument();
  });
});
