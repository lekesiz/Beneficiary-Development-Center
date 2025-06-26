"""
Socket.IO event handlers for real-time notifications
"""

from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.core.socketio import socketio
from app.models.user import User
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)


@socketio.on("connect")
def handle_connect(auth):
    """Handle client connection with JWT authentication."""
    try:
        # Verify JWT token from auth data
        if not auth or "token" not in auth:
            logger.warning("Connection attempt without token")
            return False

        # Manual JWT verification for Socket.IO
        from flask import current_app
        import jwt

        try:
            payload = jwt.decode(auth["token"], current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("sub")
        except jwt.InvalidTokenError:
            logger.warning("Invalid token in socket connection")
            return False

        # Get user from database
        db = get_db()
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(f"User {user_id} not found")
            return False

        # Join user's personal room
        user_room = f"user_{user.id}"
        join_room(user_room)

        # Join tenant room
        tenant_room = f"tenant_{user.tenant_id}"
        join_room(tenant_room)

        # Join role-based room (for coaches)
        if user.role in ["admin", "manager", "instructor", "trainer"]:
            role_room = f"role_{user.tenant_id}_{user.role}"
            join_room(role_room)
            logger.info(f"User {user.id} ({user.role}) joined role room")

        logger.info(f"User {user.id} connected to Socket.IO")

        emit(
            "connected",
            {"user_id": user.id, "role": user.role, "message": "Successfully connected to notification service"},
        )

        return True

    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return False


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected from Socket.IO")


@socketio.on("ping")
def handle_ping():
    """Handle ping to keep connection alive."""
    from datetime import datetime

    emit("pong", {"timestamp": datetime.utcnow().isoformat()})


@socketio.on("subscribe")
def handle_subscribe(data):
    """Subscribe to specific notification channels."""
    try:
        room = data.get("room")
        if room:
            join_room(room)
            emit("subscribed", {"room": room})
            logger.info(f"Client subscribed to room: {room}")
    except Exception as e:
        logger.error(f"Subscribe error: {str(e)}")
        emit("error", {"message": "Failed to subscribe"})


@socketio.on("unsubscribe")
def handle_unsubscribe(data):
    """Unsubscribe from specific notification channels."""
    try:
        room = data.get("room")
        if room:
            leave_room(room)
            emit("unsubscribed", {"room": room})
            logger.info(f"Client unsubscribed from room: {room}")
    except Exception as e:
        logger.error(f"Unsubscribe error: {str(e)}")
        emit("error", {"message": "Failed to unsubscribe"})
