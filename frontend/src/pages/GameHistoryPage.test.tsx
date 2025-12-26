/**
 * Tests for GameHistoryPage Component
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import GameHistoryPage from './GameHistoryPage';

// Mock child components
jest.mock('../components/GameHistoryTable', () => {
  return function MockGameHistoryTable() {
    return <div data-testid="game-history-table">Game History Table</div>;
  };
});

jest.mock('../components/ExportCSVButton', () => {
  return function MockExportCSVButton() {
    return <button data-testid="export-csv-button">Export CSV</button>;
  };
});

describe('GameHistoryPage', () => {
  test('renders page header with title and description', () => {
    render(<GameHistoryPage />);

    expect(screen.getByRole('heading', { name: /game history/i })).toBeInTheDocument();
    expect(screen.getByText(/view all your recorded puzzle games/i)).toBeInTheDocument();
  });

  test('renders GameHistoryTable component', () => {
    render(<GameHistoryPage />);

    expect(screen.getByTestId('game-history-table')).toBeInTheDocument();
  });

  test('renders ExportCSVButton component', () => {
    render(<GameHistoryPage />);

    expect(screen.getByTestId('export-csv-button')).toBeInTheDocument();
  });
});
