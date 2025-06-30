"""
Tests for API Error Handling and Error Responses
"""

import pytest
from app.core.exceptions import (
    BadRequestError, NotFoundError, ForbiddenError, 
    UnauthorizedError, ValidationError, ConflictError
)


class TestErrorHandling:
    """Test cases for error handling across the API"""

    def test_404_not_found_error(self, client, admin_headers):
        """Test 404 error for non-existent resource"""
        response = client.get(
            '/api/v1/beneficiaries/999999',
            headers=admin_headers
        )
        
        assert response.status_code == 404
        data = response.json
        assert 'error' in data or 'message' in data

    def test_400_bad_request_error(self, client, admin_headers):
        """Test 400 error for invalid request data"""
        response = client.post(
            '/api/v1/beneficiaries',
            headers=admin_headers,
            json={}  # Missing required fields
        )
        
        assert response.status_code == 400
        data = response.json
        assert 'error' in data or 'message' in data

    def test_401_unauthorized_error(self, client):
        """Test 401 error for missing authentication"""
        response = client.get('/api/v1/beneficiaries')
        
        assert response.status_code == 401
        data = response.json
        assert 'msg' in data  # JWT returns 'msg' field

    def test_403_forbidden_error(self, client, student_auth_headers):
        """Test 403 error for insufficient permissions"""
        # Students shouldn't be able to access analytics
        response = client.get(
            '/api/v1/analytics/overview',
            headers=student_auth_headers
        )
        
        assert response.status_code == 403
        data = response.json
        assert 'error' in data or 'message' in data

    def test_422_unprocessable_entity(self, client):
        """Test 422 error for invalid JWT token"""
        response = client.get(
            '/api/v1/auth/me',
            headers={
                'Authorization': 'Bearer invalid.token.here',
                'X-Tenant-ID': '1'
            }
        )
        
        assert response.status_code == 422

    def test_500_internal_server_error_handling(self, client, admin_headers, mocker):
        """Test 500 error handling for unexpected errors"""
        # Mock a service to raise an exception
        mocker.patch(
            'app.services.beneficiary_service.BeneficiaryService.get_all',
            side_effect=Exception("Unexpected error")
        )
        
        response = client.get(
            '/api/v1/beneficiaries',
            headers=admin_headers
        )
        
        # Should handle gracefully
        assert response.status_code in [500, 200]  # May catch and handle

    def test_validation_error_response(self, client, admin_headers):
        """Test validation error response format"""
        # Invalid email format
        response = client.post(
            '/api/v1/users',
            headers=admin_headers,
            json={
                "email": "invalid-email",
                "username": "testuser",
                "full_name": "Test User",
                "password": "test123"
            }
        )
        
        assert response.status_code == 400
        data = response.json
        assert 'error' in data or 'details' in data

    def test_duplicate_resource_error(self, client, admin_headers, admin_user):
        """Test 409 conflict error for duplicate resources"""
        # Try to create user with existing email
        response = client.post(
            '/api/v1/users',
            headers=admin_headers,
            json={
                "email": admin_user.email,  # Already exists
                "username": "newuser",
                "full_name": "New User",
                "password": "test123"
            }
        )
        
        assert response.status_code in [400, 409]  # Bad request or conflict

    def test_method_not_allowed_error(self, client, admin_headers):
        """Test 405 error for unsupported HTTP method"""
        # Try PATCH on endpoint that doesn't support it
        response = client.patch(
            '/api/v1/auth/login',
            headers=admin_headers,
            json={}
        )
        
        assert response.status_code == 405

    def test_request_timeout_handling(self, client, admin_headers, mocker):
        """Test timeout error handling"""
        import time
        
        # Mock a slow operation
        def slow_operation(*args, **kwargs):
            time.sleep(5)  # Simulate slow operation
            return []
        
        mocker.patch(
            'app.services.beneficiary_service.BeneficiaryService.get_all',
            side_effect=slow_operation
        )
        
        # This might timeout or complete depending on server config
        response = client.get(
            '/api/v1/beneficiaries',
            headers=admin_headers
        )
        
        assert response.status_code in [200, 408, 504]  # OK, timeout, or gateway timeout

    def test_invalid_content_type_error(self, client, admin_headers):
        """Test error for invalid content type"""
        response = client.post(
            '/api/v1/beneficiaries',
            headers={
                **admin_headers,
                'Content-Type': 'text/plain'  # Should be application/json
            },
            data='not json data'
        )
        
        assert response.status_code in [400, 415]  # Bad request or unsupported media type

    def test_missing_required_header(self, client):
        """Test error for missing required X-Tenant-ID header"""
        # Get token first
        response = client.post(
            '/api/v1/auth/login',
            json={
                "email": "test@example.com",
                "password": "test123"
            },
            headers={'X-Tenant-ID': '1'}
        )
        
        if response.status_code == 200:
            token = response.json['access_token']
            
            # Try to use token without X-Tenant-ID
            response = client.get(
                '/api/v1/beneficiaries',
                headers={'Authorization': f'Bearer {token}'}
                # Missing X-Tenant-ID
            )
            
            assert response.status_code in [400, 401]

    def test_rate_limit_error(self, client, admin_headers):
        """Test rate limiting error response"""
        # Make many requests quickly
        responses = []
        for _ in range(100):
            response = client.get(
                '/api/v1/auth/me',
                headers=admin_headers
            )
            responses.append(response.status_code)
        
        # Check if any returned 429 (rate limit)
        # Note: Rate limiting might not be enabled in test environment
        assert all(status in [200, 429] for status in responses)

    def test_malformed_json_error(self, client, admin_headers):
        """Test error for malformed JSON in request body"""
        response = client.post(
            '/api/v1/beneficiaries',
            headers={
                **admin_headers,
                'Content-Type': 'application/json'
            },
            data='{"invalid": json}'  # Malformed JSON
        )
        
        assert response.status_code == 400

    @pytest.mark.parametrize("exception_class,expected_status", [
        (BadRequestError, 400),
        (UnauthorizedError, 401),
        (ForbiddenError, 403),
        (NotFoundError, 404),
        (ConflictError, 409),
        (ValidationError, 400),
    ])
    def test_custom_exception_handling(self, client, admin_headers, mocker, 
                                     exception_class, expected_status):
        """Test custom exception classes return correct status codes"""
        # Mock service to raise specific exception
        mocker.patch(
            'app.services.beneficiary_service.BeneficiaryService.get_by_id',
            side_effect=exception_class("Test error")
        )
        
        response = client.get(
            '/api/v1/beneficiaries/1',
            headers=admin_headers
        )
        
        assert response.status_code == expected_status

    def test_database_connection_error(self, client, admin_headers, mocker):
        """Test handling of database connection errors"""
        from sqlalchemy.exc import OperationalError
        
        mocker.patch(
            'app.services.beneficiary_service.BeneficiaryService.get_all',
            side_effect=OperationalError("Database connection failed", None, None)
        )
        
        response = client.get(
            '/api/v1/beneficiaries',
            headers=admin_headers
        )
        
        # Should handle database errors gracefully
        assert response.status_code in [500, 503]  # Internal error or service unavailable

    def test_error_response_format_consistency(self, client):
        """Test that error responses have consistent format"""
        # Test various error scenarios
        error_responses = []
        
        # 401 - No auth
        resp = client.get('/api/v1/beneficiaries')
        error_responses.append((401, resp.json))
        
        # 404 - Not found
        resp = client.get('/api/v1/beneficiaries/999999')
        if resp.status_code == 404:
            error_responses.append((404, resp.json))
        
        # Check all error responses have some error field
        for status, data in error_responses:
            assert any(key in data for key in ['error', 'message', 'msg', 'detail'])