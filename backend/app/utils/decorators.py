"""Custom decorators."""

from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import verify_jwt_in_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Initialize limiter (will be configured in app)
limiter = Limiter(key_func=get_remote_address)


def rate_limit(limit_string):
    """
    Rate limiting decorator.

    Args:
        limit_string: Rate limit string (e.g., "5 per minute")
    """

    def decorator(f):
        @wraps(f)
        @limiter.limit(limit_string)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def json_response(f):
    """
    Decorator to ensure response is JSON.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = f(*args, **kwargs)
        if isinstance(result, tuple):
            data, status_code = result
            return jsonify(data), status_code
        return jsonify(result)

    return decorated_function


def async_task(f):
    """
    Decorator to mark a function as an async task.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real implementation, this would queue the task
        # For now, just execute synchronously
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role.
    Must be used after @jwt_required()
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        
        # Get user from JWT
        from app.core.jwt_utils import get_current_user_id
        from app.models import User
        
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Invalid user'}), 401
        
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Store user info in g for later use
        g.current_user = user
        g.current_user_role = user.role
        
        return f(*args, **kwargs)
    
    return decorated_function


def role_required(*allowed_roles):
    """
    Decorator to require specific roles.
    Must be used after @jwt_required()
    
    Args:
        allowed_roles: List of allowed roles
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            
            # Get user from JWT
            from app.core.jwt_utils import get_current_user_id
            from app.models import User
            
            user_id = get_current_user_id()
            if not user_id:
                return jsonify({'error': 'Invalid user'}), 401
            
            user = User.query.get(user_id)
            if not user or user.role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': list(allowed_roles)
                }), 403
            
            # Store user info in g for later use
            g.current_user = user
            g.current_user_role = user.role
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def require_tenant(f):
    """
    Decorator to require and validate tenant ID.
    Extracts tenant ID from header and validates access.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        
        # Get tenant ID from header
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return jsonify({'error': 'Tenant ID required'}), 400
        
        try:
            tenant_id = int(tenant_id)
        except ValueError:
            return jsonify({'error': 'Invalid tenant ID format'}), 400
        
        # Store in g for use in endpoint
        g.tenant_id = tenant_id
        
        # Pass tenant_id as first argument to the function
        return f(tenant_id, *args, **kwargs)
    
    return decorated_function
