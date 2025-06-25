"""Custom decorators."""
from functools import wraps
from flask import jsonify
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