/**
 * Comprehensive tests for ErrorMessage component.
 * Tests all error types, retry/dismiss functionality, expandable details, and accessibility.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorMessage, ErrorMessageProps } from './ErrorMessage';

describe('ErrorMessage Component', () => {
  const defaultProps: ErrorMessageProps = {
    message: 'Test error message',
  };

  describe('Basic Rendering', () => {
    test('renders with required props only', () => {
      render(<ErrorMessage {...defaultProps} />);

      expect(screen.getByText('Test error message')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    test('renders error message text', () => {
      render(<ErrorMessage {...defaultProps} message="Custom error text" />);

      expect(screen.getByText('Custom error text')).toBeInTheDocument();
    });

    test('has correct ARIA attributes', () => {
      render(<ErrorMessage {...defaultProps} />);

      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-live', 'assertive');
    });
  });

  describe('Error Types', () => {
    test('renders error type with correct icon and title', () => {
      render(<ErrorMessage {...defaultProps} type="error" />);

      expect(screen.getByText('❌')).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
    });

    test('renders warning type with correct icon and title', () => {
      render(<ErrorMessage {...defaultProps} type="warning" />);

      expect(screen.getByText('⚠️')).toBeInTheDocument();
      expect(screen.getByText('Warning')).toBeInTheDocument();
    });

    test('renders validation type with correct icon and title', () => {
      render(<ErrorMessage {...defaultProps} type="validation" />);

      expect(screen.getByText('🔧')).toBeInTheDocument();
      expect(screen.getByText('Validation Error')).toBeInTheDocument();
    });

    test('renders network type with correct icon and title', () => {
      render(<ErrorMessage {...defaultProps} type="network" />);

      expect(screen.getByText('🌐')).toBeInTheDocument();
      expect(screen.getByText('Connection Error')).toBeInTheDocument();
    });

    test('applies correct CSS class for error type', () => {
      const { container } = render(<ErrorMessage {...defaultProps} type="warning" />);

      const errorDiv = container.querySelector('.error-message--warning');
      expect(errorDiv).toBeInTheDocument();
    });
  });

  describe('Provider Display', () => {
    test('displays provider name when provided', () => {
      render(<ErrorMessage {...defaultProps} provider="openai" />);

      expect(screen.getByText(/- OpenAI/)).toBeInTheDocument();
    });

    test('formats simple provider name', () => {
      render(<ErrorMessage {...defaultProps} provider="simple" />);

      expect(screen.getByText(/- Simple Provider/)).toBeInTheDocument();
    });

    test('formats ollama provider name', () => {
      render(<ErrorMessage {...defaultProps} provider="ollama" />);

      expect(screen.getByText(/- Ollama/)).toBeInTheDocument();
    });

    test('handles unknown provider name', () => {
      render(<ErrorMessage {...defaultProps} provider="unknown" />);

      expect(screen.getByText(/- unknown/)).toBeInTheDocument();
    });

    test('does not show provider section when not provided', () => {
      render(<ErrorMessage {...defaultProps} />);

      const title = screen.getByText('Error');
      expect(title.textContent).toBe('Error');
      expect(title.textContent).not.toContain('-');
    });
  });

  describe('Error Code', () => {
    test('displays error code when provided', () => {
      render(<ErrorMessage {...defaultProps} errorCode="ERR-500" />);

      expect(screen.getByText('Error Code: ERR-500')).toBeInTheDocument();
    });

    test('does not show error code section when not provided', () => {
      render(<ErrorMessage {...defaultProps} />);

      expect(screen.queryByText(/Error Code:/)).not.toBeInTheDocument();
    });
  });

  describe('Retry Functionality', () => {
    test('shows retry button when showRetry is true', () => {
      render(<ErrorMessage {...defaultProps} showRetry={true} />);

      expect(screen.getByText('🔄 Retry')).toBeInTheDocument();
    });

    test('does not show retry button by default', () => {
      render(<ErrorMessage {...defaultProps} />);

      expect(screen.queryByText('🔄 Retry')).not.toBeInTheDocument();
    });

    test('calls onRetry when retry button is clicked', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage {...defaultProps} showRetry={true} onRetry={onRetry} />);

      fireEvent.click(screen.getByText('🔄 Retry'));

      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    test('does not crash when retry clicked without onRetry handler', () => {
      render(<ErrorMessage {...defaultProps} showRetry={true} />);

      expect(() => {
        fireEvent.click(screen.getByText('🔄 Retry'));
      }).not.toThrow();
    });
  });

  describe('Dismiss Functionality', () => {
    test('shows dismiss X button when dismissible is true', () => {
      render(<ErrorMessage {...defaultProps} dismissible={true} />);

      expect(screen.getByLabelText('Dismiss error message')).toBeInTheDocument();
    });

    test('shows dismiss action button when showDismiss is true', () => {
      render(<ErrorMessage {...defaultProps} showDismiss={true} />);

      expect(screen.getByText('Dismiss')).toBeInTheDocument();
    });

    test('hides dismiss X button when dismissible is false', () => {
      render(<ErrorMessage {...defaultProps} dismissible={false} />);

      expect(screen.queryByLabelText('Dismiss error message')).not.toBeInTheDocument();
    });

    test('calls onDismiss when X button is clicked', () => {
      const onDismiss = jest.fn();
      render(<ErrorMessage {...defaultProps} dismissible={true} onDismiss={onDismiss} />);

      fireEvent.click(screen.getByLabelText('Dismiss error message'));

      expect(onDismiss).toHaveBeenCalledTimes(1);
    });

    test('calls onDismiss when dismiss action button is clicked', () => {
      const onDismiss = jest.fn();
      render(<ErrorMessage {...defaultProps} showDismiss={true} onDismiss={onDismiss} />);

      fireEvent.click(screen.getByText('Dismiss'));

      expect(onDismiss).toHaveBeenCalledTimes(1);
    });

    test('does not crash when dismiss clicked without onDismiss handler', () => {
      render(<ErrorMessage {...defaultProps} dismissible={true} />);

      expect(() => {
        fireEvent.click(screen.getByLabelText('Dismiss error message'));
      }).not.toThrow();
    });
  });

  describe('Expandable Details', () => {
    test('shows details toggle button when details are provided', () => {
      render(<ErrorMessage {...defaultProps} details="Detailed error information" />);

      expect(screen.getByText(/Show Details/)).toBeInTheDocument();
    });

    test('does not show details section when no details provided', () => {
      render(<ErrorMessage {...defaultProps} />);

      expect(screen.queryByText(/Show Details/)).not.toBeInTheDocument();
    });

    test('expands details when toggle button is clicked', () => {
      render(<ErrorMessage {...defaultProps} details="Detailed error information" />);

      const toggleButton = screen.getByText(/Show Details/);
      fireEvent.click(toggleButton);

      expect(screen.getByText('Detailed error information')).toBeInTheDocument();
      expect(screen.getByText(/Hide Details/)).toBeInTheDocument();
    });

    test('collapses details when toggle button is clicked again', () => {
      render(<ErrorMessage {...defaultProps} details="Detailed error information" />);

      const toggleButton = screen.getByText(/Show Details/);
      fireEvent.click(toggleButton); // Expand
      fireEvent.click(screen.getByText(/Hide Details/)); // Collapse

      expect(screen.queryByText('Detailed error information')).not.toBeInTheDocument();
      expect(screen.getByText(/Show Details/)).toBeInTheDocument();
    });

    test('has correct ARIA attributes for details toggle', () => {
      render(<ErrorMessage {...defaultProps} details="Details text" />);

      const toggleButton = screen.getByText(/Show Details/);
      expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
      expect(toggleButton).toHaveAttribute('aria-controls', 'error-details');

      fireEvent.click(toggleButton);

      expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
    });

    test('details region has correct ARIA attributes', () => {
      render(<ErrorMessage {...defaultProps} details="Details text" />);

      fireEvent.click(screen.getByText(/Show Details/));

      const detailsRegion = screen.getByRole('region', { name: 'Error details' });
      expect(detailsRegion).toBeInTheDocument();
      expect(detailsRegion).toHaveAttribute('id', 'error-details');
    });

    test('renders details in pre tag for formatting', () => {
      const { container } = render(
        <ErrorMessage {...defaultProps} details="Line 1\nLine 2\nLine 3" />
      );

      fireEvent.click(screen.getByText(/Show Details/));

      const preElement = container.querySelector('pre');
      expect(preElement).toBeInTheDocument();
      // Check that all lines are present
      expect(preElement?.textContent).toContain('Line 1');
      expect(preElement?.textContent).toContain('Line 2');
      expect(preElement?.textContent).toContain('Line 3');
    });
  });

  describe('Custom Styling', () => {
    test('applies custom className', () => {
      const { container } = render(
        <ErrorMessage {...defaultProps} className="custom-error-class" />
      );

      const errorDiv = container.querySelector('.custom-error-class');
      expect(errorDiv).toBeInTheDocument();
    });

    test('combines custom className with type class', () => {
      const { container } = render(
        <ErrorMessage {...defaultProps} type="warning" className="custom-class" />
      );

      const errorDiv = container.querySelector('.error-message--warning.custom-class');
      expect(errorDiv).toBeInTheDocument();
    });
  });

  describe('Complex Scenarios', () => {
    test('renders error with all features enabled', () => {
      const onRetry = jest.fn();
      const onDismiss = jest.fn();

      render(
        <ErrorMessage
          message="Complete error message"
          type="network"
          provider="openai"
          errorCode="NET-001"
          showRetry={true}
          onRetry={onRetry}
          showDismiss={true}
          onDismiss={onDismiss}
          dismissible={true}
          details="Stack trace information"
          className="custom-error"
        />
      );

      expect(screen.getByText('Complete error message')).toBeInTheDocument();
      expect(screen.getByText('Connection Error')).toBeInTheDocument();
      expect(screen.getByText(/- OpenAI/)).toBeInTheDocument();
      expect(screen.getByText('Error Code: NET-001')).toBeInTheDocument();
      expect(screen.getByText('🔄 Retry')).toBeInTheDocument();
      expect(screen.getByText('Dismiss')).toBeInTheDocument();
      expect(screen.getByLabelText('Dismiss error message')).toBeInTheDocument();
      expect(screen.getByText(/Show Details/)).toBeInTheDocument();
    });

    test('handles both retry and dismiss actions together', () => {
      const onRetry = jest.fn();
      const onDismiss = jest.fn();

      render(
        <ErrorMessage
          {...defaultProps}
          showRetry={true}
          onRetry={onRetry}
          showDismiss={true}
          onDismiss={onDismiss}
        />
      );

      fireEvent.click(screen.getByText('🔄 Retry'));
      expect(onRetry).toHaveBeenCalledTimes(1);
      expect(onDismiss).not.toHaveBeenCalled();

      fireEvent.click(screen.getByText('Dismiss'));
      expect(onDismiss).toHaveBeenCalledTimes(1);
      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    test('allows multiple expand/collapse cycles', () => {
      render(<ErrorMessage {...defaultProps} details="Details content" />);

      const toggleButton = screen.getByText(/Show Details/);

      // Expand
      fireEvent.click(toggleButton);
      expect(screen.getByText('Details content')).toBeInTheDocument();

      // Collapse
      fireEvent.click(screen.getByText(/Hide Details/));
      expect(screen.queryByText('Details content')).not.toBeInTheDocument();

      // Expand again
      fireEvent.click(screen.getByText(/Show Details/));
      expect(screen.getByText('Details content')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('handles empty message string', () => {
      render(<ErrorMessage message="" />);

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });

    test('handles very long error message', () => {
      const longMessage = 'A'.repeat(500);
      render(<ErrorMessage message={longMessage} />);

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    test('handles special characters in message', () => {
      const specialMessage = 'Error: <script>alert("xss")</script>';
      render(<ErrorMessage message={specialMessage} />);

      expect(screen.getByText(specialMessage)).toBeInTheDocument();
    });

    test('handles multiline message', () => {
      const multilineMessage = 'Line 1\nLine 2\nLine 3';
      render(<ErrorMessage message={multilineMessage} />);

      // Check that all lines are present in the document
      expect(screen.getByText(/Line 1/)).toBeInTheDocument();
      expect(screen.getByText(/Line 2/)).toBeInTheDocument();
      expect(screen.getByText(/Line 3/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('all buttons have proper type attribute', () => {
      render(
        <ErrorMessage
          {...defaultProps}
          showRetry={true}
          showDismiss={true}
          dismissible={true}
          details="Details"
        />
      );

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveAttribute('type', 'button');
      });
    });

    test('icon elements are hidden from screen readers', () => {
      const { container } = render(<ErrorMessage {...defaultProps} type="error" />);

      const icon = container.querySelector('.error-message__icon');
      expect(icon).toHaveAttribute('aria-hidden', 'true');
    });

    test('dismiss button has accessible label', () => {
      render(<ErrorMessage {...defaultProps} dismissible={true} />);

      const dismissButton = screen.getByLabelText('Dismiss error message');
      expect(dismissButton).toBeInTheDocument();
    });
  });
});
