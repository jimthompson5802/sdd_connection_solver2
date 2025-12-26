/**
 * T036, T052: GameHistoryPage Component
 *
 * Page component that displays the game history table.
 * Serves as the main view for /game-history route.
 * Includes export CSV functionality below the table.
 */
import React from 'react';
import GameHistoryTable from '../components/GameHistoryTable';
import ExportCSVButton from '../components/ExportCSVButton';
import './GameHistoryPage.css';

const GameHistoryPage: React.FC = () => {
  return (
    <div className="game-history-page">
      <div className="page-header">
        <h1>Game History</h1>
        <p className="page-description">
          View all your recorded puzzle games with performance metrics and details.
        </p>
      </div>

      <GameHistoryTable />

      {/* T052: Add ExportCSVButton below game history table */}
      <ExportCSVButton />
    </div>
  );
};

export default GameHistoryPage;
