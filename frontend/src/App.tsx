/**
 * Main App component for the NYT Connections Puzzle Assistant.
 * Implements persistent three-region layout with sidebar navigation.
 */

import React, { useState, useCallback } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import EnhancedPuzzleInterface from './components/EnhancedPuzzleInterface';
import { ImagePuzzleSetup } from './components/ImagePuzzleSetup';
import Sidebar from './components/Sidebar';
import { PuzzleState } from './types/puzzle';
import { AppView, NavigationAction } from './types/navigation';
import { apiService } from './services/api';

const App: React.FC = () => {
  // Navigation state for the new layout
  const [currentView, setCurrentView] = useState<AppView>('initial');

  // Session ID for recording game results
  const [sessionId, setSessionId] = useState<string | null>(null);

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

  // Navigation handler for sidebar actions
  const handleNavigationAction = useCallback((action: NavigationAction) => {
    switch (action.type) {
      case 'from-file':
        setCurrentView('file-upload');
        break;
      case 'from-image':
        setCurrentView('image-setup');
        break;
      case 'toggle-menu':
        // Menu toggle is handled internally by Sidebar component
        // This callback is for logging/analytics if needed
        break;
      default:
        break;
    }
  }, []);

  const handleFileUpload = useCallback(async (content: string) => {
    setPuzzleState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await apiService.setupPuzzle(content);

      // Store the session ID for recording game results
      setSessionId(response.session_id);

      setPuzzleState({
        words: response.remaining_words,
        currentRecommendation: [],
        recommendationConnection: '',
        correctCount: 0,
        mistakeCount: 0,
        gameStatus: 'active',
        isLoading: false,
        error: null,
        previousResponses: [], // Fresh start - clear previous game's guess history
      });

      // Change view to show the puzzle interface
      setCurrentView('puzzle-active');
    } catch (error) {
      setPuzzleState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to setup puzzle',
      }));
    }
  }, []);

  const handleImageSetup = useCallback((extractedWords: string[], sessionIdFromImage?: string) => {
    // Store the session ID if provided
    if (sessionIdFromImage) {
      setSessionId(sessionIdFromImage);
    }

    // Set up puzzle state with words extracted from image
    setPuzzleState({
      words: extractedWords,
      currentRecommendation: [],
      recommendationConnection: '',
      correctCount: 0,
      mistakeCount: 0,
      gameStatus: 'active',
      isLoading: false,
      error: null,
      previousResponses: [], // Fresh start
    });

    // Transition to puzzle interface
    setCurrentView('puzzle-active');
  }, []);

  const handleImageError = useCallback((error: string) => {
    // Error handling for image setup failures
    setPuzzleState(prev => ({
      ...prev,
      error: error,
      isLoading: false
    }));
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

      // Update view when game ends
      if (response.game_status === 'won' || response.game_status === 'lost') {
        setCurrentView('puzzle-complete');
      }
    } catch (error) {
      setPuzzleState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to record response',
      }));
    }
  }, []);

  const renderMainContent = () => {
    switch (currentView) {
      case 'initial':
        return (
          <div className="welcome-message">
            <p>Select action in Left Side Bar</p>
          </div>
        );

      case 'file-upload':
        return (
          <FileUpload
            onFileUpload={handleFileUpload}
            isLoading={puzzleState.isLoading}
            error={puzzleState.error}
          />
        );

      case 'image-setup':
        return (
          <ImagePuzzleSetup
            onImageSetup={handleImageSetup}
            providers={[
              { type: 'openai', name: 'OpenAI' },
              { type: 'ollama', name: 'Ollama' },
              { type: 'simple', name: 'Simple' }
            ]}
            defaultProvider={{ type: 'openai', name: 'OpenAI' }}
            defaultModel="gpt-4-vision-preview"
            onError={handleImageError}
          />
        );      case 'puzzle-active':
      case 'puzzle-complete':
        return (
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
            llmProvider={llmProvider}
            onProviderChange={(p) => setLlmProvider(p)}
            showProviderControls={true}
            puzzleContext={''}
            previousGuesses={[]}
            sessionId={sessionId}
          />
        );

      default:
        return <div className="welcome-message"><p>Select action in Left Side Bar</p></div>;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>NYT Connections Puzzle Assistant</h1>
      </header>

      <Sidebar
        currentView={currentView}
        onNavigationAction={handleNavigationAction}
      />

      <main className="App-main" role="main">
        {renderMainContent()}
      </main>
    </div>
  );
};

export default App;
