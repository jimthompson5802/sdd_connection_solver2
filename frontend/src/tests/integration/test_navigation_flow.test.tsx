import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../../App';

describe('Navigation Flow Integration', () => {
  test('clicking "From Image" in sidebar navigates to image setup interface', () => {
    // Arrange
    render(<App />);
    
    // Act - Click "From Image" in the sidebar
    fireEvent.click(screen.getByText('From Image'));
    
    // Assert - Should show image setup interface
    expect(screen.getByText('Setup Puzzle from Image')).toBeInTheDocument();
    expect(screen.getByText('Paste image here')).toBeInTheDocument();
    expect(screen.getByLabelText('LLM Provider')).toBeInTheDocument();
    expect(screen.getByLabelText('LLM Model')).toBeInTheDocument();
    expect(screen.getByLabelText('Setup Puzzle')).toBeInTheDocument();
  });

  test('navigation from sidebar to image setup maintains app state', () => {
    // Arrange
    render(<App />);
    
    // Act - Navigate from home to image setup
    fireEvent.click(screen.getByText('From Image'));
    
    // Assert - Should be on image-setup view
    expect(screen.getByText('Setup Puzzle from Image')).toBeInTheDocument();
    
    // Verify sidebar is still accessible and functional
    expect(screen.getByText('Start New Game')).toBeInTheDocument();
    expect(screen.getByText('From File')).toBeInTheDocument();
    expect(screen.getByText('From Image')).toBeInTheDocument();
  });

  test('image setup interface displays correctly with proper layout', () => {
    // Arrange
    render(<App />);
    
    // Act
    fireEvent.click(screen.getByText('From Image'));
    
    // Assert - Check vertical layout as per ASCII diagram specification
    const imageSetupContainer = screen.getByText('Setup Puzzle from Image').closest('.image-puzzle-setup');
    expect(imageSetupContainer).toBeInTheDocument();
    
    // Should have paste area, provider selection, and setup button in vertical arrangement
    expect(screen.getByTestId('image-paste-area')).toBeInTheDocument();
    expect(screen.getByLabelText('LLM Provider')).toBeInTheDocument();
    expect(screen.getByLabelText('Setup Puzzle')).toBeInTheDocument();
  });

  test('can navigate back from image setup to other views', () => {
    // Arrange
    render(<App />);
    
    // Act - Navigate to image setup, then to file upload
    fireEvent.click(screen.getByText('From Image'));
    expect(screen.getByText('Setup Puzzle from Image')).toBeInTheDocument();
    
    fireEvent.click(screen.getByText('From File'));
    
    // Assert - Should now be on file upload view
    expect(screen.getByText('Choose Puzzle File (CSV):')).toBeInTheDocument();
    expect(screen.queryByText('Setup Puzzle from Image')).not.toBeInTheDocument();
  });
});