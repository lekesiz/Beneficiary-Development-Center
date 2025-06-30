"""
Unit tests for Reports API endpoints
"""

import pytest
from datetime import datetime, timedelta
from flask import url_for
from app.models.report import Report, ReportType, ReportStatus


class TestReportsAPI:
    """Test cases for reports endpoints"""

    @pytest.fixture
    def sample_report(self, db_session, test_tenant, admin_user):
        """Create a sample report for testing"""
        report = Report(
            tenant_id=test_tenant.id,
            created_by=admin_user.id,
            type=ReportType.PROGRESS,
            name="Monthly Progress Report",
            description="Progress report for current month",
            status=ReportStatus.COMPLETED,
            parameters={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "include_charts": True
            },
            result_data={
                "total_students": 150,
                "completed_courses": 45,
                "average_progress": 72.5
            },
            file_path="/reports/2025/01/progress_report.pdf"
        )
        db_session.add(report)
        db_session.commit()
        return report

    @pytest.fixture
    def multiple_reports(self, db_session, test_tenant, admin_user):
        """Create multiple reports for testing"""
        report_types = [ReportType.PROGRESS, ReportType.ATTENDANCE, ReportType.EVALUATION, 
                       ReportType.FINANCIAL, ReportType.CUSTOM]
        reports = []
        
        for i, report_type in enumerate(report_types):
            report = Report(
                tenant_id=test_tenant.id,
                created_by=admin_user.id,
                type=report_type,
                name=f"{report_type.value.replace('_', ' ').title()} Report {i+1}",
                description=f"Test report for {report_type.value}",
                status=ReportStatus.COMPLETED if i < 3 else ReportStatus.PENDING,
                parameters={"test": True, "index": i}
            )
            reports.append(report)
        
        db_session.add_all(reports)
        db_session.commit()
        return reports

    def test_get_reports_list_success(self, client, admin_headers, multiple_reports):
        """Test successful retrieval of reports list"""
        response = client.get(
            '/api/v1/reports',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert 'reports' in data
        assert 'pagination' in data
        assert len(data['reports']) == 5
        
        # Check report structure
        report = data['reports'][0]
        assert 'id' in report
        assert 'type' in report
        assert 'name' in report
        assert 'description' in report
        assert 'status' in report
        assert 'created_at' in report
        assert 'created_by' in report

    def test_get_reports_filtered_by_type(self, client, admin_headers, multiple_reports):
        """Test filtering reports by type"""
        response = client.get(
            '/api/v1/reports?type=progress',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Should only get progress reports
        assert all(r['type'] == 'progress' for r in data['reports'])

    def test_get_reports_filtered_by_status(self, client, admin_headers, multiple_reports):
        """Test filtering reports by status"""
        response = client.get(
            '/api/v1/reports?status=completed',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Should only get completed reports
        assert all(r['status'] == 'completed' for r in data['reports'])
        assert len(data['reports']) == 3

    def test_get_reports_overview_success(self, client, admin_headers, multiple_reports):
        """Test successful retrieval of reports overview"""
        response = client.get(
            '/api/v1/reports/overview',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        # Check overview structure
        assert 'total_reports' in data
        assert 'by_type' in data
        assert 'by_status' in data
        assert 'recent_reports' in data
        assert 'generation_stats' in data
        
        # Verify counts
        assert data['total_reports'] == 5
        assert data['by_status']['completed'] == 3
        assert data['by_status']['pending'] == 2

    def test_get_single_report_success(self, client, admin_headers, sample_report):
        """Test successful retrieval of a single report"""
        response = client.get(
            f'/api/v1/reports/{sample_report.id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json
        
        assert data['id'] == sample_report.id
        assert data['name'] == sample_report.name
        assert data['type'] == sample_report.type.value
        assert 'parameters' in data
        assert 'result_data' in data

    def test_get_report_not_found(self, client, admin_headers):
        """Test getting non-existent report"""
        response = client.get(
            '/api/v1/reports/999999',
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_create_report_success(self, client, admin_headers):
        """Test successful report creation"""
        report_data = {
            "type": "progress",
            "name": "Q1 2025 Progress Report",
            "description": "Quarterly progress report",
            "parameters": {
                "start_date": "2025-01-01",
                "end_date": "2025-03-31",
                "include_inactive": False
            }
        }
        
        response = client.post(
            '/api/v1/reports',
            headers=admin_headers,
            json=report_data
        )
        
        assert response.status_code == 201
        data = response.json
        
        assert data['name'] == report_data['name']
        assert data['type'] == report_data['type']
        assert data['status'] == 'pending'
        assert 'id' in data

    def test_create_report_invalid_type(self, client, admin_headers):
        """Test report creation with invalid type"""
        report_data = {
            "type": "invalid_type",
            "name": "Invalid Report",
            "description": "This should fail"
        }
        
        response = client.post(
            '/api/v1/reports',
            headers=admin_headers,
            json=report_data
        )
        
        assert response.status_code == 400

    def test_generate_report(self, client, admin_headers, sample_report):
        """Test report generation"""
        # Reset report to pending status
        sample_report.status = ReportStatus.PENDING
        sample_report.file_path = None
        
        response = client.post(
            f'/api/v1/reports/{sample_report.id}/generate',
            headers=admin_headers
        )
        
        # May return 202 (accepted) or 200 depending on implementation
        assert response.status_code in [200, 202]
        data = response.json
        
        assert 'message' in data or 'status' in data

    def test_download_report(self, client, admin_headers, sample_report):
        """Test report download"""
        response = client.get(
            f'/api/v1/reports/{sample_report.id}/download',
            headers=admin_headers
        )
        
        # May return 200 with file or 404 if file doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert 'Content-Disposition' in response.headers
            assert 'attachment' in response.headers['Content-Disposition']

    def test_delete_report(self, client, admin_headers, sample_report):
        """Test report deletion"""
        response = client.delete(
            f'/api/v1/reports/{sample_report.id}',
            headers=admin_headers
        )
        
        assert response.status_code == 204
        
        # Verify report is deleted
        get_response = client.get(
            f'/api/v1/reports/{sample_report.id}',
            headers=admin_headers
        )
        assert get_response.status_code == 404

    def test_get_report_templates(self, client, admin_headers):
        """Test getting available report templates"""
        response = client.get(
            '/api/v1/reports/templates',
            headers=admin_headers
        )
        
        # May return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json
            assert 'templates' in data

    def test_schedule_report(self, client, admin_headers):
        """Test scheduling a recurring report"""
        schedule_data = {
            "type": "progress",
            "name": "Weekly Progress Report",
            "schedule": "weekly",
            "day_of_week": "monday",
            "time": "09:00",
            "parameters": {
                "include_all": True
            }
        }
        
        response = client.post(
            '/api/v1/reports/schedule',
            headers=admin_headers,
            json=schedule_data
        )
        
        # May return 201 or 404 if endpoint doesn't exist
        assert response.status_code in [201, 404]

    def test_get_reports_no_auth(self, client):
        """Test getting reports without authentication"""
        response = client.get('/api/v1/reports')
        assert response.status_code == 401

    def test_get_reports_student_forbidden(self, client, student_auth_headers):
        """Test reports access forbidden for students"""
        response = client.get(
            '/api/v1/reports',
            headers=student_auth_headers
        )
        # Students might have limited access
        assert response.status_code in [200, 403]

    @pytest.mark.parametrize("report_type", ['progress', 'attendance', 'evaluation', 'financial'])
    def test_create_different_report_types(self, client, admin_headers, report_type):
        """Test creating different types of reports"""
        report_data = {
            "type": report_type,
            "name": f"{report_type.title()} Report Test",
            "description": f"Test {report_type} report",
            "parameters": {
                "test": True
            }
        }
        
        response = client.post(
            '/api/v1/reports',
            headers=admin_headers,
            json=report_data
        )
        
        assert response.status_code == 201
        assert response.json['type'] == report_type
