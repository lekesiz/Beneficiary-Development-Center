import React from 'react';
import { Button } from '@/components/ui/Button';
import { Reply, Edit2, Trash2, Copy, MoreVertical } from 'lucide-react';
import { useUpdateMessage, useDeleteMessage } from '@/hooks/useChat';
import type { Message } from '@/types/chat';

interface MessageActionsProps {
  message: Message;
  isOwnMessage: boolean;
  onReply?: () => void;
  onEdit?: () => void;
}

export const MessageActions: React.FC<MessageActionsProps> = ({
  message,
  isOwnMessage,
  onReply,
  onEdit,
}) => {
  const updateMessage = useUpdateMessage();
  const deleteMessage = useDeleteMessage();

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
  };

  const handleDelete = () => {
    if (window.confirm('Bu mesajı silmek istediğinizden emin misiniz?')) {
      deleteMessage.mutate(message.id);
    }
  };

  return (
    <div className="flex items-center gap-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-1">
      <Button
        variant="ghost"
        size="sm"
        onClick={onReply}
        title="Yanıtla"
        className="!h-7 !w-7 !p-0"
      >
        <Reply size={14} />
      </Button>

      {message.type === 'text' && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          title="Kopyala"
          className="!h-7 !w-7 !p-0"
        >
          <Copy size={14} />
        </Button>
      )}

      {isOwnMessage && message.type === 'text' && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onEdit}
          title="Düzenle"
          className="!h-7 !w-7 !p-0"
        >
          <Edit2 size={14} />
        </Button>
      )}

      {isOwnMessage && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDelete}
          title="Sil"
          className="text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300 !h-7 !w-7 !p-0"
        >
          <Trash2 size={14} />
        </Button>
      )}
    </div>
  );
};