/**
 * LLM Provider types for frontend integration.
 * Matches backend Pydantic models for type safety.
 */

export type LLMProviderType = "simple" | "ollama" | "openai";

export interface LLMProvider {
  provider_type: LLMProviderType;
  model_name: string | null;
}

export interface ProviderValidationRequest {
  provider_type: LLMProviderType;
  api_key?: string;
  base_url?: string;
}

export interface ProviderValidationResponse {
  provider_type: LLMProviderType;
  is_valid: boolean;
  status: string;
  message: string;
  details?: Record<string, any>;
}

export interface ProviderStatus {
  type: LLMProviderType;
  status: "available" | "configured" | "not_configured" | "default_config" | "invalid";
  message: string;
}

export interface ProvidersStatusResponse {
  providers: Record<string, ProviderStatus>;
  total_count: number;
  available_count: number;
}

export interface ProviderInfo {
  name: string;
  type: LLMProviderType;
  status: string;
  description: string;
  requires_config: boolean;
}

export interface ProvidersListResponse {
  providers: Record<string, ProviderInfo>;
  default_provider: LLMProviderType;
  total_count: number;
}

// Provider configuration types for settings
export interface OpenAIConfig {
  api_key: string;
  model_name?: string;
  timeout?: number;
}

export interface OllamaConfig {
  base_url: string;
  model_name?: string;
  timeout?: number;
}

export interface ProviderConfig {
  openai?: OpenAIConfig;
  ollama?: OllamaConfig;
}

// Error types for provider operations
export interface ProviderError {
  error: string;
  detail: string;
  error_code: string;
  provider_type?: LLMProviderType;
  details?: Record<string, any>;
}

// Health check types
export interface ProviderHealthResponse {
  status: "healthy" | "unhealthy";
  service: string;
  version: string;
  timestamp?: string;
  available_providers?: LLMProviderType[];
}