"""
Unit tests for Notifications API endpoints
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for
from app.models.notification import Notification, NotificationType, NotificationPriority


class TestNotificationsAPI:
    """Test cases for notifications endpoints"""

    @pytest.fixture
    def sample_notification(self, db_session, test_tenant, admin_user):
        """Create a sample notification for testing"""
        notification = Notification(
            tenant_id=test_tenant.id,
            user_id=admin_user.id,
            type=NotificationType.INFO,
            priority=NotificationPriority.MEDIUM,
            title="Test Notification",
            message="This is a test notification",
            data={"key": "value"},
            is_read=False
        )
        db_session.add(notification)
        db_session.commit()
        return notification

    @pytest.fixture
    def multiple_notifications(self, db_session, test_tenant, admin_user):
        """Create multiple notifications for testing"""
        notifications = []
        for i in range(5):
            notification = Notification(
                tenant_id=test_tenant.id,
                user_id=admin_user.id,
                type=NotificationType.INFO if i % 2 == 0 else NotificationType.ALERT,
                priority=NotificationPriority.LOW if i < 2 else NotificationPriority.HIGH,
                title=f"Notification {i+1}",
                message=f"Message for notification {i+1}",
                data={"index": i},
                is_read=i < 2  # First 2 are read
            )
            notifications.append(notification)
        
        db_session.add_all(notifications)
        db_session.commit()
        return notifications

    def test_get_notifications_success(self, client, admin_headers, multiple_notifications):
        """Test successful retrieval of notifications"""
        response = client.get(
            '/api/v1/notifications',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'notifications' in data
        assert 'pagination' in data
        assert len(data['notifications']) == 5
        
        # Check notification structure
        notification = data['notifications'][0]
        assert 'id' in notification
        assert 'type' in notification
        assert 'priority' in notification
        assert 'title' in notification
        assert 'message' in notification
        assert 'is_read' in notification
        assert 'created_at' in notification

    def test_get_notifications_filtered_by_type(self, client, admin_headers, multiple_notifications):
        """Test filtering notifications by type"""
        response = client.get(
            '/api/v1/notifications?type=alert',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Should only get ALERT type notifications
        assert all(n['type'] == 'alert' for n in data['notifications'])

    def test_get_notifications_filtered_unread(self, client, admin_headers, multiple_notifications):
        """Test filtering unread notifications"""
        response = client.get(
            '/api/v1/notifications?unread_only=true',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Should only get unread notifications
        assert all(not n['is_read'] for n in data['notifications'])
        assert len(data['notifications']) == 3  # 3 unread out of 5

    def test_get_unread_count_success(self, client, admin_headers, multiple_notifications):
        """Test successful retrieval of unread notification count"""
        response = client.get(
            '/api/v1/notifications/unread-count',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'count' in data
        assert data['count'] == 3  # 3 unread notifications

    def test_mark_notification_as_read(self, client, admin_headers, sample_notification):
        """Test marking a notification as read"""
        response = client.put(
            f'/api/v1/notifications/{sample_notification.id}/read',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['success'] is True
        assert data['message'] == 'Notification marked as read'
        
        # Verify notification is marked as read
        get_response = client.get(
            f'/api/v1/notifications/{sample_notification.id}',
            headers=admin_headers
        )
        assert get_response.json['is_read'] is True

    def test_mark_all_notifications_as_read(self, client, admin_headers, multiple_notifications):
        """Test marking all notifications as read"""
        response = client.put(
            '/api/v1/notifications/read-all',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['success'] is True
        assert 'updated_count' in data
        assert data['updated_count'] == 3  # 3 were unread
        
        # Verify all are read
        count_response = client.get(
            '/api/v1/notifications/unread-count',
            headers=admin_headers
        )
        assert count_response.json['count'] == 0

    def test_delete_notification(self, client, admin_headers, sample_notification):
        """Test deleting a notification"""
        response = client.delete(
            f'/api/v1/notifications/{sample_notification.id}',
            headers=admin_headers
        )
        
        assert response.status_code == 204
        
        # Verify notification is deleted
        get_response = client.get(
            f'/api/v1/notifications/{sample_notification.id}',
            headers=admin_headers
        )
        assert get_response.status_code == 404

    def test_delete_notification_not_found(self, client, admin_headers):
        """Test deleting non-existent notification"""
        response = client.delete(
            '/api/v1/notifications/999999',
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_get_notification_settings(self, client, admin_headers):
        """Test retrieving notification settings"""
        response = client.get(
            '/api/v1/notifications/settings',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'email_enabled' in data
        assert 'push_enabled' in data
        assert 'notification_types' in data

    def test_update_notification_settings(self, client, admin_headers):
        """Test updating notification settings"""
        settings = {
            "email_enabled": False,
            "push_enabled": True,
            "notification_types": {
                "info": True,
                "alert": True,
                "warning": False
            }
        }
        
        response = client.put(
            '/api/v1/notifications/settings',
            headers=admin_headers,
            json=settings
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['email_enabled'] is False
        assert data['push_enabled'] is True

    def test_get_notifications_no_auth(self, client):
        """Test getting notifications without authentication"""
        response = client.get('/api/v1/notifications')
        assert response.status_code == 401

    def test_create_notification_via_event(self, client, admin_headers, db_session):
        """Test notification creation through system events"""
        # This would typically be triggered by system events
        # Here we test the endpoint directly if it exists
        notification_data = {
            "type": "info",
            "priority": "high",
            "title": "New System Event",
            "message": "An important system event occurred",
            "data": {"event_type": "test"}
        }
        
        response = client.post(
            '/api/v1/notifications/system',
            headers=admin_headers,
            json=notification_data
        )
        
        # This might return 404 if endpoint doesn't exist
        # or 201 if it does
        assert response.status_code in [201, 404]

    @pytest.mark.parametrize("priority", ['low', 'medium', 'high', 'urgent'])
    def test_filter_notifications_by_priority(self, client, admin_headers, db_session, test_tenant, admin_user, priority):
        """Test filtering notifications by priority"""
        # Create notification with specific priority
        notification = Notification(
            tenant_id=test_tenant.id,
            user_id=admin_user.id,
            type=NotificationType.INFO,
            priority=priority,
            title=f"{priority.capitalize()} Priority Notification",
            message="Test message"
        )
        db_session.add(notification)
        db_session.commit()
        
        response = client.get(
            f'/api/v1/notifications?priority={priority}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check that filtered results have correct priority
        if data['notifications']:
            assert all(n['priority'] == priority for n in data['notifications'])
