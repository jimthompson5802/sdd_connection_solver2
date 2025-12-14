/**
 * Comprehensive tests for LLMProviderInput component.
 * Tests provider selection, model configuration, validation, and state management.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LLMProviderInput, LLMProviderInputProps } from './LLMProviderInput';
import { LLMProvider } from '../types/llm-provider';

describe('LLMProviderInput Component', () => {
  const mockSimpleProvider: LLMProvider = {
    provider_type: 'simple',
    model_name: null,
  };

  const mockOllamaProvider: LLMProvider = {
    provider_type: 'ollama',
    model_name: 'qwen2.5:32b',
  };

  const mockOpenAIProvider: LLMProvider = {
    provider_type: 'openai',
    model_name: 'gpt-4o-mini',
  };

  const defaultProps: LLMProviderInputProps = {
    value: mockSimpleProvider,
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    test('renders provider selection dropdown', () => {
      render(<LLMProviderInput {...defaultProps} />);

      expect(screen.getByLabelText('Provider Type')).toBeInTheDocument();
    });

    test('displays all provider options', () => {
      render(<LLMProviderInput {...defaultProps} />);

      const select = screen.getByLabelText('Provider Type') as HTMLSelectElement;
      const options = Array.from(select.options).map(opt => opt.value);

      expect(options).toContain('simple');
      expect(options).toContain('ollama');
      expect(options).toContain('openai');
    });

    test('shows current provider value', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} />);

      const select = screen.getByLabelText('Provider Type') as HTMLSelectElement;
      expect(select.value).toBe('ollama');
    });

    test('has proper ARIA attributes for provider select', () => {
      render(<LLMProviderInput {...defaultProps} />);

      const select = screen.getByLabelText('Provider Type');
      expect(select).toHaveAttribute('aria-describedby', 'provider-description');
    });
  });

  describe('Provider Type Changes', () => {
    test('calls onChange when provider type changes', () => {
      const onChange = jest.fn();
      render(<LLMProviderInput {...defaultProps} onChange={onChange} />);

      const select = screen.getByLabelText('Provider Type');
      fireEvent.change(select, { target: { value: 'ollama' } });

      expect(onChange).toHaveBeenCalledWith({
        provider_type: 'ollama',
        model_name: 'qwen2.5:32b', // Default for ollama
      });
    });

    test('sets default model name for ollama', () => {
      const onChange = jest.fn();
      render(<LLMProviderInput {...defaultProps} onChange={onChange} />);

      const select = screen.getByLabelText('Provider Type');
      fireEvent.change(select, { target: { value: 'ollama' } });

      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          provider_type: 'ollama',
          model_name: 'qwen2.5:32b',
        })
      );
    });

    test('sets default model name for openai', () => {
      const onChange = jest.fn();
      render(<LLMProviderInput {...defaultProps} onChange={onChange} />);

      const select = screen.getByLabelText('Provider Type');
      fireEvent.change(select, { target: { value: 'openai' } });

      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          provider_type: 'openai',
          model_name: 'gpt-4o-mini',
        })
      );
    });

    test('sets null model name for simple provider', () => {
      const onChange = jest.fn();
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} onChange={onChange} />);

      const select = screen.getByLabelText('Provider Type');
      fireEvent.change(select, { target: { value: 'simple' } });

      expect(onChange).toHaveBeenCalledWith(
        expect.objectContaining({
          provider_type: 'simple',
          model_name: null,
        })
      );
    });

    test('clears validation result when provider changes', async () => {
      const onValidate = jest.fn().mockResolvedValue(true);
      render(
        <LLMProviderInput
          {...defaultProps}
          value={mockOllamaProvider}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      // Wait for initial validation
      await waitFor(() => {
        expect(screen.getByText(/ollama provider is available/)).toBeInTheDocument();
      });

      // Change provider
      const select = screen.getByLabelText('Provider Type');
      fireEvent.change(select, { target: { value: 'simple' } });

      // Validation result should be cleared
      expect(screen.queryByText(/ollama provider is available/)).not.toBeInTheDocument();
    });
  });

  describe('Provider Descriptions', () => {
    test('shows description for simple provider', () => {
      render(<LLMProviderInput {...defaultProps} value={mockSimpleProvider} />);

      expect(screen.getByText(/Fast rule-based recommendations/)).toBeInTheDocument();
    });

    test('shows description for ollama provider', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} />);

      expect(screen.getByText(/Local AI models running on your machine/)).toBeInTheDocument();
    });

    test('shows description for openai provider', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOpenAIProvider} />);

      expect(screen.getByText(/Advanced AI models from OpenAI/)).toBeInTheDocument();
    });

    test('updates description when provider changes', () => {
      const { rerender } = render(<LLMProviderInput {...defaultProps} value={mockSimpleProvider} />);

      expect(screen.getByText(/Fast rule-based/)).toBeInTheDocument();

      rerender(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} />);

      expect(screen.getByText(/Local AI models/)).toBeInTheDocument();
      expect(screen.queryByText(/Fast rule-based/)).not.toBeInTheDocument();
    });
  });

  describe('Model Name Input', () => {
    test('does not show model input for simple provider', () => {
      render(<LLMProviderInput {...defaultProps} value={mockSimpleProvider} />);

      expect(screen.queryByLabelText('Model Name')).not.toBeInTheDocument();
    });

    test('shows model input for ollama provider', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} />);

      expect(screen.getByLabelText('Model Name')).toBeInTheDocument();
    });

    test('shows model input for openai provider', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOpenAIProvider} />);

      expect(screen.getByLabelText('Model Name')).toBeInTheDocument();
    });

    test('displays current model name in input', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} />);

      const input = screen.getByLabelText('Model Name') as HTMLInputElement;
      expect(input.value).toBe('qwen2.5:32b');
    });

    test('calls onChange when model name changes', () => {
      const onChange = jest.fn();
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} onChange={onChange} />);

      const input = screen.getByLabelText('Model Name');
      fireEvent.change(input, { target: { value: 'llama2' } });

      expect(onChange).toHaveBeenCalledWith({
        provider_type: 'ollama',
        model_name: 'llama2',
      });
    });

    test('sets model_name to null when input is cleared', () => {
      const onChange = jest.fn();
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} onChange={onChange} />);

      const input = screen.getByLabelText('Model Name');
      fireEvent.change(input, { target: { value: '' } });

      expect(onChange).toHaveBeenCalledWith({
        provider_type: 'ollama',
        model_name: null,
      });
    });

    test('has proper ARIA attributes for model input', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} />);

      const input = screen.getByLabelText('Model Name');
      expect(input).toHaveAttribute('aria-describedby', 'model-description');
    });

    test('shows placeholder with default model for ollama', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} />);

      const input = screen.getByLabelText('Model Name') as HTMLInputElement;
      expect(input.placeholder).toBe('Default: qwen2.5:32b');
    });

    test('shows placeholder with default model for openai', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOpenAIProvider} />);

      const input = screen.getByLabelText('Model Name') as HTMLInputElement;
      expect(input.placeholder).toBe('Default: gpt-4o-mini');
    });
  });

  describe('Model Descriptions', () => {
    test('shows ollama model description', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} />);

      expect(screen.getByText(/Enter the name of an Ollama model/)).toBeInTheDocument();
      expect(screen.getByText(/qwen2.5:32b, codellama, mistral/)).toBeInTheDocument();
    });

    test('shows openai model description', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOpenAIProvider} />);

      expect(screen.getByText(/Enter an OpenAI model name/)).toBeInTheDocument();
      expect(screen.getByText(/gpt-4o-mini, gpt-4/)).toBeInTheDocument();
    });
  });

  describe('Validation Functionality', () => {
    test('does not show validation section by default', () => {
      render(<LLMProviderInput {...defaultProps} />);

      expect(screen.queryByText('Test Connection')).not.toBeInTheDocument();
    });

    test('shows validation button when showValidation is true', () => {
      render(<LLMProviderInput {...defaultProps} showValidation={true} />);

      expect(screen.getByText('Test Connection')).toBeInTheDocument();
    });

    test('calls onValidate when test button is clicked', async () => {
      const onValidate = jest.fn().mockResolvedValue(true);
      render(
        <LLMProviderInput
          {...defaultProps}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      fireEvent.click(screen.getByText('Test Connection'));

      await waitFor(() => {
        expect(onValidate).toHaveBeenCalledWith(mockSimpleProvider);
      });
    });

    test('shows loading state during validation', async () => {
      const onValidate = jest.fn(() => new Promise(resolve => setTimeout(() => resolve(true), 100)));
      render(
        <LLMProviderInput
          {...defaultProps}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      fireEvent.click(screen.getByText('Test Connection'));

      expect(screen.getByText('Validating...')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText('Test Connection')).toBeInTheDocument();
      });
    });

    test('shows success message on valid provider', async () => {
      const onValidate = jest.fn().mockResolvedValue(true);
      render(
        <LLMProviderInput
          {...defaultProps}
          value={mockOllamaProvider}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      fireEvent.click(screen.getByText('Test Connection'));

      await waitFor(() => {
        expect(screen.getByText('✓')).toBeInTheDocument();
        expect(screen.getByText(/ollama provider is available/)).toBeInTheDocument();
      });
    });

    test('shows error message on invalid provider', async () => {
      const onValidate = jest.fn().mockResolvedValue(false);
      render(
        <LLMProviderInput
          {...defaultProps}
          value={mockOllamaProvider}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      fireEvent.click(screen.getByText('Test Connection'));

      await waitFor(() => {
        expect(screen.getByText('✗')).toBeInTheDocument();
        expect(screen.getByText(/ollama provider is not available/)).toBeInTheDocument();
      });
    });

    test('shows error message on validation exception', async () => {
      const onValidate = jest.fn().mockRejectedValue(new Error('Connection failed'));
      render(
        <LLMProviderInput
          {...defaultProps}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      fireEvent.click(screen.getByText('Test Connection'));

      await waitFor(() => {
        expect(screen.getByText(/Validation failed: Connection failed/)).toBeInTheDocument();
      });
    });

    test('handles non-Error exception in validation', async () => {
      const onValidate = jest.fn().mockRejectedValue('String error');
      render(
        <LLMProviderInput
          {...defaultProps}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      fireEvent.click(screen.getByText('Test Connection'));

      await waitFor(() => {
        expect(screen.getByText(/Validation failed: Unknown error/)).toBeInTheDocument();
      });
    });

    test('auto-validates after provider change', async () => {
      const onValidate = jest.fn().mockResolvedValue(true);
      render(
        <LLMProviderInput
          {...defaultProps}
          value={mockSimpleProvider}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      const select = screen.getByLabelText('Provider Type');
      fireEvent.change(select, { target: { value: 'ollama' } });

      await waitFor(() => {
        expect(onValidate).toHaveBeenCalled();
      }, { timeout: 1000 });
    });

    test('validation result has proper ARIA attributes', async () => {
      const onValidate = jest.fn().mockResolvedValue(true);
      render(
        <LLMProviderInput
          {...defaultProps}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      fireEvent.click(screen.getByText('Test Connection'));

      await waitFor(() => {
        const result = screen.getByRole('alert');
        expect(result).toHaveAttribute('aria-live', 'polite');
      });
    });

    test('applies correct CSS class for valid result', async () => {
      const onValidate = jest.fn().mockResolvedValue(true);
      const { container } = render(
        <LLMProviderInput
          {...defaultProps}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      fireEvent.click(screen.getByText('Test Connection'));

      await waitFor(() => {
        expect(container.querySelector('.validation-result.valid')).toBeInTheDocument();
      });
    });

    test('applies correct CSS class for invalid result', async () => {
      const onValidate = jest.fn().mockResolvedValue(false);
      const { container } = render(
        <LLMProviderInput
          {...defaultProps}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      fireEvent.click(screen.getByText('Test Connection'));

      await waitFor(() => {
        expect(container.querySelector('.validation-result.invalid')).toBeInTheDocument();
      });
    });
  });

  describe('Disabled State', () => {
    test('disables provider select when disabled prop is true', () => {
      render(<LLMProviderInput {...defaultProps} disabled={true} />);

      const select = screen.getByLabelText('Provider Type');
      expect(select).toBeDisabled();
    });

    test('disables model input when disabled prop is true', () => {
      render(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} disabled={true} />);

      const input = screen.getByLabelText('Model Name');
      expect(input).toBeDisabled();
    });

    test('disables validation button when disabled prop is true', () => {
      render(<LLMProviderInput {...defaultProps} showValidation={true} disabled={true} />);

      const button = screen.getByText('Test Connection');
      expect(button).toBeDisabled();
    });

    test('disables validation button during validation', async () => {
      const onValidate = jest.fn(() => new Promise(resolve => setTimeout(() => resolve(true), 100)));
      render(
        <LLMProviderInput
          {...defaultProps}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      const button = screen.getByText('Test Connection');
      fireEvent.click(button);

      expect(button).toBeDisabled();

      await waitFor(() => {
        expect(button).not.toBeDisabled();
      });
    });
  });

  describe('Custom Styling', () => {
    test('applies custom className', () => {
      const { container } = render(
        <LLMProviderInput {...defaultProps} className="custom-provider-input" />
      );

      expect(container.querySelector('.custom-provider-input')).toBeInTheDocument();
    });

    test('combines custom className with base class', () => {
      const { container } = render(
        <LLMProviderInput {...defaultProps} className="custom-class" />
      );

      expect(container.querySelector('.llm-provider-input.custom-class')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('handles onChange being called without onValidate', () => {
      render(<LLMProviderInput {...defaultProps} showValidation={true} />);

      const select = screen.getByLabelText('Provider Type');

      expect(() => {
        fireEvent.change(select, { target: { value: 'ollama' } });
      }).not.toThrow();
    });

    test('handles validation button click without onValidate', () => {
      render(<LLMProviderInput {...defaultProps} showValidation={true} />);

      expect(() => {
        fireEvent.click(screen.getByText('Test Connection'));
      }).not.toThrow();
    });

    test('handles empty model name gracefully', () => {
      const provider: LLMProvider = {
        provider_type: 'ollama',
        model_name: '',
      };

      render(<LLMProviderInput {...defaultProps} value={provider} />);

      const input = screen.getByLabelText('Model Name') as HTMLInputElement;
      expect(input.value).toBe('');
    });
  });

  describe('Integration Scenarios', () => {
    test('complete workflow: change provider, update model, validate', async () => {
      const onChange = jest.fn();
      const onValidate = jest.fn().mockResolvedValue(true);

      const { rerender, unmount } = render(
        <LLMProviderInput
          {...defaultProps}
          onChange={onChange}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      // Change provider
      const select = screen.getByLabelText('Provider Type');
      fireEvent.change(select, { target: { value: 'ollama' } });
      expect(onChange).toHaveBeenCalledWith({
        provider_type: 'ollama',
        model_name: 'qwen2.5:32b',
      });

      // Update component with new value
      rerender(
        <LLMProviderInput
          value={mockOllamaProvider}
          onChange={onChange}
          showValidation={true}
          onValidate={onValidate}
        />
      );

      // Change model
      const input = screen.getByLabelText('Model Name');
      fireEvent.change(input, { target: { value: 'llama2' } });
      expect(onChange).toHaveBeenCalledWith({
        provider_type: 'ollama',
        model_name: 'llama2',
      });

      // Validate - use getAllByText and select first button to handle multiple matches
      const buttons = screen.getAllByText('Test Connection');
      fireEvent.click(buttons[0]);
      await waitFor(() => {
        expect(onValidate).toHaveBeenCalled();
        expect(screen.getByText('✓')).toBeInTheDocument();
      });
    });

    test('switching between providers updates UI correctly', () => {
      const { rerender } = render(<LLMProviderInput {...defaultProps} value={mockSimpleProvider} />);

      expect(screen.queryByLabelText('Model Name')).not.toBeInTheDocument();
      expect(screen.getByText(/Fast rule-based/)).toBeInTheDocument();

      rerender(<LLMProviderInput {...defaultProps} value={mockOllamaProvider} />);

      expect(screen.getByLabelText('Model Name')).toBeInTheDocument();
      expect(screen.getByText(/Local AI models/)).toBeInTheDocument();

      rerender(<LLMProviderInput {...defaultProps} value={mockOpenAIProvider} />);

      expect(screen.getByLabelText('Model Name')).toBeInTheDocument();
      expect(screen.getByText(/Advanced AI models/)).toBeInTheDocument();
    });
  });
});
