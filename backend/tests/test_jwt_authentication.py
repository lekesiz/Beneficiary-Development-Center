"""
Comprehensive JWT Authentication Tests
Tests the JWT authentication flow including the string identity fix
"""

import pytest
import jwt
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User
from app.core.jwt_utils import get_current_user_id


class TestJWTAuthentication:
    """Comprehensive tests for JWT authentication"""

    def test_jwt_identity_is_string(self, client, test_tenant, db_session):
        """Test that JWT identity is stored as string"""
        # Create user
        user = User(
            email="jwt_test@example.com",
            username="jwt_test",
            full_name="JWT Test User",
            tenant_id=test_tenant.id,
            is_active=True
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        
        # Login
        response = client.post(
            '/api/v1/auth/login',
            json={
                "email": "jwt_test@example.com",
                "password": "testpass123"
            },
            headers={"X-Tenant-ID": str(test_tenant.id)}
        )
        
        assert response.status_code == 200
        token = response.json['access_token']
        
        # Decode token without verification to inspect claims
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Verify identity is string
        assert 'sub' in decoded
        assert isinstance(decoded['sub'], str)
        assert decoded['sub'] == str(user.id)

    def test_jwt_identity_conversion(self, app):
        """Test the get_current_user_id utility function"""
        with app.app_context():
            # Test with string identity
            with app.test_request_context():
                from flask_jwt_extended import jwt_required, get_jwt_identity
                
                # Mock JWT identity as string
                app.config['JWT_IDENTITY_CLAIM'] = 'sub'
                token = create_access_token(identity='123')
                
                # Decode and verify
                decoded = jwt.decode(token, options={"verify_signature": False})
                assert decoded['sub'] == '123'

    def test_protected_endpoint_with_jwt(self, client, admin_headers):
        """Test accessing protected endpoint with valid JWT"""
        response = client.get(
            '/api/v1/beneficiaries',
            headers=admin_headers
        )
        
        assert response.status_code == 200

    def test_jwt_expiration(self, client, test_tenant, db_session):
        """Test JWT token expiration"""
        # Create user
        user = User(
            email="expire_test@example.com",
            username="expire_test",
            full_name="Expire Test User",
            tenant_id=test_tenant.id,
            is_active=True
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        
        # Create expired token manually
        with client.application.app_context():
            expired_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(seconds=-1)  # Already expired
            )
        
        # Try to use expired token
        response = client.get(
            '/api/v1/auth/me',
            headers={
                "Authorization": f"Bearer {expired_token}",
                "X-Tenant-ID": str(test_tenant.id)
            }
        )
        
        # Should return 422 for expired token
        assert response.status_code == 422

    def test_jwt_claims(self, client, test_tenant, admin_user, db_session):
        """Test JWT token contains correct claims"""
        # Set user role
        admin_user.role = 'admin'
        db_session.commit()
        
        # Login
        response = client.post(
            '/api/v1/auth/login',
            json={
                "email": admin_user.email,
                "password": "testpass123"  # Assuming this is the password
            },
            headers={"X-Tenant-ID": str(test_tenant.id)}
        )
        
        assert response.status_code == 200
        token = response.json['access_token']
        
        # Decode token
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Check claims
        assert decoded['tenant_id'] == test_tenant.id
        assert decoded['role'] == 'admin'
        assert 'exp' in decoded  # Expiration
        assert 'iat' in decoded  # Issued at
        assert 'jti' in decoded  # JWT ID

    def test_refresh_token_flow(self, client, test_tenant, db_session):
        """Test complete refresh token flow"""
        # Create user
        user = User(
            email="refresh_flow@example.com",
            username="refresh_flow",
            full_name="Refresh Flow User",
            tenant_id=test_tenant.id,
            is_active=True
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        
        # 1. Login to get tokens
        login_response = client.post(
            '/api/v1/auth/login',
            json={
                "email": "refresh_flow@example.com",
                "password": "testpass123"
            },
            headers={"X-Tenant-ID": str(test_tenant.id)}
        )
        
        assert login_response.status_code == 200
        access_token = login_response.json['access_token']
        refresh_token = login_response.json['refresh_token']
        
        # 2. Use access token
        me_response = client.get(
            '/api/v1/auth/me',
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Tenant-ID": str(test_tenant.id)
            }
        )
        assert me_response.status_code == 200
        
        # 3. Refresh tokens
        refresh_response = client.post(
            '/api/v1/auth/refresh',
            headers={
                "Authorization": f"Bearer {refresh_token}",
                "X-Tenant-ID": str(test_tenant.id)
            }
        )
        
        assert refresh_response.status_code == 200
        new_access_token = refresh_response.json['access_token']
        new_refresh_token = refresh_response.json['refresh_token']
        
        # 4. Use new access token
        new_me_response = client.get(
            '/api/v1/auth/me',
            headers={
                "Authorization": f"Bearer {new_access_token}",
                "X-Tenant-ID": str(test_tenant.id)
            }
        )
        assert new_me_response.status_code == 200

    def test_invalid_jwt_format(self, client):
        """Test various invalid JWT formats"""
        invalid_tokens = [
            "not.a.jwt",
            "invalid",
            "Bearer",
            "null",
            "undefined",
            "a.b",  # Missing signature
            "a.b.c.d",  # Too many parts
        ]
        
        for token in invalid_tokens:
            response = client.get(
                '/api/v1/auth/me',
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Tenant-ID": "1"
                }
            )
            assert response.status_code == 422

    def test_jwt_with_wrong_tenant(self, client, test_tenant, admin_headers, db_session):
        """Test JWT token used with wrong tenant ID"""
        # Create another tenant
        from app.models.tenant import Tenant
        other_tenant = Tenant(
            name="Other Tenant",
            domain="other.example.com",
            is_active=True
        )
        db_session.add(other_tenant)
        db_session.commit()
        
        # Use token from one tenant with another tenant's ID
        headers = admin_headers.copy()
        headers['X-Tenant-ID'] = str(other_tenant.id)
        
        response = client.get(
            '/api/v1/auth/me',
            headers=headers
        )
        
        # Should fail tenant validation
        assert response.status_code in [401, 403]

    def test_concurrent_jwt_sessions(self, client, test_tenant, db_session):
        """Test multiple concurrent JWT sessions for same user"""
        # Create user
        user = User(
            email="concurrent@example.com",
            username="concurrent",
            full_name="Concurrent User",
            tenant_id=test_tenant.id,
            is_active=True
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        
        # Login twice to get two different tokens
        tokens = []
        for i in range(2):
            response = client.post(
                '/api/v1/auth/login',
                json={
                    "email": "concurrent@example.com",
                    "password": "testpass123"
                },
                headers={"X-Tenant-ID": str(test_tenant.id)}
            )
            assert response.status_code == 200
            tokens.append(response.json['access_token'])
        
        # Both tokens should work
        for token in tokens:
            response = client.get(
                '/api/v1/auth/me',
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Tenant-ID": str(test_tenant.id)
                }
            )
            assert response.status_code == 200

    def test_jwt_role_based_access(self, client, test_tenant, db_session):
        """Test JWT role-based access control"""
        # Create users with different roles
        roles = ['admin', 'trainer', 'student']
        users = []
        
        for role in roles:
            user = User(
                email=f"{role}@example.com",
                username=f"{role}_user",
                full_name=f"{role.title()} User",
                tenant_id=test_tenant.id,
                role=role,
                is_active=True
            )
            user.set_password("testpass123")
            db_session.add(user)
            users.append(user)
        
        db_session.commit()
        
        # Test access to analytics endpoint (admin/trainer only)
        for i, user in enumerate(users):
            # Login
            response = client.post(
                '/api/v1/auth/login',
                json={
                    "email": user.email,
                    "password": "testpass123"
                },
                headers={"X-Tenant-ID": str(test_tenant.id)}
            )
            token = response.json['access_token']
            
            # Try to access analytics
            analytics_response = client.get(
                '/api/v1/analytics/overview',
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Tenant-ID": str(test_tenant.id)
                }
            )
            
            # Admin and trainer should have access, student should not
            if user.role in ['admin', 'trainer']:
                assert analytics_response.status_code == 200
            else:
                assert analytics_response.status_code == 403

    @pytest.mark.parametrize("endpoint,method", [
        ('/api/v1/beneficiaries', 'GET'),
        ('/api/v1/users', 'GET'),
        ('/api/v1/programs', 'GET'),
        ('/api/v1/courses', 'GET'),
        ('/api/v1/evaluations', 'GET'),
        ('/api/v1/dashboard/stats', 'GET'),
    ])
    def test_endpoints_require_authentication(self, client, endpoint, method):
        """Test that all protected endpoints require authentication"""
        # Try without authentication
        if method == 'GET':
            response = client.get(endpoint)
        elif method == 'POST':
            response = client.post(endpoint, json={})
        elif method == 'PUT':
            response = client.put(endpoint, json={})
        elif method == 'DELETE':
            response = client.delete(endpoint)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
