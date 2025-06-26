import React, { useState } from 'react';
import { ConversationItem } from './ConversationItem';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { EmptyState } from '@/components/ui/EmptyState';
import { Search, Plus, MessageSquare } from 'lucide-react';
import { useConversations } from '@/hooks/useChat';
import type { ConversationFilters } from '@/types/chat';

interface ConversationListProps {
  selectedId?: number;
  onSelect: (id: number) => void;
}

export const ConversationList: React.FC<ConversationListProps> = ({
  selectedId,
  onSelect,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<ConversationFilters>({
    search: '',
  });

  const { data, isLoading, error } = useConversations(filters);

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setFilters(prev => ({ ...prev, search: value }));
  };

  const handleNewConversation = () => {
    // TODO: Open new conversation modal
    console.log('New conversation');
  };

  if (error) {
    return (
      <div className="p-4">
        <EmptyState
          icon={MessageSquare}
          title="Hata"
          description="Sohbetler yüklenirken bir hata oluştu"
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Mesajlar</h2>
          <Button
            size="sm"
            onClick={handleNewConversation}
            title="Yeni Sohbet"
          >
            <Plus size={16} />
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
          <Input
            type="text"
            placeholder="Sohbet ara..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <LoadingSpinner />
          </div>
        ) : data?.conversations.length === 0 ? (
          <EmptyState
            icon={MessageSquare}
            title="Sohbet Yok"
            description={searchQuery ? "Aramanızla eşleşen sohbet bulunamadı" : "Henüz bir sohbet başlatmadınız"}
            action={
              !searchQuery && (
                <Button onClick={handleNewConversation}>
                  Yeni Sohbet Başlat
                </Button>
              )
            }
          />
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {data?.conversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isSelected={conversation.id === selectedId}
                onClick={() => onSelect(conversation.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};