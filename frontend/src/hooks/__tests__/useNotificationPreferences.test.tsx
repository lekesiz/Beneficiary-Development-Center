import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import { usersApi } from '@/api/users';

import { useNotificationPreferences } from '../useNotificationPreferences';

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
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useNotificationPreferences', () => {
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

  it('should fetch notification preferences', async () => {
    vi.mocked(usersApi.getPreferences).mockResolvedValue({
      data: { preferences: mockPreferences },
    } as any);

    const { result } = renderHook(() => useNotificationPreferences(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.preferences).toEqual(mockPreferences);
    expect(usersApi.getPreferences).toHaveBeenCalledTimes(1);
  });

  it('should update notification preferences', async () => {
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

    const { result } = renderHook(() => useNotificationPreferences(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    result.current.updatePreferences(updatedPreferences);

    await waitFor(() => {
      expect(result.current.isUpdating).toBe(false);
    });

    expect(usersApi.updatePreferences).toHaveBeenCalledWith(updatedPreferences);
  });

  it('should handle errors when fetching preferences', async () => {
    const error = new Error('Failed to fetch preferences');
    vi.mocked(usersApi.getPreferences).mockRejectedValue(error);

    const { result } = renderHook(() => useNotificationPreferences(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.preferences).toBeUndefined();
  });
});
