/**
 * Chat API client
 */
import type {
  Conversation,
  Message,
  ConversationFilters,
  MessageFilters,
  ConversationsResponse,
  MessagesResponse,
  CreateConversationRequest,
  UpdateConversationRequest,
  SendMessageRequest,
  UpdateMessageRequest,
  MarkAsReadRequest,
  AddParticipantsRequest,
  RemoveParticipantRequest,
  ChatUser,
  ChatStatistics,
  ChatNotification,
} from '../types/chat';

import apiClient from './client';

const CHAT_BASE_URL = '/chat';

export const chatApi = {
  /**
   * Get all conversations with optional filters
   */
  getConversations: async (filters?: ConversationFilters): Promise<ConversationsResponse> => {
    const params = new URLSearchParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const response = await apiClient.get<ConversationsResponse>(
      `${CHAT_BASE_URL}/conversations?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get conversation by ID
   */
  getConversationById: async (id: number): Promise<Conversation> => {
    const response = await apiClient.get<Conversation>(
      `${CHAT_BASE_URL}/conversations/${id}`
    );
    return response.data;
  },

  /**
   * Create new conversation
   */
  createConversation: async (data: CreateConversationRequest): Promise<Conversation> => {
    const response = await apiClient.post<Conversation>(
      `${CHAT_BASE_URL}/conversations`,
      data
    );
    return response.data;
  },

  /**
   * Update conversation
   */
  updateConversation: async (
    id: number,
    data: UpdateConversationRequest
  ): Promise<Conversation> => {
    const response = await apiClient.put<Conversation>(
      `${CHAT_BASE_URL}/conversations/${id}`,
      data
    );
    return response.data;
  },

  /**
   * Delete conversation
   */
  deleteConversation: async (id: number): Promise<void> => {
    await apiClient.delete(`${CHAT_BASE_URL}/conversations/${id}`);
  },

  /**
   * Get messages in a conversation
   */
  getMessages: async (filters: MessageFilters): Promise<MessagesResponse> => {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });

    const response = await apiClient.get<MessagesResponse>(
      `${CHAT_BASE_URL}/messages?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get message by ID
   */
  getMessageById: async (id: number): Promise<Message> => {
    const response = await apiClient.get<Message>(
      `${CHAT_BASE_URL}/messages/${id}`
    );
    return response.data;
  },

  /**
   * Send a message
   */
  sendMessage: async (data: SendMessageRequest): Promise<Message> => {
    const response = await apiClient.post<Message>(
      `${CHAT_BASE_URL}/messages`,
      data
    );
    return response.data;
  },

  /**
   * Update a message
   */
  updateMessage: async (id: number, data: UpdateMessageRequest): Promise<Message> => {
    const response = await apiClient.put<Message>(
      `${CHAT_BASE_URL}/messages/${id}`,
      data
    );
    return response.data;
  },

  /**
   * Delete a message
   */
  deleteMessage: async (id: number): Promise<void> => {
    await apiClient.delete(`${CHAT_BASE_URL}/messages/${id}`);
  },

  /**
   * Mark messages as read
   */
  markAsRead: async (conversationId: number, data: MarkAsReadRequest): Promise<void> => {
    await apiClient.post(
      `${CHAT_BASE_URL}/conversations/${conversationId}/read`,
      data
    );
  },

  /**
   * Add participants to a group conversation
   */
  addParticipants: async (
    conversationId: number,
    data: AddParticipantsRequest
  ): Promise<Conversation> => {
    const response = await apiClient.post<Conversation>(
      `${CHAT_BASE_URL}/conversations/${conversationId}/participants`,
      data
    );
    return response.data;
  },

  /**
   * Remove participant from a group conversation
   */
  removeParticipant: async (
    conversationId: number,
    data: RemoveParticipantRequest
  ): Promise<Conversation> => {
    const response = await apiClient.delete<Conversation>(
      `${CHAT_BASE_URL}/conversations/${conversationId}/participants/${data.userId}`
    );
    return response.data;
  },

  /**
   * Leave a group conversation
   */
  leaveConversation: async (conversationId: number): Promise<void> => {
    await apiClient.post(
      `${CHAT_BASE_URL}/conversations/${conversationId}/leave`
    );
  },

  /**
   * Search users for starting conversations
   */
  searchUsers: async (query: string): Promise<ChatUser[]> => {
    const response = await apiClient.get<ChatUser[]>(
      `${CHAT_BASE_URL}/users/search?q=${encodeURIComponent(query)}`
    );
    return response.data;
  },

  /**
   * Get chat statistics
   */
  getStatistics: async (): Promise<ChatStatistics> => {
    const response = await apiClient.get<ChatStatistics>(
      `${CHAT_BASE_URL}/statistics`
    );
    return response.data;
  },

  /**
   * Get chat notifications
   */
  getNotifications: async (unreadOnly = false): Promise<ChatNotification[]> => {
    const params = unreadOnly ? '?unread_only=true' : '';
    const response = await apiClient.get<ChatNotification[]>(
      `${CHAT_BASE_URL}/notifications${params}`
    );
    return response.data;
  },

  /**
   * Mark notification as read
   */
  markNotificationAsRead: async (notificationId: number): Promise<void> => {
    await apiClient.put(
      `${CHAT_BASE_URL}/notifications/${notificationId}/read`
    );
  },

  /**
   * Upload attachment
   */
  uploadAttachment: async (file: File): Promise<{ id: number; url: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<{ id: number; url: string }>(
      `${CHAT_BASE_URL}/attachments`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Send typing status
   */
  sendTypingStatus: async (conversationId: number, isTyping: boolean): Promise<void> => {
    await apiClient.post(
      `${CHAT_BASE_URL}/conversations/${conversationId}/typing`,
      { isTyping }
    );
  },
};

export default chatApi;