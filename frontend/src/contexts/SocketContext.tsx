import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
  useCallback,
} from 'react';
import toast from 'react-hot-toast';
import { io, Socket } from 'socket.io-client';
import { useQueryClient } from '@tanstack/react-query';

import { useAuth } from './AuthContext';
import { chatQueryKeys } from '@/hooks/useChat';
import type { Message } from '@/types/chat';

interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  emit: (event: string, data?: any) => void;
  on: (event: string, callback: (data: any) => void) => void;
  off: (event: string, callback?: (data: any) => void) => void;
  // Chat-specific methods
  sendMessage: (conversationId: number, content: string, attachments?: any[]) => void;
  sendTypingStatus: (conversationId: number, isTyping: boolean) => void;
  markAsRead: (conversationId: number, messageIds: number[]) => void;
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
  const queryClient = useQueryClient();

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

      // Chat event listeners
      
      // New message event
      socketInstance.on('message:new', (message: Message) => {
        // Update messages in the conversation
        queryClient.setQueryData(
          chatQueryKeys.messagesList(message.conversationId),
          (oldData: any) => {
            if (!oldData) return oldData;
            
            // Check if message already exists (to prevent duplicates)
            const messageExists = oldData.pages.some((page: any) =>
              page.messages.some((msg: Message) => msg.id === message.id)
            );
            
            if (messageExists) return oldData;
            
            return {
              ...oldData,
              pages: oldData.pages.map((page: any, index: number) => {
                if (index === 0) {
                  return {
                    ...page,
                    messages: [message, ...page.messages],
                  };
                }
                return page;
              }),
            };
          }
        );

        // Update conversation list to show latest message
        queryClient.invalidateQueries({ 
          queryKey: chatQueryKeys.conversations() 
        });

        // Show notification for new message if not from current user
        const currentUserId = parseInt(localStorage.getItem('user_id') || '0');
        if (message.sender.id !== currentUserId) {
          const senderName = message.sender.fullName || `${message.sender.firstName} ${message.sender.lastName}`;
          toast(`${senderName}: ${message.content}`, {
            icon: '💬',
            duration: 5000,
          });
        }
      });

      // Typing status event
      socketInstance.on('message:typing', (data: {
        conversationId: number;
        userId: number;
        userName: string;
        isTyping: boolean;
      }) => {
        // You can store typing status in a separate state or context
        // For now, we'll just log it
        console.log('Typing status:', data);
        
        // Optionally, you can store this in React Query cache
        queryClient.setQueryData(
          ['chat', 'typing', data.conversationId],
          (oldData: any) => {
            if (!oldData) {
              return data.isTyping ? [data] : [];
            }
            
            if (data.isTyping) {
              // Add user to typing list
              return [...oldData.filter((t: any) => t.userId !== data.userId), data];
            } else {
              // Remove user from typing list
              return oldData.filter((t: any) => t.userId !== data.userId);
            }
          }
        );
      });

      // Read receipt event
      socketInstance.on('message:read_receipt', (data: {
        conversationId: number;
        messageIds: number[];
        userId: number;
        readAt: string;
      }) => {
        // Update messages in cache to mark them as read
        queryClient.setQueryData(
          chatQueryKeys.messagesList(data.conversationId),
          (oldData: any) => {
            if (!oldData) return oldData;
            
            return {
              ...oldData,
              pages: oldData.pages.map((page: any) => ({
                ...page,
                messages: page.messages.map((msg: Message) => {
                  if (data.messageIds.includes(msg.id)) {
                    // Add read receipt to message
                    const readByExists = msg.readBy.some(
                      (read) => read.userId === data.userId
                    );
                    
                    if (!readByExists) {
                      return {
                        ...msg,
                        readBy: [
                          ...msg.readBy,
                          {
                            userId: data.userId,
                            readAt: data.readAt,
                          },
                        ],
                      };
                    }
                  }
                  return msg;
                }),
              })),
            };
          }
        );

        // Update conversation unread count
        queryClient.invalidateQueries({
          queryKey: chatQueryKeys.conversationDetail(data.conversationId),
        });
      });

      setSocket(socketInstance);

      // Cleanup on unmount
      return () => {
        // Remove all chat event listeners
        socketInstance.off('message:new');
        socketInstance.off('message:typing');
        socketInstance.off('message:read_receipt');
        socketInstance.off('notification');
        socketInstance.off('notification:new');
        socketInstance.off('connect');
        socketInstance.off('disconnect');
        socketInstance.off('connect_error');
        
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
  }, [isAuthenticated, user, queryClient]);

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

  // Chat-specific methods
  const sendMessage = useCallback(
    (conversationId: number, content: string, attachments?: any[]) => {
      if (socket && isConnected) {
        socket.emit('message:send', {
          conversationId,
          content,
          attachments,
        });
      } else {
        console.warn('Socket not connected. Cannot send message');
      }
    },
    [socket, isConnected]
  );

  const sendTypingStatus = useCallback(
    (conversationId: number, isTyping: boolean) => {
      if (socket && isConnected) {
        socket.emit('message:typing', {
          conversationId,
          isTyping,
        });
      }
    },
    [socket, isConnected]
  );

  const markAsRead = useCallback(
    (conversationId: number, messageIds: number[]) => {
      if (socket && isConnected) {
        socket.emit('message:mark_read', {
          conversationId,
          messageIds,
        });
      }
    },
    [socket, isConnected]
  );

  const value = {
    socket,
    isConnected,
    emit,
    on,
    off,
    sendMessage,
    sendTypingStatus,
    markAsRead,
  };

  return (
    <SocketContext.Provider value={value}>{children}</SocketContext.Provider>
  );
};
