/**
 * Custom hook to integrate Socket.io with chat functionality
 * This demonstrates how to use the Socket context for chat features
 */
import { useEffect, useCallback, useRef } from 'react';
import { useSocket } from '@/contexts/SocketContext';
import { useQueryClient } from '@tanstack/react-query';
import { chatQueryKeys } from './useChat';

interface UseChatSocketOptions {
  conversationId?: number;
  onMessageReceived?: (message: any) => void;
  onTypingUpdate?: (typingUsers: any[]) => void;
}

export const useChatSocket = ({
  conversationId,
  onMessageReceived,
  onTypingUpdate,
}: UseChatSocketOptions = {}) => {
  const { socket, isConnected, sendMessage, sendTypingStatus, markAsRead } = useSocket();
  const queryClient = useQueryClient();
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // Join conversation room when conversationId changes
  useEffect(() => {
    if (socket && isConnected && conversationId) {
      socket.emit('conversation:join', { conversationId });

      return () => {
        socket.emit('conversation:leave', { conversationId });
      };
    }
  }, [socket, isConnected, conversationId]);

  // Send a message through socket
  const sendChatMessage = useCallback(
    (content: string, attachments?: any[]) => {
      if (!conversationId) return;
      
      sendMessage(conversationId, content, attachments);
    },
    [conversationId, sendMessage]
  );

  // Send typing status with debouncing
  const sendTyping = useCallback(
    (isTyping: boolean) => {
      if (!conversationId) return;

      // Clear any existing timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }

      sendTypingStatus(conversationId, isTyping);

      // Auto-stop typing after 3 seconds
      if (isTyping) {
        typingTimeoutRef.current = setTimeout(() => {
          sendTypingStatus(conversationId, false);
        }, 3000);
      }
    },
    [conversationId, sendTypingStatus]
  );

  // Mark messages as read
  const markMessagesAsRead = useCallback(
    (messageIds: number[]) => {
      if (!conversationId || messageIds.length === 0) return;
      
      markAsRead(conversationId, messageIds);
    },
    [conversationId, markAsRead]
  );

  // Get typing users for current conversation
  const getTypingUsers = useCallback(() => {
    if (!conversationId) return [];

    const typingData = queryClient.getQueryData<any[]>(['chat', 'typing', conversationId]);
    return typingData || [];
  }, [conversationId, queryClient]);

  // Listen for typing updates
  useEffect(() => {
    if (!conversationId || !onTypingUpdate) return;

    const checkTypingStatus = () => {
      const typingUsers = getTypingUsers();
      onTypingUpdate(typingUsers);
    };

    // Check typing status every 500ms
    const interval = setInterval(checkTypingStatus, 500);

    return () => clearInterval(interval);
  }, [conversationId, getTypingUsers, onTypingUpdate]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  return {
    isConnected,
    sendChatMessage,
    sendTyping,
    markMessagesAsRead,
    getTypingUsers,
  };
};