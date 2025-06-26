"""Chat models for real-time messaging between users."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import TenantBaseModel
from app.extensions import db


class Conversation(TenantBaseModel):
    """Conversation model representing a chat thread between two users."""

    __tablename__ = "conversations"

    # Basic fields
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Participants
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Conversation metadata
    last_message_at = Column(DateTime)
    last_message_preview = Column(String(255))  # Preview of the last message
    
    # Read status for each user
    user1_last_read_at = Column(DateTime)
    user2_last_read_at = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)  # Can be used to archive conversations
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], backref="conversations_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], backref="conversations_as_user2")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    # Indexes and constraints
    __table_args__ = (
        # Ensure unique conversation between two users within a tenant
        UniqueConstraint("user1_id", "user2_id", "tenant_id", name="_users_tenant_uc"),
        # Index for efficient querying by users
        Index("idx_conversation_user1", "user1_id"),
        Index("idx_conversation_user2", "user2_id"),
        Index("idx_conversation_last_message", "last_message_at"),
    )
    
    def get_other_user(self, current_user_id):
        """Get the other participant in the conversation."""
        return self.user2 if self.user1_id == current_user_id else self.user1
    
    def get_unread_count(self, user_id):
        """Get count of unread messages for a user."""
        last_read = self.user1_last_read_at if self.user1_id == user_id else self.user2_last_read_at
        
        if not last_read:
            # If never read, all messages are unread
            return len(self.messages)
        
        # Count messages after last read
        return sum(1 for msg in self.messages if msg.created_at > last_read and msg.sender_id != user_id)
    
    def mark_as_read(self, user_id):
        """Mark conversation as read for a user."""
        if self.user1_id == user_id:
            self.user1_last_read_at = datetime.utcnow()
        else:
            self.user2_last_read_at = datetime.utcnow()
        self.save()
    
    def update_last_message(self, message):
        """Update last message information."""
        self.last_message_at = message.created_at
        self.last_message_preview = message.content[:255] if len(message.content) > 255 else message.content
        self.save()
    
    def to_dict(self, current_user_id=None, include_messages=False):
        """Convert to dictionary."""
        data = super().to_dict()
        
        # Add computed fields
        if current_user_id:
            other_user = self.get_other_user(current_user_id)
            data["other_user"] = {
                "id": other_user.id,
                "full_name": other_user.full_name,
                "email": other_user.email,
                "avatar_url": other_user.avatar_url,
            }
            data["unread_count"] = self.get_unread_count(current_user_id)
            
        # Include recent messages if requested
        if include_messages:
            # Get last 50 messages by default
            recent_messages = sorted(self.messages, key=lambda m: m.created_at, reverse=True)[:50]
            data["messages"] = [msg.to_dict() for msg in reversed(recent_messages)]
        
        # Convert UUID to string
        if "uuid" in data:
            data["uuid"] = str(data["uuid"])
            
        return data
    
    def __repr__(self):
        """String representation."""
        return f"<Conversation between User:{self.user1_id} and User:{self.user2_id}>"


class ChatMessage(TenantBaseModel):
    """Chat message model for individual messages within conversations."""

    __tablename__ = "chat_messages"

    # Basic fields
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Relationships
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    
    # Status fields
    read_at = Column(DateTime)  # When the message was read by receiver
    delivered_at = Column(DateTime)  # When the message was delivered to receiver
    edited_at = Column(DateTime)  # If message was edited
    
    # Metadata
    message_metadata = Column(db.JSON, default=dict)  # For attachments, links, etc.
    
    # Soft delete support
    is_deleted = Column(Boolean, default=False)
    deleted_for_sender = Column(Boolean, default=False)
    deleted_for_receiver = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_message_conversation", "conversation_id"),
        Index("idx_message_sender", "sender_id"),
        Index("idx_message_receiver", "receiver_id"),
        Index("idx_message_created", "created_at"),
        Index("idx_message_read_status", "receiver_id", "read_at"),
    )
    
    def mark_as_read(self):
        """Mark message as read."""
        if not self.read_at:
            self.read_at = datetime.utcnow()
            self.save()
            
    def mark_as_delivered(self):
        """Mark message as delivered."""
        if not self.delivered_at:
            self.delivered_at = datetime.utcnow()
            self.save()
    
    def edit_content(self, new_content):
        """Edit message content."""
        self.content = new_content
        self.edited_at = datetime.utcnow()
        self.save()
    
    def delete_for_user(self, user_id):
        """Soft delete message for a specific user."""
        if user_id == self.sender_id:
            self.deleted_for_sender = True
        elif user_id == self.receiver_id:
            self.deleted_for_receiver = True
            
        # If deleted for both users, mark as fully deleted
        if self.deleted_for_sender and self.deleted_for_receiver:
            self.is_deleted = True
            
        self.save()
    
    def to_dict(self, exclude=None):
        """Convert to dictionary."""
        data = super().to_dict(exclude=exclude)
        
        # Add sender information
        data["sender"] = {
            "id": self.sender.id,
            "full_name": self.sender.full_name,
            "avatar_url": self.sender.avatar_url,
        }
        
        # Add status flags
        data["is_read"] = self.read_at is not None
        data["is_delivered"] = self.delivered_at is not None
        data["is_edited"] = self.edited_at is not None
        
        # Convert UUID to string
        if "uuid" in data:
            data["uuid"] = str(data["uuid"])
            
        return data
    
    def __repr__(self):
        """String representation."""
        return f"<ChatMessage from User:{self.sender_id} to User:{self.receiver_id}>"