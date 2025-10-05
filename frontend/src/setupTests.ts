// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Jest setup for LLM Provider Integration testing
import 'jest-fetch-mock';

// Mock fetch for API calls
import fetchMock from 'jest-fetch-mock';
fetchMock.enableMocks();

// Mock console methods in tests to reduce noise
const originalError = console.error;
const originalWarn = console.warn;

beforeEach(() => {
  fetchMock.resetMocks();
  // Suppress console errors/warnings in tests unless needed
  console.error = jest.fn();
  console.warn = jest.fn();
});

afterEach(() => {
  console.error = originalError;
  console.warn = originalWarn;
});

// Global test utilities for LLM provider mocking
declare global {
  var mockLLMProviderResponse: (response: any) => void;
  var mockLLMProviderError: (status: number, message: string) => void;
  var testLLMProviders: {
    simple: { provider_type: string; model_name: null };
    ollama: { provider_type: string; model_name: string };
    openai: { provider_type: string; model_name: string };
  };
  var testRecommendationResponse: {
    recommended_words: string[];
    connection_explanation: string;
    confidence_score: number;
    provider_used: any;
    generation_time_ms: number;
  };
}

global.mockLLMProviderResponse = (response: any) => {
  fetchMock.mockResponseOnce(JSON.stringify(response));
};

global.mockLLMProviderError = (status: number, message: string) => {
  fetchMock.mockRejectOnce(new Error(message));
};

// Common test data for LLM providers
global.testLLMProviders = {
  simple: { provider_type: 'simple', model_name: null },
  ollama: { provider_type: 'ollama', model_name: 'llama2' },
  openai: { provider_type: 'openai', model_name: 'gpt-3.5-turbo' }
};

global.testRecommendationResponse = {
  recommended_words: ['BASS', 'FLOUNDER', 'SALMON', 'TROUT'],
  connection_explanation: 'These are all types of fish',
  confidence_score: 0.87,
  provider_used: global.testLLMProviders.ollama,
  generation_time_ms: 2340
};
