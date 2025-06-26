import React from 'react';
import { Avatar } from '@/components/ui/Avatar';
import type { ChatUser } from '@/types/chat';

interface MessageAvatarProps {
  user: ChatUser;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  showOnlineStatus?: boolean;
}

export const MessageAvatar: React.FC<MessageAvatarProps> = ({
  user,
  size = 'sm',
  showOnlineStatus = false,
}) => {
  return (
    <div className="relative">
      <Avatar
        src={user.avatarUrl}
        alt={user.fullName}
        fallback={user.fullName}
        size={size}
      />
      {showOnlineStatus && user.isOnline && (
        <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-white dark:border-gray-800" />
      )}
    </div>
  );
};