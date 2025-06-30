"""
Socket.IO configuration and event handlers
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token, get_jwt_identity, get_jwt
from flask import request
from functools import wraps
import logging
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
from app.core.database import get_db
from datetime import datetime
from app.services.chat_service import ChatService
from app.models.chat import Conversation, ChatMessage

logger = logging.getLogger(__name__)

# Import socketio from extensions
from app.extensions import socketio

# Store user sessions
user_sessions = {}


def init_socketio(app):
    """Initialize Socket.IO with Flask app."""
    cors_allowed_origins = app.config.get("CORS_ORIGINS", "*")
    socketio.init_app(
        app, cors_allowed_origins=cors_allowed_origins, logger=True, engineio_logger=True, async_mode="threading"
    )

    # Register event handlers
    register_handlers(socketio)

    return socketio


def authenticated_only(f):
    """Decorator to require authentication for socket events."""

    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            # Get session ID from request
            sid = request.sid

            # Check if user is authenticated
            if sid not in user_sessions:
                logger.warning(f"Unauthenticated socket event attempt from {sid}")
                disconnect()
                return False

            # Add user info to kwargs
            kwargs["current_user"] = user_sessions[sid]
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Authentication error in socket event: {str(e)}")
            disconnect()
            return False

    return wrapped


def verify_jwt_token(token):
    """Verify JWT token and return user info."""
    try:
        # Decode the token
        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")

        if not user_id:
            return None

        # Get user from database
        from app.models.user import User

        db = get_db()
        try:
            user = db.session.query(User).filter_by(id=user_id).first()
            if user and user.is_active:
                return {
                    "user_id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "tenant_id": user.tenant_id,
                    "full_name": user.full_name,
                }
        finally:
            db.close()

    except ExpiredSignatureError:
        logger.warning("Expired JWT token in socket connection")
    except InvalidTokenError:
        logger.warning("Invalid JWT token in socket connection")
    except Exception as e:
        logger.error(f"Error verifying JWT token: {str(e)}")

    return None


def register_handlers(socketio):
    """Register Socket.IO event handlers."""

    @socketio.on("connect")
    def handle_connect(auth):
        """Handle client connection."""
        logger.info(f"New socket connection attempt from {request.sid}")

        # Check if auth data is provided
        if not auth or "token" not in auth:
            logger.warning("Connection attempt without auth token")
            emit("error", {"message": "Authentication required"})
            return False

        # Verify JWT token
        user_info = verify_jwt_token(auth["token"])
        if not user_info:
            logger.warning("Connection attempt with invalid token")
            emit("error", {"message": "Invalid authentication token"})
            return False

        # Store user session
        sid = request.sid
        user_sessions[sid] = user_info

        # Join user-specific room
        user_room = f"user_{user_info['user_id']}"
        join_room(user_room)

        # Join tenant room
        tenant_room = f"tenant_{user_info['tenant_id']}"
        join_room(tenant_room)

        # Join role-specific room
        role_room = f"role_{user_info['tenant_id']}_{user_info['role']}"
        join_room(role_room)

        logger.info(f"User {user_info['email']} connected successfully")
        emit("connected", {"status": "connected", "user_id": user_info["user_id"], "role": user_info["role"]})

        return True

    @socketio.on("disconnect")
    def handle_disconnect():
        """Handle client disconnection."""
        sid = request.sid

        # Clean up user session
        if sid in user_sessions:
            user_info = user_sessions[sid]
            logger.info(f"User {user_info['email']} disconnected")

            # Leave all rooms
            user_room = f"user_{user_info['user_id']}"
            leave_room(user_room)

            tenant_room = f"tenant_{user_info['tenant_id']}"
            leave_room(tenant_room)

            role_room = f"role_{user_info['tenant_id']}_{user_info['role']}"
            leave_room(role_room)

            # Remove session
            del user_sessions[sid]
        else:
            logger.info("Anonymous client disconnected")

    @socketio.on("join_room")
    @authenticated_only
    def handle_join_room(data, current_user=None):
        """Join a specific room."""
        room = data.get("room")
        if room:
            # Validate room access (e.g., only join program rooms if enrolled)
            # For now, allow joining any room
            join_room(room)
            logger.info(f"User {current_user['email']} joined room {room}")
            emit("joined_room", {"room": room})

    @socketio.on("leave_room")
    @authenticated_only
    def handle_leave_room(data, current_user=None):
        """Leave a specific room."""
        room = data.get("room")
        if room:
            leave_room(room)
            logger.info(f"User {current_user['email']} left room {room}")
            emit("left_room", {"room": room})

    @socketio.on("ping")
    @authenticated_only
    def handle_ping(data, current_user=None):
        """Handle ping to keep connection alive."""
        emit("pong", {"timestamp": data.get("timestamp")})

    @socketio.on("message:send")
    @authenticated_only
    def handle_message_send(data, current_user=None):
        """Handle sending a new message."""
        try:
            # Extract data
            recipient_id = data.get("recipient_id")
            content = data.get("content")
            message_metadata = data.get("message_metadata", {})

            # Validate inputs
            if not recipient_id or not content:
                emit("message:error", {"error": "Recipient ID and content are required"})
                return

            if not isinstance(content, str) or len(content.strip()) == 0:
                emit("message:error", {"error": "Message content cannot be empty"})
                return

            if len(content) > 5000:  # Max message length
                emit("message:error", {"error": "Message content too long (max 5000 characters)"})
                return

            # Get database session
            db = get_db()
            try:
                chat_service = ChatService(db.session)

                # Send the message
                message = chat_service.send_message(
                    sender_id=current_user["user_id"],
                    receiver_id=recipient_id,
                    content=content.strip(),
                    tenant_id=current_user["tenant_id"],
                    message_metadata=message_metadata,
                )

                # Get conversation for additional info
                conversation = message.conversation

                # Prepare message data
                message_data = message.to_dict()
                message_data["conversation_uuid"] = str(conversation.uuid)

                # Emit to sender (confirmation)
                emit("message:sent", {"message": message_data, "conversation_id": conversation.id})

                # Emit to recipient's private room
                recipient_room = f"user_{recipient_id}"
                emit(
                    "message:new",
                    {
                        "message": message_data,
                        "conversation_id": conversation.id,
                        "sender": {
                            "id": current_user["user_id"],
                            "full_name": current_user["full_name"],
                            "email": current_user["email"],
                        },
                    },
                    room=recipient_room,
                )

                logger.info(f"Message sent from user {current_user['user_id']} to user {recipient_id}")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            emit("message:error", {"error": "Failed to send message"})

    @socketio.on("message:mark_as_read")
    @authenticated_only
    def handle_mark_as_read(data, current_user=None):
        """Mark messages as read in a conversation."""
        try:
            conversation_id = data.get("conversation_id")
            message_ids = data.get("message_ids", [])  # Optional: specific messages

            if not conversation_id:
                emit("message:error", {"error": "Conversation ID is required"})
                return

            db = get_db()
            try:
                chat_service = ChatService(db.session)

                # If specific message IDs provided, mark those
                if message_ids:
                    for msg_id in message_ids:
                        message = (
                            db.session.query(ChatMessage)
                            .filter_by(
                                id=msg_id, receiver_id=current_user["user_id"], tenant_id=current_user["tenant_id"]
                            )
                            .first()
                        )

                        if message and not message.read_at:
                            message.mark_as_read()

                    db.session.commit()
                    count = len(message_ids)
                else:
                    # Mark all messages in conversation as read
                    count = chat_service.mark_messages_as_read(
                        conversation_id=conversation_id,
                        user_id=current_user["user_id"],
                        tenant_id=current_user["tenant_id"],
                    )

                # Get the conversation to notify the other user
                conversation = (
                    db.session.query(Conversation)
                    .filter_by(id=conversation_id, tenant_id=current_user["tenant_id"])
                    .first()
                )

                if conversation:
                    # Determine the other user
                    other_user_id = (
                        conversation.user2_id
                        if conversation.user1_id == current_user["user_id"]
                        else conversation.user1_id
                    )

                    # Emit read receipt to the other user
                    other_user_room = f"user_{other_user_id}"
                    emit(
                        "message:read_receipt",
                        {
                            "conversation_id": conversation_id,
                            "reader_id": current_user["user_id"],
                            "count": count,
                            "message_ids": message_ids,
                        },
                        room=other_user_room,
                    )

                # Confirm to the reader
                emit("message:marked_as_read", {"conversation_id": conversation_id, "count": count})

                logger.info(f"Marked {count} messages as read for user {current_user['user_id']}")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error marking messages as read: {str(e)}")
            emit("message:error", {"error": "Failed to mark messages as read"})

    @socketio.on("message:typing")
    @authenticated_only
    def handle_typing(data, current_user=None):
        """Handle typing indicator."""
        try:
            conversation_id = data.get("conversation_id")
            is_typing = data.get("is_typing", False)

            if not conversation_id:
                return  # Silently ignore if no conversation ID

            db = get_db()
            try:
                # Get the conversation to find the other user
                conversation = (
                    db.session.query(Conversation)
                    .filter_by(id=conversation_id, tenant_id=current_user["tenant_id"])
                    .first()
                )

                if not conversation:
                    return

                # Check if user is part of the conversation
                if current_user["user_id"] not in [conversation.user1_id, conversation.user2_id]:
                    return

                # Determine the other user
                other_user_id = (
                    conversation.user2_id if conversation.user1_id == current_user["user_id"] else conversation.user1_id
                )

                # Emit typing indicator to the other user
                other_user_room = f"user_{other_user_id}"
                emit(
                    "message:typing",
                    {
                        "conversation_id": conversation_id,
                        "user_id": current_user["user_id"],
                        "is_typing": is_typing,
                        "user": {"id": current_user["user_id"], "full_name": current_user["full_name"]},
                    },
                    room=other_user_room,
                )

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error handling typing indicator: {str(e)}")

    @socketio.on("message:get_history")
    @authenticated_only
    def handle_get_history(data, current_user=None):
        """Get message history for a conversation."""
        try:
            conversation_id = data.get("conversation_id")
            page = data.get("page", 1)
            per_page = data.get("per_page", 50)
            before_timestamp = data.get("before_timestamp")

            if not conversation_id:
                emit("message:error", {"error": "Conversation ID is required"})
                return

            db = get_db()
            try:
                chat_service = ChatService(db.session)

                # Convert timestamp string to datetime if provided
                before_dt = None
                if before_timestamp:
                    try:
                        before_dt = datetime.fromisoformat(before_timestamp.replace("Z", "+00:00"))
                    except:
                        pass

                # Get message history
                result = chat_service.get_conversation_messages(
                    conversation_id=conversation_id,
                    user_id=current_user["user_id"],
                    tenant_id=current_user["tenant_id"],
                    page=page,
                    per_page=per_page,
                    before_timestamp=before_dt,
                )

                # Emit history to the requester
                emit("message:history", result)

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error getting message history: {str(e)}")
            emit("message:error", {"error": "Failed to get message history"})

    @socketio.on("conversation:get_list")
    @authenticated_only
    def handle_get_conversations(data, current_user=None):
        """Get user's conversation list."""
        try:
            page = data.get("page", 1)
            per_page = data.get("per_page", 20)
            active_only = data.get("active_only", True)

            db = get_db()
            try:
                chat_service = ChatService(db.session)

                # Get conversations
                result = chat_service.get_user_conversations(
                    user_id=current_user["user_id"],
                    tenant_id=current_user["tenant_id"],
                    page=page,
                    per_page=per_page,
                    active_only=active_only,
                )

                # Emit conversations to the requester
                emit("conversation:list", result)

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}")
            emit("message:error", {"error": "Failed to get conversations"})

    @socketio.on("message:delete")
    @authenticated_only
    def handle_message_delete(data, current_user=None):
        """Handle message deletion."""
        try:
            message_id = data.get("message_id")

            if not message_id:
                emit("message:error", {"error": "Message ID is required"})
                return

            db = get_db()
            try:
                chat_service = ChatService(db.session)

                # Delete the message
                success = chat_service.delete_message(
                    message_id=message_id, user_id=current_user["user_id"], tenant_id=current_user["tenant_id"]
                )

                if success:
                    # Emit deletion confirmation
                    emit("message:deleted", {"message_id": message_id, "deleted": True})

                    logger.info(f"Message {message_id} deleted by user {current_user['user_id']}")
                else:
                    emit("message:error", {"error": "Failed to delete message"})

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
            emit(
                "message:error",
                {
                    "error": (
                        str(e)
                        if "not found" in str(e).lower() or "cannot delete" in str(e).lower()
                        else "Failed to delete message"
                    )
                },
            )


def emit_to_user(user_id, event, data):
    """Emit event to a specific user."""
    if socketio:
        room = f"user_{user_id}"
        socketio.emit(event, data, room=room)


def emit_to_role(tenant_id, role, event, data):
    """Emit event to all users with a specific role in a tenant."""
    if socketio:
        room = f"role_{tenant_id}_{role}"
        socketio.emit(event, data, room=room)


def emit_to_tenant(tenant_id, event, data):
    """Emit event to all users in a tenant."""
    if socketio:
        room = f"tenant_{tenant_id}"
        socketio.emit(event, data, room=room)


def emit_coach_notification(tenant_id, notification_data):
    """Emit notification to all coaches in a tenant."""
    if socketio:
        # Emit to instructors and trainers (coaches)
        for role in ["instructor", "trainer", "manager", "admin"]:
            emit_to_role(tenant_id, role, "coach_notification", notification_data)


def emit_chat_notification(user_id, notification_data):
    """Emit chat notification to a specific user."""
    if socketio:
        emit_to_user(user_id, "chat_notification", notification_data)


def emit_message_to_conversation(conversation_id, event, data, exclude_user_id=None):
    """Emit event to all participants in a conversation."""
    if socketio:
        db = get_db()
        try:
            conversation = db.session.query(Conversation).filter_by(id=conversation_id).first()
            if conversation:
                # Emit to both participants
                if conversation.user1_id != exclude_user_id:
                    emit_to_user(conversation.user1_id, event, data)
                if conversation.user2_id != exclude_user_id:
                    emit_to_user(conversation.user2_id, event, data)
        finally:
            db.close()
