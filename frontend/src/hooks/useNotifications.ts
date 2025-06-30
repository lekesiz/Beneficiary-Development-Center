import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/api/client';

// Type definitions for notifications
export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  category: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  is_read: boolean;
  read_at: string | null;
  action_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_prev: boolean;
    has_next: boolean;
  };
  unread_count: number;
}

export interface NotificationSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  categories: {
    program_updates: boolean;
    evaluation_reminders: boolean;
    achievement_notifications: boolean;
    coach_messages: boolean;
    system_alerts: boolean;
  };
  frequency: {
    immediate: boolean;
    daily_digest: boolean;
    weekly_digest: boolean;
  };
  quiet_hours: {
    enabled: boolean;
    start_time: string;
    end_time: string;
  };
}

export interface NotificationsSummary {
  summary: {
    total_notifications: number;
    unread_notifications: number;
    priority_breakdown: Record<string, number>;
    category_breakdown: Record<string, number>;
  };
  recent_notifications: Notification[];
}

// API functions
const notificationsApi = {
  getNotifications: async (params?: {
    page?: number;
    per_page?: number;
    unread_only?: boolean;
    category?: string;
    priority?: string;
  }): Promise<NotificationsResponse> => {
    const searchParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
    }

    const response = await apiClient.get(`/notifications?${searchParams}`);
    return response.data;
  },

  markAsRead: async (notificationId: number): Promise<{ notification: Notification }> => {
    const response = await apiClient.put(`/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllAsRead: async (): Promise<{ updated_count: number }> => {
    const response = await apiClient.put('/notifications/mark-all-read');
    return response.data;
  },

  deleteNotification: async (notificationId: number): Promise<void> => {
    await apiClient.delete(`/notifications/${notificationId}`);
  },

  batchDelete: async (notificationIds: number[]): Promise<{ deleted_count: number }> => {
    const response = await apiClient.post('/notifications/batch-delete', {
      notification_ids: notificationIds
    });
    return response.data;
  },

  getSettings: async (): Promise<{ settings: NotificationSettings }> => {
    const response = await apiClient.get('/notifications/settings');
    return response.data;
  },

  updateSettings: async (settings: Partial<NotificationSettings>): Promise<{ settings: NotificationSettings }> => {
    const response = await apiClient.put('/notifications/settings', settings);
    return response.data;
  },

  sendTestNotification: async (message?: string): Promise<{ notification: Notification }> => {
    const response = await apiClient.post('/notifications/test', { message });
    return response.data;
  },

  getSummary: async (): Promise<NotificationsSummary> => {
    const response = await apiClient.get('/notifications/summary');
    return response.data;
  }
};

// React Query hooks

export const useNotifications = (params?: {
  page?: number;
  per_page?: number;
  unread_only?: boolean;
  category?: string;
  priority?: string;
}) => {
  return useQuery({
    queryKey: ['notifications', params],
    queryFn: () => notificationsApi.getNotifications(params),
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 2 * 60 * 1000, // Refresh every 2 minutes
  });
};

export const useUnreadNotifications = () => {
  return useQuery({
    queryKey: ['notifications', { unread_only: true }],
    queryFn: () => notificationsApi.getNotifications({ unread_only: true }),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 1 * 60 * 1000, // Refresh every minute
  });
};

export const useNotificationsSummary = () => {
  return useQuery({
    queryKey: ['notifications', 'summary'],
    queryFn: notificationsApi.getSummary,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
};

export const useMarkNotificationAsRead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: notificationsApi.markAsRead,
    onSuccess: () => {
      // Invalidate all notification queries to refresh counts
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

export const useMarkAllNotificationsAsRead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: notificationsApi.markAllAsRead,
    onSuccess: () => {
      // Invalidate all notification queries
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

export const useDeleteNotification = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: notificationsApi.deleteNotification,
    onSuccess: () => {
      // Invalidate notification queries
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

export const useBatchDeleteNotifications = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: notificationsApi.batchDelete,
    onSuccess: () => {
      // Invalidate notification queries
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

export const useNotificationSettings = () => {
  return useQuery({
    queryKey: ['notifications', 'settings'],
    queryFn: notificationsApi.getSettings,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useUpdateNotificationSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: notificationsApi.updateSettings,
    onSuccess: () => {
      // Invalidate settings query
      queryClient.invalidateQueries({ queryKey: ['notifications', 'settings'] });
    },
  });
};

export const useSendTestNotification = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: notificationsApi.sendTestNotification,
    onSuccess: () => {
      // Invalidate notification queries to show the new test notification
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

// Custom hook for notification badge count
export const useNotificationBadgeCount = () => {
  const { data: summary } = useNotificationsSummary();
  return summary?.summary.unread_notifications || 0;
};

// Custom hook for real-time notifications (would integrate with Socket.IO)
export const useRealTimeNotifications = () => {
  const queryClient = useQueryClient();

  // This would set up Socket.IO listeners for real-time notifications
  // For now, it's a placeholder that returns the current unread count
  const { data: summary } = useNotificationsSummary();

  const refreshNotifications = () => {
    queryClient.invalidateQueries({ queryKey: ['notifications'] });
  };

  return {
    unreadCount: summary?.summary.unread_notifications || 0,
    refreshNotifications,
  };
};