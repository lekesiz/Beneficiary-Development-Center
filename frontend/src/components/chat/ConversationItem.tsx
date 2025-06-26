import { formatDistanceToNow , tr } from 'date-fns';
import { Pin, VolumeX } from 'lucide-react';
import React from 'react';

import { Avatar } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils';
import type { Conversation } from '@/types/chat';

interface ConversationItemProps {
  conversation: Conversation;
  isSelected: boolean;
  onClick: () => void;
}

export const ConversationItem: React.FC<ConversationItemProps> = ({
  conversation,
  isSelected,
  onClick,
}) => {
  const currentUserId = parseInt(localStorage.getItem('user_id') || '0');
  
  // Get display name and avatar
  const getDisplayInfo = () => {
    if (conversation.type === 'direct') {
      const otherUser = conversation.participants.find(p => p.id !== currentUserId);
      return {
        name: otherUser?.fullName || 'Kullanıcı',
        avatar: otherUser?.avatarUrl,
        fallback: otherUser?.fullName || 'K',
        isOnline: otherUser?.isOnline,
      };
    }
    return {
      name: conversation.name || 'Grup Sohbeti',
      avatar: conversation.avatarUrl,
      fallback: conversation.name || 'G',
      isOnline: false,
    };
  };

  const displayInfo = getDisplayInfo();

  // Format last message
  const getLastMessagePreview = () => {
    if (!conversation.lastMessage) return 'Henüz mesaj yok';
    
    const isSentByMe = conversation.lastMessage.sender.id === currentUserId;
    const prefix = isSentByMe ? 'Sen: ' : `${conversation.lastMessage.sender.firstName}: `;
    
    if (conversation.lastMessage.type === 'image') {
      return `${prefix}📷 Fotoğraf`;
    }
    if (conversation.lastMessage.type === 'file') {
      return `${prefix}📎 Dosya`;
    }
    
    const maxLength = 50;
    const content = conversation.lastMessage.content;
    return prefix + (content.length > maxLength ? content.substring(0, maxLength) + '...' : content);
  };

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-4 cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-700/50',
        isSelected && 'bg-gray-100 dark:bg-gray-700'
      )}
      onClick={onClick}
    >
      {/* Avatar */}
      <div className="relative flex-shrink-0">
        <Avatar
          src={displayInfo.avatar}
          fallback={displayInfo.name}
          alt={displayInfo.name}
          size="md"
        />
        {displayInfo.isOnline && (
          <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-gray-800" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            <h3 className={cn(
              'font-medium truncate',
              conversation.unreadCount > 0 && 'text-gray-900 dark:text-white'
            )}>
              {displayInfo.name}
            </h3>
            {conversation.isPinned && (
              <Pin className="text-gray-400" size={14} />
            )}
            {conversation.isMuted && (
              <VolumeX className="text-gray-400" size={14} />
            )}
          </div>
          {conversation.lastMessageAt && (
            <span className="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0">
              {formatDistanceToNow(new Date(conversation.lastMessageAt), {
                addSuffix: true,
                locale: tr,
              })}
            </span>
          )}
        </div>
        
        <div className="flex items-center justify-between">
          <p className={cn(
            'text-sm truncate',
            conversation.unreadCount > 0 
              ? 'text-gray-900 dark:text-white font-medium' 
              : 'text-gray-600 dark:text-gray-400'
          )}>
            {getLastMessagePreview()}
          </p>
          {conversation.unreadCount > 0 && (
            <Badge variant="default" size="sm" className="ml-2 flex-shrink-0">
              {conversation.unreadCount > 99 ? '99+' : conversation.unreadCount}
            </Badge>
          )}
        </div>
      </div>
    </div>
  );
};