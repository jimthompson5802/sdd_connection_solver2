/**
 * Component Contracts: Image-Based Puzzle Setup
 * 
 * Feature: 004-image-puzzle-setup
 * Component: ImagePuzzleSetup
 * 
 * This file defines TypeScript interfaces for component props and internal state,
 * ensuring type safety and clear contracts between components.
 */

// ============================================================================
// Component Props
// ============================================================================

/**
 * Props for ImagePuzzleSetup component
 * 
 * Main component for image-based puzzle setup workflow. Handles:
 * - Image paste from clipboard
 * - Image preview
 * - Provider/model selection
 * - API call to extract words
 * - Error handling and retry
 * 
 * @example Usage in App.tsx
 * ```typescript
 * {currentView === 'image-setup' && (
 *   <ImagePuzzleSetup
 *     onImageSetup={handleImageSetup}
 *     providers={availableProviders}
 *     defaultProvider={selectedProvider}
 *     defaultModel={selectedModel}
 *     onError={handleError}
 *   />
 * )}
 * ```
 */
export interface ImagePuzzleSetupProps {
  /**
   * Callback invoked when puzzle setup succeeds
   * 
   * Receives array of 16 extracted words from image.
   * Parent component (App.tsx) should:
   * - Create puzzle session with words
   * - Switch to puzzle-active view
   * - Initialize EnhancedPuzzleInterface
   * 
   * @param words - Array of exactly 16 extracted words (lowercase)
   * 
   * @example
   * ```typescript
   * const handleImageSetup = (words: string[]) => {
   *   setRemainingWords(words);
   *   setCurrentView('puzzle-active');
   * };
   * ```
   */
  onImageSetup: (words: string[]) => void;

  /**
   * Available LLM providers for word extraction
   * 
   * Passed from App state (same providers used for puzzle solving).
   * Used to populate provider dropdown.
   * 
   * Must contain at least one provider with vision capability.
   * Simple provider can be included but will return error if selected.
   * 
   * @example
   * ```typescript
   * const providers: LLMProviderType[] = [
   *   { type: 'openai', displayName: 'OpenAI', models: ['gpt-4-vision-preview'] },
   *   { type: 'ollama', displayName: 'Ollama', models: ['llava', 'bakllava'] }
   * ];
   * ```
   */
  providers: LLMProviderType[];

  /**
   * Default provider selection
   * 
   * From App state (user's last selected provider or first available).
   * Used to pre-populate provider dropdown.
   * 
   * Must exist in providers array.
   */
  defaultProvider: LLMProviderType;

  /**
   * Default model name for selected provider
   * 
   * From App state (user's last selected model or first available for provider).
   * Used to pre-populate model dropdown.
   * 
   * Must exist in defaultProvider.models array.
   */
  defaultModel: string;

  /**
   * Error callback for displaying errors
   * 
   * Invoked when:
   * - Image validation fails (size, format)
   * - API request fails (network error)
   * - LLM extraction fails (wrong word count, model no vision)
   * 
   * Parent component should display error to user and allow retry.
   * 
   * @param error - User-friendly error message
   * 
   * @example
   * ```typescript
   * const handleError = (error: string) => {
   *   setErrorMessage(error);
   *   setShowErrorToast(true);
   * };
   * ```
   */
  onError: (error: string) => void;
}

/**
 * LLM Provider configuration
 * 
 * Existing type from frontend/src/types/puzzle.ts
 * Included here for reference and type completeness.
 */
export interface LLMProviderType {
  /** Provider identifier (openai, ollama, simple) */
  type: string;

  /** Available models for this provider */
  models: string[];

  /** Display name for UI */
  displayName: string;
}

// ============================================================================
// Component State
// ============================================================================

/**
 * Internal state for ImagePuzzleSetup component
 * 
 * Tracks pasted image data, validation status, and UI state.
 * Not exposed to parent component.
 * 
 * @example State initialization
 * ```typescript
 * const [imageState, setImageState] = useState<ImagePasteState>({
 *   imageData: null,
 *   imageMime: null,
 *   previewUrl: null,
 *   sizeBytes: 0,
 *   isValid: false,
 *   error: null
 * });
 * ```
 */
export interface ImagePasteState {
  /**
   * Base64-encoded image data (for API request)
   * 
   * Generated from Clipboard API Blob via FileReader.
   * Excludes data URL prefix (e.g., "data:image/png;base64,")
   * 
   * null when no image pasted yet.
   */
  imageData: string | null;

  /**
   * Image MIME type
   * 
   * Extracted from Clipboard API Blob.type
   * 
   * Examples: "image/png", "image/jpeg", "image/gif"
   * null when no image pasted yet.
   */
  imageMime: string | null;

  /**
   * Object URL for preview rendering
   * 
   * Created via URL.createObjectURL(blob) for <img> src attribute.
   * Must be revoked when component unmounts or new image pasted.
   * 
   * null when no image pasted yet.
   */
  previewUrl: string | null;

  /**
   * Image size in bytes (original, before base64 encoding)
   * 
   * Used for validation (must be <= 5MB)
   * Extracted from Clipboard API Blob.size
   * 
   * 0 when no image pasted yet.
   */
  sizeBytes: number;

  /**
   * Validation state
   * 
   * true if image meets all requirements:
   * - Size <= 5MB
   * - MIME type supported
   * - Base64 data present
   * 
   * Drives "Setup Puzzle" button enabled state.
   */
  isValid: boolean;

  /**
   * Validation error message
   * 
   * null when image is valid or no image pasted yet.
   * Contains user-friendly error message when validation fails.
   * 
   * Example errors:
   * - "Image too large (max 5MB)"
   * - "Unsupported format: image/bmp"
   * - "No image data found"
   */
  error: string | null;
}

/**
 * UI loading state during API call
 * 
 * Tracks async operations for loading indicators and button states.
 * 
 * @example State initialization
 * ```typescript
 * const [loadingState, setLoadingState] = useState<LoadingState>({
 *   isLoading: false,
 *   statusMessage: null
 * });
 * ```
 */
export interface LoadingState {
  /**
   * Whether API call is in progress
   * 
   * true during setupPuzzleFromImage() call.
   * Used to:
   * - Show loading spinner
   * - Disable "Setup Puzzle" button
   * - Show status message
   */
  isLoading: boolean;

  /**
   * Status message during loading
   * 
   * Examples:
   * - "Extracting words from image..."
   * - "Processing with OpenAI GPT-4 Vision..."
   * - "Contacting LLM provider..."
   * 
   * null when not loading.
   */
  statusMessage: string | null;
}

/**
 * Provider/Model selection state
 * 
 * Tracks user's selected provider and model for word extraction.
 * 
 * @example State initialization
 * ```typescript
 * const [selection, setSelection] = useState<ProviderSelectionState>({
 *   selectedProvider: props.defaultProvider,
 *   selectedModel: props.defaultModel
 * });
 * ```
 */
export interface ProviderSelectionState {
  /**
   * Currently selected provider
   * 
   * Updated when user changes provider dropdown.
   * When provider changes, selectedModel should reset to first model in new provider's models array.
   */
  selectedProvider: LLMProviderType;

  /**
   * Currently selected model name
   * 
   * Updated when user changes model dropdown.
   * Must exist in selectedProvider.models array.
   */
  selectedModel: string;
}

// ============================================================================
// Event Handlers
// ============================================================================

/**
 * Paste event handler type
 * 
 * Attached to document or component for clipboard paste detection.
 * 
 * @example
 * ```typescript
 * const handlePaste: PasteEventHandler = async (event) => {
 *   event.preventDefault();
 *   
 *   const items = event.clipboardData?.items;
 *   if (!items) return;
 *   
 *   for (const item of items) {
 *     if (item.type.startsWith('image/')) {
 *       const blob = item.getAsFile();
 *       if (blob) {
 *         await processImage(blob);
 *       }
 *     }
 *   }
 * };
 * 
 * useEffect(() => {
 *   document.addEventListener('paste', handlePaste);
 *   return () => document.removeEventListener('paste', handlePaste);
 * }, []);
 * ```
 */
export type PasteEventHandler = (event: ClipboardEvent) => void | Promise<void>;

/**
 * Provider change handler type
 * 
 * Invoked when user selects different provider from dropdown.
 * 
 * @example
 * ```typescript
 * const handleProviderChange: ProviderChangeHandler = (provider) => {
 *   setSelection({
 *     selectedProvider: provider,
 *     selectedModel: provider.models[0]  // Reset to first model
 *   });
 * };
 * ```
 */
export type ProviderChangeHandler = (provider: LLMProviderType) => void;

/**
 * Model change handler type
 * 
 * Invoked when user selects different model from dropdown.
 * 
 * @example
 * ```typescript
 * const handleModelChange: ModelChangeHandler = (modelName) => {
 *   setSelection(prev => ({
 *     ...prev,
 *     selectedModel: modelName
 *   }));
 * };
 * ```
 */
export type ModelChangeHandler = (modelName: string) => void;

/**
 * Setup button click handler type
 * 
 * Invoked when user clicks "Setup Puzzle" button.
 * Should validate state, call API, and handle response.
 * 
 * @example
 * ```typescript
 * const handleSetupClick: SetupClickHandler = async () => {
 *   if (!imageState.isValid || !imageState.imageData || !imageState.imageMime) {
 *     onError('Please paste an image first');
 *     return;
 *   }
 *   
 *   setLoadingState({ isLoading: true, statusMessage: 'Extracting words...' });
 *   
 *   try {
 *     const response = await api.setupPuzzleFromImage(
 *       imageState.imageData,
 *       imageState.imageMime,
 *       selection.selectedProvider.type,
 *       selection.selectedModel
 *     );
 *     
 *     if (response.status === 'success') {
 *       onImageSetup(response.remaining_words);
 *     } else {
 *       onError(response.message || 'Setup failed');
 *     }
 *   } catch (error) {
 *     onError(error.message || 'Network error');
 *   } finally {
 *     setLoadingState({ isLoading: false, statusMessage: null });
 *   }
 * };
 * ```
 */
export type SetupClickHandler = () => void | Promise<void>;

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Image processing result
 * 
 * Returned by processImage() helper function after extracting data from Clipboard API Blob.
 */
export interface ImageProcessingResult {
  /** Base64-encoded image data (without data URL prefix) */
  imageData: string;

  /** Image MIME type from blob.type */
  imageMime: string;

  /** Object URL for preview (from URL.createObjectURL) */
  previewUrl: string;

  /** Image size in bytes from blob.size */
  sizeBytes: number;
}

/**
 * Process Clipboard API Blob to extract image data
 * 
 * @example
 * ```typescript
 * async function processImage(blob: Blob): Promise<ImageProcessingResult> {
 *   const imageData = await blobToBase64(blob);
 *   const previewUrl = URL.createObjectURL(blob);
 *   
 *   return {
 *     imageData,
 *     imageMime: blob.type,
 *     previewUrl,
 *     sizeBytes: blob.size
 *   };
 * }
 * ```
 */
export type ProcessImageFunction = (blob: Blob) => Promise<ImageProcessingResult>;

/**
 * Convert Blob to base64 string
 * 
 * @example
 * ```typescript
 * async function blobToBase64(blob: Blob): Promise<string> {
 *   return new Promise((resolve, reject) => {
 *     const reader = new FileReader();
 *     reader.onloadend = () => {
 *       const dataUrl = reader.result as string;
 *       // Remove "data:image/png;base64," prefix
 *       const base64 = dataUrl.split(',')[1];
 *       resolve(base64);
 *     };
 *     reader.onerror = reject;
 *     reader.readAsDataURL(blob);
 *   });
 * }
 * ```
 */
export type BlobToBase64Function = (blob: Blob) => Promise<string>;

// ============================================================================
// Validation Functions
// ============================================================================

/**
 * Client-side image validation result
 * 
 * Returned by validateImage() function.
 */
export interface ImageValidationResult {
  /** Whether image passes all validation checks */
  isValid: boolean;

  /** Error message if validation fails */
  error: string | null;
}

/**
 * Validate image before enabling "Setup Puzzle" button
 * 
 * @example
 * ```typescript
 * function validateImage(
 *   sizeBytes: number,
 *   imageMime: string,
 *   imageData: string | null
 * ): ImageValidationResult {
 *   // Size check
 *   if (sizeBytes > 5_242_880) {
 *     return { isValid: false, error: 'Image too large (max 5MB)' };
 *   }
 *   
 *   // MIME type check
 *   const supported = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
 *   if (!supported.includes(imageMime)) {
 *     return { isValid: false, error: `Unsupported format: ${imageMime}` };
 *   }
 *   
 *   // Data presence check
 *   if (!imageData || imageData.trim() === '') {
 *     return { isValid: false, error: 'No image data' };
 *   }
 *   
 *   return { isValid: true, error: null };
 * }
 * ```
 */
export type ValidateImageFunction = (
  sizeBytes: number,
  imageMime: string,
  imageData: string | null
) => ImageValidationResult;

// ============================================================================
// Component Layout Structure
// ============================================================================

/**
 * Component layout structure (for implementation reference)
 * 
 * Describes the visual structure of ImagePuzzleSetup component.
 * Matches ASCII diagram from spec.md.
 */
export interface ComponentLayout {
  /** Main container with instructions and paste area */
  container: {
    /** Heading: "Setup Puzzle from Image" */
    heading: string;

    /** Instruction text: "Paste an image of a 4x4 word grid (CMD+V / CTRL+V)" */
    instructions: string;

    /** Paste target area (full component) */
    pasteArea: {
      /** Image preview (shown when image pasted) */
      preview: {
        /** <img> element with src={previewUrl} */
        imageElement: HTMLImageElement;

        /** Image metadata: size, dimensions */
        metadata: string;
      } | null;

      /** Placeholder (shown when no image pasted) */
      placeholder: {
        /** Icon: camera or image icon */
        icon: string;

        /** Text: "Paste image here" */
        text: string;
      } | null;
    };

    /** Error message display (shown when validation fails) */
    errorDisplay: {
      /** Error icon */
      icon: string;

      /** Error message text */
      message: string;
    } | null;

    /** Provider and model selection */
    selectionControls: {
      /** Provider dropdown */
      providerDropdown: {
        label: 'Provider';
        options: LLMProviderType[];
        value: LLMProviderType;
        onChange: ProviderChangeHandler;
      };

      /** Model dropdown */
      modelDropdown: {
        label: 'Model';
        options: string[];
        value: string;
        onChange: ModelChangeHandler;
      };
    };

    /** Setup button */
    setupButton: {
      /** Button text: "Setup Puzzle" */
      text: string;

      /** Button enabled when image valid */
      enabled: boolean;

      /** Button click handler */
      onClick: SetupClickHandler;
    };

    /** Loading indicator (shown during API call) */
    loadingIndicator: {
      /** Spinner icon */
      spinner: string;

      /** Status message */
      message: string;
    } | null;
  };
}

// ============================================================================
// Testing Utilities
// ============================================================================

/**
 * Mock Clipboard API for testing
 * 
 * @example
 * ```typescript
 * const mockClipboard: MockClipboardData = {
 *   items: [
 *     {
 *       type: 'image/png',
 *       getAsFile: () => new Blob(['fake image data'], { type: 'image/png' })
 *     }
 *   ]
 * };
 * 
 * const event = new ClipboardEvent('paste', { clipboardData: mockClipboard });
 * ```
 */
export interface MockClipboardData {
  items: Array<{
    type: string;
    getAsFile: () => Blob | null;
  }>;
}

/**
 * Test fixture for ImagePuzzleSetupProps
 * 
 * @example
 * ```typescript
 * const mockProps: ImagePuzzleSetupProps = {
 *   onImageSetup: jest.fn(),
 *   providers: [
 *     { type: 'openai', displayName: 'OpenAI', models: ['gpt-4-vision-preview'] }
 *   ],
 *   defaultProvider: { type: 'openai', displayName: 'OpenAI', models: ['gpt-4-vision-preview'] },
 *   defaultModel: 'gpt-4-vision-preview',
 *   onError: jest.fn()
 * };
 * 
 * render(<ImagePuzzleSetup {...mockProps} />);
 * ```
 */
export type MockImagePuzzleSetupProps = ImagePuzzleSetupProps;

/**
 * Test fixture for successful ImageSetupResponse
 * 
 * @example
 * ```typescript
 * const mockSuccessResponse: ImageSetupResponse = {
 *   remaining_words: ["apple", "banana", "cherry", ...],  // 16 words
 *   status: "success"
 * };
 * 
 * jest.spyOn(api, 'setupPuzzleFromImage').mockResolvedValue(mockSuccessResponse);
 * ```
 */
export interface MockSuccessResponse {
  remaining_words: [string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string];
  status: 'success';
}

/**
 * Test fixture for error ImageSetupResponse
 * 
 * @example
 * ```typescript
 * const mockErrorResponse: MockErrorResponse = {
 *   remaining_words: [],
 *   status: "error",
 *   message: "Could not extract 16 words from image"
 * };
 * 
 * jest.spyOn(api, 'setupPuzzleFromImage').mockResolvedValue(mockErrorResponse);
 * ```
 */
export interface MockErrorResponse {
  remaining_words: [];
  status: 'error';
  message: string;
}
