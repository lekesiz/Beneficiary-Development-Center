"""JWT Debug Middleware for development."""

from flask import request, current_app
from flask_jwt_extended import decode_token
import logging

logger = logging.getLogger(__name__)


def init_jwt_debug_middleware(app):
    """Initialize JWT debug middleware."""
    
    @app.before_request
    def jwt_debug():
        """Log JWT information for debugging."""
        if request.path.startswith('/api/'):
            # Log request details
            current_app.logger.debug(f"JWT Debug - Request: {request.method} {request.path}")
            
            # Check Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header:
                current_app.logger.debug(f"JWT Debug - Auth header present: {auth_header[:50]}...")
                
                # Try to decode token without verification for debugging
                try:
                    if auth_header.startswith('Bearer '):
                        token = auth_header.split(' ')[1]
                        # Decode without verification to see contents
                        decoded = decode_token(token, allow_expired=True)
                        current_app.logger.debug(f"JWT Debug - Token contents: sub={decoded.get('sub')}, tenant_id={decoded.get('tenant_id')}, role={decoded.get('role')}")
                        current_app.logger.debug(f"JWT Debug - Token expiry: exp={decoded.get('exp')}, iat={decoded.get('iat')}")
                except Exception as e:
                    current_app.logger.debug(f"JWT Debug - Failed to decode token: {str(e)}")
            else:
                current_app.logger.debug("JWT Debug - No Authorization header present")
            
            # Log other relevant headers
            tenant_header = request.headers.get('X-Tenant-ID')
            if tenant_header:
                current_app.logger.debug(f"JWT Debug - Tenant header: {tenant_header}")