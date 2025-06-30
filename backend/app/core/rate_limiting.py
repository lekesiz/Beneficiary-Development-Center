"""
Advanced rate limiting configuration for BDC Platform
Implements tiered rate limits based on user roles and endpoints
"""

from flask import current_app, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_rate_limit_key() -> str:
    """
    Generate rate limit key based on user authentication status
    
    Returns:
        Rate limit key combining IP and user ID if authenticated
    """
    # Get real IP address
    from app.core.security import get_real_ip
    ip_address = get_real_ip()
    
    # Include user ID if authenticated
    user_id = getattr(g, 'current_user_id', None)
    
    if user_id:
        return f"{ip_address}:user:{user_id}"
    
    return f"{ip_address}:anonymous"


def get_rate_limit_for_endpoint() -> str:
    """
    Get rate limit based on endpoint and user role
    
    Returns:
        Rate limit string (e.g., "100 per hour")
    """
    # Get user role
    user_role = getattr(g, 'current_user_role', 'anonymous')
    
    # Define rate limits by role
    role_limits = {
        'admin': {
            'default': '10000 per hour',
            'auth': '100 per hour',
            'files': '1000 per hour',
            'api': '5000 per hour'
        },
        'trainer': {
            'default': '5000 per hour',
            'auth': '50 per hour',
            'files': '500 per hour',
            'api': '2000 per hour'
        },
        'student': {
            'default': '1000 per hour',
            'auth': '20 per hour',
            'files': '100 per hour',
            'api': '500 per hour'
        },
        'anonymous': {
            'default': '100 per hour',
            'auth': '10 per hour',
            'files': '0 per hour',  # No file access for anonymous
            'api': '50 per hour'
        }
    }
    
    # Determine endpoint category
    endpoint = request.endpoint or ''
    
    if 'auth' in endpoint:
        category = 'auth'
    elif 'files' in endpoint:
        category = 'files'
    elif 'api' in endpoint:
        category = 'api'
    else:
        category = 'default'
    
    # Get limits for role
    limits = role_limits.get(user_role, role_limits['anonymous'])
    limit = limits.get(category, limits['default'])
    
    # Log rate limit application
    logger.debug(f"Rate limit for {user_role} on {category}: {limit}")
    
    return limit


def create_limiter(app=None) -> Limiter:
    """
    Create and configure Flask-Limiter instance
    
    Args:
        app: Flask application instance
        
    Returns:
        Configured Limiter instance
    """
    limiter = Limiter(
        app=app,
        key_func=get_rate_limit_key,
        default_limits=["1000 per hour", "100 per minute"],
        storage_uri=lambda: current_app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
        strategy='fixed-window-elastic-expiry',
        headers_enabled=True,
        swallow_errors=True,
        on_breach=handle_rate_limit_exceeded
    )
    
    return limiter


def handle_rate_limit_exceeded(request_limit):
    """
    Handle rate limit exceeded events
    
    Args:
        request_limit: The limit that was exceeded
    """
    from app.core.security import log_security_event
    
    # Log the event
    log_security_event('rate_limit_exceeded', {
        'limit': str(request_limit.limit),
        'endpoint': request.endpoint,
        'user_role': getattr(g, 'current_user_role', 'anonymous')
    })
    
    # Could also trigger alerts, temporary bans, etc.
    

# Predefined rate limit decorators for common use cases
def auth_rate_limit():
    """Rate limit for authentication endpoints"""
    return "5 per minute, 20 per hour"


def api_rate_limit():
    """Rate limit for general API endpoints"""
    return get_rate_limit_for_endpoint()


def file_upload_rate_limit():
    """Rate limit for file upload endpoints"""
    return "10 per hour, 100 per day"


def search_rate_limit():
    """Rate limit for search endpoints"""
    return "30 per minute, 500 per hour"


def export_rate_limit():
    """Rate limit for data export endpoints"""
    return "5 per hour, 20 per day"


def webhook_rate_limit():
    """Rate limit for webhook endpoints"""
    return "1000 per minute"


# Endpoint-specific rate limit configurations
ENDPOINT_LIMITS = {
    # Authentication endpoints
    'api_v1.auth.login': '5 per minute, 20 per hour',
    'api_v1.auth.register': '3 per hour, 10 per day',
    'api_v1.auth.forgot_password': '3 per hour',
    'api_v1.auth.reset_password': '3 per hour',
    
    # File endpoints
    'api_v1.files.upload_file': '10 per hour, 50 per day',
    'api_v1.files.download_file': '100 per hour',
    'api_v1.files.get_upload_url': '20 per hour',
    
    # Search endpoints
    'api_v1.beneficiaries.search': '30 per minute',
    'api_v1.programs.search': '30 per minute',
    
    # Export endpoints
    'api_v1.reports.export': '5 per hour',
    'api_v1.beneficiaries.export': '5 per hour',
    
    # Admin endpoints
    'api_v1.admin': '1000 per hour',
    
    # Public endpoints
    'api_v1.health': '60 per minute',
    'api_v1.status': '60 per minute'
}


def configure_endpoint_limits(limiter: Limiter):
    """
    Configure specific rate limits for endpoints
    
    Args:
        limiter: Flask-Limiter instance
    """
    # This function is not compatible with flask-limiter 3.x
    # Rate limits should be applied using decorators instead
    pass


# Custom rate limit error messages
RATE_LIMIT_MESSAGES = {
    'auth': 'Too many authentication attempts. Please try again later.',
    'files': 'File operation rate limit exceeded. Please wait before trying again.',
    'api': 'API rate limit exceeded. Please reduce your request frequency.',
    'default': 'Rate limit exceeded. Please try again later.'
}


def get_rate_limit_message() -> str:
    """Get appropriate rate limit error message based on endpoint"""
    endpoint = request.endpoint or ''
    
    if 'auth' in endpoint:
        return RATE_LIMIT_MESSAGES['auth']
    elif 'files' in endpoint:
        return RATE_LIMIT_MESSAGES['files']
    elif 'api' in endpoint:
        return RATE_LIMIT_MESSAGES['api']
    
    return RATE_LIMIT_MESSAGES['default']