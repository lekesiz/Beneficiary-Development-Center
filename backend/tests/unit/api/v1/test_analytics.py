"""
Unit tests for Analytics API endpoints
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for


class TestAnalyticsAPI:
    """Test cases for analytics endpoints"""

    def test_get_analytics_overview_success(self, client, admin_headers):
        """Test successful retrieval of analytics overview"""
        response = client.get(
            '/api/v1/analytics/overview',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check response structure
        assert 'beneficiaries' in data
        assert 'programs' in data
        assert 'evaluations' in data
        assert 'users' in data
        
        # Check beneficiaries metrics
        beneficiaries = data['beneficiaries']
        assert 'total' in beneficiaries
        assert 'active' in beneficiaries
        assert 'inactive' in beneficiaries
        assert 'by_status' in beneficiaries
        assert 'recent_registrations' in beneficiaries
        
        # Check programs metrics
        programs = data['programs']
        assert 'total' in programs
        assert 'active' in programs
        assert 'completed' in programs
        assert 'by_category' in programs
        assert 'enrollment_trends' in programs
        
        # Check evaluations metrics
        evaluations = data['evaluations']
        assert 'total' in evaluations
        assert 'active' in evaluations
        assert 'avg_score' in evaluations
        assert 'total_attempts' in evaluations
        assert 'completion_rate' in evaluations
        
        # Check users metrics
        users = data['users']
        assert 'total' in users
        assert 'by_role' in users
        assert 'active_today' in users
        assert 'active_this_week' in users
        assert 'active_this_month' in users

    def test_get_analytics_overview_no_auth(self, client):
        """Test analytics overview without authentication"""
        response = client.get('/api/v1/analytics/overview')
        assert response.status_code == 401

    def test_get_analytics_overview_student_forbidden(self, client, student_auth_headers):
        """Test analytics overview forbidden for students"""
        response = client.get(
            '/api/v1/analytics/overview',
            headers=student_auth_headers
        )
        assert response.status_code == 403

    def test_get_analytics_overview_trainer_allowed(self, client, trainer_auth_headers):
        """Test analytics overview allowed for trainers"""
        response = client.get(
            '/api/v1/analytics/overview',
            headers=trainer_auth_headers
        )
        assert response.status_code == 200

    def test_get_program_analytics_success(self, client, admin_headers, sample_program):
        """Test successful retrieval of program analytics"""
        response = client.get(
            f'/api/v1/analytics/programs/{sample_program.id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check response structure
        assert 'program' in data
        assert 'enrollments' in data
        assert 'completion_rate' in data
        assert 'average_progress' in data
        assert 'by_status' in data

    def test_get_program_analytics_not_found(self, client, admin_headers):
        """Test program analytics for non-existent program"""
        response = client.get(
            '/api/v1/analytics/programs/999999',
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_get_user_analytics_success(self, client, admin_headers):
        """Test successful retrieval of user analytics"""
        response = client.get(
            '/api/v1/analytics/users',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check response structure
        assert 'total_users' in data
        assert 'by_role' in data
        assert 'by_status' in data
        assert 'registration_trends' in data
        assert 'activity_metrics' in data

    def test_get_evaluation_analytics_success(self, client, admin_headers, sample_evaluation):
        """Test successful retrieval of evaluation analytics"""
        response = client.get(
            f'/api/v1/analytics/evaluations/{sample_evaluation.id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check response structure
        assert 'evaluation' in data
        assert 'total_attempts' in data
        assert 'unique_participants' in data
        assert 'average_score' in data
        assert 'pass_rate' in data
        assert 'score_distribution' in data

    def test_export_analytics_csv(self, client, admin_headers):
        """Test exporting analytics data as CSV"""
        response = client.get(
            '/api/v1/analytics/export?format=csv&type=overview',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert response.content_type == 'text/csv'
        assert 'Content-Disposition' in response.headers
        assert 'attachment' in response.headers['Content-Disposition']

    def test_export_analytics_excel(self, client, admin_headers):
        """Test exporting analytics data as Excel"""
        response = client.get(
            '/api/v1/analytics/export?format=excel&type=overview',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def test_get_performance_metrics(self, client, admin_headers):
        """Test retrieval of performance metrics"""
        response = client.get(
            '/api/v1/analytics/performance?period=month',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check response structure
        assert 'period' in data
        assert 'metrics' in data
        assert 'trends' in data
        assert 'comparisons' in data

    @pytest.mark.parametrize("period", ['day', 'week', 'month', 'quarter', 'year'])
    def test_get_analytics_by_period(self, client, admin_headers, period):
        """Test analytics retrieval for different time periods"""
        response = client.get(
            f'/api/v1/analytics/overview?period={period}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'period' in data
        assert data['period'] == period
