/**
 * TypeScript type definitions for the NYT Connections Puzzle Assistant.
 * Defines interfaces for puzzle state, API requests/responses, and component props.
 */

// API Request/Response Types
export interface SetupPuzzleRequest {
  file_content: string;
}

export interface SetupPuzzleResponse {
  remaining_words: string[];
  status: string;
}

export interface NextRecommendationResponse {
  words: string[];
  connection: string;
  status: string;
}

export interface RecordResponseRequest {
  response_type: 'correct' | 'incorrect' | 'one-away';
  color?: 'Yellow' | 'Green' | 'Blue' | 'Purple';
}

export interface RecordResponseResponse {
  remaining_words: string[];
  correct_count: number;
  mistake_count: number;
  game_status: 'active' | 'won' | 'lost';
}

// Application State Types
export interface PuzzleState {
  words: string[];
  currentRecommendation: string[];
  recommendationConnection: string;
  correctCount: number;
  mistakeCount: number;
  gameStatus: 'waiting' | 'active' | 'won' | 'lost';
  isLoading: boolean;
  error: string | null;
  previousResponses: UserResponse[];
}

export interface UserResponse {
  type: 'correct' | 'incorrect' | 'one-away';
  color?: string;
  words: string[];
  timestamp: Date;
}

// Component Props Types
export interface FileUploadProps {
  onFileUpload: (content: string) => void;
  isLoading?: boolean;
  error?: string | null;
}

export interface PuzzleInterfaceProps {
  words: string[];
  recommendation: string[];
  recommendationConnection: string;
  correctCount: number;
  mistakeCount: number;
  gameStatus: 'waiting' | 'active' | 'won' | 'lost';
  isLoading: boolean;
  error: string | null;
  onGetRecommendation: () => void;
  onRecordResponse: (type: 'correct' | 'incorrect' | 'one-away', color?: string, words?: string[]) => void;
  previousResponses: UserResponse[];
}

export interface RecommendationDisplayProps {
  words: string[];
  connection: string;
  onGetRecommendation: () => void;
  isLoading?: boolean;
}

export interface ResponseButtonsProps {
  onRecordResponse: (type: 'correct' | 'incorrect' | 'one-away', color?: string) => void;
  isDisabled?: boolean;
}

export interface GameStatusProps {
  correctCount: number;
  mistakeCount: number;
  gameStatus: 'waiting' | 'active' | 'won' | 'lost';
  wordsRemaining: number;
}

// Utility Types
export type ResponseType = 'correct' | 'incorrect' | 'one-away';
export type GameStatus = 'waiting' | 'active' | 'won' | 'lost';
export type ConnectionColor = 'Yellow' | 'Green' | 'Blue' | 'Purple';

// Constants
export const MAX_MISTAKES = 4;
export const TOTAL_GROUPS = 4;
export const WORDS_PER_GROUP = 4;
export const TOTAL_WORDS = 16;

export const CONNECTION_COLORS: ConnectionColor[] = ['Yellow', 'Green', 'Blue', 'Purple'];

export const COLOR_DIFFICULTY_MAP: Record<ConnectionColor, number> = {
  'Yellow': 1,
  'Green': 2,
  'Blue': 3,
  'Purple': 4,
};

// Error Types
export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

export class PuzzleError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'PuzzleError';
  }
}

// Validation Utilities
export const isValidResponseType = (type: string): type is ResponseType => {
  return ['correct', 'incorrect', 'one-away'].includes(type);
};

export const isValidConnectionColor = (color: string): color is ConnectionColor => {
  return CONNECTION_COLORS.includes(color as ConnectionColor);
};

export const isValidGameStatus = (status: string): status is GameStatus => {
  return ['waiting', 'active', 'won', 'lost'].includes(status);
};