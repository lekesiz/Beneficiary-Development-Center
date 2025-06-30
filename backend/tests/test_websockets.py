"""
Tests for WebSocket functionality
"""

import pytest
import json
from flask_socketio import SocketIOTestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app import create_app, socketio
from app.models.user import User
from app.services.notification_service import NotificationService
from app.core.socketio import user_sessions


@pytest.fixture
def app():
    """Create test app with SocketIO"""
    app = create_app("testing")
    return app


@pytest.fixture
def socket_client(app):
    """Create SocketIO test client"""
    return SocketIOTestClient(app, socketio)


@pytest.fixture
def valid_jwt_token(app):
    """Generate a valid JWT token for testing"""
    from flask_jwt_extended import create_access_token

    with app.app_context():
        # Create test user data
        identity = 1  # user_id
        additional_claims = {"email": "test@example.com", "role": "admin", "tenant_id": 1}

        token = create_access_token(
            identity=identity, additional_claims=additional_claims, expires_delta=timedelta(hours=1)
        )
        return token


@pytest.fixture
def expired_jwt_token(app):
    """Generate an expired JWT token for testing"""
    from flask_jwt_extended import create_access_token

    with app.app_context():
        identity = 1
        additional_claims = {"email": "test@example.com", "role": "admin", "tenant_id": 1}

        # Create token that expired 1 hour ago
        token = create_access_token(
            identity=identity, additional_claims=additional_claims, expires_delta=timedelta(hours=-1)
        )
        return token


class TestWebSocketAuthentication:
    """Test WebSocket authentication"""

    def test_connect_without_auth(self, socket_client):
        """Test connection without authentication token"""
        # Try to connect without auth
        socket_client.connect(auth=None)

        # Should receive error event
        received = socket_client.get_received()
        assert len(received) > 0
        assert received[0]["name"] == "error"
        assert "Authentication required" in received[0]["args"][0]["message"]

        # Should not be connected
        assert not socket_client.is_connected()

    def test_connect_with_invalid_token(self, socket_client):
        """Test connection with invalid token"""
        # Try to connect with invalid token
        socket_client.connect(auth={"token": "invalid_token"})

        # Should receive error event
        received = socket_client.get_received()
        assert len(received) > 0
        assert received[0]["name"] == "error"
        assert received[0]["args"][0]["code"] == "INVALID_TOKEN"
        assert "Invalid or expired authentication token" in received[0]["args"][0]["message"]

        # Should not be connected
        assert not socket_client.is_connected()

    def test_connect_with_expired_token(self, socket_client, expired_jwt_token):
        """Test connection with expired token"""
        # Try to connect with expired token
        socket_client.connect(auth={"token": expired_jwt_token})

        # Should receive error event
        received = socket_client.get_received()
        assert len(received) > 0
        assert received[0]["name"] == "error"
        assert received[0]["args"][0]["code"] == "INVALID_TOKEN"
        assert "Invalid or expired authentication token" in received[0]["args"][0]["message"]

        # Should not be connected
        assert not socket_client.is_connected()

    @patch("app.core.socketio.get_db")
    def test_connect_with_valid_token(self, mock_get_db, socket_client, valid_jwt_token):
        """Test successful connection with valid token"""
        # Mock database and user
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = "admin"
        mock_user.tenant_id = 1
        mock_user.is_active = True
        mock_user.full_name = "Test User"

        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_get_db.return_value = iter([mock_db])

        # Connect with valid token
        socket_client.connect(auth={"token": valid_jwt_token})

        # Should receive connected event
        received = socket_client.get_received()
        assert len(received) > 0
        assert received[0]["name"] == "connected"
        assert received[0]["args"][0]["status"] == "connected"
        assert received[0]["args"][0]["user_id"] == 1
        assert received[0]["args"][0]["role"] == "admin"

        # Should be connected
        assert socket_client.is_connected()

    @patch("app.core.socketio.get_db")
    def test_user_rooms_on_connect(self, mock_get_db, socket_client, valid_jwt_token):
        """Test that user automatically joins appropriate rooms on connect"""
        # Mock database and user
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = "admin"
        mock_user.tenant_id = 1
        mock_user.is_active = True
        mock_user.full_name = "Test User"

        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_get_db.return_value = iter([mock_db])

        # Connect with valid token
        socket_client.connect(auth={"token": valid_jwt_token})

        # User should be in user sessions
        # Note: In test environment, we can't directly check room membership
        # but we can verify the connection was successful
        assert socket_client.is_connected()


class TestWebSocketEvents:
    """Test WebSocket events"""

    @patch("app.core.socketio.get_db")
    def test_ping_pong(self, mock_get_db, socket_client, valid_jwt_token):
        """Test ping/pong functionality"""
        # Setup mock
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = "admin"
        mock_user.tenant_id = 1
        mock_user.is_active = True
        mock_user.full_name = "Test User"

        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_get_db.return_value = iter([mock_db])

        # Connect
        socket_client.connect(auth={"token": valid_jwt_token})
        socket_client.get_received()  # Clear connection messages

        # Send ping
        timestamp = datetime.utcnow().isoformat()
        socket_client.emit("ping", {"timestamp": timestamp})

        # Should receive pong
        received = socket_client.get_received()
        assert len(received) > 0
        assert received[0]["name"] == "pong"
        assert received[0]["args"][0]["timestamp"] == timestamp

    @patch("app.core.socketio.get_db")
    def test_join_room(self, mock_get_db, socket_client, valid_jwt_token):
        """Test joining a custom room"""
        # Setup mock
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = "admin"
        mock_user.tenant_id = 1
        mock_user.is_active = True
        mock_user.full_name = "Test User"

        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_get_db.return_value = iter([mock_db])

        # Connect
        socket_client.connect(auth={"token": valid_jwt_token})
        socket_client.get_received()  # Clear connection messages

        # Join room
        socket_client.emit("join_room", {"room": "program_123"})

        # Should receive joined_room event
        received = socket_client.get_received()
        assert len(received) > 0
        assert received[0]["name"] == "joined_room"
        assert received[0]["args"][0]["room"] == "program_123"

    @patch("app.core.socketio.get_db")
    def test_leave_room(self, mock_get_db, socket_client, valid_jwt_token):
        """Test leaving a room"""
        # Setup mock
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.role = "admin"
        mock_user.tenant_id = 1
        mock_user.is_active = True
        mock_user.full_name = "Test User"

        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_get_db.return_value = iter([mock_db])

        # Connect and join room
        socket_client.connect(auth={"token": valid_jwt_token})
        socket_client.get_received()  # Clear connection messages
        socket_client.emit("join_room", {"room": "program_123"})
        socket_client.get_received()  # Clear join messages

        # Leave room
        socket_client.emit("leave_room", {"room": "program_123"})

        # Should receive left_room event
        received = socket_client.get_received()
        assert len(received) > 0
        assert received[0]["name"] == "left_room"
        assert received[0]["args"][0]["room"] == "program_123"


class TestNotificationService:
    """Test notification service"""

    @patch("app.core.database.get_db")
    def test_send_notification_to_user(self, mock_get_db):
        """Test sending notification to a specific user"""
        # Mock database and user
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"

        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user

        # Create service with mocked db
        service = NotificationService()
        service.db = mock_db

        # Test sending notification
        result = service.send_notification_to_user(user_id=1, event_name="test_event", data={"message": "Test message"})

        assert result is True

    def test_send_notification_to_nonexistent_user(self):
        """Test sending notification to non-existent user"""
        # Mock database with no user
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        service = NotificationService()
        service.db = mock_db

        # Test sending notification
        result = service.send_notification_to_user(
            user_id=999, event_name="test_event", data={"message": "Test message"}
        )

        assert result is False

    def test_send_notification_to_role(self):
        """Test sending notification to a role"""
        # Mock database
        mock_db = MagicMock()

        service = NotificationService()
        service.db = mock_db

        # Test sending notification
        result = service.send_notification_to_role(
            tenant_id=1, role="admin", event_name="test_event", data={"message": "Test message"}
        )

        assert result is True

    def test_send_notification_to_tenant(self):
        """Test sending notification to entire tenant"""
        # Mock database
        mock_db = MagicMock()

        service = NotificationService()
        service.db = mock_db

        # Test sending notification
        result = service.send_notification_to_tenant(
            tenant_id=1, event_name="test_event", data={"message": "Test message"}
        )

        assert result is True

    @patch("app.core.database.get_db")
    def test_notify_program_created(self, mock_get_db):
        """Test program creation notification"""
        # Mock database and user
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user

        service = NotificationService()
        service.db = mock_db

        # Test notification
        service.notify_program_created(program_id=1, program_title="Test Program", created_by_id=1, tenant_id=1)

        # Verify user query was called
        mock_db.query.assert_called()

    def test_broadcast_announcement(self):
        """Test broadcasting announcement"""
        # Mock database
        mock_db = MagicMock()

        service = NotificationService()
        service.db = mock_db

        # Test broadcast to all
        service.broadcast_announcement(
            tenant_id=1, title="System Maintenance", message="System will be down for maintenance", priority="high"
        )

        # Test broadcast to specific roles
        service.broadcast_announcement(
            tenant_id=1,
            title="Admin Notice",
            message="Important admin update",
            priority="urgent",
            roles=["admin", "manager"],
        )
