/**
 * API client types for v2 endpoints integration.
 * Provides type-safe interfaces for backend communication.
 */

import type { 
  LLMProvider, 
  ProviderValidationRequest, 
  ProviderValidationResponse,
  ProvidersStatusResponse,
  ProvidersListResponse,
  ProviderHealthResponse
} from './llm-provider';

import type {
  RecommendationRequest,
  RecommendationResponse,
  RecommendationError,
  GenerateRecommendationRequest,
  GenerateRecommendationResponse
} from './recommendation';

// Base API response wrapper
export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  status: number;
  statusText: string;
}

// API error interface
export interface ApiError {
  error: string;
  detail: string;
  error_code: string;
  path?: string;
  details?: Record<string, any>;
  errors?: Array<{
    field: string;
    message: string;
    type: string;
  }>;
}

// HTTP methods for API calls
export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

// Request configuration
export interface ApiRequestConfig {
  method: HttpMethod;
  url: string;
  data?: any;
  params?: Record<string, string | number | boolean>;
  headers?: Record<string, string>;
  timeout?: number;
}

// API client interface
export interface ApiClient {
  // Recommendation endpoints
  generateRecommendation: (request: GenerateRecommendationRequest) => Promise<ApiResponse<GenerateRecommendationResponse>>;
  getRecommendationHealth: () => Promise<ApiResponse<ProviderHealthResponse>>;
  listProviders: () => Promise<ApiResponse<ProvidersListResponse>>;
  
  // Provider validation endpoints
  validateProvider: (request: ProviderValidationRequest) => Promise<ApiResponse<ProviderValidationResponse>>;
  getProvidersStatus: () => Promise<ApiResponse<ProvidersStatusResponse>>;
  
  // Generic request method
  request: <T>(config: ApiRequestConfig) => Promise<ApiResponse<T>>;
}

// Configuration for API client
export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  headers?: Record<string, string>;
  withCredentials?: boolean;
}

// Endpoints constants
export const API_ENDPOINTS = {
  V2_RECOMMENDATIONS: '/api/v2/recommendations',
  V2_RECOMMENDATIONS_HEALTH: '/api/v2/recommendations/health',
  V2_RECOMMENDATIONS_PROVIDERS: '/api/v2/recommendations/providers',
  V2_PROVIDERS_VALIDATE: '/api/v2/providers/validate',
  V2_PROVIDERS_STATUS: '/api/v2/providers/status',
} as const;

// HTTP status codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

// Error codes from backend
export const ERROR_CODES = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INSUFFICIENT_WORDS: 'INSUFFICIENT_WORDS',
  INVALID_PROVIDER: 'INVALID_PROVIDER',
  LLM_PROVIDER_ERROR: 'LLM_PROVIDER_ERROR',
  CONFIGURATION_ERROR: 'CONFIGURATION_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
} as const;

// Request/Response pairs for specific endpoints
export interface RecommendationEndpoints {
  'POST /api/v2/recommendations': {
    request: GenerateRecommendationRequest;
    response: GenerateRecommendationResponse;
  };
  'GET /api/v2/recommendations/health': {
    request: never;
    response: ProviderHealthResponse;
  };
  'GET /api/v2/recommendations/providers': {
    request: never;
    response: ProvidersListResponse;
  };
}

export interface ProviderEndpoints {
  'POST /api/v2/providers/validate': {
    request: ProviderValidationRequest;
    response: ProviderValidationResponse;
  };
  'GET /api/v2/providers/status': {
    request: never;
    response: ProvidersStatusResponse;
  };
}

// Combined endpoint types
export type ApiEndpoints = RecommendationEndpoints & ProviderEndpoints;

// Utility type to extract request type for an endpoint
export type EndpointRequest<T extends keyof ApiEndpoints> = ApiEndpoints[T]['request'];

// Utility type to extract response type for an endpoint
export type EndpointResponse<T extends keyof ApiEndpoints> = ApiEndpoints[T]['response'];

// Loading states for different operations
export interface LoadingStates {
  generateRecommendation: boolean;
  validateProvider: boolean;
  getProviderStatus: boolean;
  getProviderHealth: boolean;
}

// Cache configuration for API responses
export interface CacheConfig {
  enabled: boolean;
  ttl: number; // Time to live in milliseconds
  maxSize: number; // Maximum number of cached responses
}

// Retry configuration for failed requests
export interface RetryConfig {
  enabled: boolean;
  maxAttempts: number;
  backoffMs: number;
  retryCondition: (error: ApiError) => boolean;
}