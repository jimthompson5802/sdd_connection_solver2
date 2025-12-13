import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ImagePuzzleSetup } from './ImagePuzzleSetup';

// Mock the api service
const mockSetupPuzzleFromImage = jest.fn(() => Promise.resolve({
  status: 'success',
  remaining_words: ['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8', 'word9', 'word10', 'word11', 'word12', 'word13', 'word14', 'word15', 'word16']
}));

jest.mock('../services/api', () => ({
  setupPuzzleFromImage: mockSetupPuzzleFromImage
}));

describe('ImagePuzzleSetup - Provider/Model Configuration', () => {
  const baseProviders = [
    { type: 'openai', name: 'OpenAI' },
    { type: 'ollama', name: 'Ollama' },
    { type: 'simple', name: 'Simple Provider' }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    global.URL.createObjectURL = jest.fn(() => 'blob:fake-url');
    global.URL.revokeObjectURL = jest.fn();
  });

  describe('Provider Dropdown Population', () => {
    test('populates provider dropdown from props', () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: baseProviders,
        defaultProvider: { type: 'openai', name: 'OpenAI' },
        defaultModel: 'gpt-4-vision-preview',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      const providerSelect = screen.getByLabelText('LLM Provider');
      expect(providerSelect).toBeInTheDocument();
      
      // Check all providers are in the dropdown
      expect(screen.getByDisplayValue('OpenAI')).toBeInTheDocument();
      expect(screen.getByText('Ollama')).toBeInTheDocument();
      expect(screen.getByText('Simple Provider')).toBeInTheDocument();
    });

    test('handles empty providers list gracefully', () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: [],
        defaultProvider: { type: 'openai', name: 'OpenAI' },
        defaultModel: 'gpt-4-vision-preview',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      const providerSelect = screen.getByLabelText('LLM Provider');
      expect(providerSelect).toBeInTheDocument();
      
      // Should not crash and should still render the select element
      expect(providerSelect.children.length).toBe(0);
    });
  });

  describe('Default Provider Selection', () => {
    test('sets default provider from props', () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: baseProviders,
        defaultProvider: { type: 'ollama', name: 'Ollama' },
        defaultModel: 'llava:latest',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      const providerSelect = screen.getByLabelText('LLM Provider') as HTMLSelectElement;
      expect(providerSelect.value).toBe('ollama');
    });

    test('falls back gracefully if default provider not in list', () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: [{ type: 'openai', name: 'OpenAI' }],
        defaultProvider: { type: 'missing', name: 'Missing Provider' },
        defaultModel: 'some-model',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      const providerSelect = screen.getByLabelText('LLM Provider') as HTMLSelectElement;
      // Should fall back to first available provider
      expect(providerSelect.value).toBe('openai');
    });
  });

  describe('Model Dropdown Dynamic Population', () => {
    test('populates different models based on selected provider', async () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: baseProviders,
        defaultProvider: { type: 'openai', name: 'OpenAI' },
        defaultModel: 'gpt-4-vision-preview',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      const providerSelect = screen.getByLabelText('LLM Provider');
      const modelSelect = screen.getByLabelText('LLM Model');
      
      // Initial state - OpenAI models should be shown
      expect(screen.getByDisplayValue('GPT-4 Vision Preview')).toBeInTheDocument();
      
      // Change to Ollama provider
      fireEvent.change(providerSelect, { target: { value: 'ollama' } });
      
      await waitFor(() => {
        // Should now show Ollama models
        expect(screen.getByText('llava:latest')).toBeInTheDocument();
        expect(screen.getByText('llava:13b')).toBeInTheDocument();
        expect(screen.getByText('llava:34b')).toBeInTheDocument();
      });
    });

    test('updates model selection when provider changes', async () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: baseProviders,
        defaultProvider: { type: 'openai', name: 'OpenAI' },
        defaultModel: 'gpt-4-vision-preview',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      const providerSelect = screen.getByLabelText('LLM Provider');
      const modelSelect = screen.getByLabelText('LLM Model') as HTMLSelectElement;
      
      // Initial model value
      expect(modelSelect.value).toBe('gpt-4-vision-preview');
      
      // Change provider
      fireEvent.change(providerSelect, { target: { value: 'simple' } });
      
      await waitFor(() => {
        // Should reset to first model of new provider
        expect(modelSelect.value).toBe('simple-model');
      });
    });
  });

  describe('Default Model Selection', () => {
    test('sets default model from props when provider matches', () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: baseProviders,
        defaultProvider: { type: 'openai', name: 'OpenAI' },
        defaultModel: 'gpt-4o',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      const modelSelect = screen.getByLabelText('LLM Model') as HTMLSelectElement;
      expect(modelSelect.value).toBe('gpt-4o');
    });

    test('falls back to first model when default not available for provider', async () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: baseProviders,
        defaultProvider: { type: 'ollama', name: 'Ollama' },
        defaultModel: 'nonexistent-model',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      const modelSelect = screen.getByLabelText('LLM Model') as HTMLSelectElement;
      
      await waitFor(() => {
        // Should fall back to first available Ollama model
        expect(modelSelect.value).toBe('llava:latest');
      });
    });
  });

  describe('Model Availability by Provider', () => {
    test('shows correct models for OpenAI provider', () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: [{ type: 'openai', name: 'OpenAI' }],
        defaultProvider: { type: 'openai', name: 'OpenAI' },
        defaultModel: 'gpt-4-vision-preview',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      // Should show OpenAI vision models
      expect(screen.getByText('GPT-4 Vision Preview')).toBeInTheDocument();
      expect(screen.getByText('GPT-4 Turbo')).toBeInTheDocument();
      expect(screen.getByText('GPT-4o')).toBeInTheDocument();
    });

    test('shows correct models for Ollama provider', async () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: [{ type: 'ollama', name: 'Ollama' }],
        defaultProvider: { type: 'ollama', name: 'Ollama' },
        defaultModel: 'llava:latest',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      await waitFor(() => {
        // Should show Ollama vision models
        expect(screen.getByText('llava:latest')).toBeInTheDocument();
        expect(screen.getByText('llava:13b')).toBeInTheDocument();
        expect(screen.getByText('llava:34b')).toBeInTheDocument();
      });
    });

    test('shows correct models for Simple provider', async () => {
      const props = {
        onImageSetup: jest.fn(),
        providers: [{ type: 'simple', name: 'Simple Provider' }],
        defaultProvider: { type: 'simple', name: 'Simple Provider' },
        defaultModel: 'simple-model',
        onError: jest.fn()
      };

      render(<ImagePuzzleSetup {...props} />);
      
      await waitFor(() => {
        // Should show Simple provider model
        expect(screen.getByText('Simple Model')).toBeInTheDocument();
      });
    });
  });
});