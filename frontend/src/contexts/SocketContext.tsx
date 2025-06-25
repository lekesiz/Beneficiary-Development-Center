import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from 'react';
import toast from 'react-hot-toast';
import { io, Socket } from 'socket.io-client';

import { useAuth } from './AuthContext';

interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  emit: (event: string, data?: any) => void;
  on: (event: string, callback: (data: any) => void) => void;
  off: (event: string, callback?: (data: any) => void) => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

interface SocketProviderProps {
  children: ReactNode;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated && user) {
      // Initialize socket connection
      const socketInstance = io(
        import.meta.env.VITE_API_URL || 'http://localhost:5000',
        {
          auth: {
            token: localStorage.getItem('access_token'),
            tenantId: localStorage.getItem('tenant_id'),
          },
          transports: ['websocket', 'polling'],
        }
      );

      socketInstance.on('connect', () => {
        console.log('Socket connected');
        setIsConnected(true);

        // Join user's room
        socketInstance.emit('join', {
          userId: user.id,
          tenantId: user.tenantId,
        });
      });

      socketInstance.on('disconnect', () => {
        console.log('Socket disconnected');
        setIsConnected(false);
      });

      socketInstance.on('connect_error', (error) => {
        console.error('Socket connection error:', error);
      });

      // Global notification handler
      socketInstance.on('notification', (data) => {
        if (data.type === 'info') {
          toast(data.message, { icon: 'ℹ️' });
        } else if (data.type === 'success') {
          toast.success(data.message);
        } else if (data.type === 'error') {
          toast.error(data.message);
        } else {
          toast(data.message);
        }
      });

      // New notification handler with priority-based styling
      socketInstance.on('notification:new', (notification) => {
        const getNotificationIcon = (priority: string) => {
          switch (priority) {
            case 'urgent':
              return '🚨';
            case 'high':
              return '⚠️';
            case 'medium':
              return 'ℹ️';
            case 'low':
              return '📝';
            default:
              return '🔔';
          }
        };

        const getToastConfig = (priority: string) => {
          switch (priority) {
            case 'urgent':
              return {
                duration: 8000,
                style: {
                  background: '#fee2e2',
                  color: '#991b1b',
                  border: '1px solid #fca5a5',
                },
              };
            case 'high':
              return {
                duration: 6000,
                style: {
                  background: '#fef3c7',
                  color: '#92400e',
                  border: '1px solid #fcd34d',
                },
              };
            case 'medium':
              return {
                duration: 4000,
                style: {
                  background: '#dbeafe',
                  color: '#1e40af',
                  border: '1px solid #93c5fd',
                },
              };
            case 'low':
              return {
                duration: 3000,
                style: {
                  background: '#f0f9ff',
                  color: '#0369a1',
                  border: '1px solid #bae6fd',
                },
              };
            default:
              return { duration: 4000 };
          }
        };

        const icon = getNotificationIcon(notification.priority);
        const config = getToastConfig(notification.priority);

        toast(notification.message, {
          icon,
          ...config,
        });
      });

      setSocket(socketInstance);

      // Cleanup on unmount
      return () => {
        socketInstance.disconnect();
      };
    } else {
      // Disconnect socket if user logs out
      if (socket) {
        socket.disconnect();
        setSocket(null);
        setIsConnected(false);
      }
    }
  }, [isAuthenticated, user]);

  const emit = (event: string, data?: any) => {
    if (socket && isConnected) {
      socket.emit(event, data);
    } else {
      console.warn('Socket not connected. Cannot emit event:', event);
    }
  };

  const on = (event: string, callback: (data: any) => void) => {
    if (socket) {
      socket.on(event, callback);
    }
  };

  const off = (event: string, callback?: (data: any) => void) => {
    if (socket) {
      if (callback) {
        socket.off(event, callback);
      } else {
        socket.off(event);
      }
    }
  };

  const value = {
    socket,
    isConnected,
    emit,
    on,
    off,
  };

  return (
    <SocketContext.Provider value={value}>{children}</SocketContext.Provider>
  );
};
