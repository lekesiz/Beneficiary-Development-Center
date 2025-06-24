"""Custom decorators for the application."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.core.database import get_db
from app.models.user import User


def requires_role(allowed_roles):
    """Decorator to check if user has one of the allowed roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user
            current_user_id = get_jwt_identity()
            db = next(get_db())
            
            try:
                current_user = db.query(User).get(current_user_id)
                
                if not current_user:
                    return jsonify({'error': 'User not found'}), 404
                
                # Check if user has one of the allowed roles
                if current_user.role not in allowed_roles:
                    return jsonify({
                        'error': f'Access denied. Required roles: {", ".join(allowed_roles)}'
                    }), 403
                
                return f(*args, **kwargs)
                
            finally:
                db.close()
                
        return decorated_function
    return decorator


def tenant_required(f):
    """Decorator to ensure user has tenant_id."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get current user
        current_user_id = get_jwt_identity()
        db = next(get_db())
        
        try:
            current_user = db.query(User).get(current_user_id)
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 404
            
            if not current_user.tenant_id:
                return jsonify({'error': 'Tenant ID required'}), 400
                
            return f(*args, **kwargs)
            
        finally:
            db.close()
            
    return decorated_function


def rate_limit(max_requests=100, window_seconds=3600):
    """Rate limiting decorator (to be implemented with Redis)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Implement rate limiting with Redis
            # For now, just pass through
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_json(*required_fields):
    """Decorator to validate required JSON fields."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Check required fields
            missing_fields = []
            for field in required_fields:
                if field not in data or data[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator


def async_task(f):
    """Decorator to run function as async task with Celery."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement Celery task execution
        # For now, execute synchronously
        return f(*args, **kwargs)
    return decorated_function


def cache_result(timeout=300):
    """Cache function result (to be implemented with Redis)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Implement caching with Redis
            # For now, just execute the function
            return f(*args, **kwargs)
        return decorated_function
    return decorator