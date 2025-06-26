"""Chat service for managing conversations and messages."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session

from app.models.chat import Conversation, ChatMessage
from app.models.user import User
from app.services.base import BaseService
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError
from app.core.logging import logger


class ChatService(BaseService[Conversation]):
    """Service for managing chat conversations and messages."""

    def __init__(self, db: Session):
        """Initialize the chat service."""
        super().__init__(Conversation, db)
        self.message_model = ChatMessage

    def get_user_conversations(
        self,
        user_id: int,
        tenant_id: int,
        page: int = 1,
        per_page: int = 20,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """Get all conversations for a user with pagination."""
        try:
            # Base query for conversations where user is a participant
            query = self.db.query(Conversation).filter(
                Conversation.tenant_id == tenant_id,
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id
                )
            )
            
            # Filter active conversations if requested
            if active_only:
                query = query.filter(Conversation.is_active == True)
            
            # Order by last message timestamp
            query = query.order_by(desc(Conversation.last_message_at))
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            conversations = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # Convert to dict with additional info
            conversations_data = []
            for conv in conversations:
                conv_dict = conv.to_dict(current_user_id=user_id)
                conversations_data.append(conv_dict)
            
            return {
                "conversations": conversations_data,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            raise

    def get_or_create_conversation(
        self,
        user1_id: int,
        user2_id: int,
        tenant_id: int
    ) -> Conversation:
        """Get existing conversation or create a new one between two users."""
        try:
            # Ensure user1_id is always the smaller ID for consistency
            if user1_id > user2_id:
                user1_id, user2_id = user2_id, user1_id
            
            # Check if conversation already exists
            conversation = self.db.query(Conversation).filter(
                Conversation.tenant_id == tenant_id,
                Conversation.user1_id == user1_id,
                Conversation.user2_id == user2_id
            ).first()
            
            if conversation:
                return conversation
            
            # Create new conversation
            conversation = Conversation(
                user1_id=user1_id,
                user2_id=user2_id,
                tenant_id=tenant_id
            )
            
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            
            return conversation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    def get_conversation_messages(
        self,
        conversation_id: int,
        user_id: int,
        tenant_id: int,
        page: int = 1,
        per_page: int = 50,
        before_timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get messages for a conversation with pagination."""
        try:
            # First verify the conversation exists and user has access
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.tenant_id == tenant_id
            ).first()
            
            if not conversation:
                raise NotFoundError("Conversation not found")
            
            # Check if user is a participant
            if user_id not in [conversation.user1_id, conversation.user2_id]:
                raise ForbiddenError("You are not a participant in this conversation")
            
            # Base query for messages
            query = self.db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.tenant_id == tenant_id,
                ChatMessage.is_deleted == False
            )
            
            # Filter out messages deleted for this user
            if user_id == conversation.user1_id:
                query = query.filter(ChatMessage.deleted_for_sender == False)
            else:
                query = query.filter(ChatMessage.deleted_for_receiver == False)
            
            # Filter by timestamp if provided (for loading older messages)
            if before_timestamp:
                query = query.filter(ChatMessage.created_at < before_timestamp)
            
            # Order by creation time descending (newest first)
            query = query.order_by(desc(ChatMessage.created_at))
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            messages = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # Reverse to have oldest first in the response
            messages.reverse()
            
            # Mark conversation as read for this user
            conversation.mark_as_read(user_id)
            
            # Convert to dict
            messages_data = [msg.to_dict() for msg in messages]
            
            return {
                "messages": messages_data,
                "conversation_id": conversation_id,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {str(e)}")
            raise

    def send_message(
        self,
        sender_id: int,
        receiver_id: int,
        content: str,
        tenant_id: int,
        message_metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Send a message from one user to another."""
        try:
            # Get or create conversation
            conversation = self.get_or_create_conversation(
                sender_id, 
                receiver_id, 
                tenant_id
            )
            
            # Create message
            message = ChatMessage(
                conversation_id=conversation.id,
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content,
                tenant_id=tenant_id,
                message_metadata=message_metadata or {}
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            # Update conversation's last message info
            conversation.update_last_message(message)
            
            return message
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error sending message: {str(e)}")
            raise

    def mark_messages_as_read(
        self,
        conversation_id: int,
        user_id: int,
        tenant_id: int
    ) -> int:
        """Mark all messages in a conversation as read for a user."""
        try:
            # Get unread messages
            unread_messages = self.db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.receiver_id == user_id,
                ChatMessage.tenant_id == tenant_id,
                ChatMessage.read_at.is_(None)
            ).all()
            
            # Mark each as read
            count = 0
            for message in unread_messages:
                message.mark_as_read()
                count += 1
            
            self.db.commit()
            
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking messages as read: {str(e)}")
            raise

    def delete_message(
        self,
        message_id: int,
        user_id: int,
        tenant_id: int
    ) -> bool:
        """Soft delete a message for a user."""
        try:
            message = self.db.query(ChatMessage).filter(
                ChatMessage.id == message_id,
                ChatMessage.tenant_id == tenant_id
            ).first()
            
            if not message:
                raise NotFoundError("Message not found")
            
            # Check if user is sender or receiver
            if user_id not in [message.sender_id, message.receiver_id]:
                raise ForbiddenError("You cannot delete this message")
            
            # Soft delete for the user
            message.delete_for_user(user_id)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting message: {str(e)}")
            raise

    def get_unread_count(self, user_id: int, tenant_id: int) -> int:
        """Get total unread message count for a user."""
        try:
            count = self.db.query(ChatMessage).filter(
                ChatMessage.receiver_id == user_id,
                ChatMessage.tenant_id == tenant_id,
                ChatMessage.read_at.is_(None),
                ChatMessage.is_deleted == False,
                ChatMessage.deleted_for_receiver == False
            ).count()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            raise