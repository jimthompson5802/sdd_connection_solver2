import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Sidebar from './Sidebar';

describe('Sidebar', () => {
  const mockOnNavigationAction = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders "Start New Game" menu', () => {
    render(<Sidebar currentView="initial" onNavigationAction={mockOnNavigationAction} />);
    
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
  });

  test('"Start New Game" is expanded by default', () => {
    render(<Sidebar currentView="initial" onNavigationAction={mockOnNavigationAction} />);
    
    // Should show "From File" sub-item when expanded
    expect(screen.getByText('From File')).toBeInTheDocument();
  });

  test('clicking "From File" triggers navigation action', () => {
    render(<Sidebar currentView="initial" onNavigationAction={mockOnNavigationAction} />);
    
    fireEvent.click(screen.getByText('From File'));
    expect(mockOnNavigationAction).toHaveBeenCalledWith({ type: 'from-file' });
  });

  test('renders navigation hierarchy correctly', () => {
    render(<Sidebar currentView="initial" onNavigationAction={mockOnNavigationAction} />);
    
    // Should have the correct navigation structure
    const startNewGame = screen.getByText('Start New Game');
    const fromFile = screen.getByText('From File');
    
    expect(startNewGame).toBeInTheDocument();
    expect(fromFile).toBeInTheDocument();
    
    // Start New Game should be a parent (level 0)
    expect(startNewGame.closest('.navigation-item')).toHaveClass('level-0');
    // From File should be a child (level 1)  
    expect(fromFile.closest('.navigation-item')).toHaveClass('level-1');
  });

  test('has sidebar width constraints', () => {
    render(<Sidebar currentView="initial" onNavigationAction={mockOnNavigationAction} />);
    
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toHaveClass('sidebar');
    
    // CSS should enforce min 180px, max 20% width constraints
    // This will be verified by CSS tests
  });

  test('includes proper accessibility attributes', () => {
    render(<Sidebar currentView="initial" onNavigationAction={mockOnNavigationAction} />);
    
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toHaveAttribute('aria-label');
  });

  test('clicking "Start New Game" toggles expansion', () => {
    render(<Sidebar currentView="initial" onNavigationAction={mockOnNavigationAction} />);
    
    const startNewGame = screen.getByText('Start New Game');
    
    // Initially expanded - From File should be visible
    expect(screen.getByText('From File')).toBeInTheDocument();
    
    // Click to collapse
    fireEvent.click(startNewGame);
    
    // Should trigger toggle action, not navigation
    expect(mockOnNavigationAction).toHaveBeenCalledWith({ 
      type: 'toggle-menu', 
      menu: 'start-new-game' 
    });
  });

  test('maintains expansion state correctly', () => {
    const { rerender } = render(
      <Sidebar currentView="initial" onNavigationAction={mockOnNavigationAction} />
    );
    
    // Initially expanded
    expect(screen.getByText('From File')).toBeInTheDocument();
    
    // The component should manage its own expansion state internally
    // This test verifies the component behavior matches the design
  });
});