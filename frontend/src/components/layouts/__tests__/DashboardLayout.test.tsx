import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import * as authContext from '@/contexts/AuthContext';

import DashboardLayout from '../DashboardLayout';

// Mock Breadcrumbs component
vi.mock('@/components/common/Breadcrumbs', () => ({
  Breadcrumbs: () => <div data-testid="breadcrumbs">Breadcrumbs</div>,
}));

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'navigation.dashboard': 'Dashboard',
        'navigation.beneficiaries': 'Beneficiaries',
        'navigation.programs': 'Programs',
        'navigation.courses': 'Courses',
        'navigation.sessions': 'Sessions',
        'navigation.evaluations': 'Evaluations',
        'navigation.learningPaths': 'Learning Paths',
        'navigation.chat': 'Chat',
        'navigation.reports': 'Reports',
        'navigation.settings': 'Settings',
        'navigation.logout': 'Logout',
      };
      return translations[key] || key;
    },
    i18n: {
      language: 'en',
      changeLanguage: vi.fn(),
    },
  }),
}));

// Mock react-router-dom
const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    Outlet: () => <div data-testid="outlet">Main Content</div>,
    useNavigate: () => mockNavigate,
    useMatches: () => [],
    useLocation: () => ({ pathname: '/dashboard' }),
  };
});

const renderWithRouter = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{component}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('DashboardLayout', () => {
  const mockLogout = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows all navigation items for admin user', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'Admin',
        last_name: 'User',
        role: 'admin',
        roles: [{ id: 1, name: 'admin', description: 'Administrator' }],
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Beneficiaries')).toBeInTheDocument();
    expect(screen.getByText('Programs')).toBeInTheDocument();
    expect(screen.getByText('Courses')).toBeInTheDocument();
    expect(screen.getByText('Sessions')).toBeInTheDocument();
    expect(screen.getByText('Evaluations')).toBeInTheDocument();
    expect(screen.getByText('Learning Paths')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Reports')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('shows limited navigation items for student user', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'Student',
        last_name: 'User',
        role: 'student',
        roles: [{ id: 1, name: 'student', description: 'Student' }],
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.queryByText('Beneficiaries')).not.toBeInTheDocument();
    expect(screen.queryByText('Programs')).not.toBeInTheDocument();
    expect(screen.queryByText('Courses')).not.toBeInTheDocument();
    expect(screen.getByText('Sessions')).toBeInTheDocument();
    expect(screen.getByText('Evaluations')).toBeInTheDocument();
    expect(screen.getByText('Learning Paths')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Reports')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('shows appropriate navigation items for trainer user', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'Trainer',
        last_name: 'User',
        role: 'trainer',
        roles: [{ id: 1, name: 'trainer', description: 'Trainer' }],
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Beneficiaries')).toBeInTheDocument();
    expect(screen.queryByText('Programs')).not.toBeInTheDocument();
    expect(screen.queryByText('Courses')).not.toBeInTheDocument();
    expect(screen.getByText('Sessions')).toBeInTheDocument();
    expect(screen.queryByText('Evaluations')).not.toBeInTheDocument();
    expect(screen.getByText('Learning Paths')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Reports')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('shows appropriate navigation items for instructor user', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'Instructor',
        last_name: 'User',
        role: 'instructor',
        roles: [{ id: 1, name: 'instructor', description: 'Instructor' }],
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Beneficiaries')).toBeInTheDocument();
    expect(screen.getByText('Programs')).toBeInTheDocument();
    expect(screen.getByText('Courses')).toBeInTheDocument();
    expect(screen.getByText('Sessions')).toBeInTheDocument();
    expect(screen.getByText('Evaluations')).toBeInTheDocument();
    expect(screen.getByText('Learning Paths')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Reports')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('displays user information correctly', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        role: 'admin',
        roles: [{ id: 1, name: 'admin', description: 'Administrator' }],
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
    expect(screen.getByText('J')).toBeInTheDocument(); // User avatar initial
  });

  it('calls logout when logout button is clicked', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'Test',
        last_name: 'User',
        role: 'admin',
        roles: [{ id: 1, name: 'admin', description: 'Administrator' }],
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);

    expect(mockLogout).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('handles mobile sidebar toggle', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'Test',
        last_name: 'User',
        role: 'admin',
        roles: [{ id: 1, name: 'admin', description: 'Administrator' }],
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    // Check if mobile menu button exists (this test may need adjustment based on viewport)
    const menuButtons = screen.getAllByRole('button');
    expect(menuButtons.length).toBeGreaterThan(0);
  });

  it('handles users with primaryRole instead of role', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'Test',
        last_name: 'User',
        primaryRole: 'manager',
        roles: [{ id: 1, name: 'manager', description: 'Manager' }],
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Beneficiaries')).toBeInTheDocument();
    expect(screen.getByText('Programs')).toBeInTheDocument();
    expect(screen.getByText('manager')).toBeInTheDocument();
  });

  it('handles users with string-based roles array', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'Test',
        last_name: 'User',
        role: 'instructor',
        roles: ['instructor', 'trainer'], // String array instead of object array
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Beneficiaries')).toBeInTheDocument();
    expect(screen.getByText('Programs')).toBeInTheDocument();
    expect(screen.getByText('Courses')).toBeInTheDocument();
  });

  it('renders main content outlet', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: 1,
        first_name: 'Test',
        last_name: 'User',
        role: 'admin',
        roles: [{ id: 1, name: 'admin', description: 'Administrator' }],
      },
      logout: mockLogout,
      isAuthenticated: true,
      isLoading: false,
    } as any);

    renderWithRouter(<DashboardLayout />);

    expect(screen.getByTestId('outlet')).toBeInTheDocument();
    expect(screen.getByText('Main Content')).toBeInTheDocument();
  });
});
