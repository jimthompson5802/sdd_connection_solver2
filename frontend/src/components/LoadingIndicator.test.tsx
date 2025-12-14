/**
 * Comprehensive tests for LoadingIndicator component.
 * Tests loading states, progress display, elapsed time, phase transitions, and cancel functionality.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { LoadingIndicator, LoadingIndicatorProps } from './LoadingIndicator';

// Mock timers for predictable time-based tests
jest.useFakeTimers();

describe('LoadingIndicator Component', () => {
  const defaultProps: LoadingIndicatorProps = {
    isLoading: true,
  };

  afterEach(() => {
    jest.clearAllTimers();
  });

  describe('Basic Rendering', () => {
    test('renders nothing when isLoading is false', () => {
      const { container } = render(<LoadingIndicator isLoading={false} />);

      expect(container.firstChild).toBeNull();
    });

    test('renders loading indicator when isLoading is true', () => {
      render(<LoadingIndicator {...defaultProps} />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    test('has proper ARIA attributes', () => {
      render(<LoadingIndicator {...defaultProps} />);

      const indicator = screen.getByRole('status');
      expect(indicator).toHaveAttribute('aria-live', 'polite');
    });

    test('renders default message', () => {
      render(<LoadingIndicator {...defaultProps} />);

      expect(screen.getByText('Generating recommendation...')).toBeInTheDocument();
    });

    test('renders custom message', () => {
      render(<LoadingIndicator {...defaultProps} message="Custom loading message" />);

      expect(screen.getByText('Custom loading message')).toBeInTheDocument();
    });

    test('applies custom className', () => {
      const { container } = render(
        <LoadingIndicator {...defaultProps} className="custom-loader" />
      );

      expect(container.querySelector('.loading-indicator.custom-loader')).toBeInTheDocument();
    });
  });

  describe('Provider Icons', () => {
    test('displays OpenAI icon', () => {
      render(<LoadingIndicator {...defaultProps} provider="openai" />);

      expect(screen.getByText('🤖')).toBeInTheDocument();
    });

    test('displays Ollama icon', () => {
      render(<LoadingIndicator {...defaultProps} provider="ollama" />);

      expect(screen.getByText('🦙')).toBeInTheDocument();
    });

    test('displays Simple icon', () => {
      render(<LoadingIndicator {...defaultProps} provider="simple" />);

      expect(screen.getByText('⚡')).toBeInTheDocument();
    });

    test('displays default icon for unknown provider', () => {
      render(<LoadingIndicator {...defaultProps} provider="unknown" />);

      expect(screen.getByText('🧠')).toBeInTheDocument();
    });

    test('displays default icon when no provider specified', () => {
      render(<LoadingIndicator {...defaultProps} />);

      expect(screen.getByText('🧠')).toBeInTheDocument();
    });

    test('handles case-insensitive provider names', () => {
      render(<LoadingIndicator {...defaultProps} provider="OPENAI" />);

      expect(screen.getByText('🤖')).toBeInTheDocument();
    });
  });

  describe('Phase Messages', () => {
    test('shows initializing phase at start', () => {
      render(<LoadingIndicator {...defaultProps} />);

      expect(screen.getByText(/Initializing.../)).toBeInTheDocument();
    });

    test('includes provider in initializing message', () => {
      render(<LoadingIndicator {...defaultProps} provider="OpenAI" />);

      expect(screen.getByText('Initializing (OpenAI)...')).toBeInTheDocument();
    });

    test('transitions to processing phase', async () => {
      render(<LoadingIndicator {...defaultProps} provider="OpenAI" estimatedDuration={1000} />);

      // Advance time to 25% (should be in processing phase)
      act(() => {
        jest.advanceTimersByTime(250);
      });

      await waitFor(() => {
        expect(screen.getByText('Processing with OpenAI...')).toBeInTheDocument();
      });
    });

    test('transitions to validating phase', async () => {
      render(<LoadingIndicator {...defaultProps} estimatedDuration={1000} />);

      // Advance time to 75% (should be in validating phase)
      act(() => {
        jest.advanceTimersByTime(750);
      });

      await waitFor(() => {
        expect(screen.getByText('Validating response...')).toBeInTheDocument();
      });
    });

    test('transitions to finalizing phase', async () => {
      render(<LoadingIndicator {...defaultProps} estimatedDuration={1000} />);

      // Advance time to 95% (should be in finalizing phase)
      act(() => {
        jest.advanceTimersByTime(950);
      });

      await waitFor(() => {
        expect(screen.getByText('Finalizing recommendation...')).toBeInTheDocument();
      });
    });

    test('uses default provider name "AI" when provider not specified', async () => {
      render(<LoadingIndicator {...defaultProps} estimatedDuration={1000} />);

      act(() => {
        jest.advanceTimersByTime(300);
      });

      await waitFor(() => {
        expect(screen.getByText('Processing with AI...')).toBeInTheDocument();
      });
    });
  });

  describe('Progress Display', () => {
    test('shows progress bar by default', () => {
      render(<LoadingIndicator {...defaultProps} />);

      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    test('hides progress bar when showProgress is false', () => {
      render(<LoadingIndicator {...defaultProps} showProgress={false} />);

      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });

    test('progress bar has proper ARIA attributes', () => {
      render(<LoadingIndicator {...defaultProps} />);

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuemin', '0');
      expect(progressBar).toHaveAttribute('aria-valuemax', '100');
      expect(progressBar).toHaveAttribute('aria-valuenow');
    });

    test('progress starts at 0%', () => {
      render(<LoadingIndicator {...defaultProps} />);

      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    test('progress increases over time', async () => {
      render(<LoadingIndicator {...defaultProps} estimatedDuration={1000} />);

      act(() => {
        jest.advanceTimersByTime(500);
      });

      await waitFor(() => {
        const progressText = screen.getByText(/\d+%/);
        const percentValue = parseInt(progressText.textContent || '0');
        expect(percentValue).toBeGreaterThan(40);
        expect(percentValue).toBeLessThan(60);
      });
    });

    test('progress caps at 95%', async () => {
      render(<LoadingIndicator {...defaultProps} estimatedDuration={1000} />);

      // Advance beyond estimated duration
      act(() => {
        jest.advanceTimersByTime(2000);
      });

      await waitFor(() => {
        expect(screen.getByText('95%')).toBeInTheDocument();
      });
    });

    test('progress bar width matches percentage', async () => {
      const { container } = render(
        <LoadingIndicator {...defaultProps} estimatedDuration={1000} />
      );

      act(() => {
        jest.advanceTimersByTime(500);
      });

      await waitFor(() => {
        const progressFill = container.querySelector('.progress-fill') as HTMLElement;
        const width = progressFill?.style.width;
        const widthPercent = parseInt(width || '0');
        expect(widthPercent).toBeGreaterThan(40);
        expect(widthPercent).toBeLessThan(60);
      });
    });
  });

  describe('Elapsed Time Display', () => {
    test('shows elapsed time by default', () => {
      render(<LoadingIndicator {...defaultProps} />);

      expect(screen.getByText(/Elapsed:/)).toBeInTheDocument();
    });

    test('hides elapsed time when showElapsedTime is false', () => {
      render(<LoadingIndicator {...defaultProps} showElapsedTime={false} />);

      expect(screen.queryByText(/Elapsed:/)).not.toBeInTheDocument();
    });

    test('elapsed time starts at 0s', () => {
      render(<LoadingIndicator {...defaultProps} />);

      expect(screen.getByText('Elapsed: 0s')).toBeInTheDocument();
    });

    test('elapsed time increases in seconds', async () => {
      render(<LoadingIndicator {...defaultProps} />);

      act(() => {
        jest.advanceTimersByTime(3500);
      });

      await waitFor(() => {
        expect(screen.getByText('Elapsed: 3s')).toBeInTheDocument();
      });
    });

    test('elapsed time formats as MM:SS after 60 seconds', async () => {
      render(<LoadingIndicator {...defaultProps} />);

      act(() => {
        jest.advanceTimersByTime(75000);
      });

      await waitFor(() => {
        expect(screen.getByText('Elapsed: 1:15')).toBeInTheDocument();
      });
    });

    test('elapsed time pads seconds with zero', async () => {
      render(<LoadingIndicator {...defaultProps} />);

      act(() => {
        jest.advanceTimersByTime(125000);
      });

      await waitFor(() => {
        expect(screen.getByText('Elapsed: 2:05')).toBeInTheDocument();
      });
    });

    test('handles multiple minutes correctly', async () => {
      render(<LoadingIndicator {...defaultProps} />);

      act(() => {
        jest.advanceTimersByTime(183000);
      });

      await waitFor(() => {
        expect(screen.getByText('Elapsed: 3:03')).toBeInTheDocument();
      });
    });
  });

  describe('Cancel Functionality', () => {
    test('does not show cancel button by default', () => {
      render(<LoadingIndicator {...defaultProps} />);

      expect(screen.queryByText('Cancel')).not.toBeInTheDocument();
    });

    test('shows cancel button when onCancel is provided', () => {
      const onCancel = jest.fn();
      render(<LoadingIndicator {...defaultProps} onCancel={onCancel} />);

      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    test('cancel button has proper type attribute', () => {
      const onCancel = jest.fn();
      render(<LoadingIndicator {...defaultProps} onCancel={onCancel} />);

      const button = screen.getByText('Cancel');
      expect(button).toHaveAttribute('type', 'button');
    });

    test('cancel button has proper ARIA label', () => {
      const onCancel = jest.fn();
      render(<LoadingIndicator {...defaultProps} onCancel={onCancel} />);

      const button = screen.getByLabelText('Cancel recommendation generation');
      expect(button).toBeInTheDocument();
    });

    test('calls onCancel when cancel button is clicked', () => {
      const onCancel = jest.fn();
      render(<LoadingIndicator {...defaultProps} onCancel={onCancel} />);

      fireEvent.click(screen.getByText('Cancel'));

      expect(onCancel).toHaveBeenCalledTimes(1);
    });

    test('cancel button is clickable multiple times', () => {
      const onCancel = jest.fn();
      render(<LoadingIndicator {...defaultProps} onCancel={onCancel} />);

      const button = screen.getByText('Cancel');
      fireEvent.click(button);
      fireEvent.click(button);

      expect(onCancel).toHaveBeenCalledTimes(2);
    });
  });

  describe('State Management', () => {
    test('resets state when isLoading changes from true to false', async () => {
      const { rerender } = render(<LoadingIndicator isLoading={true} estimatedDuration={1000} />);

      // Advance time
      act(() => {
        jest.advanceTimersByTime(500);
      });

      await waitFor(() => {
        expect(screen.queryByText('0%')).not.toBeInTheDocument();
      });

      // Stop loading
      rerender(<LoadingIndicator isLoading={false} estimatedDuration={1000} />);

      // Start loading again
      rerender(<LoadingIndicator isLoading={true} estimatedDuration={1000} />);

      // Should be reset
      expect(screen.getByText('0%')).toBeInTheDocument();
      expect(screen.getByText('Elapsed: 0s')).toBeInTheDocument();
    });

    test('continues updating when still loading', async () => {
      render(<LoadingIndicator {...defaultProps} estimatedDuration={1000} />);

      act(() => {
        jest.advanceTimersByTime(300);
      });

      await waitFor(() => {
        expect(screen.queryByText('0%')).not.toBeInTheDocument();
      });

      act(() => {
        jest.advanceTimersByTime(300);
      });

      await waitFor(() => {
        const progressText = screen.getByText(/\d+%/);
        const percentValue = parseInt(progressText.textContent || '0');
        expect(percentValue).toBeGreaterThan(50);
      });
    });

    test('clears interval on unmount', () => {
      const { unmount } = render(<LoadingIndicator {...defaultProps} />);

      const clearIntervalSpy = jest.spyOn(global, 'clearInterval');
      unmount();

      expect(clearIntervalSpy).toHaveBeenCalled();
      clearIntervalSpy.mockRestore();
    });

    test('updates when estimatedDuration changes', async () => {
      const { rerender } = render(
        <LoadingIndicator isLoading={true} estimatedDuration={1000} />
      );

      act(() => {
        jest.advanceTimersByTime(500);
      });

      await waitFor(() => {
        const progressText = screen.getByText(/\d+%/);
        const percent1 = parseInt(progressText.textContent || '0');
        expect(percent1).toBeGreaterThan(40);
      });

      // Change estimated duration
      rerender(<LoadingIndicator isLoading={true} estimatedDuration={2000} />);

      // Progress should reset and recalculate
      act(() => {
        jest.advanceTimersByTime(100);
      });

      await waitFor(() => {
        const progressText = screen.getByText(/\d+%/);
        const percent2 = parseInt(progressText.textContent || '0');
        expect(percent2).toBeLessThan(20);
      });
    });
  });

  describe('Visual Elements', () => {
    test('renders spinner rings', () => {
      const { container } = render(<LoadingIndicator {...defaultProps} />);

      const rings = container.querySelectorAll('.spinner-ring');
      expect(rings.length).toBe(3);
    });

    test('renders loading dots', () => {
      const { container } = render(<LoadingIndicator {...defaultProps} />);

      const dots = container.querySelector('.loading-dots');
      expect(dots).toBeInTheDocument();
      expect(dots?.querySelectorAll('span').length).toBe(3);
    });

    test('spinner has aria-hidden', () => {
      const { container } = render(<LoadingIndicator {...defaultProps} />);

      const spinner = container.querySelector('.spinner');
      expect(spinner).toHaveAttribute('aria-hidden', 'true');
    });

    test('provider icon has aria-hidden', () => {
      const { container } = render(<LoadingIndicator {...defaultProps} provider="openai" />);

      const icon = container.querySelector('.provider-icon');
      expect(icon).toHaveAttribute('aria-hidden', 'true');
    });

    test('loading dots have aria-hidden', () => {
      const { container } = render(<LoadingIndicator {...defaultProps} />);

      const dots = container.querySelector('.loading-dots');
      expect(dots).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Edge Cases', () => {
    test('handles very short estimatedDuration', async () => {
      render(<LoadingIndicator {...defaultProps} estimatedDuration={100} />);

      act(() => {
        jest.advanceTimersByTime(50);
      });

      await waitFor(() => {
        const progressText = screen.getByText(/\d+%/);
        const percentValue = parseInt(progressText.textContent || '0');
        expect(percentValue).toBeGreaterThan(0);
        expect(percentValue).toBeLessThanOrEqual(95);
      });
    });

    test('handles very long estimatedDuration', async () => {
      render(<LoadingIndicator {...defaultProps} estimatedDuration={60000} />);

      act(() => {
        jest.advanceTimersByTime(6000);
      });

      await waitFor(() => {
        const progressText = screen.getByText(/\d+%/);
        const percentValue = parseInt(progressText.textContent || '0');
        expect(percentValue).toBeLessThan(20);
      });
    });

    test('handles empty string message', () => {
      render(<LoadingIndicator {...defaultProps} message="" />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    test('handles empty string provider', () => {
      render(<LoadingIndicator {...defaultProps} provider="" />);

      expect(screen.getByText('🧠')).toBeInTheDocument();
    });

    test('handles empty string className', () => {
      const { container } = render(<LoadingIndicator {...defaultProps} className="" />);

      expect(container.querySelector('.loading-indicator')).toBeInTheDocument();
    });
  });

  describe('Integration Scenarios', () => {
    test('complete loading cycle with all features enabled', async () => {
      const onCancel = jest.fn();
      render(
        <LoadingIndicator
          isLoading={true}
          message="Processing your request"
          provider="OpenAI"
          showProgress={true}
          showElapsedTime={true}
          estimatedDuration={2000}
          onCancel={onCancel}
          className="custom-loader"
        />
      );

      // Initial state
      expect(screen.getByText('Processing your request')).toBeInTheDocument();
      expect(screen.getByText('Initializing (OpenAI)...')).toBeInTheDocument();
      expect(screen.getByText('🤖')).toBeInTheDocument();
      expect(screen.getByText('0%')).toBeInTheDocument();
      expect(screen.getByText('Elapsed: 0s')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();

      // Mid-progress
      act(() => {
        jest.advanceTimersByTime(1000);
      });

      await waitFor(() => {
        expect(screen.getByText('Processing with OpenAI...')).toBeInTheDocument();
        const progressText = screen.getByText(/\d+%/);
        const percentValue = parseInt(progressText.textContent || '0');
        expect(percentValue).toBeGreaterThan(40);
        expect(screen.getByText('Elapsed: 1s')).toBeInTheDocument();
      });

      // Near completion
      act(() => {
        jest.advanceTimersByTime(1000);
      });

      await waitFor(() => {
        expect(screen.getByText('Finalizing recommendation...')).toBeInTheDocument();
      });

      // Cancel
      fireEvent.click(screen.getByText('Cancel'));
      expect(onCancel).toHaveBeenCalled();
    });

    test('minimal configuration still works', () => {
      render(<LoadingIndicator isLoading={true} />);

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText('Generating recommendation...')).toBeInTheDocument();
    });

    test('all optional features disabled', () => {
      render(
        <LoadingIndicator
          isLoading={true}
          showProgress={false}
          showElapsedTime={false}
        />
      );

      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
      expect(screen.queryByText(/Elapsed:/)).not.toBeInTheDocument();
      expect(screen.queryByText('Cancel')).not.toBeInTheDocument();
    });
  });
});
