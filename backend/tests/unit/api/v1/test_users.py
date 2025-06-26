"""Tests for user API endpoints."""

import pytest
from flask import json
from unittest.mock import patch, MagicMock

from app.models.user import User


class TestUserPreferences:
    """Test user preferences endpoints."""

    def test_get_user_preferences_success(self, client, auth_headers):
        """Test getting user preferences successfully."""
        with patch('app.api.v1.users.User.query.get') as mock_get:
            # Mock user with preferences
            mock_user = MagicMock(spec=User)
            mock_user.preferences = {
                'notifications': {
                    'email': {
                        'new_message': True,
                        'appointment_reminder': True,
                        'evaluation_completed': False,
                        'course_enrollment': True,
                        'program_update': True
                    },
                    'in_app': {
                        'new_message': True,
                        'appointment_reminder': True,
                        'evaluation_completed': True,
                        'course_enrollment': True,
                        'program_update': True
                    }
                }
            }
            mock_get.return_value = mock_user

            response = client.get('/api/v1/users/me/preferences', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'preferences' in data
            assert 'notifications' in data['preferences']
            assert 'email' in data['preferences']['notifications']
            assert 'in_app' in data['preferences']['notifications']

    def test_get_user_preferences_with_defaults(self, client, auth_headers):
        """Test getting user preferences returns defaults when not set."""
        with patch('app.api.v1.users.User.query.get') as mock_get:
            # Mock user without preferences
            mock_user = MagicMock(spec=User)
            mock_user.preferences = {}
            mock_get.return_value = mock_user

            response = client.get('/api/v1/users/me/preferences', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'preferences' in data
            assert 'notifications' in data['preferences']
            
            # Check defaults are applied
            assert data['preferences']['notifications']['email']['new_message'] is True
            assert data['preferences']['notifications']['in_app']['new_message'] is True

    def test_get_user_preferences_user_not_found(self, client, auth_headers):
        """Test getting preferences when user not found."""
        with patch('app.api.v1.users.User.query.get') as mock_get:
            mock_get.return_value = None

            response = client.get('/api/v1/users/me/preferences', headers=auth_headers)
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['message'] == 'User not found'

    def test_update_user_preferences_success(self, client, auth_headers, db_session):
        """Test updating user preferences successfully."""
        with patch('app.api.v1.users.User.query.get') as mock_get, \
             patch('app.api.v1.users.db.session.query') as mock_query, \
             patch('app.api.v1.users.db.session.commit') as mock_commit, \
             patch('app.api.v1.users.log_user_action') as mock_log:
            
            # Mock user
            mock_user = MagicMock(spec=User)
            mock_user.id = 1
            mock_user.tenant_id = 1
            mock_user.email = 'test@example.com'
            mock_user.preferences = {}
            mock_get.return_value = mock_user
            
            # Mock query chain
            mock_filter = MagicMock()
            mock_filter.update.return_value = None
            mock_query.return_value.filter_by.return_value = mock_filter

            # Request data
            request_data = {
                'notifications': {
                    'email': {
                        'new_message': False,
                        'appointment_reminder': True,
                        'evaluation_completed': True,
                        'course_enrollment': False,
                        'program_update': True
                    },
                    'in_app': {
                        'new_message': True,
                        'appointment_reminder': True,
                        'evaluation_completed': True,
                        'course_enrollment': True,
                        'program_update': False
                    }
                }
            }

            response = client.put(
                '/api/v1/users/me/preferences',
                headers=auth_headers,
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Preferences updated successfully'
            assert 'preferences' in data
            
            # Verify database operations
            mock_commit.assert_called_once()
            mock_log.assert_called_once_with(
                'update_preferences',
                user_id=1,
                tenant_id=1,
                email='test@example.com',
                preferences_type='notifications'
            )

    def test_update_user_preferences_invalid_format(self, client, auth_headers):
        """Test updating preferences with invalid format."""
        with patch('app.api.v1.users.User.query.get') as mock_get:
            mock_user = MagicMock(spec=User)
            mock_get.return_value = mock_user

            # Missing notifications key
            request_data = {'invalid': 'data'}

            response = client.put(
                '/api/v1/users/me/preferences',
                headers=auth_headers,
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['message'] == 'Invalid preferences format'

    def test_update_user_preferences_user_not_found(self, client, auth_headers):
        """Test updating preferences when user not found."""
        with patch('app.api.v1.users.User.query.get') as mock_get:
            mock_get.return_value = None

            request_data = {
                'notifications': {
                    'email': {'new_message': True},
                    'in_app': {'new_message': True}
                }
            }

            response = client.put(
                '/api/v1/users/me/preferences',
                headers=auth_headers,
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['message'] == 'User not found'

    def test_update_user_preferences_database_error(self, client, auth_headers):
        """Test handling database error during preference update."""
        with patch('app.api.v1.users.User.query.get') as mock_get, \
             patch('app.api.v1.users.db.session.query') as mock_query:
            
            mock_user = MagicMock(spec=User)
            mock_user.preferences = {}
            mock_get.return_value = mock_user
            
            # Simulate database error
            mock_query.side_effect = Exception('Database error')

            request_data = {
                'notifications': {
                    'email': {'new_message': True},
                    'in_app': {'new_message': True}
                }
            }

            response = client.put(
                '/api/v1/users/me/preferences',
                headers=auth_headers,
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'Failed to update preferences' in data['message']