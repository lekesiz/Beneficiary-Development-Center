/**
 * Example component demonstrating how to use the Socket context for real-time chat
 * This file shows the integration of Socket.io events with React Query
 */
import React, { useState, useEffect, useRef } from 'react';

import { useSocket } from '@/contexts/SocketContext';
import { useMessages, useSendMessage, useAutoMarkAsRead } from '@/hooks/useChat';
import { useChatSocket } from '@/hooks/useChatSocket';
import { useTypingStatus } from '@/hooks/useTypingStatus';

interface ChatComponentExampleProps {
  conversationId: number;
}

export const ChatComponentExample: React.FC<ChatComponentExampleProps> = ({
  conversationId,
}) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Socket connection and methods
  const { socket, on, off } = useSocket();
  
  // Custom hook for chat socket features
  const {
    isConnected,
    sendChatMessage,
    sendTyping,
    markMessagesAsRead,
  } = useChatSocket({ conversationId });

  // React Query hooks
  const { data: messagesData, isLoading } = useMessages(conversationId);
  const sendMessageMutation = useSendMessage();
  
  // Get typing users
  const { data: typingUsers = [] } = useTypingStatus(conversationId);
  
  // Auto-mark messages as read
  useAutoMarkAsRead(conversationId);

  // Handle typing indicator
  useEffect(() => {
    let typingTimeout: NodeJS.Timeout;
    
    const handleInputChange = () => {
      if (!isTyping) {
        setIsTyping(true);
        sendTyping(true);
      }
      
      clearTimeout(typingTimeout);
      typingTimeout = setTimeout(() => {
        setIsTyping(false);
        sendTyping(false);
      }, 1000);
    };

    return () => clearTimeout(typingTimeout);
  }, [isTyping, sendTyping]);

  // Send message handler
  const handleSendMessage = async () => {
    if (!message.trim()) return;
    
    try {
      // Send through API (will also emit socket event from backend)
      await sendMessageMutation.mutateAsync({
        conversationId,
        content: message.trim(),
      });
      
      // Alternatively, you can send directly through socket
      // sendChatMessage(message.trim());
      
      setMessage('');
      setIsTyping(false);
      sendTyping(false);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  // Listen for custom events (example)
  useEffect(() => {
    if (!socket) return;
    
    // Example: Listen for user joined conversation
    const handleUserJoined = (data: { userId: number; userName: string }) => {
      console.log(`${data.userName} joined the conversation`);
    };
    
    on('conversation:user_joined', handleUserJoined);
    
    return () => {
      off('conversation:user_joined', handleUserJoined);
    };
  }, [socket, on, off]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messagesData]);

  // Get all messages from paginated data
  const allMessages = messagesData?.pages.flatMap(page => page.messages) || [];

  return (
    <div className="flex flex-col h-full">
      {/* Connection Status */}
      <div className="px-4 py-2 bg-gray-100 dark:bg-gray-800">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoading ? (
          <div className="text-center text-gray-500">Loading messages...</div>
        ) : (
          <>
            {allMessages.map((msg) => (
              <div
                key={msg.id}
                className="mb-4 p-3 rounded-lg bg-gray-100 dark:bg-gray-800"
              >
                <div className="font-semibold">{msg.sender.fullName}</div>
                <div>{msg.content}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(msg.createdAt).toLocaleTimeString()}
                  {msg.readBy.length > 0 && (
                    <span className="ml-2">
                      ✓✓ Read by {msg.readBy.length}
                    </span>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Typing Indicator */}
      {typingUsers.length > 0 && (
        <div className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400">
          {typingUsers.map(user => user.userName).join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...
        </div>
      )}

      {/* Message Input */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              if (e.target.value) {
                sendTyping(true);
              }
            }}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSendMessage();
              }
            }}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600"
          />
          <button
            onClick={handleSendMessage}
            disabled={!message.trim() || sendMessageMutation.isPending}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {sendMessageMutation.isPending ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * Usage example in a parent component:
 * 
 * import { ChatComponentExample } from '@/examples/ChatComponentExample';
 * 
 * function ChatPage() {
 *   const [selectedConversationId, setSelectedConversationId] = useState<number>(1);
 *   
 *   return (
 *     <div className="h-screen">
 *       <ChatComponentExample conversationId={selectedConversationId} />
 *     </div>
 *   );
 * }
 */