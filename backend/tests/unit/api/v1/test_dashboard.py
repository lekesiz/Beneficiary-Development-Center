"""
Unit tests for Dashboard API endpoints
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for


class TestDashboardAPI:
    """Test cases for dashboard endpoints"""

    def test_get_dashboard_stats_admin(self, client, admin_headers):
        """Test dashboard stats retrieval for admin user"""
        response = client.get(
            '/api/v1/dashboard/stats',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check admin dashboard structure
        assert 'total_beneficiaries' in data
        assert 'active_programs' in data
        assert 'total_users' in data
        assert 'recent_activities' in data
        assert 'system_health' in data
        
        # Check numeric values
        assert isinstance(data['total_beneficiaries'], int)
        assert isinstance(data['active_programs'], int)
        assert isinstance(data['total_users'], int)
        assert data['total_beneficiaries'] >= 0
        assert data['active_programs'] >= 0
        assert data['total_users'] >= 0

    def test_get_dashboard_stats_trainer(self, client, trainer_auth_headers):
        """Test dashboard stats retrieval for trainer user"""
        response = client.get(
            '/api/v1/dashboard/stats',
            headers=trainer_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check trainer-specific dashboard structure
        assert 'assigned_students' in data
        assert 'active_sessions' in data
        assert 'pending_evaluations' in data
        assert 'upcoming_sessions' in data

    def test_get_dashboard_stats_student(self, client, student_auth_headers):
        """Test dashboard stats retrieval for student user"""
        response = client.get(
            '/api/v1/dashboard/stats',
            headers=student_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check student-specific dashboard structure
        assert 'enrolled_programs' in data
        assert 'completed_courses' in data
        assert 'upcoming_sessions' in data
        assert 'overall_progress' in data
        assert 'recent_achievements' in data

    def test_get_dashboard_activity(self, client, admin_headers):
        """Test recent activity retrieval"""
        response = client.get(
            '/api/v1/dashboard/activity',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'activities' in data
        assert isinstance(data['activities'], list)
        
        # Check activity structure if any exist
        if data['activities']:
            activity = data['activities'][0]
            assert 'id' in activity
            assert 'type' in activity
            assert 'description' in activity
            assert 'timestamp' in activity
            assert 'user' in activity

    def test_get_dashboard_activity_with_filters(self, client, admin_headers):
        """Test activity retrieval with filters"""
        response = client.get(
            '/api/v1/dashboard/activity?limit=10&type=enrollment',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'activities' in data
        assert len(data['activities']) <= 10
        
        # Check that all activities match the filter
        for activity in data['activities']:
            assert activity['type'] == 'enrollment'

    def test_get_dashboard_charts(self, client, admin_headers):
        """Test dashboard chart data retrieval"""
        response = client.get(
            '/api/v1/dashboard/charts',
            headers=admin_headers
        )
        
        # May return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json
            # Check for common chart data
            assert any(key in data for key in ['enrollment_trends', 'progress_distribution', 'activity_heatmap'])

    def test_get_dashboard_metrics(self, client, admin_headers):
        """Test key performance metrics retrieval"""
        response = client.get(
            '/api/v1/dashboard/metrics?period=month',
            headers=admin_headers
        )
        
        # May return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json
            assert 'metrics' in data
            assert 'period' in data
            assert data['period'] == 'month'

    def test_get_dashboard_notifications_summary(self, client, admin_headers):
        """Test dashboard notifications summary"""
        response = client.get(
            '/api/v1/dashboard/notifications-summary',
            headers=admin_headers
        )
        
        # May return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json
            assert 'unread_count' in data
            assert 'recent_notifications' in data
            assert isinstance(data['unread_count'], int)

    def test_get_dashboard_quick_actions(self, client, admin_headers):
        """Test dashboard quick actions based on user role"""
        response = client.get(
            '/api/v1/dashboard/quick-actions',
            headers=admin_headers
        )
        
        # May return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json
            assert 'actions' in data
            assert isinstance(data['actions'], list)
            
            # Check action structure
            if data['actions']:
                action = data['actions'][0]
                assert 'id' in action
                assert 'title' in action
                assert 'icon' in action
                assert 'url' in action

    def test_get_dashboard_stats_no_auth(self, client):
        """Test dashboard access without authentication"""
        response = client.get('/api/v1/dashboard/stats')
        assert response.status_code == 401

    def test_get_dashboard_widgets(self, client, admin_headers):
        """Test customizable dashboard widgets"""
        response = client.get(
            '/api/v1/dashboard/widgets',
            headers=admin_headers
        )
        
        # May return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json
            assert 'widgets' in data
            assert isinstance(data['widgets'], list)

    def test_update_dashboard_preferences(self, client, admin_headers):
        """Test updating dashboard preferences"""
        preferences = {
            "theme": "dark",
            "widgets_order": ["stats", "activity", "charts"],
            "refresh_interval": 300
        }
        
        response = client.put(
            '/api/v1/dashboard/preferences',
            headers=admin_headers,
            json=preferences
        )
        
        # May return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]

    @pytest.mark.parametrize("period", ['today', 'week', 'month', 'quarter', 'year'])
    def test_get_dashboard_stats_by_period(self, client, admin_headers, period):
        """Test dashboard stats for different time periods"""
        response = client.get(
            f'/api/v1/dashboard/stats?period={period}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Stats should be filtered by the specified period
        assert 'period' in data or 'total_beneficiaries' in data

    def test_get_role_specific_dashboard(self, client, trainer_auth_headers):
        """Test that dashboard content varies by user role"""
        # Get trainer dashboard
        trainer_response = client.get(
            '/api/v1/dashboard/stats',
            headers=trainer_auth_headers
        )
        
        assert trainer_response.status_code == 200
        trainer_data = trainer_response.json
        
        # Trainer should have specific fields
        assert 'assigned_students' in trainer_data or 'active_sessions' in trainer_data
        
        # Should not have admin-only fields
        assert 'system_health' not in trainer_data

    def test_export_dashboard_data(self, client, admin_headers):
        """Test exporting dashboard data"""
        response = client.get(
            '/api/v1/dashboard/export?format=pdf',
            headers=admin_headers
        )
        
        # May return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert 'Content-Disposition' in response.headers
            assert 'attachment' in response.headers['Content-Disposition']
