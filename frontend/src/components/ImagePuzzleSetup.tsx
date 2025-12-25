import React, { useState, useCallback } from 'react';
import { ImageSetupRequest, ImagePasteState } from '../types/puzzle';
import { LLMProviderOption } from '../types/llm-provider';
import './ImagePuzzleSetup.css';

export interface ImagePuzzleSetupProps {
  onImageSetup: (words: string[], sessionId?: string) => void;    // Callback with extracted words and optional session_id
  providers: LLMProviderOption[];              // Available LLM providers
  defaultProvider: LLMProviderOption;          // Default provider selection
  defaultModel: string;                        // Default model selection
  onError: (error: string) => void;            // Error callback
}

// Model mappings by provider type
const PROVIDER_MODELS: Record<string, { value: string; label: string }[]> = {
  openai: [
    { value: 'gpt-4-vision-preview', label: 'GPT-4 Vision Preview' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
    { value: 'gpt-4o', label: 'GPT-4o' }
  ],
  ollama: [
    { value: 'llava:latest', label: 'llava:latest' },
    { value: 'llava:13b', label: 'llava:13b' },
    { value: 'llava:34b', label: 'llava:34b' },
    { value: 'llava', label: 'LLaVA' },
    { value: 'bakllava', label: 'BakLLaVA' },
    { value: 'llava-llama3', label: 'LLaVA Llama3' }
  ],
  simple: [
    { value: 'simple-model', label: 'Simple Model' }
  ]
};

export const ImagePuzzleSetup: React.FC<ImagePuzzleSetupProps> = ({
  onImageSetup,
  providers,
  defaultProvider,
  defaultModel,
  onError
}) => {
  // Get the initial provider - use default if available, otherwise first in list
  const getInitialProvider = (): string => {
    const providerExists = providers.some(p => p.type === defaultProvider.type);
    return providerExists ? defaultProvider.type : (providers[0]?.type || 'openai');
  };

  // Get the initial model for a provider
  const getInitialModel = (providerType: string): string => {
    const availableModels = PROVIDER_MODELS[providerType] || [];

    // If default model is available for this provider, use it
    const modelExists = availableModels.some(m => m.value === defaultModel);
    if (modelExists) {
      return defaultModel;
    }

    // Otherwise use first available model for this provider
    return availableModels[0]?.value || 'gpt-4-vision-preview';
  };

  const initialProvider = getInitialProvider();
  const initialModel = getInitialModel(initialProvider);

  // Image paste state
  const [imageState, setImageState] = useState<ImagePasteState>({
    imageData: null,
    imageMime: null,
    previewUrl: null,
    sizeBytes: 0,
    isValid: false,
    error: null
  });

  // Provider/model selection state
  const [selectedProvider, setSelectedProvider] = useState<string>(initialProvider);
  const [selectedModel, setSelectedModel] = useState<string>(initialModel);

  // Loading state
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Error state
  const [extractionError, setExtractionError] = useState<string | null>(null);

  // Handle paste events
  const handlePaste = useCallback(async (event: React.ClipboardEvent) => {
    event.preventDefault();
    setExtractionError(null);

    try {
      // Access clipboard data
      const clipboardData = event.clipboardData;
      if (!clipboardData) {
        setImageState(prev => ({ ...prev, error: 'No clipboard data available' }));
        return;
      }

      // Look for image data in clipboard
      let imageFile: File | null = null;

      // Check clipboard items for images
      const items = Array.from(clipboardData.items);
      for (const item of items) {
        if (item.kind === 'file' && item.type.startsWith('image/')) {
          imageFile = item.getAsFile();
          break;
        }
      }

      if (!imageFile) {
        setImageState(prev => ({
          ...prev,
          error: 'Please paste a valid image',
          isValid: false
        }));
        return;
      }

      // Validate file size (5MB limit)
      const maxSize = 5 * 1024 * 1024; // 5MB in bytes
      if (imageFile.size > maxSize) {
        setImageState(prev => ({
          ...prev,
          error: 'Image too large (max 5MB)',
          isValid: false
        }));
        return;
      }

      // Validate MIME type
      const supportedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
      if (!supportedTypes.includes(imageFile.type)) {
        setImageState(prev => ({
          ...prev,
          error: `Unsupported image format. Supported: ${supportedTypes.join(', ')}`,
          isValid: false
        }));
        return;
      }

      // Convert to base64
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        if (result) {
          // Extract base64 data (remove data URL prefix)
          const base64Data = result.split(',')[1];

          // Create object URL for preview
          const previewUrl = URL.createObjectURL(imageFile!);

          setImageState({
            imageData: base64Data,
            imageMime: imageFile!.type,
            previewUrl: previewUrl,
            sizeBytes: imageFile!.size,
            isValid: true,
            error: null
          });
        }
      };

      reader.onerror = () => {
        setImageState(prev => ({
          ...prev,
          error: 'Failed to read image file',
          isValid: false
        }));
      };

      reader.readAsDataURL(imageFile);

    } catch (error) {
      console.error('Paste handling error:', error);
      setImageState(prev => ({
        ...prev,
        error: 'Failed to process pasted image',
        isValid: false
      }));
    }
  }, []);

  // Handle provider change
  const handleProviderChange = useCallback((newProvider: string) => {
    setSelectedProvider(newProvider);

    // Update model to first available for new provider
    const availableModels = PROVIDER_MODELS[newProvider] || [];
    const firstModel = availableModels[0]?.value || 'gpt-4-vision-preview';
    setSelectedModel(firstModel);
  }, []);

  // Handle setup puzzle button click
  const handleSetupPuzzle = useCallback(async () => {
    if (!imageState.isValid || !imageState.imageData || !imageState.imageMime) {
      return;
    }

    setIsLoading(true);
    setExtractionError(null);

    try {
      // Import API service dynamically to avoid circular dependencies
      const { apiService } = await import('../services/api');

      // Prepare request
      const request: ImageSetupRequest = {
        image_base64: imageState.imageData,
        image_mime: imageState.imageMime,
        provider_type: selectedProvider,
        model_name: selectedModel
      };

      // Call API
      const response = await apiService.setupPuzzleFromImage(request);

      if (response.status === 'success') {
        // Success - call callback with extracted words and optional session_id
        onImageSetup(response.remaining_words, response.session_id);
      } else {
        // API returned error status
        const errorMsg = response.message || 'Failed to extract words from image';
        setExtractionError(errorMsg);
        onError(errorMsg);
      }

    } catch (error) {
      console.error('Setup puzzle error:', error);
      let errorMsg = 'LLM unable to extract puzzle words';

      if (error instanceof Error) {
        // Extract meaningful error from backend
        if (error.message.includes('No valid 4x4 word grid detected')) {
          errorMsg = 'No puzzle grid detected in this image. Please paste an image showing a 4x4 grid of words from a NYT Connections puzzle.';
        } else if (error.message.includes('Unable to extract puzzle from image')) {
          errorMsg = 'The image does not contain a valid 4x4 word grid. Please paste an image of a NYT Connections puzzle.';
        } else if (error.message.includes('not contain readable text')) {
          errorMsg = 'Unable to read text from image. Please ensure the image is clear and contains visible words.';
        } else if (error.message.includes('appears to be sentences')) {
          errorMsg = 'The image contains sentences instead of a word grid. Please paste a puzzle image with a 4x4 grid of words.';
        } else if (error.message.includes('Too many repeated words')) {
          errorMsg = 'The image does not appear to contain a valid puzzle grid. Please paste a NYT Connections puzzle image.';
        } else {
          errorMsg = error.message;
        }
      }

      setExtractionError(errorMsg);
      onError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [imageState, selectedProvider, selectedModel, onImageSetup, onError]);

  // Clean up object URLs when component unmounts or image changes
  React.useEffect(() => {
    return () => {
      if (imageState.previewUrl) {
        URL.revokeObjectURL(imageState.previewUrl);
      }
    };
  }, [imageState.previewUrl]);

  return (
    <div className="image-puzzle-setup">
      <h2>Setup Puzzle from Image</h2>

      {/* Image paste area */}
      <div
        className={`paste-area ${imageState.imageData ? 'has-image' : ''}`}
        data-testid="image-paste-area"
        onPaste={handlePaste}
        tabIndex={0}
      >
        {!imageState.imageData ? (
          <div className="paste-placeholder">
            <div className="paste-icon">📋</div>
            <p className="paste-text">Paste image here</p>
            <p className="paste-hint">
              Press <kbd>Cmd+V</kbd> (Mac) or <kbd>Ctrl+V</kbd> (Windows/Linux)
            </p>
          </div>
        ) : (
          <div className="image-preview">
            <img
              src={imageState.previewUrl || ''}
              alt="Pasted preview"
              className="preview-image"
            />
            <div className="image-info">
              <p>Size: {Math.round(imageState.sizeBytes / 1024)}KB</p>
              <p>Format: {imageState.imageMime}</p>
            </div>
          </div>
        )}
      </div>

      {/* Error display */}
      {imageState.error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {imageState.error}
        </div>
      )}

      {extractionError && (
        <div className="error-message">
          <span className="error-icon">🤖</span>
          {extractionError}
        </div>
      )}

      {/* Provider and model selection */}
      <div className="provider-selection">
        <div className="form-row">
          <div className="form-field">
            <label htmlFor="provider-select">Provider:</label>
            <select
              id="provider-select"
              value={selectedProvider}
              onChange={(e) => handleProviderChange(e.target.value)}
              aria-label="LLM Provider"
            >
              {providers.map(provider => (
                <option key={provider.type} value={provider.type}>
                  {provider.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="model-select">Model:</label>
            <select
              id="model-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              aria-label="LLM Model"
            >
              {(PROVIDER_MODELS[selectedProvider] || []).map(model => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Setup puzzle button */}
      <div className="setup-actions">
        <button
          className="setup-button"
          onClick={handleSetupPuzzle}
          disabled={!imageState.isValid || isLoading}
          aria-label="Setup Puzzle"
        >
          {isLoading ? (
            <>
              <span className="loading-spinner">⏳</span>
              Extracting words...
            </>
          ) : (
            'Setup Puzzle'
          )}
        </button>
      </div>
    </div>
  );
};