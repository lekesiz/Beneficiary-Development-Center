import { MessageSquare, Menu, X } from 'lucide-react';
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { useConversation, useAutoMarkAsRead } from '@/hooks/useChat';
import { cn } from '@/lib/utils';

import { ChatInput } from './ChatInput';
import { ConversationList } from './ConversationList';
import { MessageStream } from './MessageStream';

export const ChatLayout: React.FC = () => {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const selectedConversationId = conversationId ? parseInt(conversationId) : undefined;
  const { data: conversation } = useConversation(
    selectedConversationId || 0,
    !!selectedConversationId
  );

  // Auto mark messages as read when viewing conversation
  useAutoMarkAsRead(selectedConversationId || 0, !!selectedConversationId);

  const handleConversationSelect = (id: number) => {
    navigate(`/chat/${id}`);
    setIsMobileSidebarOpen(false);
  };

  return (
    <div className="flex h-full bg-gray-50 dark:bg-gray-900">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between p-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
          >
            {isMobileSidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </Button>
          <h1 className="text-lg font-semibold">Messages</h1>
          <div className="w-10" /> {/* Spacer for balance */}
        </div>
      </div>

      {/* Sidebar - Desktop */}
      <div
        className={cn(
          'hidden lg:block transition-all duration-300 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800',
          isSidebarOpen ? 'w-80' : 'w-0 overflow-hidden'
        )}
      >
        <ConversationList selectedId={selectedConversationId} onSelect={handleConversationSelect} />
      </div>

      {/* Sidebar - Mobile */}
      <div
        className={cn(
          'lg:hidden fixed inset-0 z-50 transform transition-transform duration-300',
          isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div
          className="absolute inset-0 bg-black/50"
          onClick={() => setIsMobileSidebarOpen(false)}
          onKeyDown={(e) => e.key === 'Escape' && setIsMobileSidebarOpen(false)}
          role="button"
          tabIndex={0}
          aria-label="Close sidebar"
        />
        <div className="relative w-80 h-full bg-white dark:bg-gray-800">
          <ConversationList
            selectedId={selectedConversationId}
            onSelect={handleConversationSelect}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Toggle Sidebar Button - Desktop */}
        <div className="hidden lg:block p-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="mb-4"
          >
            <Menu size={20} />
          </Button>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col pt-16 lg:pt-0">
          {selectedConversationId && conversation ? (
            <>
              {/* Conversation Header */}
              <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold">
                      {conversation.type === 'direct'
                        ? conversation.participants.find(
                            (p) => p.id !== parseInt(localStorage.getItem('user_id') || '0')
                          )?.fullName || 'User'
                        : conversation.name || 'Group Chat'}
                    </h2>
                    {conversation.type === 'group' && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {conversation.participants.length} participants
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-hidden">
                <MessageStream conversationId={selectedConversationId} />
              </div>

              {/* Input */}
              <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
                <ChatInput conversationId={selectedConversationId} />
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <EmptyState
                icon={MessageSquare}
                title="Select a chat"
                description="Start by selecting a chat or start a new conversation"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatLayout;
