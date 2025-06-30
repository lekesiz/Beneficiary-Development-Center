/**
 * Chat system types
 */

export interface ChatUser {
  id: number;
  uuid: string;
  firstName: string;
  lastName: string;
  fullName: string;
  avatarUrl?: string;
  role: string;
  isOnline?: boolean;
  lastSeenAt?: string;
}

export interface Conversation {
  id: number;
  uuid: string;
  type: 'direct' | 'group';
  name?: string; // For group conversations
  avatarUrl?: string; // For group conversations
  participants: ChatUser[];
  lastMessage?: Message;
  unreadCount: number;
  isPinned: boolean;
  isMuted: boolean;
  createdAt: string;
  updatedAt: string;
  lastMessageAt?: string;
}

export interface Message {
  id: number;
  uuid: string;
  conversationId: number;
  sender: ChatUser;
  content: string;
  type: 'text' | 'image' | 'file' | 'system';
  attachments?: MessageAttachment[];
  readBy: MessageReadStatus[];
  isEdited: boolean;
  editedAt?: string;
  replyTo?: Message;
  createdAt: string;
  updatedAt: string;
}

export interface MessageAttachment {
  id: number;
  url: string;
  name: string;
  size: number;
  mimeType: string;
  thumbnailUrl?: string;
}

export interface MessageReadStatus {
  userId: number;
  readAt: string;
}

export interface ConversationFilters {
  type?: 'direct' | 'group';
  search?: string;
  hasUnread?: boolean;
  isPinned?: boolean;
  participantId?: number;
  page?: number;
  limit?: number;
}

export interface MessageFilters {
  conversationId: number;
  search?: string;
  beforeId?: number;
  afterId?: number;
  limit?: number;
}

export interface ConversationsResponse {
  conversations: Conversation[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface MessagesResponse {
  messages: Message[];
  total: number;
  hasMore: boolean;
  oldestMessageId?: number;
  newestMessageId?: number;
}

export interface CreateConversationRequest {
  type: 'direct' | 'group';
  participantIds: number[];
  name?: string; // Required for group conversations
  avatarUrl?: string;
}

export interface UpdateConversationRequest {
  name?: string;
  avatarUrl?: string;
  isPinned?: boolean;
  isMuted?: boolean;
}

export interface SendMessageRequest {
  conversationId: number;
  content: string;
  type?: 'text' | 'image' | 'file';
  attachmentIds?: number[];
  replyToId?: number;
}

export interface UpdateMessageRequest {
  content: string;
}

export interface MarkAsReadRequest {
  messageIds: number[];
}

export interface AddParticipantsRequest {
  userIds: number[];
}

export interface RemoveParticipantRequest {
  userId: number;
}

export interface TypingStatus {
  conversationId: number;
  userId: number;
  isTyping: boolean;
}

export interface OnlineStatus {
  userId: number;
  isOnline: boolean;
  lastSeenAt?: string;
}

export interface ChatNotification {
  id: number;
  type: 'new_message' | 'mention' | 'reaction';
  conversationId: number;
  messageId?: number;
  senderId: number;
  content: string;
  isRead: boolean;
  createdAt: string;
}

export interface ChatStatistics {
  totalConversations: number;
  unreadConversations: number;
  totalMessages: number;
  unreadMessages: number;
  activeConversations: number;
}
