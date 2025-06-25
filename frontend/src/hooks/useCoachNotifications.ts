import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

import { toast } from '@/components/ui/Toast';
import { useAuth } from '@/contexts/AuthContext';

export interface CoachNotification {
  id: string;
  type: 'help_request' | 'milestone_completed';
  student_id: number;
  student_name: string;
  milestone_id: number;
  milestone_title: string;
  learning_path_title: string;
  message?: string;
  timestamp: string;
  priority?: 'high' | 'medium' | 'low';
  path_completed?: boolean;
  read: boolean;
}

interface UseCoachNotificationsReturn {
  notifications: CoachNotification[];
  unreadCount: number;
  markAsRead: (notificationId: string) => void;
  markAllAsRead: () => void;
  clearNotification: (notificationId: string) => void;
  isConnected: boolean;
}

export function useCoachNotifications(): UseCoachNotificationsReturn {
  const { user, token } = useAuth();
  const queryClient = useQueryClient();
  const [socket, setSocket] = useState<Socket | null>(null);
  const [notifications, setNotifications] = useState<CoachNotification[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize Socket.IO connection
  useEffect(() => {
    if (
      !user ||
      !token ||
      !['admin', 'manager', 'instructor', 'trainer'].includes(user.role)
    ) {
      return;
    }

    const socketInstance = io(
      process.env.REACT_APP_API_URL || 'http://localhost:5000',
      {
        auth: {
          token: token,
        },
        transports: ['websocket', 'polling'],
        withCredentials: true,
      }
    );

    socketInstance.on('connect', () => {
      console.log('Connected to notification service');
      setIsConnected(true);
    });

    socketInstance.on('disconnect', () => {
      console.log('Disconnected from notification service');
      setIsConnected(false);
    });

    socketInstance.on(
      'coach_notification',
      (notification: Omit<CoachNotification, 'id' | 'read'>) => {
        const newNotification: CoachNotification = {
          ...notification,
          id: `${notification.type}_${notification.student_id}_${
            notification.milestone_id
          }_${Date.now()}`,
          read: false,
        };

        setNotifications((prev) => [newNotification, ...prev]);

        // Show toast notification
        if (notification.type === 'help_request') {
          toast({
            title: '🆘 Yardım Talebi',
            description: `${notification.student_name} "${notification.milestone_title}" için yardım istiyor`,
            variant: 'warning',
            duration: 5000,
          });
        } else if (notification.type === 'milestone_completed') {
          toast({
            title: '✅ Milestone Tamamlandı',
            description: `${notification.student_name} "${notification.milestone_title}" hedefini tamamladı`,
            variant: 'success',
            duration: 4000,
          });
        }

        // Invalidate relevant queries
        queryClient.invalidateQueries({ queryKey: ['studentMilestones'] });
        queryClient.invalidateQueries({ queryKey: ['coachStudents'] });
      }
    );

    setSocket(socketInstance);

    return () => {
      socketInstance.disconnect();
    };
  }, [user, token, queryClient]);

  // Load persisted notifications from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('coach_notifications');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setNotifications(parsed);
      } catch (error) {
        console.error('Failed to parse saved notifications:', error);
      }
    }
  }, []);

  // Save notifications to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('coach_notifications', JSON.stringify(notifications));
  }, [notifications]);

  const markAsRead = useCallback((notificationId: string) => {
    setNotifications((prev) =>
      prev.map((notif) =>
        notif.id === notificationId ? { ...notif, read: true } : notif
      )
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((notif) => ({ ...notif, read: true })));
  }, []);

  const clearNotification = useCallback((notificationId: string) => {
    setNotifications((prev) =>
      prev.filter((notif) => notif.id !== notificationId)
    );
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    clearNotification,
    isConnected,
  };
}
