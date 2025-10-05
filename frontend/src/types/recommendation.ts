/**
 * Recommendation types for LLM-powered word suggestions.
 * Matches backend Pydantic models for type safety.
 */

import type { LLMProvider } from './llm-provider';

// Outcome types for guess attempts
export type GuessOutcome = "correct" | "incorrect" | "one-away";

// Difficulty levels for completed groups
export type DifficultyLevel = "straightforward" | "tricky" | "red-herring" | "unknown";

export interface GuessAttempt {
  words: string[];
  outcome: GuessOutcome;
  actual_connection?: string;
  timestamp: string; // ISO 8601 format
}

export interface CompletedGroup {
  words: string[];
  connection: string;
  difficulty_level: DifficultyLevel;
  color?: string;
}

export interface PuzzleState {
  remaining_words: string[];
  completed_groups: CompletedGroup[];
  total_mistakes: number;
  max_mistakes: number;
  game_status: "active" | "won" | "lost";
}

export interface RecommendationRequest {
  llm_provider: LLMProvider;
  remaining_words: string[];
  previous_guesses?: GuessAttempt[];
  puzzle_context?: string;
}

export interface RecommendationResponse {
  recommended_words: string[];
  connection_explanation: string;
  confidence_score: number; // 0.0 to 1.0
  provider_used: string;
  generation_time_ms?: number; // null for simple provider
  puzzle_state?: PuzzleState;
  alternative_suggestions?: string[][];
}

// Request/response types for the API endpoints
export interface GenerateRecommendationRequest {
  llm_provider: LLMProvider;
  remaining_words: string[];
  previous_guesses?: GuessAttempt[];
  puzzle_context?: string;
}

export interface GenerateRecommendationResponse extends RecommendationResponse {}

// Error types specific to recommendations
export interface RecommendationError {
  error: string;
  detail: string;
  error_code: string;
  path?: string;
  errors?: Array<{
    field: string;
    message: string;
    type: string;
  }>;
}

// Loading state for recommendations
export interface RecommendationLoadingState {
  isLoading: boolean;
  provider?: string;
  startTime?: number;
  progress?: number;
}

// Validation types for recommendation requests
export interface ValidationError {
  field: string;
  message: string;
  type: string;
}

export interface RequestValidationError {
  error: string;
  message: string;
  error_code: string;
  errors: ValidationError[];
}

// Types for recommendation history and tracking
export interface RecommendationHistory {
  request: RecommendationRequest;
  response: RecommendationResponse;
  timestamp: string;
  success: boolean;
  error?: RecommendationError;
}

// Settings and preferences for recommendations
export interface RecommendationSettings {
  preferred_provider: string;
  enable_explanations: boolean;
  show_confidence_scores: boolean;
  enable_alternative_suggestions: boolean;
  timeout_seconds: number;
}

// Metrics and analytics for recommendations
export interface RecommendationMetrics {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  average_response_time: number;
  provider_usage: Record<string, number>;
  success_rate_by_provider: Record<string, number>;
}