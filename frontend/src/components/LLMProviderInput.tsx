/**
 * LLM Provider Input Component
 * Allows users to select and configure LLM providers for recommendations.
 */

import React, { useState, useEffect, useCallback } from 'react';
import type { LLMProvider, LLMProviderType } from '../types/llm-provider';
import './LLMProviderInput.css';

export interface LLMProviderInputProps {
  value: LLMProvider;
  onChange: (provider: LLMProvider) => void;
  disabled?: boolean;
  showValidation?: boolean;
  onValidate?: (provider: LLMProvider) => Promise<boolean>;
  className?: string;
}

export interface LLMProviderInputState {
  isValidating: boolean;
  validationResult?: {
    isValid: boolean;
    message: string;
  };
}

export const LLMProviderInput: React.FC<LLMProviderInputProps> = ({
  value,
  onChange,
  disabled = false,
  showValidation = false,
  onValidate,
  className = ''
}) => {
  const [state, setState] = useState<LLMProviderInputState>({
    isValidating: false
  });

  const providerOptions: Array<{ value: LLMProviderType; label: string; description: string }> = [
    { 
      value: 'simple', 
      label: 'Simple (Rule-based)', 
      description: 'Fast rule-based recommendations using pattern matching' 
    },
    { 
      value: 'ollama', 
      label: 'Ollama (Local AI)', 
      description: 'Local AI models running on your machine' 
    },
    { 
      value: 'openai', 
      label: 'OpenAI (Cloud AI)', 
      description: 'Advanced AI models from OpenAI (requires API key)' 
    }
  ];

  const handleProviderTypeChange = (newProviderType: LLMProviderType) => {
    const newProvider: LLMProvider = {
      provider_type: newProviderType,
      model_name: getDefaultModelName(newProviderType)
    };
    
    onChange(newProvider);
    
    // Clear previous validation
    setState(prev => ({ ...prev, validationResult: undefined }));
  };

  const handleModelNameChange = (newModelName: string) => {
    const newProvider: LLMProvider = {
      ...value,
      model_name: newModelName || null
    };
    
    onChange(newProvider);
  };

  const getDefaultModelName = (providerType: LLMProviderType): string | null => {
    switch (providerType) {
      case 'simple':
        return null;
      case 'ollama':
        return 'llama2';
      case 'openai':
        return 'gpt-3.5-turbo';
      default:
        return null;
    }
  };

  const validateProvider = useCallback(async () => {
    if (!onValidate) return;

    setState(prev => ({ ...prev, isValidating: true }));

    try {
      const isValid = await onValidate(value);
      setState(prev => ({
        ...prev,
        isValidating: false,
        validationResult: {
          isValid,
          message: isValid
            ? `${value.provider_type} provider is available`
            : `${value.provider_type} provider is not available`
        }
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isValidating: false,
        validationResult: {
          isValid: false,
          message: `Validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`
        }
      }));
    }
  }, [onValidate, value]);

  useEffect(() => {
    // Auto-validate when provider changes (if validation is enabled)
    if (showValidation && onValidate && !state.isValidating) {
      const timeoutId = setTimeout(validateProvider, 500);
      return () => clearTimeout(timeoutId);
    }
  }, [value, showValidation, onValidate, state.isValidating, validateProvider]);

  const selectedOption = providerOptions.find(opt => opt.value === value.provider_type);
  const requiresModelName = value.provider_type !== 'simple';

  return (
    <div className={`llm-provider-input ${className}`}>
      <div className="provider-selection">
        <label htmlFor="provider-type" className="provider-label">
          Provider Type
        </label>
        <select
          id="provider-type"
          value={value.provider_type}
          onChange={(e) => handleProviderTypeChange(e.target.value as LLMProviderType)}
          disabled={disabled}
          className="provider-select"
          aria-describedby="provider-description"
        >
          {providerOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        
        {selectedOption && (
          <p id="provider-description" className="provider-description">
            {selectedOption.description}
          </p>
        )}
      </div>

      {requiresModelName && (
        <div className="model-selection">
          <label htmlFor="model-name" className="model-label">
            Model Name
          </label>
          <input
            id="model-name"
            type="text"
            value={value.model_name || ''}
            onChange={(e) => handleModelNameChange(e.target.value)}
            disabled={disabled}
            className="model-input"
            placeholder={`Default: ${getDefaultModelName(value.provider_type)}`}
            aria-describedby="model-description"
          />
          <p id="model-description" className="model-description">
            {value.provider_type === 'ollama' && 
              'Enter the name of an Ollama model (e.g., llama2, codellama, mistral)'}
            {value.provider_type === 'openai' && 
              'Enter an OpenAI model name (e.g., gpt-3.5-turbo, gpt-4)'}
          </p>
        </div>
      )}

      {showValidation && (
        <div className="validation-section">
          <button
            type="button"
            onClick={validateProvider}
            disabled={disabled || state.isValidating}
            className="validate-button"
          >
            {state.isValidating ? 'Validating...' : 'Test Connection'}
          </button>
          
          {state.validationResult && (
            <div 
              className={`validation-result ${state.validationResult.isValid ? 'valid' : 'invalid'}`}
              role="alert"
              aria-live="polite"
            >
              <span className="validation-icon">
                {state.validationResult.isValid ? '✓' : '✗'}
              </span>
              <span className="validation-message">
                {state.validationResult.message}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LLMProviderInput;