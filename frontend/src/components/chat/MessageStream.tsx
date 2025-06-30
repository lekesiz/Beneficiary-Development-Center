import { format, isToday, isYesterday } from 'date-fns';
import { MessageSquare, AlertCircle } from 'lucide-react';
import React, { useEffect, useRef, useCallback, useState } from 'react';
import { useInView } from 'react-intersection-observer';

import { EmptyState } from '@/components/ui/EmptyState';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useMessages } from '@/hooks/useChat';

import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';

interface MessageStreamProps {
  conversationId: number;
}

export const MessageStream: React.FC<MessageStreamProps> = ({ conversationId }) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  const { data, isLoading, error, hasNextPage, fetchNextPage, isFetchingNextPage } =
    useMessages(conversationId);

  // Intersection observer for infinite scroll
  const { ref: topRef } = useInView({
    threshold: 0,
    rootMargin: '100px',
    onChange: (inView) => {
      if (inView && hasNextPage && !isFetchingNextPage) {
        fetchNextPage();
      }
    },
  });

  // Format date header
  const formatDateHeader = (date: Date) => {
    if (isToday(date)) return 'Today';
    if (isYesterday(date)) return 'Yesterday';
    return format(date, 'd MMMM yyyy');
  };

  // Group messages by date
  const groupMessagesByDate = useCallback(() => {
    if (!data?.pages) return [];

    const groups: Array<{ date: string; messages: any[] }> = [];
    const allMessages = data.pages.flatMap((page: any) => page.messages || []).reverse();

    allMessages.forEach((message) => {
      const messageDate = formatDateHeader(new Date(message.createdAt));
      const existingGroup = groups.find((g) => g.date === messageDate);

      if (existingGroup) {
        existingGroup.messages.push(message);
      } else {
        groups.push({ date: messageDate, messages: [message] });
      }
    });

    return groups;
  }, [data]);

  // Scroll to bottom
  const scrollToBottom = useCallback((smooth = true) => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto' });
    }
  }, []);

  // Handle scroll events
  const handleScroll = useCallback(() => {
    if (!scrollContainerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
    setAutoScroll(isNearBottom);
  }, []);

  // Auto scroll to bottom on new messages
  useEffect(() => {
    if (autoScroll && data?.pages?.[0]?.messages?.length) {
      scrollToBottom();
    }
  }, [data?.pages?.[0]?.messages?.length, autoScroll, scrollToBottom]);

  // Initial scroll to bottom
  useEffect(() => {
    scrollToBottom(false);
  }, [conversationId, scrollToBottom]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <EmptyState
          icon={AlertCircle}
          title="Error"
          description="An error occurred while loading messages"
          action={{
            text: 'Refresh',
            onClick: () => window.location.reload(),
          }}
        />
      </div>
    );
  }

  const messageGroups = groupMessagesByDate();

  if (messageGroups.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <EmptyState
          icon={MessageSquare}
          title="No messages yet"
          description="Send a message to start the conversation"
        />
      </div>
    );
  }

  return (
    <div
      ref={scrollContainerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto px-4 py-4"
    >
      {/* Load more indicator */}
      <div ref={topRef} className="h-1" />
      {isFetchingNextPage && (
        <div className="flex justify-center py-4">
          <LoadingSpinner size="sm" />
        </div>
      )}

      {/* Messages */}
      {messageGroups.map((group) => (
        <div key={group.date}>
          {/* Date Header */}
          <div className="flex items-center justify-center my-4">
            <div className="bg-gray-200 dark:bg-gray-700 px-3 py-1 rounded-full">
              <span className="text-xs text-gray-600 dark:text-gray-400">{group.date}</span>
            </div>
          </div>

          {/* Messages */}
          {group.messages.map((message, messageIndex) => {
            const previousMessage = messageIndex > 0 ? group.messages[messageIndex - 1] : null;
            const nextMessage =
              messageIndex < group.messages.length - 1 ? group.messages[messageIndex + 1] : null;

            // Check if this is the first message from this sender in a sequence
            const isFirstInSequence =
              !previousMessage || previousMessage.sender.id !== message.sender.id;

            // Check if this is the last message from this sender in a sequence
            const isLastInSequence = !nextMessage || nextMessage.sender.id !== message.sender.id;

            return (
              <ChatMessage
                key={message.id}
                message={message}
                isFirstInSequence={isFirstInSequence}
                isLastInSequence={isLastInSequence}
              />
            );
          })}
        </div>
      ))}

      {/* Typing Indicator */}
      <TypingIndicator conversationId={conversationId} />

      {/* Bottom ref for scrolling */}
      <div ref={bottomRef} />
    </div>
  );
};
