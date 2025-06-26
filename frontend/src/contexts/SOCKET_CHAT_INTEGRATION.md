# Socket Context - Chat Integration Guide

This document explains how to use the updated Socket Context for real-time chat functionality.

## Overview

The Socket Context has been enhanced to handle chat-related events and integrate with React Query for seamless cache updates. It provides real-time functionality for:

- New message notifications
- Typing indicators
- Read receipts
- Automatic cache synchronization

## Socket Events

### Incoming Events (Server → Client)

#### `message:new`
Fired when a new message is sent in any conversation the user is part of.

```typescript
{
  id: number;
  conversationId: number;
  sender: ChatUser;
  content: string;
  // ... other message properties
}
```

#### `message:typing`
Fired when a user starts or stops typing in a conversation.

```typescript
{
  conversationId: number;
  userId: number;
  userName: string;
  isTyping: boolean;
}
```

#### `message:read_receipt`
Fired when messages are marked as read by a user.

```typescript
{
  conversationId: number;
  messageIds: number[];
  userId: number;
  readAt: string;
}
```

### Outgoing Events (Client → Server)

#### `message:send`
Send a new message to a conversation.

```typescript
socket.emit('message:send', {
  conversationId: number;
  content: string;
  attachments?: any[];
});
```

#### `message:typing`
Send typing status to other participants.

```typescript
socket.emit('message:typing', {
  conversationId: number;
  isTyping: boolean;
});
```

#### `message:mark_read`
Mark messages as read.

```typescript
socket.emit('message:mark_read', {
  conversationId: number;
  messageIds: number[];
});
```

## Usage Examples

### Basic Usage

```typescript
import { useSocket } from '@/contexts/SocketContext';

function ChatComponent() {
  const { 
    isConnected, 
    sendMessage, 
    sendTypingStatus, 
    markAsRead 
  } = useSocket();
  
  // Send a message
  const handleSendMessage = (conversationId: number, content: string) => {
    sendMessage(conversationId, content);
  };
  
  // Send typing status
  const handleTyping = (conversationId: number) => {
    sendTypingStatus(conversationId, true);
    
    // Stop typing after 2 seconds
    setTimeout(() => {
      sendTypingStatus(conversationId, false);
    }, 2000);
  };
  
  // Mark messages as read
  const handleMarkAsRead = (conversationId: number, messageIds: number[]) => {
    markAsRead(conversationId, messageIds);
  };
}
```

### Using the Custom Hook

```typescript
import { useChatSocket } from '@/hooks/useChatSocket';

function ChatWindow({ conversationId }: { conversationId: number }) {
  const {
    isConnected,
    sendChatMessage,
    sendTyping,
    markMessagesAsRead,
    getTypingUsers,
  } = useChatSocket({ conversationId });
  
  // Component logic...
}
```

### Listening for Custom Events

```typescript
import { useSocket } from '@/contexts/SocketContext';
import { useEffect } from 'react';

function ChatNotifications() {
  const { socket, on, off } = useSocket();
  
  useEffect(() => {
    if (!socket) return;
    
    const handleNewMessage = (message: Message) => {
      // Custom handling for new messages
      console.log('New message received:', message);
    };
    
    on('message:new', handleNewMessage);
    
    return () => {
      off('message:new', handleNewMessage);
    };
  }, [socket, on, off]);
}
```

## Integration with React Query

The Socket Context automatically updates React Query caches when events are received:

1. **New Messages**: Added to the message list cache for the conversation
2. **Typing Status**: Stored in a separate query cache with key `['chat', 'typing', conversationId]`
3. **Read Receipts**: Updates message objects in the cache with read status

### Accessing Typing Status

```typescript
import { useTypingStatus } from '@/hooks/useTypingStatus';

function TypingIndicator({ conversationId }: { conversationId: number }) {
  const { data: typingUsers = [] } = useTypingStatus(conversationId);
  
  if (typingUsers.length === 0) return null;
  
  return (
    <div>
      {typingUsers.map(user => user.userName).join(', ')} 
      {typingUsers.length === 1 ? 'is' : 'are'} typing...
    </div>
  );
}
```

## Best Practices

1. **Connection Management**: Always check `isConnected` before sending events
2. **Cleanup**: Use the `off` method to remove event listeners when components unmount
3. **Typing Debounce**: Implement debouncing for typing indicators to avoid excessive events
4. **Error Handling**: Socket methods log warnings when not connected but don't throw errors
5. **Cache Updates**: Let the Socket Context handle cache updates automatically - avoid manual cache manipulation for real-time events

## Complete Example

See `/src/examples/ChatComponentExample.tsx` for a complete implementation demonstrating all features.