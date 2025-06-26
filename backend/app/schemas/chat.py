"""Schemas for chat-related operations."""

from marshmallow import Schema, fields, validate


class ConversationSchema(Schema):
    """Schema for conversation data."""
    
    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    user1_id = fields.Integer(required=True)
    user2_id = fields.Integer(required=True)
    last_message_at = fields.DateTime(dump_only=True)
    last_message_preview = fields.String(dump_only=True)
    user1_last_read_at = fields.DateTime(dump_only=True)
    user2_last_read_at = fields.DateTime(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    other_user = fields.Dict(dump_only=True)
    unread_count = fields.Integer(dump_only=True)
    messages = fields.List(fields.Dict(), dump_only=True)


class ChatMessageSchema(Schema):
    """Schema for chat message data."""
    
    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    conversation_id = fields.Integer(required=True)
    sender_id = fields.Integer(required=True)
    receiver_id = fields.Integer(required=True)
    content = fields.String(required=True, validate=validate.Length(min=1, max=5000))
    read_at = fields.DateTime(dump_only=True)
    delivered_at = fields.DateTime(dump_only=True)
    edited_at = fields.DateTime(dump_only=True)
    message_metadata = fields.Dict(required=False)
    is_deleted = fields.Boolean(dump_only=True)
    deleted_for_sender = fields.Boolean(dump_only=True)
    deleted_for_receiver = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    sender = fields.Dict(dump_only=True)
    is_read = fields.Boolean(dump_only=True)
    is_delivered = fields.Boolean(dump_only=True)
    is_edited = fields.Boolean(dump_only=True)


class SendMessageRequestSchema(Schema):
    """Schema for sending a message request."""
    
    receiver_id = fields.Integer(required=True)
    content = fields.String(required=True, validate=validate.Length(min=1, max=5000))
    message_metadata = fields.Dict(required=False)


class CreateConversationRequestSchema(Schema):
    """Schema for creating a conversation request."""
    
    user_id = fields.Integer(required=True)


class ConversationListResponseSchema(Schema):
    """Schema for conversation list response."""
    
    conversations = fields.List(fields.Nested(ConversationSchema))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    pages = fields.Integer()


class MessageListResponseSchema(Schema):
    """Schema for message list response."""
    
    messages = fields.List(fields.Nested(ChatMessageSchema))
    conversation_id = fields.Integer()
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    pages = fields.Integer()