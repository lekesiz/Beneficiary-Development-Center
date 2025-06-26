/**
 * React Query hooks for Chat
 */
import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { toast } from 'react-hot-toast';

import { chatApi } from '../api/chat';
import type {
  Conversation,
  Message,
  ConversationFilters,
  MessageFilters,
  CreateConversationRequest,
  UpdateConversationRequest,
  SendMessageRequest,
  UpdateMessageRequest,
  MarkAsReadRequest,
  AddParticipantsRequest,
  RemoveParticipantRequest,
  ChatUser,
} from '../types/chat';

// Query Keys
export const chatQueryKeys = {
  all: ['chat'] as const,
  conversations: () => [...chatQueryKeys.all, 'conversations'] as const,
  conversationsList: (filters?: ConversationFilters) =>
    [...chatQueryKeys.conversations(), filters] as const,
  conversationDetail: (id: number) =>
    [...chatQueryKeys.conversations(), id] as const,
  messages: () => [...chatQueryKeys.all, 'messages'] as const,
  messagesList: (conversationId: number) =>
    [...chatQueryKeys.messages(), conversationId] as const,
  messageDetail: (id: number) =>
    [...chatQueryKeys.messages(), 'detail', id] as const,
  users: () => [...chatQueryKeys.all, 'users'] as const,
  userSearch: (query: string) =>
    [...chatQueryKeys.users(), 'search', query] as const,
  statistics: () => [...chatQueryKeys.all, 'statistics'] as const,
  notifications: () => [...chatQueryKeys.all, 'notifications'] as const,
};

/**
 * Hook to get all conversations with filters
 */
export const useConversations = (filters?: ConversationFilters) => {
  return useQuery({
    queryKey: chatQueryKeys.conversationsList(filters),
    queryFn: () => chatApi.getConversations(filters),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute for real-time updates
  });
};

/**
 * Hook to get conversation by ID
 */
export const useConversation = (id: number, enabled = true) => {
  return useQuery({
    queryKey: chatQueryKeys.conversationDetail(id),
    queryFn: () => chatApi.getConversationById(id),
    enabled: enabled && !!id,
    staleTime: 30 * 1000, // 30 seconds
  });
};

/**
 * Hook to get messages with infinite scroll
 */
export const useMessages = (conversationId: number, enabled = true) => {
  return useInfiniteQuery({
    queryKey: chatQueryKeys.messagesList(conversationId),
    queryFn: ({ pageParam }) =>
      chatApi.getMessages({
        conversationId,
        beforeId: pageParam,
        limit: 50,
      }),
    getNextPageParam: (lastPage) => {
      if (!lastPage.hasMore) return undefined;
      return lastPage.oldestMessageId;
    },
    enabled: enabled && !!conversationId,
    staleTime: 10 * 1000, // 10 seconds
    refetchInterval: 30 * 1000, // Refetch every 30 seconds for new messages
  });
};

/**
 * Hook to search users
 */
export const useSearchUsers = (query: string, enabled = true) => {
  return useQuery({
    queryKey: chatQueryKeys.userSearch(query),
    queryFn: () => chatApi.searchUsers(query),
    enabled: enabled && query.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get chat statistics
 */
export const useChatStatistics = () => {
  return useQuery({
    queryKey: chatQueryKeys.statistics(),
    queryFn: () => chatApi.getStatistics(),
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 2 * 60 * 1000, // Refetch every 2 minutes
  });
};

/**
 * Hook to get chat notifications
 */
export const useChatNotifications = (unreadOnly = false) => {
  return useQuery({
    queryKey: [...chatQueryKeys.notifications(), unreadOnly],
    queryFn: () => chatApi.getNotifications(unreadOnly),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute
  });
};

/**
 * Hook to create conversation
 */
export const useCreateConversation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateConversationRequest) => chatApi.createConversation(data),
    onSuccess: (newConversation) => {
      // Invalidate and refetch conversations list
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.conversations() });
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.statistics() });

      // Add to cache
      queryClient.setQueryData(
        chatQueryKeys.conversationDetail(newConversation.id),
        newConversation
      );

      toast.success('Sohbet başarıyla oluşturuldu');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Sohbet oluşturulurken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to update conversation
 */
export const useUpdateConversation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateConversationRequest }) =>
      chatApi.updateConversation(id, data),
    onSuccess: (updatedConversation) => {
      // Update cached data
      queryClient.setQueryData(
        chatQueryKeys.conversationDetail(updatedConversation.id),
        updatedConversation
      );

      // Invalidate lists to refresh
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.conversations() });

      toast.success('Sohbet güncellendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Sohbet güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to delete conversation
 */
export const useDeleteConversation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => chatApi.deleteConversation(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({
        queryKey: chatQueryKeys.conversationDetail(deletedId),
      });

      // Remove messages
      queryClient.removeQueries({
        queryKey: chatQueryKeys.messagesList(deletedId),
      });

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.conversations() });
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.statistics() });

      toast.success('Sohbet silindi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Sohbet silinirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to send message
 */
export const useSendMessage = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SendMessageRequest) => chatApi.sendMessage(data),
    onSuccess: (newMessage) => {
      // Add optimistically to messages list
      queryClient.setQueryData(
        chatQueryKeys.messagesList(newMessage.conversationId),
        (oldData: any) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            pages: oldData.pages.map((page: any, index: number) => {
              if (index === 0) {
                return {
                  ...page,
                  messages: [newMessage, ...page.messages],
                };
              }
              return page;
            }),
          };
        }
      );

      // Invalidate conversation to update last message
      queryClient.invalidateQueries({
        queryKey: chatQueryKeys.conversationDetail(newMessage.conversationId),
      });
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.conversations() });
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Mesaj gönderilirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to update message
 */
export const useUpdateMessage = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateMessageRequest }) =>
      chatApi.updateMessage(id, data),
    onSuccess: (updatedMessage) => {
      // Update in messages list
      queryClient.setQueryData(
        chatQueryKeys.messagesList(updatedMessage.conversationId),
        (oldData: any) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            pages: oldData.pages.map((page: any) => ({
              ...page,
              messages: page.messages.map((msg: Message) =>
                msg.id === updatedMessage.id ? updatedMessage : msg
              ),
            })),
          };
        }
      );

      toast.success('Mesaj güncellendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Mesaj güncellenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to delete message
 */
export const useDeleteMessage = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => chatApi.deleteMessage(id),
    onSuccess: (_, deletedId) => {
      // Remove from all message lists (we don't know which conversation)
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.messages() });

      toast.success('Mesaj silindi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Mesaj silinirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to mark messages as read
 */
export const useMarkAsRead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      conversationId,
      data,
    }: {
      conversationId: number;
      data: MarkAsReadRequest;
    }) => chatApi.markAsRead(conversationId, data),
    onSuccess: (_, { conversationId }) => {
      // Update conversation unread count
      queryClient.invalidateQueries({
        queryKey: chatQueryKeys.conversationDetail(conversationId),
      });
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.conversations() });
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.statistics() });
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.notifications() });
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Mesajlar okundu olarak işaretlenemedi';
      toast.error(message);
    },
  });
};

/**
 * Hook to add participants to conversation
 */
export const useAddParticipants = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      conversationId,
      data,
    }: {
      conversationId: number;
      data: AddParticipantsRequest;
    }) => chatApi.addParticipants(conversationId, data),
    onSuccess: (updatedConversation) => {
      // Update cached conversation
      queryClient.setQueryData(
        chatQueryKeys.conversationDetail(updatedConversation.id),
        updatedConversation
      );

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.conversations() });

      toast.success('Katılımcılar eklendi');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Katılımcılar eklenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to remove participant from conversation
 */
export const useRemoveParticipant = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      conversationId,
      data,
    }: {
      conversationId: number;
      data: RemoveParticipantRequest;
    }) => chatApi.removeParticipant(conversationId, data),
    onSuccess: (updatedConversation) => {
      // Update cached conversation
      queryClient.setQueryData(
        chatQueryKeys.conversationDetail(updatedConversation.id),
        updatedConversation
      );

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.conversations() });

      toast.success('Katılımcı çıkarıldı');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Katılımcı çıkarılırken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to leave conversation
 */
export const useLeaveConversation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (conversationId: number) => chatApi.leaveConversation(conversationId),
    onSuccess: (_, conversationId) => {
      // Remove from cache
      queryClient.removeQueries({
        queryKey: chatQueryKeys.conversationDetail(conversationId),
      });

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.conversations() });
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.statistics() });

      toast.success('Sohbetten ayrıldınız');
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Sohbetten ayrılırken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to upload attachment
 */
export const useUploadAttachment = () => {
  return useMutation({
    mutationFn: (file: File) => chatApi.uploadAttachment(file),
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Dosya yüklenirken hata oluştu';
      toast.error(message);
    },
  });
};

/**
 * Hook to mark notification as read
 */
export const useMarkNotificationAsRead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId: number) =>
      chatApi.markNotificationAsRead(notificationId),
    onSuccess: () => {
      // Invalidate notifications
      queryClient.invalidateQueries({ queryKey: chatQueryKeys.notifications() });
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.message || 'Bildirim okundu olarak işaretlenemedi';
      toast.error(message);
    },
  });
};

/**
 * Hook to send typing status
 */
export const useSendTypingStatus = () => {
  return useMutation({
    mutationFn: ({
      conversationId,
      isTyping,
    }: {
      conversationId: number;
      isTyping: boolean;
    }) => chatApi.sendTypingStatus(conversationId, isTyping),
  });
};

/**
 * Hook to automatically mark messages as read when viewing conversation
 */
export const useAutoMarkAsRead = (conversationId: number, enabled = true) => {
  const markAsRead = useMarkAsRead();
  const { data: messagesData } = useMessages(conversationId, enabled);

  useEffect(() => {
    if (!enabled || !messagesData) return;

    // Get all unread messages
    const unreadMessageIds: number[] = [];
    messagesData.pages.forEach((page) => {
      page.messages.forEach((message) => {
        const currentUserId = parseInt(localStorage.getItem('user_id') || '0');
        const isRead = message.readBy.some((read) => read.userId === currentUserId);
        if (!isRead && message.sender.id !== currentUserId) {
          unreadMessageIds.push(message.id);
        }
      });
    });

    // Mark as read if there are unread messages
    if (unreadMessageIds.length > 0) {
      markAsRead.mutate({
        conversationId,
        data: { messageIds: unreadMessageIds },
      });
    }
  }, [conversationId, enabled, messagesData, markAsRead]);
};