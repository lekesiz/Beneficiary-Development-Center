"""API endpoints for chat functionality."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

from app.services.chat_service import ChatService
from app.models.user import User
from app.core.decorators import require_tenant
from app.extensions import db
from app.core.logging import logger
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


bp = Blueprint("chat", __name__, url_prefix="/api/v1")


class SendMessageSchema(Schema):
    """Schema for sending a message."""

    receiver_id = fields.Integer(required=True)
    content = fields.String(required=True, validate=validate.Length(min=1, max=5000))
    message_metadata = fields.Dict(required=False)


class CreateConversationSchema(Schema):
    """Schema for creating a conversation."""

    user_id = fields.Integer(required=True)


send_message_schema = SendMessageSchema()
create_conversation_schema = CreateConversationSchema()


@bp.route("/conversations", methods=["GET"])
@jwt_required()
@require_tenant()
def get_conversations():
    """
    Get list of current user's conversations.

    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - active_only: Filter only active conversations (default: true)

    Returns:
    - List of conversations with participant details and last message
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Verify user exists
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get query parameters
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        active_only = request.args.get("active_only", "true").lower() == "true"

        # Validate pagination
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "per_page must be between 1 and 100"}), 400

        # Get conversations
        chat_service = ChatService(db.session)
        result = chat_service.get_user_conversations(
            user_id=user_id, tenant_id=tenant_id, page=page, per_page=per_page, active_only=active_only
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        return jsonify({"error": "Failed to fetch conversations"}), 500


@bp.route("/conversations/<int:conversation_id>/messages", methods=["GET"])
@jwt_required()
@require_tenant()
def get_conversation_messages(conversation_id):
    """
    Fetch message history for a conversation.

    Path parameters:
    - conversation_id: ID of the conversation

    Query parameters:
    - page: Page number (default: 1)
    - per_page: Messages per page (default: 50)
    - before: ISO timestamp to load messages before (for pagination)

    Returns:
    - List of messages in the conversation
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get query parameters
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))
        before = request.args.get("before")

        # Validate pagination
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "per_page must be between 1 and 100"}), 400

        # Parse before timestamp if provided
        before_timestamp = None
        if before:
            try:
                before_timestamp = datetime.fromisoformat(before.replace("Z", "+00:00"))
            except ValueError:
                return jsonify({"error": "Invalid before timestamp format"}), 400

        # Get messages
        chat_service = ChatService(db.session)
        result = chat_service.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            tenant_id=tenant_id,
            page=page,
            per_page=per_page,
            before_timestamp=before_timestamp,
        )

        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        return jsonify({"error": "Failed to fetch messages"}), 500


@bp.route("/conversations", methods=["POST"])
@jwt_required()
@require_tenant()
def create_conversation():
    """
    Create a new conversation with another user.

    Request body:
    - user_id: ID of the other user to start conversation with

    Returns:
    - Created conversation details
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        current_user_id = get_jwt_identity()

        # Validate request data
        try:
            data = create_conversation_schema.load(request.get_json())
        except ValidationError as e:
            return jsonify({"error": "Validation error", "messages": e.messages}), 400

        other_user_id = data["user_id"]

        # Validate users
        if current_user_id == other_user_id:
            return jsonify({"error": "Cannot create conversation with yourself"}), 400

        # Verify other user exists
        other_user = db.session.query(User).filter_by(id=other_user_id, tenant_id=tenant_id).first()

        if not other_user:
            return jsonify({"error": "User not found"}), 404

        # Create or get conversation
        chat_service = ChatService(db.session)
        conversation = chat_service.get_or_create_conversation(
            user1_id=current_user_id, user2_id=other_user_id, tenant_id=tenant_id
        )

        return jsonify(conversation.to_dict(current_user_id=current_user_id)), 201

    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        return jsonify({"error": "Failed to create conversation"}), 500


@bp.route("/messages", methods=["POST"])
@jwt_required()
@require_tenant()
def send_message():
    """
    Send a message to another user (REST backup for WebSocket).

    Request body:
    - receiver_id: ID of the recipient user
    - content: Message content
    - message_metadata: Optional metadata (attachments, etc.)

    Returns:
    - Sent message details
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        sender_id = get_jwt_identity()

        # Validate request data
        try:
            data = send_message_schema.load(request.get_json())
        except ValidationError as e:
            return jsonify({"error": "Validation error", "messages": e.messages}), 400

        receiver_id = data["receiver_id"]
        content = data["content"]
        message_metadata = data.get("message_metadata", {})

        # Validate users
        if sender_id == receiver_id:
            return jsonify({"error": "Cannot send message to yourself"}), 400

        # Verify receiver exists
        receiver = db.session.query(User).filter_by(id=receiver_id, tenant_id=tenant_id).first()

        if not receiver:
            return jsonify({"error": "Receiver not found"}), 404

        # Send message
        chat_service = ChatService(db.session)
        message = chat_service.send_message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            tenant_id=tenant_id,
            message_metadata=message_metadata,
        )

        return jsonify(message.to_dict()), 201

    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({"error": "Failed to send message"}), 500


@bp.route("/conversations/<int:conversation_id>/read", methods=["PUT"])
@jwt_required()
@require_tenant()
def mark_conversation_as_read(conversation_id):
    """
    Mark all messages in a conversation as read.

    Path parameters:
    - conversation_id: ID of the conversation

    Returns:
    - Number of messages marked as read
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Mark messages as read
        chat_service = ChatService(db.session)
        count = chat_service.mark_messages_as_read(
            conversation_id=conversation_id, user_id=user_id, tenant_id=tenant_id
        )

        return jsonify({"messages_marked": count}), 200

    except Exception as e:
        logger.error(f"Error marking messages as read: {str(e)}")
        return jsonify({"error": "Failed to mark messages as read"}), 500


@bp.route("/messages/<int:message_id>", methods=["DELETE"])
@jwt_required()
@require_tenant()
def delete_message(message_id):
    """
    Delete a message (soft delete for the current user).

    Path parameters:
    - message_id: ID of the message to delete

    Returns:
    - Success status
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Delete message
        chat_service = ChatService(db.session)
        chat_service.delete_message(message_id=message_id, user_id=user_id, tenant_id=tenant_id)

        return jsonify({"message": "Message deleted successfully"}), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error deleting message: {str(e)}")
        return jsonify({"error": "Failed to delete message"}), 500


@bp.route("/unread-count", methods=["GET"])
@jwt_required()
@require_tenant()
def get_unread_count():
    """
    Get total unread message count for the current user.

    Returns:
    - Total unread message count
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get unread count
        chat_service = ChatService(db.session)
        count = chat_service.get_unread_count(user_id=user_id, tenant_id=tenant_id)

        return jsonify({"unread_count": count}), 200

    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        return jsonify({"error": "Failed to get unread count"}), 500
