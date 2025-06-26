import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';

import { usersApi } from '@/api/users';

import Settings from '../Settings';

// Mock the API
vi.mock('@/api/users', () => ({
  usersApi: {
    getPreferences: vi.fn(),
    updatePreferences: vi.fn(),
  },
}));

// Mock toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Settings Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockPreferences = {
    notifications: {
      email: {
        new_message: true,
        appointment_reminder: true,
        evaluation_completed: false,
        course_enrollment: true,
        program_update: true,
      },
      in_app: {
        new_message: true,
        appointment_reminder: true,
        evaluation_completed: true,
        course_enrollment: true,
        program_update: true,
      },
    },
  };

  it('should render the settings page with tabs', () => {
    vi.mocked(usersApi.getPreferences).mockResolvedValue({
      data: { preferences: mockPreferences },
    } as any);

    render(<Settings />, { wrapper: createWrapper() });

    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Manage your account settings and preferences')).toBeInTheDocument();

    // Check tabs
    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Security')).toBeInTheDocument();
    expect(screen.getByText('Appearance')).toBeInTheDocument();
  });

  it('should switch between tabs', async () => {
    vi.mocked(usersApi.getPreferences).mockResolvedValue({
      data: { preferences: mockPreferences },
    } as any);

    render(<Settings />, { wrapper: createWrapper() });

    // Default tab should be Profile
    expect(screen.getByText('Profile Settings')).toBeInTheDocument();

    // Click on Notifications tab
    fireEvent.click(screen.getByText('Notifications'));
    
    // Wait for notification preferences to load
    await waitFor(() => {
      expect(screen.getByText('Notification Preferences')).toBeInTheDocument();
    });

    // Click on Security tab
    fireEvent.click(screen.getByText('Security'));
    expect(screen.getByText('Security Settings')).toBeInTheDocument();

    // Click on Appearance tab
    fireEvent.click(screen.getByText('Appearance'));
    expect(screen.getByText('Appearance Settings')).toBeInTheDocument();
  });

  it('should load and display notification preferences', async () => {
    vi.mocked(usersApi.getPreferences).mockResolvedValue({
      data: { preferences: mockPreferences },
    } as any);

    render(<Settings />, { wrapper: createWrapper() });

    // Switch to Notifications tab
    fireEvent.click(screen.getByText('Notifications'));

    await waitFor(() => {
      expect(screen.getByText('New Messages')).toBeInTheDocument();
      expect(screen.getByText('Appointment Reminders')).toBeInTheDocument();
      expect(screen.getByText('Evaluation Completed')).toBeInTheDocument();
      expect(screen.getByText('Course Enrollment')).toBeInTheDocument();
      expect(screen.getByText('Program Updates')).toBeInTheDocument();
    });

    // Check that API was called
    expect(usersApi.getPreferences).toHaveBeenCalledTimes(1);
  });

  it('should update notification preferences when toggling switches', async () => {
    vi.mocked(usersApi.getPreferences).mockResolvedValue({
      data: { preferences: mockPreferences },
    } as any);

    const updatedPreferences = {
      ...mockPreferences,
      notifications: {
        ...mockPreferences.notifications,
        email: {
          ...mockPreferences.notifications.email,
          new_message: false,
        },
      },
    };

    vi.mocked(usersApi.updatePreferences).mockResolvedValue({
      data: {
        message: 'Preferences updated successfully',
        preferences: updatedPreferences,
      },
    } as any);

    render(<Settings />, { wrapper: createWrapper() });

    // Switch to Notifications tab
    fireEvent.click(screen.getByText('Notifications'));

    await waitFor(() => {
      expect(screen.getByText('New Messages')).toBeInTheDocument();
    });

    // Find and click the email toggle for new messages
    const emailToggles = screen.getAllByRole('button', { name: /Toggle email notifications/i });
    fireEvent.click(emailToggles[0]);

    await waitFor(() => {
      expect(usersApi.updatePreferences).toHaveBeenCalledWith(
        expect.objectContaining({
          notifications: expect.objectContaining({
            email: expect.objectContaining({
              new_message: false,
            }),
          }),
        })
      );
    });
  });

  it('should handle tab navigation with URL hash', async () => {
    vi.mocked(usersApi.getPreferences).mockResolvedValue({
      data: { preferences: mockPreferences },
    } as any);

    // Set initial hash
    window.location.hash = '#notifications';

    render(<Settings />, { wrapper: createWrapper() });

    // Should open notifications tab directly
    await waitFor(() => {
      expect(screen.getByText('Notification Preferences')).toBeInTheDocument();
    });
  });
});