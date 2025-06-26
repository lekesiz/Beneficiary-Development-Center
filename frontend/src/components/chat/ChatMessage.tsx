import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { MessageAvatar } from './MessageAvatar';
import { MessageActions } from './MessageActions';
import { format } from 'date-fns';
import { Check, CheckCheck, Edit2, Reply } from 'lucide-react';
import type { Message } from '@/types/chat';

interface ChatMessageProps {
  message: Message;
  isFirstInSequence: boolean;
  isLastInSequence: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isFirstInSequence,
  isLastInSequence,
}) => {
  const [showActions, setShowActions] = useState(false);
  const currentUserId = parseInt(localStorage.getItem('user_id') || '0');
  const isOwnMessage = message.sender.id === currentUserId;

  // Check if message is read by all recipients
  const isReadByAll = message.readBy.length >= 2; // Assuming direct messages for now

  // Format message content based on type
  const renderContent = () => {
    switch (message.type) {
      case 'image':
        return (
          <div className="max-w-sm">
            <img
              src={message.attachments?.[0]?.url}
              alt="Shared image"
              className="rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
              onClick={() => window.open(message.attachments?.[0]?.url, '_blank')}
            />
          </div>
        );
      
      case 'file':
        return (
          <a
            href={message.attachments?.[0]?.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <span className="text-2xl">📎</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {message.attachments?.[0]?.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {formatFileSize(message.attachments?.[0]?.size || 0)}
              </p>
            </div>
          </a>
        );
      
      case 'system':
        return (
          <div className="text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400 italic">
              {message.content}
            </p>
          </div>
        );
      
      default:
        return (
          <div className="break-words whitespace-pre-wrap">
            {message.content}
          </div>
        );
    }
  };

  if (message.type === 'system') {
    return (
      <div className="flex justify-center my-4">
        {renderContent()}
      </div>
    );
  }

  return (
    <div
      className={cn(
        'flex gap-2 mb-1',
        isOwnMessage ? 'justify-end' : 'justify-start',
        isLastInSequence && 'mb-4'
      )}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Avatar for other users */}
      {!isOwnMessage && (
        <div className="flex-shrink-0 w-8">
          {isLastInSequence && (
            <MessageAvatar user={message.sender} size="sm" />
          )}
        </div>
      )}

      {/* Message content */}
      <div className={cn('flex flex-col max-w-[70%]', isOwnMessage && 'items-end')}>
        {/* Sender name for first message in sequence */}
        {!isOwnMessage && isFirstInSequence && (
          <span className="text-xs text-gray-500 dark:text-gray-400 mb-1 ml-3">
            {message.sender.fullName}
          </span>
        )}

        <div className="flex items-end gap-2">
          {/* Actions (shown on hover) */}
          {showActions && (
            <div className={cn('opacity-0 animate-fadeIn', isOwnMessage && 'order-2')}>
              <MessageActions
                message={message}
                isOwnMessage={isOwnMessage}
              />
            </div>
          )}

          {/* Message bubble */}
          <div
            className={cn(
              'relative px-4 py-2 rounded-2xl',
              isOwnMessage
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100',
              isOwnMessage && !isFirstInSequence && 'rounded-tr-md',
              isOwnMessage && !isLastInSequence && 'rounded-br-md',
              !isOwnMessage && !isFirstInSequence && 'rounded-tl-md',
              !isOwnMessage && !isLastInSequence && 'rounded-bl-md'
            )}
          >
            {/* Reply indicator */}
            {message.replyTo && (
              <div className={cn(
                'mb-2 p-2 -mx-2 -mt-1 rounded-lg border-l-2',
                isOwnMessage 
                  ? 'bg-blue-400/20 border-blue-300' 
                  : 'bg-gray-200 dark:bg-gray-600 border-gray-400 dark:border-gray-500'
              )}>
                <div className="flex items-center gap-1 mb-1">
                  <Reply size={12} />
                  <span className="text-xs font-medium">
                    {message.replyTo.sender.firstName}
                  </span>
                </div>
                <p className="text-xs opacity-75 line-clamp-2">
                  {message.replyTo.content}
                </p>
              </div>
            )}

            {/* Message content */}
            {renderContent()}

            {/* Edit indicator */}
            {message.isEdited && (
              <span className={cn(
                'text-xs ml-2',
                isOwnMessage ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
              )}>
                (düzenlendi)
              </span>
            )}
          </div>
        </div>

        {/* Time and read status */}
        {isLastInSequence && (
          <div className={cn(
            'flex items-center gap-1 mt-1 text-xs',
            isOwnMessage ? 'mr-3' : 'ml-3'
          )}>
            <span className="text-gray-500 dark:text-gray-400">
              {format(new Date(message.createdAt), 'HH:mm')}
            </span>
            {isOwnMessage && (
              <span className="text-gray-500 dark:text-gray-400">
                {isReadByAll ? (
                  <CheckCheck size={14} className="text-blue-500" />
                ) : (
                  <Check size={14} />
                )}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to format file size
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}