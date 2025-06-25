import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import ErrorBoundary from '../ErrorBoundary';

// Mock console.error to avoid noise in tests
const originalConsoleError = console.error;
beforeEach(() => {
  console.error = vi.fn();
});

afterEach(() => {
  console.error = originalConsoleError;
});

// Test component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('renders error UI when there is an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(
      screen.getByText(
        'We apologize for the inconvenience. An unexpected error has occurred. Please try refreshing the page or returning to the home page.'
      )
    ).toBeInTheDocument();
  });

  it('renders custom fallback UI when provided', () => {
    const customFallback = <div>Custom error message</div>;

    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom error message')).toBeInTheDocument();
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
  });

  it('shows action buttons in error state', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Refresh Page')).toBeInTheDocument();
    expect(screen.getByText('Go Home')).toBeInTheDocument();
    expect(screen.getByText('Report this error')).toBeInTheDocument();
  });

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Error Details (Development Mode)')).toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });

  it('does not show error details in production mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.queryByText('Error Details (Development Mode)')).not.toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });

  it('calls window.location.reload when refresh button is clicked', () => {
    const reloadMock = vi.fn();
    
    // Mock window.location.reload
    Object.defineProperty(window, 'location', {
      value: {
        ...window.location,
        reload: reloadMock,
      },
      writable: true,
    });

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    const refreshButton = screen.getByText('Refresh Page');
    fireEvent.click(refreshButton);

    expect(reloadMock).toHaveBeenCalled();
  });

  it('navigates to home when go home button is clicked', () => {
    // Mock window.location.href setter
    Object.defineProperty(window, 'location', {
      value: {
        ...window.location,
        href: '',
      },
      writable: true,
    });

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    const homeButton = screen.getByText('Go Home');
    fireEvent.click(homeButton);

    expect(window.location.href).toBe('/dashboard');
  });

  it('opens mailto link when report error button is clicked', () => {
    const originalOpen = window.open;
    window.open = vi.fn();

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    const reportButton = screen.getByText('Report this error');
    fireEvent.click(reportButton);

    expect(window.open).toHaveBeenCalledWith(
      expect.stringContaining('mailto:support@bdc.com')
    );

    window.open = originalOpen;
  });

  it('logs error to console when error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(console.error).toHaveBeenCalledWith(
      'ErrorBoundary caught an error:',
      expect.any(Error),
      expect.any(Object)
    );
  });
});