import { render, screen, fireEvent } from '@testing-library/react';
import { useNavigate } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import ErrorPage from '../ErrorPage';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

const mockNavigate = vi.fn();

describe('ErrorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useNavigate).mockReturnValue(mockNavigate);
  });

  it('renders 404 error page with correct content', () => {
    render(<ErrorPage statusCode={404} />);

    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText('Page Not Found')).toBeInTheDocument();
    expect(screen.getByText(/can't find the page you're looking for/)).toBeInTheDocument();
    expect(screen.getByText('Go Back')).toBeInTheDocument();
    expect(screen.getByText('Go Home')).toBeInTheDocument();
    expect(screen.queryByText('Try Again')).not.toBeInTheDocument();
    expect(screen.queryByText('Contact Support')).not.toBeInTheDocument();
  });

  it('renders 403 error page with correct content', () => {
    render(<ErrorPage statusCode={403} />);

    expect(screen.getByText('403')).toBeInTheDocument();
    expect(screen.getByText('Access Denied')).toBeInTheDocument();
    expect(screen.getByText(/don't have permission to access/)).toBeInTheDocument();
    expect(screen.getByText('Go Back')).toBeInTheDocument();
    expect(screen.getByText('Go Home')).toBeInTheDocument();
    expect(screen.getByText('Contact Support')).toBeInTheDocument();
    expect(screen.queryByText('Try Again')).not.toBeInTheDocument();
  });

  it('renders 500 error page with correct content', () => {
    render(<ErrorPage statusCode={500} />);

    expect(screen.getByText('500')).toBeInTheDocument();
    expect(screen.getByText('Server Error')).toBeInTheDocument();
    expect(screen.getByText(/Something went wrong on our end/)).toBeInTheDocument();
    expect(screen.getByText('Go Back')).toBeInTheDocument();
    expect(screen.getByText('Go Home')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
    expect(screen.getByText('Contact Support')).toBeInTheDocument();
  });

  it('allows custom title and description override', () => {
    render(
      <ErrorPage
        statusCode={404}
        title="Custom Title"
        description="Custom description for testing"
      />
    );

    expect(screen.getByText('Custom Title')).toBeInTheDocument();
    expect(screen.getByText('Custom description for testing')).toBeInTheDocument();
    expect(screen.queryByText('Page Not Found')).not.toBeInTheDocument();
  });

  it('navigates back when Go Back button is clicked', () => {
    render(<ErrorPage statusCode={404} />);

    const backButton = screen.getByText('Go Back');
    fireEvent.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });

  it('navigates to dashboard when Go Home button is clicked', () => {
    render(<ErrorPage statusCode={404} />);

    const homeButton = screen.getByText('Go Home');
    fireEvent.click(homeButton);

    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('reloads page when Try Again button is clicked', () => {
    const reloadMock = vi.fn();
    Object.defineProperty(window, 'location', {
      value: {
        ...window.location,
        reload: reloadMock,
      },
      writable: true,
    });

    render(<ErrorPage statusCode={500} />);

    const tryAgainButton = screen.getByText('Try Again');
    fireEvent.click(tryAgainButton);

    expect(reloadMock).toHaveBeenCalled();
  });

  it('opens mailto when Contact Support button is clicked', () => {
    const openMock = vi.fn();
    window.open = openMock;

    render(<ErrorPage statusCode={500} />);

    const contactButton = screen.getByText('Contact Support');
    fireEvent.click(contactButton);

    expect(openMock).toHaveBeenCalledWith(
      expect.stringContaining('mailto:support@bdc.com')
    );
  });

  it('allows custom button visibility overrides', () => {
    render(
      <ErrorPage
        statusCode={404}
        showBackButton={false}
        showHomeButton={true}
        showRefreshButton={true}
        showContactButton={true}
      />
    );

    expect(screen.queryByText('Go Back')).not.toBeInTheDocument();
    expect(screen.getByText('Go Home')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
    expect(screen.getByText('Contact Support')).toBeInTheDocument();
  });

  it('displays error code and timestamp', () => {
    render(<ErrorPage statusCode={404} />);

    expect(screen.getByText(/Error Code: 404/)).toBeInTheDocument();
    expect(screen.getByText(/Time:/)).toBeInTheDocument();
  });

  it('shows appropriate tip text for each error type', () => {
    const { rerender } = render(<ErrorPage statusCode={404} />);
    expect(screen.getByText(/Check the URL for typos/)).toBeInTheDocument();

    rerender(<ErrorPage statusCode={403} />);
    expect(screen.getByText(/contact your administrator/)).toBeInTheDocument();

    rerender(<ErrorPage statusCode={500} />);
    expect(screen.getByText(/automatically notified/)).toBeInTheDocument();
  });
});