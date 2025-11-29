/**
 * Main App component for the NYT Connections Puzzle Assistant.
 * Manages application state and coordinates between FileUpload and PuzzleInterface components.
 */

import React, { useState, useCallback } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import EnhancedPuzzleInterface from './components/EnhancedPuzzleInterface';
import { PuzzleState } from './types/puzzle';
import { apiService } from './services/api';

const App: React.FC = () => {
  const [puzzleState, setPuzzleState] = useState<PuzzleState>({
    words: [],
    currentRecommendation: [],
    recommendationConnection: '',
    correctCount: 0,
    mistakeCount: 0,
    gameStatus: 'waiting',
    isLoading: false,
    error: null,
    previousResponses: [],
  });

  // LLM provider selection stored at app-level so it can be persisted or shared
  const [llmProvider, setLlmProvider] = useState<import('./types/llm-provider').LLMProvider | null>(null);

  const handleFileUpload = useCallback(async (content: string) => {
    setPuzzleState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await apiService.setupPuzzle(content);
      
      setPuzzleState(prev => ({
        ...prev,
        words: response.remaining_words,
        currentRecommendation: [],
        recommendationConnection: '',
        correctCount: 0,
        mistakeCount: 0,
        gameStatus: 'active',
        isLoading: false,
        error: null,
      }));
    } catch (error) {
      setPuzzleState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to setup puzzle',
      }));
    }
  }, []);

  const handleRecordResponse = useCallback(async (
    type: 'correct' | 'incorrect' | 'one-away',
    color?: string,
    attemptWords?: string[]
  ) => {
    setPuzzleState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // include the provided attemptWords so backend can record; if undefined, backend will fallback
      const response = await apiService.recordResponse(type, color, attemptWords);

      // Append to previousResponses locally for UI history.
      // Prefer the explicit attemptWords when provided (LLM or traditional),
      // otherwise fall back to the previous recommendation words.
      setPuzzleState(prev => ({
        ...prev,
        words: response.remaining_words,
        correctCount: response.correct_count,
        mistakeCount: response.mistake_count,
        gameStatus: response.game_status,
        currentRecommendation: [], // Clear recommendation after response
        recommendationConnection: '',
        isLoading: false,
        error: null,
        previousResponses: [
          ...prev.previousResponses,
          {
            type,
            color,
            words: attemptWords ?? prev.currentRecommendation,
            timestamp: new Date(),
          },
        ],
      }));
    } catch (error) {
      setPuzzleState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to record response',
      }));
    }
  }, []);

  return (
    <div className="App">
      <header>
        <h1 className="App-header">NYT Connections Puzzle Assistant</h1>
      </header>

      <main className="App-main">
        {puzzleState.gameStatus === 'waiting' ? (
          <FileUpload
            onFileUpload={handleFileUpload}
            isLoading={puzzleState.isLoading}
            error={puzzleState.error}
          />
        ) : (
          <div className="puzzle-section">
            <div className="upload-new">
              <button
                onClick={() => setPuzzleState({
                  words: [],
                  currentRecommendation: [],
                  recommendationConnection: '',
                  correctCount: 0,
                  mistakeCount: 0,
                  gameStatus: 'waiting',
                  isLoading: false,
                  error: null,
                  previousResponses: [],
                })}
                className="secondary-button"
              >
                Upload New Puzzle
              </button>
            </div>
            
            <EnhancedPuzzleInterface
              words={puzzleState.words}
              recommendation={puzzleState.currentRecommendation}
              recommendationConnection={puzzleState.recommendationConnection}
              correctCount={puzzleState.correctCount}
              mistakeCount={puzzleState.mistakeCount}
              gameStatus={puzzleState.gameStatus}
              isLoading={puzzleState.isLoading}
              error={puzzleState.error}
              onRecordResponse={handleRecordResponse}
              previousResponses={puzzleState.previousResponses}
              // LLM-related props (start with no provider configured)
              llmProvider={llmProvider}
              onProviderChange={(p) => setLlmProvider(p)}
              showProviderControls={true}
              puzzleContext={''}
              previousGuesses={[]}
            />
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
