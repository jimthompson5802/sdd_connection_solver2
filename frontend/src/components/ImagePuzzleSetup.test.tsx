import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ImagePuzzleSetup } from './ImagePuzzleSetup';
import { LLMProviderOption } from '../types/llm-provider';

// Mock the api service
const mockSetupPuzzleFromImage = jest.fn(() => Promise.resolve({
  status: 'success',
  remaining_words: ['word1', 'word2', 'word3', 'word4', 'word5', 'word6', 'word7', 'word8', 'word9', 'word10', 'word11', 'word12', 'word13', 'word14', 'word15', 'word16']
}));

jest.mock('../services/api', () => ({
  setupPuzzleFromImage: mockSetupPuzzleFromImage
}));

describe('ImagePuzzleSetup - Enhanced UX', () => {
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

    // Mock URL methods for tests
    global.URL.createObjectURL = jest.fn(() => 'blob:fake-url');
    global.URL.revokeObjectURL = jest.fn();
  });

  describe('Placeholder Display', () => {
    test('displays placeholder content when no image is pasted', () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      // Should show placeholder icon, text, and keyboard hints
      expect(screen.getByText('📋')).toBeInTheDocument();
      expect(screen.getByText('Paste image here')).toBeInTheDocument();
      expect(screen.getByText('Cmd+V')).toBeInTheDocument();
      expect(screen.getByText('Ctrl+V')).toBeInTheDocument();

      // Check for platform hints text (broken up by elements)
      const hintElement = screen.getByText(/Press/);
      expect(hintElement).toBeInTheDocument();
      expect(hintElement.textContent).toMatch(/Mac.*Windows\/Linux/);
    });

    test('placeholder area has proper visual affordance styling', () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      const pasteArea = screen.getByTestId('image-paste-area');
      expect(pasteArea).toHaveClass('paste-area');
      expect(pasteArea).not.toHaveClass('has-image');

      const placeholder = screen.getByText('Paste image here').closest('.paste-placeholder');
      expect(placeholder).toBeInTheDocument();
    });
  });

  describe('Image Preview', () => {
    test('displays image preview after successful paste', async () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      const pasteArea = screen.getByTestId('image-paste-area');

      // Create mock image data
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

      // Mock FileReader
      const mockFileReader = {
        readAsDataURL: jest.fn(),
        result: 'data:image/png;base64,fakebase64data',
        onload: null as any,
        onerror: null as any
      };

      global.FileReader = jest.fn(() => mockFileReader) as any;
      global.URL.createObjectURL = jest.fn(() => 'blob:fake-url');

      // Simulate paste event
      fireEvent.paste(pasteArea, mockClipboardEvent as any);

      // Simulate FileReader onload
      if (mockFileReader.onload) {
        mockFileReader.onload({ target: mockFileReader } as any);
      }

      await waitFor(() => {
        expect(screen.getByAltText('Pasted preview')).toBeInTheDocument();
        expect(screen.getByText(/Size:.*KB/)).toBeInTheDocument();
        expect(screen.getByText(/Format: image\/png/)).toBeInTheDocument();
      });
    });

    test('image preview has proper sizing and aspect ratio', async () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      const pasteArea = screen.getByTestId('image-paste-area');
      const mockFile = new File(['fake image data'], 'test.jpg', { type: 'image/jpeg' });

      const mockClipboardEvent = {
        preventDefault: jest.fn(),
        clipboardData: {
          items: [{
            kind: 'file',
            type: 'image/jpeg',
            getAsFile: () => mockFile
          }]
        }
      };

      const mockFileReader = {
        readAsDataURL: jest.fn(),
        result: 'data:image/jpeg;base64,fakebase64data',
        onload: null as any,
        onerror: null as any
      };

      global.FileReader = jest.fn(() => mockFileReader) as any;
      global.URL.createObjectURL = jest.fn(() => 'blob:fake-url');

      fireEvent.paste(pasteArea, mockClipboardEvent as any);

      if (mockFileReader.onload) {
        mockFileReader.onload({ target: mockFileReader } as any);
      }

      await waitFor(() => {
        const previewImage = screen.getByAltText('Pasted preview');
        expect(previewImage).toHaveClass('preview-image');
      });
    });
  });

  describe('Invalid Content Handling', () => {
    test('displays error message when pasting non-image content', async () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      const pasteArea = screen.getByTestId('image-paste-area');

      // Mock clipboard with text content (no image)
      const mockClipboardEvent = {
        preventDefault: jest.fn(),
        clipboardData: {
          items: [{
            kind: 'string',
            type: 'text/plain',
            getAsFile: () => null
          }]
        }
      };

      fireEvent.paste(pasteArea, mockClipboardEvent as any);

      await waitFor(() => {
        expect(screen.getByText('Please paste a valid image')).toBeInTheDocument();
      });
    });

    test('displays error for unsupported image formats', async () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      const pasteArea = screen.getByTestId('image-paste-area');
      const mockFile = new File(['fake image data'], 'test.bmp', { type: 'image/bmp' });

      const mockClipboardEvent = {
        preventDefault: jest.fn(),
        clipboardData: {
          items: [{
            kind: 'file',
            type: 'image/bmp',
            getAsFile: () => mockFile
          }]
        }
      };

      fireEvent.paste(pasteArea, mockClipboardEvent as any);

      await waitFor(() => {
        expect(screen.getByText(/Unsupported image format.*png.*jpeg.*jpg.*gif.*webp/)).toBeInTheDocument();
      });
    });
  });

  describe('Image Clear/Replace Capability', () => {
    test('allows pasting new image to replace existing one', async () => {
      render(<ImagePuzzleSetup {...defaultProps} />);

      const pasteArea = screen.getByTestId('image-paste-area');

      // First image
      const firstFile = new File(['fake image data'], 'first.png', { type: 'image/png' });
      const firstClipboardEvent = {
        preventDefault: jest.fn(),
        clipboardData: {
          items: [{
            kind: 'file',
            type: 'image/png',
            getAsFile: () => firstFile
          }]
        }
      };

      const mockFileReader1 = {
        readAsDataURL: jest.fn(),
        result: 'data:image/png;base64,firstimage',
        onload: null as any,
        onerror: null as any
      };

      global.FileReader = jest.fn(() => mockFileReader1) as any;
      global.URL.createObjectURL = jest.fn(() => 'blob:first-url');
      global.URL.revokeObjectURL = jest.fn();

      fireEvent.paste(pasteArea, firstClipboardEvent as any);
      if (mockFileReader1.onload) {
        mockFileReader1.onload({ target: mockFileReader1 } as any);
      }

      await waitFor(() => {
        expect(screen.getByAltText('Pasted preview')).toBeInTheDocument();
      });

      // Second image (replacement)
      const secondFile = new File(['different image data'], 'second.jpg', { type: 'image/jpeg' });
      const secondClipboardEvent = {
        preventDefault: jest.fn(),
        clipboardData: {
          items: [{
            kind: 'file',
            type: 'image/jpeg',
            getAsFile: () => secondFile
          }]
        }
      };

      const mockFileReader2 = {
        readAsDataURL: jest.fn(),
        result: 'data:image/jpeg;base64,secondimage',
        onload: null as any,
        onerror: null as any
      };

      global.FileReader = jest.fn(() => mockFileReader2) as any;
      global.URL.createObjectURL = jest.fn(() => 'blob:second-url');

      fireEvent.paste(pasteArea, secondClipboardEvent as any);
      if (mockFileReader2.onload) {
        mockFileReader2.onload({ target: mockFileReader2 } as any);
      }

      await waitFor(() => {
        expect(screen.getByText(/Format: image\/jpeg/)).toBeInTheDocument();
        // Should have revoked the old URL
        expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('blob:first-url');
      });
    });
  });
});