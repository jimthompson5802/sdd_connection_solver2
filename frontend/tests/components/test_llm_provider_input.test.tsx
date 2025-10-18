/**
 * Component tests for LLM provider input field.
 * These tests validate the LLM provider selection UI component.
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LLMProviderInput } from '../../src/components/LLMProviderInput';

describe('LLMProviderInput Component', () => {
  test('renders provider selection dropdown', () => {
    // This will fail until component exists
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'simple', model_name: null }}
        onChange={mockOnChange}
      />
    );
    
    // Should have provider type selection
    expect(screen.getByLabelText(/provider type/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue(/simple/i)).toBeInTheDocument();
  });

  test('shows model name input for openai provider', async () => {
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'openai', model_name: 'gpt-3.5-turbo' }}
        onChange={mockOnChange}
      />
    );
    
    // Should show model name input for OpenAI
    expect(screen.getByLabelText(/model name/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue(/gpt-3.5-turbo/i)).toBeInTheDocument();
  });

  test('shows model name input for ollama provider', async () => {
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'ollama', model_name: 'llama2' }}
        onChange={mockOnChange}
      />
    );
    
    // Should show model name input for Ollama
    expect(screen.getByLabelText(/model name/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue(/llama2/i)).toBeInTheDocument();
  });

  test('hides model name input for simple provider', () => {
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'simple', model_name: null }}
        onChange={mockOnChange}
      />
    );
    
    // Should not show model name input for simple provider
    expect(screen.queryByLabelText(/model name/i)).not.toBeInTheDocument();
  });

  test('calls onChange when provider type changes', async () => {
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'simple', model_name: null }}
        onChange={mockOnChange}
      />
    );
    
    // Change provider type
    const providerSelect = screen.getByLabelText(/provider type/i);
    fireEvent.change(providerSelect, { target: { value: 'openai' } });
    
    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledWith({
        provider_type: 'openai',
        model_name: 'gpt-3.5-turbo' // Should set default model
      });
    });
  });

  test('calls onChange when model name changes', async () => {
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'openai', model_name: 'gpt-3.5-turbo' }}
        onChange={mockOnChange}
      />
    );
    
    // Change model name
    const modelInput = screen.getByLabelText(/model name/i);
    fireEvent.change(modelInput, { target: { value: 'gpt-4' } });
    
    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledWith({
        provider_type: 'openai',
        model_name: 'gpt-4'
      });
    });
  });

  test('validates required model name for LLM providers', async () => {
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'openai', model_name: '' }}
        onChange={mockOnChange}
        showValidation={true}
      />
    );
    
    // Should show validation error for empty model name
    expect(screen.getByText(/model name is required/i)).toBeInTheDocument();
  });

  test('shows provider availability status', async () => {
    const mockOnChange = jest.fn();
    
    // Mock provider availability check
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        providers_available: [
          { provider_type: 'simple', available: true },
          { provider_type: 'openai', available: false, error_message: 'API key not configured' },
          { provider_type: 'ollama', available: true }
        ]
      })
    });
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'openai', model_name: 'gpt-3.5-turbo' }}
        onChange={mockOnChange}
        checkAvailability={true}
      />
    );
    
    // Should show availability status
    await waitFor(() => {
      expect(screen.getByText(/api key not configured/i)).toBeInTheDocument();
    });
  });

  test('provides default model suggestions', () => {
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'openai', model_name: '' }}
        onChange={mockOnChange}
      />
    );
    
    // Should show model suggestions
    expect(screen.getByText(/gpt-3.5-turbo/i)).toBeInTheDocument();
    expect(screen.getByText(/gpt-4/i)).toBeInTheDocument();
  });

  test('handles provider configuration errors gracefully', async () => {
    const mockOnChange = jest.fn();
    
    // Mock failed availability check
    global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'openai', model_name: 'gpt-3.5-turbo' }}
        onChange={mockOnChange}
        checkAvailability={true}
      />
    );
    
    // Should handle error gracefully
    await waitFor(() => {
      expect(screen.queryByText(/network error/i)).not.toBeInTheDocument();
    });
  });

  test('preserves provider selection on re-render', () => {
    const mockOnChange = jest.fn();
    
    const { rerender } = render(
      <LLMProviderInput
        value={{ provider_type: 'ollama', model_name: 'llama2' }}
        onChange={mockOnChange}
      />
    );
    
    // Re-render with same props
    rerender(
      <LLMProviderInput
        value={{ provider_type: 'ollama', model_name: 'llama2' }}
        onChange={mockOnChange}
      />
    );
    
    // Should preserve selection
    expect(screen.getByDisplayValue(/llama2/i)).toBeInTheDocument();
  });

  test('supports disabled state', () => {
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'simple', model_name: null }}
        onChange={mockOnChange}
        disabled={true}
      />
    );
    
    // Should disable input fields
    expect(screen.getByLabelText(/provider type/i)).toBeDisabled();
  });

  test('provides accessibility labels and roles', () => {
    const mockOnChange = jest.fn();
    
    render(
      <LLMProviderInput
        value={{ provider_type: 'openai', model_name: 'gpt-3.5-turbo' }}
        onChange={mockOnChange}
      />
    );
    
    // Should have proper accessibility attributes
    expect(screen.getByRole('combobox', { name: /provider type/i })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: /model name/i })).toBeInTheDocument();
  });
});