import { render, screen, fireEvent } from '@testing-library/react';
import { useNavigate } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import * as authContext from '@/contexts/AuthContext';
import { renderWithProviders } from '@/tests/utils/test-utils';

import ReportsList from '../ReportsList';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

const mockNavigate = vi.fn();

describe('ReportsList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useNavigate).mockReturnValue(mockNavigate);
  });

  it('renders the reports listing page with title and description', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        role: 'student',
        roles: [{ id: 1, name: 'student', description: 'Student' }],
      },
      isAuthenticated: true,
      isLoading: false,
    } as any);

    render(<ReportsList />);

    expect(screen.getByText('Reports & Analytics')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Access comprehensive reports and analytics to track progress and performance.'
      )
    ).toBeInTheDocument();
  });

  it('shows My Development Report for all users', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        role: 'student',
        roles: [{ id: 1, name: 'student', description: 'Student' }],
      },
      isAuthenticated: true,
      isLoading: false,
    } as any);

    render(<ReportsList />);

    expect(screen.getByText('My Development Report')).toBeInTheDocument();
    expect(
      screen.getByText(
        'View your personal learning progress, skill development, and achievement summary.'
      )
    ).toBeInTheDocument();
  });

  it('shows role-specific reports for admin users', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        role: 'admin',
        roles: [{ id: 1, name: 'admin', description: 'Administrator' }],
      },
      isAuthenticated: true,
      isLoading: false,
    } as any);

    render(<ReportsList />);

    expect(screen.getByText('Program Analytics')).toBeInTheDocument();
    expect(screen.getByText('Beneficiary Overview')).toBeInTheDocument();
    expect(screen.getByText('Evaluation Insights')).toBeInTheDocument();
  });

  it('navigates to correct route when report card is clicked', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        role: 'student',
        roles: [{ id: 1, name: 'student', description: 'Student' }],
      },
      isAuthenticated: true,
      isLoading: false,
    } as any);

    render(<ReportsList />);

    const reportCard = screen.getByText('My Development Report').closest('div');
    fireEvent.click(reportCard!);

    expect(mockNavigate).toHaveBeenCalledWith('/reports/my-development');
  });

  it('shows quick actions for admin users', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        role: 'admin',
        roles: [{ id: 1, name: 'admin', description: 'Administrator' }],
      },
      isAuthenticated: true,
      isLoading: false,
    } as any);

    render(<ReportsList />);

    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('Export All Data')).toBeInTheDocument();
    expect(screen.getByText('Schedule Reports')).toBeInTheDocument();
    expect(screen.getByText('Create Custom Report')).toBeInTheDocument();
  });

  it('does not show quick actions for non-admin users', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        role: 'student',
        roles: [{ id: 1, name: 'student', description: 'Student' }],
      },
      isAuthenticated: true,
      isLoading: false,
    } as any);

    render(<ReportsList />);

    expect(screen.queryByText('Quick Actions')).not.toBeInTheDocument();
  });

  it('shows empty state when user has no access to reports', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: null,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    render(<ReportsList />);

    expect(screen.getByText('No Reports Available')).toBeInTheDocument();
    expect(
      screen.getByText(
        "You don't have access to any reports at this time. Contact your administrator for access."
      )
    ).toBeInTheDocument();
  });
});
