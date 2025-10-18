/**
 * Integration tests for provider selection flow.
 * These tests validate the complete provider selection user journey.
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ProviderSelectionFlow } from '../../src/components/ProviderSelectionFlow';

describe('Provider Selection Flow Integration', () => {
  beforeEach(() => {
    // Mock API calls
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('renders provider selection with health check', async () => {
    // Mock health check response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'healthy',
        providers_available: [
          { provider_type: 'simple', available: true },
          { provider_type: 'openai', available: true },
          { provider_type: 'ollama', available: false, error_message: 'Not configured' }
        ]
      })
    });

    // This will fail until component exists
    render(<ProviderSelectionFlow onProviderSelected={jest.fn()} />);
    
    // Should check health on mount
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/v2/health');
    });
    
    // Should show available providers
    expect(screen.getByText(/simple/i)).toBeInTheDocument();
    expect(screen.getByText(/openai/i)).toBeInTheDocument();
    expect(screen.getByText(/ollama/i)).toBeInTheDocument();
    expect(screen.getByText(/not configured/i)).toBeInTheDocument();
  });

  test('handles provider selection and configuration', async () => {
    const mockOnProviderSelected = jest.fn();
    
    // Mock health check
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'healthy',
        providers_available: [
          { provider_type: 'openai', available: true }
        ]
      })
    });

    render(<ProviderSelectionFlow onProviderSelected={mockOnProviderSelected} />);
    
    await waitFor(() => {
      expect(screen.getByText(/openai/i)).toBeInTheDocument();
    });
    
    // Select OpenAI provider
    fireEvent.click(screen.getByText(/openai/i));
    
    // Should show model configuration
    expect(screen.getByLabelText(/model name/i)).toBeInTheDocument();
    
    // Configure model
    fireEvent.change(screen.getByLabelText(/model name/i), {
      target: { value: 'gpt-4' }
    });
    
    // Confirm selection
    fireEvent.click(screen.getByText(/confirm/i));
    
    // Should call callback with provider configuration
    expect(mockOnProviderSelected).toHaveBeenCalledWith({
      provider_type: 'openai',
      model_name: 'gpt-4'
    });
  });

  test('validates provider configuration before selection', async () => {
    const mockOnProviderSelected = jest.fn();
    
    // Mock health check
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'healthy',
        providers_available: [
          { provider_type: 'openai', available: true }
        ]
      })
    });

    render(<ProviderSelectionFlow onProviderSelected={mockOnProviderSelected} />);
    
    await waitFor(() => {
      expect(screen.getByText(/openai/i)).toBeInTheDocument();
    });
    
    // Select OpenAI provider
    fireEvent.click(screen.getByText(/openai/i));
    
    // Try to confirm without model name
    fireEvent.click(screen.getByText(/confirm/i));
    
    // Should show validation error
    expect(screen.getByText(/model name is required/i)).toBeInTheDocument();
    
    // Should not call callback
    expect(mockOnProviderSelected).not.toHaveBeenCalled();
  });

  test('handles provider availability errors gracefully', async () => {
    // Mock failed health check
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<ProviderSelectionFlow onProviderSelected={jest.fn()} />);
    
    // Should show fallback UI
    await waitFor(() => {
      expect(screen.getByText(/unable to check provider status/i)).toBeInTheDocument();
    });
    
    // Should still allow simple provider selection
    expect(screen.getByText(/simple/i)).toBeInTheDocument();
  });

  test('shows provider recommendations based on availability', async () => {
    // Mock health check with mixed availability
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'healthy',
        providers_available: [
          { provider_type: 'simple', available: true },
          { provider_type: 'openai', available: false, error_message: 'API key missing' },
          { provider_type: 'ollama', available: true }
        ]
      })
    });

    render(<ProviderSelectionFlow onProviderSelected={jest.fn()} />);
    
    await waitFor(() => {
      expect(screen.getByText(/simple/i)).toBeInTheDocument();
    });
    
    // Should highlight available providers
    expect(screen.getByText(/recommended/i)).toBeInTheDocument();
    
    // Should show setup instructions for unavailable providers
    expect(screen.getByText(/api key missing/i)).toBeInTheDocument();
  });

  test('supports provider switching during configuration', async () => {
    const mockOnProviderSelected = jest.fn();
    
    // Mock health check
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'healthy',
        providers_available: [
          { provider_type: 'openai', available: true },
          { provider_type: 'ollama', available: true }
        ]
      })
    });

    render(<ProviderSelectionFlow onProviderSelected={mockOnProviderSelected} />);
    
    await waitFor(() => {
      expect(screen.getByText(/openai/i)).toBeInTheDocument();
    });
    
    // Select OpenAI first
    fireEvent.click(screen.getByText(/openai/i));
    fireEvent.change(screen.getByLabelText(/model name/i), {
      target: { value: 'gpt-3.5-turbo' }
    });
    
    // Switch to Ollama
    fireEvent.click(screen.getByText(/ollama/i));
    
    // Should clear previous configuration and show Ollama config
    expect(screen.getByLabelText(/model name/i)).toHaveValue('');
    expect(screen.getByPlaceholderText(/llama2/i)).toBeInTheDocument();
  });

  test('persists provider selection in session storage', async () => {
    const mockOnProviderSelected = jest.fn();
    
    // Mock sessionStorage
    const mockSessionStorage = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn()
    };
    Object.defineProperty(window, 'sessionStorage', {
      value: mockSessionStorage,
      writable: true
    });
    
    // Mock health check
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'healthy',
        providers_available: [
          { provider_type: 'simple', available: true }
        ]
      })
    });

    render(<ProviderSelectionFlow onProviderSelected={mockOnProviderSelected} />);
    
    await waitFor(() => {
      expect(screen.getByText(/simple/i)).toBeInTheDocument();
    });
    
    // Select simple provider
    fireEvent.click(screen.getByText(/simple/i));
    fireEvent.click(screen.getByText(/confirm/i));
    
    // Should persist selection
    expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
      'selectedProvider',
      JSON.stringify({ provider_type: 'simple', model_name: null })
    );
  });

  test('restores previous provider selection on load', async () => {
    // Mock previous selection in sessionStorage
    const mockSessionStorage = {
      getItem: jest.fn().mockReturnValue(
        JSON.stringify({ provider_type: 'openai', model_name: 'gpt-4' })
      ),
      setItem: jest.fn(),
      removeItem: jest.fn()
    };
    Object.defineProperty(window, 'sessionStorage', {
      value: mockSessionStorage,
      writable: true
    });
    
    // Mock health check
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'healthy',
        providers_available: [
          { provider_type: 'openai', available: true }
        ]
      })
    });

    render(<ProviderSelectionFlow onProviderSelected={jest.fn()} />);
    
    // Should restore previous selection
    await waitFor(() => {
      expect(screen.getByDisplayValue(/gpt-4/i)).toBeInTheDocument();
    });
  });

  test('provides help documentation for each provider', async () => {
    // Mock health check
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'healthy',
        providers_available: [
          { provider_type: 'openai', available: false, error_message: 'API key missing' }
        ]
      })
    });

    render(<ProviderSelectionFlow onProviderSelected={jest.fn()} />);
    
    await waitFor(() => {
      expect(screen.getByText(/openai/i)).toBeInTheDocument();
    });
    
    // Click help for OpenAI
    fireEvent.click(screen.getByLabelText(/help for openai/i));
    
    // Should show setup instructions
    expect(screen.getByText(/set your openai api key/i)).toBeInTheDocument();
    expect(screen.getByText(/OPENAI_API_KEY/i)).toBeInTheDocument();
  });

  test('handles network errors during provider health check', async () => {
    // Mock network error
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<ProviderSelectionFlow onProviderSelected={jest.fn()} />);
    
    // Should show error state with fallback options
    await waitFor(() => {
      expect(screen.getByText(/connection error/i)).toBeInTheDocument();
    });
    
    // Should allow retry
    fireEvent.click(screen.getByText(/retry/i));
    
    // Should attempt health check again
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });
});