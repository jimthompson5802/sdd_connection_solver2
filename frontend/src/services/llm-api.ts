/**
 * LLM API service for handling LLM provider operations and recommendations.
 * Integrates with v2 backend endpoints for LLM provider management.
 */

import {
  LLMProvider,
  ProviderValidationRequest,
  ProviderValidationResponse,
  ProvidersStatusResponse,
  ProvidersListResponse
} from '../types/llm-provider';

import {
  GenerateRecommendationRequest,
  GenerateRecommendationResponse,
  RecommendationError
} from '../types/recommendation';

import { ApiError, ApiResponse } from '../types/api';

/**
 * LLM API Service for provider management and recommendations
 */
export class LLMApiService {
  private baseUrl: string;
  private timeout: number;

  constructor(baseUrl?: string, timeout: number = 30000) {
    this.baseUrl = baseUrl || process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.timeout = timeout;
  }

  /**
   * Create a fetch request with timeout and error handling
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit = {},
    timeoutMs: number = this.timeout
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Request timeout after ${timeoutMs}ms`);
      }
      throw error;
    }
  }

  /**
   * Handle API response and extract data or throw error
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorData: any;
      try {
        errorData = await response.json();
      } catch {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Handle different error response formats
      if (errorData.detail) {
        throw new Error(errorData.detail);
      } else if (errorData.message) {
        throw new Error(errorData.message);
      } else if (errorData.error) {
        throw new Error(errorData.error);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    }

    try {
      return await response.json();
    } catch (error) {
      throw new Error('Invalid JSON response from server');
    }
  }

  /**
   * Get list of available LLM providers
   */
  async getProviders(): Promise<ProvidersListResponse> {
    try {
      const response = await this.fetchWithTimeout(`${this.baseUrl}/api/v2/providers`);
      return this.handleResponse<ProvidersListResponse>(response);
    } catch (error) {
      throw new Error(`Failed to get providers: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get status of all LLM providers
   */
  async getProvidersStatus(): Promise<ProvidersStatusResponse> {
    try {
      const response = await this.fetchWithTimeout(`${this.baseUrl}/api/v2/providers/status`);
      return this.handleResponse<ProvidersStatusResponse>(response);
    } catch (error) {
      throw new Error(`Failed to get provider status: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Validate a specific LLM provider configuration
   */
  async validateProvider(request: ProviderValidationRequest): Promise<ProviderValidationResponse> {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/api/v2/providers/validate`,
        {
          method: 'POST',
          body: JSON.stringify(request),
        }
      );
      return this.handleResponse<ProviderValidationResponse>(response);
    } catch (error) {
      throw new Error(`Failed to validate provider: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate recommendations using specified LLM provider
   */
  async generateRecommendation(request: GenerateRecommendationRequest): Promise<GenerateRecommendationResponse> {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/api/v2/recommendations`,
        {
          method: 'POST',
          body: JSON.stringify(request),
        },
        60000 // 60 second timeout for LLM requests
      );
      return this.handleResponse<GenerateRecommendationResponse>(response);
    } catch (error) {
      throw new Error(`Failed to generate recommendation: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Test connectivity to the backend API
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await this.fetchWithTimeout(`${this.baseUrl}/health`, {}, 5000);
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Get available models for a specific provider type
   */
  async getProviderModels(providerType: string): Promise<string[]> {
    try {
      const response = await this.fetchWithTimeout(`${this.baseUrl}/api/v2/providers/${providerType}/models`);
      const data = await this.handleResponse<{ models: string[] }>(response);
      return data.models;
    } catch (error) {
      // If endpoint doesn't exist, return empty array
      if (error instanceof Error && error.message.includes('404')) {
        return [];
      }
      throw new Error(`Failed to get models for ${providerType}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

/**
 * Singleton instance of the LLM API service
 */
export const llmApiService = new LLMApiService();

/**
 * Hook for using LLM API service in React components
 */
export function useLLMApi() {
  return llmApiService;
}

export default LLMApiService;