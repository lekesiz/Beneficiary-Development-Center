import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Send, Paperclip, Smile, X } from 'lucide-react';
import { useSendMessage, useSendTypingStatus, useUploadAttachment } from '@/hooks/useChat';
import type { Message } from '@/types/chat';

interface ChatInputProps {
  conversationId: number;
  replyTo?: Message;
  onCancelReply?: () => void;
  editingMessage?: Message;
  onCancelEdit?: () => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  conversationId,
  replyTo,
  onCancelReply,
  editingMessage,
  onCancelEdit,
}) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  const sendMessage = useSendMessage();
  const sendTypingStatus = useSendTypingStatus();
  const uploadAttachment = useUploadAttachment();

  // Focus textarea on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Set message when editing
  useEffect(() => {
    if (editingMessage) {
      setMessage(editingMessage.content);
      textareaRef.current?.focus();
    }
  }, [editingMessage]);

  // Handle typing status
  const handleTyping = () => {
    if (!isTyping) {
      setIsTyping(true);
      sendTypingStatus.mutate({ conversationId, isTyping: true });
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout to stop typing
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      sendTypingStatus.mutate({ conversationId, isTyping: false });
    }, 3000);
  };

  // Handle input change
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    handleTyping();

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  // Handle send message
  const handleSend = () => {
    if (!message.trim() && !editingMessage) return;

    if (editingMessage) {
      // TODO: Implement edit message
      console.log('Edit message:', editingMessage.id, message);
      onCancelEdit?.();
    } else {
      sendMessage.mutate({
        conversationId,
        content: message.trim(),
        type: 'text',
        replyToId: replyTo?.id,
      });
    }

    setMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Handle file upload
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const attachment = await uploadAttachment.mutateAsync(file);
      sendMessage.mutate({
        conversationId,
        content: file.name,
        type: file.type.startsWith('image/') ? 'image' : 'file',
        attachmentIds: [attachment.id],
      });
    } catch (error) {
      console.error('File upload failed:', error);
    }

    // Reset input
    e.target.value = '';
  };

  // Cleanup typing status on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      if (isTyping) {
        sendTypingStatus.mutate({ conversationId, isTyping: false });
      }
    };
  }, [conversationId, isTyping, sendTypingStatus]);

  return (
    <div className="flex flex-col gap-2">
      {/* Reply/Edit indicator */}
      {(replyTo || editingMessage) && (
        <div className="flex items-center justify-between px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {editingMessage ? 'Mesajı düzenle' : `${replyTo?.sender.firstName}'e yanıt`}
            </p>
            <p className="text-sm truncate">
              {editingMessage?.content || replyTo?.content}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={editingMessage ? onCancelEdit : onCancelReply}
            className="!h-7 !w-7 !p-0"
          >
            <X size={16} />
          </Button>
        </div>
      )}

      {/* Input area */}
      <div className="flex items-end gap-2">
        {/* File upload */}
        <div className="flex-shrink-0">
          <input
            type="file"
            id="file-upload"
            className="hidden"
            onChange={handleFileSelect}
            accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt"
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <div className="inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none hover:bg-accent hover:text-accent-foreground focus-visible:ring-accent h-9 px-3 text-sm">
              <Paperclip size={20} />
            </div>
          </label>
        </div>

        {/* Message input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyPress}
            placeholder="Mesaj yazın..."
            className="w-full px-4 py-2 pr-10 resize-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            rows={1}
            style={{ minHeight: '40px', maxHeight: '120px' }}
          />
          
          {/* Emoji picker button */}
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-2 bottom-2 !h-7 !w-7 !p-0"
            onClick={() => console.log('Open emoji picker')}
          >
            <Smile size={20} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
          </Button>
        </div>

        {/* Send button */}
        <Button
          onClick={handleSend}
          disabled={!message.trim() && !editingMessage}
          size="sm"
          className="flex-shrink-0"
        >
          <Send size={20} />
        </Button>
      </div>
    </div>
  );
};