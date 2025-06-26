import React, { useEffect, useState } from 'react';

import { useSocket } from '@/contexts/SocketContext';
import type { ChatUser, TypingStatus } from '@/types/chat';

import { MessageAvatar } from './MessageAvatar';

interface TypingIndicatorProps {
  conversationId: number;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ conversationId }) => {
  const [typingUsers, setTypingUsers] = useState<ChatUser[]>([]);
  const { socket, isConnected } = useSocket();
  const currentUserId = parseInt(localStorage.getItem('user_id') || '0');

  useEffect(() => {
    if (!socket || !isConnected) return;

    // Join conversation room
    socket.emit('join_conversation', conversationId);

    // Listen for typing events
    const handleTypingStatus = (data: TypingStatus & { user: ChatUser }) => {
      if (data.conversationId !== conversationId || data.userId === currentUserId) return;

      setTypingUsers(prev => {
        if (data.isTyping) {
          // Add user if not already typing
          const exists = prev.some(u => u.id === data.userId);
          if (!exists) {
            return [...prev, data.user];
          }
          return prev;
        } else {
          // Remove user from typing
          return prev.filter(u => u.id !== data.userId);
        }
      });
    };

    socket.on('typing_status', handleTypingStatus);

    return () => {
      socket.off('typing_status', handleTypingStatus);
      socket.emit('leave_conversation', conversationId);
    };
  }, [socket, isConnected, conversationId, currentUserId]);

  if (typingUsers.length === 0) return null;

  const getTypingText = () => {
    if (typingUsers.length === 1) {
      return `${typingUsers[0].firstName} yazıyor...`;
    } else if (typingUsers.length === 2) {
      return `${typingUsers[0].firstName} ve ${typingUsers[1].firstName} yazıyor...`;
    } else {
      return `${typingUsers.length} kişi yazıyor...`;
    }
  };

  return (
    <div className="flex items-center gap-2 px-4 py-2">
      <div className="flex -space-x-2">
        {typingUsers.slice(0, 3).map(user => (
          <MessageAvatar key={user.id} user={user} size="xs" />
        ))}
      </div>
      <div className="flex items-center gap-1">
        <span className="text-sm text-gray-500 dark:text-gray-400 italic">
          {getTypingText()}
        </span>
        <div className="flex gap-1">
          <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
};