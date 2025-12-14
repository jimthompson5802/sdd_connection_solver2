import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ImagePuzzleSetup } from './ImagePuzzleSetup';
import { LLMProviderOption } from '../types/llm-provider';

// Mock the api service
const mockSetupPuzzleFromImage = jest.fn();

jest.mock('../services/api', () => ({
  apiService: {
    setupPuzzleFromImage: mockSetupPuzzleFromImage
  },
  setupPuzzleFromImage: mockSetupPuzzleFromImage
}));

describe('ImagePuzzleSetup - Error Handling', () => {
  const defaultProps = {
    onImageSetup: jest.fn(),
    providers: [
      { type: 'openai', name: 'OpenAI' },
      { type: 'ollama', name: 'Ollama' }
    ] as LLMProviderOption[],
    defaultProvider: { type: 'openai', name: 'OpenAI' } as LLMProviderOption,
    defaultModel: 'gpt-4-vision-preview',
    onError: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.URL.createObjectURL = jest.fn(() => 'blob:fake-url');
    global.URL.revokeObjectURL = jest.fn();

    // Reset API mock to successful response
    mockSetupPuzzleFromImage.mockResolvedValue({
      status: 'success',
      remaining_words: Array.from({ length: 16 }, (_, i) => `word${i + 1}`)
    });
  });

  describe('Image Size Validation', () => {
    test('displays error for oversized image (>5MB)', async () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      const pasteArea = screen.getByTestId('image-paste-area');

      // Create a mock oversized file (6MB)
      const oversizedFile = new File(['x'.repeat(6 * 1024 * 1024)], 'large.png', { type: 'image/png' });

      const mockClipboardEvent = {
        preventDefault: jest.fn(),
        clipboardData: {
          items: [{
            kind: 'file',
            type: 'image/png',
            getAsFile: () => oversizedFile
          }]
        }
      };

      fireEvent.paste(pasteArea, mockClipboardEvent as any);

      await waitFor(() => {
        expect(screen.getByText('Image too large (max 5MB)')).toBeInTheDocument();
      });

      // Setup button should remain disabled
      const setupButton = screen.getByLabelText('Setup Puzzle') as HTMLButtonElement;
      expect(setupButton.disabled).toBe(true);
    });

    test('accepts image under 5MB limit', async () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      const pasteArea = screen.getByTestId('image-paste-area');

      // Create a mock file under 5MB (1MB)
      const validFile = new File(['x'.repeat(1024 * 1024)], 'valid.png', { type: 'image/png' });

      const mockClipboardEvent = {
        preventDefault: jest.fn(),
        clipboardData: {
          items: [{
            kind: 'file',
            type: 'image/png',
            getAsFile: () => validFile
          }]
        }
      };

      const mockFileReader = {
        readAsDataURL: jest.fn(),
        result: 'data:image/png;base64,validimagedata',
        onload: null as any,
        onerror: null as any
      };

      global.FileReader = jest.fn(() => mockFileReader) as any;

      fireEvent.paste(pasteArea, mockClipboardEvent as any);

      // Simulate FileReader onload
      if (mockFileReader.onload) {
        mockFileReader.onload({ target: mockFileReader } as any);
      }

      await waitFor(() => {
        expect(screen.getByAltText('Pasted image preview')).toBeInTheDocument();
        expect(screen.queryByText('Image too large (max 5MB)')).not.toBeInTheDocument();
      });

      // Setup button should be enabled
      const setupButton = screen.getByLabelText('Setup Puzzle') as HTMLButtonElement;
      expect(setupButton.disabled).toBe(false);
    });
  });

  describe('Backend Error Handling', () => {
    test('displays error for HTTP 413 payload too large', async () => {
      // Mock API to throw 413 error
      mockSetupPuzzleFromImage.mockRejectedValue(new Error('Request entity too large (413)'));

      render(<ImagePuzzleSetup {...defaultProps} />);

      // Setup valid image first
      const pasteArea = screen.getByTestId('image-paste-area');
      const mockFile = new File(['fake image data'], 'test.png', { type: 'image/png' });

      const mockClipboardEvent = {
        preventDefault: jest.fn(),
        clipboardData: {
          items: [{
            kind: 'file',
            type: 'image/png',
            getAsFile: () => mockFile
          }]
        }
      };

      const mockFileReader = {
        readAsDataURL: jest.fn(),
        result: 'data:image/png;base64,testimage',
        onload: null as any,
        onerror: null as any
      };

      global.FileReader = jest.fn(() => mockFileReader) as any;

      fireEvent.paste(pasteArea, mockClipboardEvent as any);

      if (mockFileReader.onload) {
        mockFileReader.onload({ target: mockFileReader } as any);
      }

      await waitFor(() => {
        expect(screen.getByAltText('Pasted image preview')).toBeInTheDocument();
      });

      // Click setup button to trigger error
      const setupButton = screen.getByLabelText('Setup Puzzle');
      fireEvent.click(setupButton);

      await waitFor(() => {
        expect(screen.getByText(/Request entity too large|Image file size exceeds server limits/)).toBeInTheDocument();
      });
    });

    test('displays error for HTTP 400 wrong word count', async () => {
      // Mock API to throw 400 error
      mockSetupPuzzleFromImage.mockRejectedValue(new Error('LLM unable to extract 16 puzzle words from image (400)'));

      render(<ImagePuzzleSetup {...defaultProps} />);

      // Setup valid image and trigger extraction
      await setupValidImageAndExtract();

      await waitFor(() => {
        expect(screen.getByText(/LLM unable to extract.*puzzle words/)).toBeInTheDocument();
      });
    });

    test('displays error for HTTP 400 model no vision', async () => {
      // Mock API to throw model error
      mockSetupPuzzleFromImage.mockRejectedValue(new Error('Selected model does not support vision capabilities (400)'));

      render(<ImagePuzzleSetup {...defaultProps} />);

      await setupValidImageAndExtract();

      await waitFor(() => {
        expect(screen.getByText(/model does not support vision/)).toBeInTheDocument();
      });
    });

    test('displays error for HTTP 422 missing fields', async () => {
      // Mock API to throw validation error
      mockSetupPuzzleFromImage.mockRejectedValue(new Error('Missing required fields: image_base64 (422)'));

      render(<ImagePuzzleSetup {...defaultProps} />);

      await setupValidImageAndExtract();

      await waitFor(() => {
        expect(screen.getByText(/Missing required fields/)).toBeInTheDocument();
      });
    });

    test('displays error for HTTP 500 provider failure', async () => {
      // Mock API to throw provider error
      mockSetupPuzzleFromImage.mockRejectedValue(new Error('LLM provider connection failed (500)'));

      render(<ImagePuzzleSetup {...defaultProps} />);

      await setupValidImageAndExtract();

      await waitFor(() => {
        expect(screen.getByText(/LLM provider.*failed|Unable to connect to LLM service/)).toBeInTheDocument();
      });
    });
  });

  describe('Error State Preservation', () => {
    test('preserves image data and selections after extraction error', async () => {
      // Mock API to fail
      mockSetupPuzzleFromImage.mockRejectedValue(new Error('Extraction failed'));

      render(<ImagePuzzleSetup {...defaultProps} />);

      // Setup image and provider selection
      await setupValidImageAndExtract();

      // Change provider selection before error
      const providerSelect = screen.getByLabelText('LLM Provider');
      fireEvent.change(providerSelect, { target: { value: 'ollama' } });

      await waitFor(() => {
        expect(screen.getByText(/Extraction failed/)).toBeInTheDocument();
      });

      // Verify image and selections are preserved
      expect(screen.getByAltText('Pasted image preview')).toBeInTheDocument();
      expect((providerSelect as HTMLSelectElement).value).toBe('ollama');

      // User should be able to retry
      const setupButton = screen.getByLabelText('Setup Puzzle') as HTMLButtonElement;
      expect(setupButton.disabled).toBe(false);
    });

    test('allows retry after error without re-uploading image', async () => {
      // Mock API to fail first, succeed second
      mockSetupPuzzleFromImage
        .mockRejectedValueOnce(new Error('First attempt failed'))
        .mockResolvedValue({
          status: 'success',
          remaining_words: Array.from({ length: 16 }, (_, i) => `word${i + 1}`)
        });

      render(<ImagePuzzleSetup {...defaultProps} />);

      await setupValidImageAndExtract();

      // First attempt should show error
      await waitFor(() => {
        expect(screen.getByText(/First attempt failed/)).toBeInTheDocument();
      });

      // Retry should succeed
      const setupButton = screen.getByLabelText('Setup Puzzle');
      fireEvent.click(setupButton);

      await waitFor(() => {
        expect(mockSetupPuzzleFromImage).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Loading States', () => {
    test('shows loading indicator during extraction', async () => {
      // Mock API with delayed response
      mockSetupPuzzleFromImage.mockImplementation(() =>
        new Promise(resolve => setTimeout(() => resolve({
          status: 'success',
          remaining_words: Array.from({ length: 16 }, (_, i) => `word${i + 1}`)
        }), 100))
      );

      render(<ImagePuzzleSetup {...defaultProps} />);

      await setupValidImageAndExtract();

      // Should show loading state immediately
      expect(screen.getByText('Extracting words...')).toBeInTheDocument();
      expect(screen.getByText('⏳')).toBeInTheDocument();

      // Button should be disabled during loading
      const setupButton = screen.getByLabelText('Setup Puzzle') as HTMLButtonElement;
      expect(setupButton.disabled).toBe(true);

      // Wait for completion
      await waitFor(() => {
        expect(screen.queryByText('Extracting words...')).not.toBeInTheDocument();
      }, { timeout: 200 });
    });

    test('disables setup button when no image pasted', () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      const setupButton = screen.getByLabelText('Setup Puzzle') as HTMLButtonElement;
      expect(setupButton.disabled).toBe(true);
      expect(setupButton.textContent).toBe('Setup Puzzle');
    });
  });

  // Helper function to setup valid image and trigger extraction
  async function setupValidImageAndExtract() {
    const pasteArea = screen.getByTestId('image-paste-area');
    const mockFile = new File(['fake image data'], 'test.png', { type: 'image/png' });

    const mockClipboardEvent = {
      preventDefault: jest.fn(),
      clipboardData: {
        items: [{
          kind: 'file',
          type: 'image/png',
          getAsFile: () => mockFile
        }]
      }
    };

    const mockFileReader = {
      readAsDataURL: jest.fn(),
      result: 'data:image/png;base64,testimage',
      onload: null as any,
      onerror: null as any
    };

    global.FileReader = jest.fn(() => mockFileReader) as any;

    fireEvent.paste(pasteArea, mockClipboardEvent as any);

    if (mockFileReader.onload) {
      mockFileReader.onload({ target: mockFileReader } as any);
    }

    await waitFor(() => {
      expect(screen.getByAltText('Pasted image preview')).toBeInTheDocument();
    });

    const setupButton = screen.getByLabelText('Setup Puzzle');
    fireEvent.click(setupButton);
  }
});