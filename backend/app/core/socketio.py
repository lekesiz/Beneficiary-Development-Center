"""
Socket.IO configuration and event handlers
"""
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_login import current_user
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Initialize SocketIO instance (will be configured in app factory)
socketio = None


def init_socketio(app):
    """Initialize Socket.IO with Flask app."""
    global socketio
    
    cors_allowed_origins = app.config.get('CORS_ORIGINS', '*')
    socketio = SocketIO(
        app,
        cors_allowed_origins=cors_allowed_origins,
        logger=True,
        engineio_logger=True,
        async_mode='threading'
    )
    
    # Register event handlers
    register_handlers(socketio)
    
    return socketio


def authenticated_only(f):
    """Decorator to require authentication for socket events."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
            return False
        return f(*args, **kwargs)
    return wrapped


def register_handlers(socketio):
    """Register Socket.IO event handlers."""
    
    @socketio.on('connect')
    @authenticated_only
    def handle_connect():
        """Handle client connection."""
        # Join user's personal room
        user_room = f"user_{current_user.id}"
        join_room(user_room)
        
        # Join tenant room
        tenant_room = f"tenant_{current_user.tenant_id}"
        join_room(tenant_room)
        
        # Join role-based room
        role_room = f"role_{current_user.tenant_id}_{current_user.role}"
        join_room(role_room)
        
        logger.info(f"User {current_user.id} connected to Socket.IO")
        
        emit('connected', {
            'user_id': current_user.id,
            'role': current_user.role
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        if current_user.is_authenticated:
            logger.info(f"User {current_user.id} disconnected from Socket.IO")
    
    @socketio.on('join_room')
    @authenticated_only
    def handle_join_room(data):
        """Join a specific room."""
        room = data.get('room')
        if room:
            join_room(room)
            emit('joined_room', {'room': room})
    
    @socketio.on('leave_room')
    @authenticated_only
    def handle_leave_room(data):
        """Leave a specific room."""
        room = data.get('room')
        if room:
            leave_room(room)
            emit('left_room', {'room': room})


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
        for role in ['instructor', 'trainer', 'manager', 'admin']:
            emit_to_role(tenant_id, role, 'coach_notification', notification_data)