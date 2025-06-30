"""
Admin API endpoints with enhanced security
Demonstrates usage of security decorators and rate limiting
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.core.security import (
    require_https, 
    validate_api_key, 
    validate_ip_whitelist,
    rate_limit_by_ip,
    log_security_event
)
from app.core.jwt_utils import get_current_user_id
from app.models import User
from app.extensions import limiter
from app.utils.decorators import admin_required

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
@limiter.limit("100 per hour")
def list_users():
    """List all users (admin only)"""
    user_id = get_current_user_id()
    
    # Log admin access
    log_security_event('admin_access', {
        'admin_id': user_id,
        'resource': 'user_list'
    })
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Query users
    users = User.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'users': [u.to_dict() for u in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    }), 200


@admin_bp.route('/security/events', methods=['GET'])
@jwt_required()
@admin_required
@require_https
@limiter.limit("50 per hour")
def security_events():
    """Get security events (requires HTTPS)"""
    # This would typically query a security events table
    # For now, return mock data
    
    events = [
        {
            'id': 1,
            'event_type': 'failed_login',
            'ip_address': '192.168.1.100',
            'timestamp': '2025-06-27T10:30:00Z',
            'details': {'username': 'admin@test.com'}
        },
        {
            'id': 2,
            'event_type': 'rate_limit_exceeded',
            'ip_address': '10.0.0.50',
            'timestamp': '2025-06-27T11:00:00Z',
            'details': {'endpoint': '/api/v1/auth/login'}
        }
    ]
    
    return jsonify({
        'events': events,
        'total': len(events)
    }), 200


@admin_bp.route('/system/config', methods=['GET'])
@validate_api_key
@validate_ip_whitelist(['127.0.0.1', '10.0.0.0/8', '172.16.0.0/12'])
@rate_limit_by_ip(max_requests=10, window=3600)
def system_config():
    """
    Get system configuration (API key + IP whitelist required)
    This endpoint is for external monitoring systems
    """
    import os
    
    config = {
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'gae_service': os.environ.get('GAE_SERVICE', 'default'),
        'gae_version': os.environ.get('GAE_VERSION', 'local'),
        'features': {
            'ai_insights': True,
            'file_uploads': True,
            'webhooks': False
        }
    }
    
    return jsonify(config), 200


@admin_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit("5 per hour")
def clear_cache():
    """Clear application cache"""
    from app.extensions import cache
    
    try:
        cache.clear()
        
        log_security_event('cache_cleared', {
            'admin_id': get_current_user_id()
        })
        
        return jsonify({
            'message': 'Cache cleared successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to clear cache',
            'details': str(e)
        }), 500


@admin_bp.route('/rate-limits', methods=['GET'])
@jwt_required()
@admin_required
def get_rate_limits():
    """Get current rate limit configuration"""
    from app.core.rate_limiting import ENDPOINT_LIMITS
    
    return jsonify({
        'endpoint_limits': ENDPOINT_LIMITS,
        'default_limits': ["1000 per hour", "100 per minute"]
    }), 200


@admin_bp.route('/health/detailed', methods=['GET'])
@jwt_required()
@admin_required
def detailed_health():
    """Get detailed health information"""
    from app.extensions import db, cache
    import psutil
    
    health = {
        'status': 'healthy',
        'components': {}
    }
    
    # Database health
    try:
        db.session.execute('SELECT 1')
        health['components']['database'] = {
            'status': 'healthy',
            'pool_size': db.engine.pool.size(),
            'checked_out_connections': db.engine.pool.checkedout()
        }
    except Exception as e:
        health['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health['status'] = 'degraded'
    
    # Cache health
    try:
        cache.set('health_check', True, timeout=10)
        if cache.get('health_check'):
            health['components']['cache'] = {'status': 'healthy'}
        else:
            health['components']['cache'] = {'status': 'unhealthy'}
    except Exception as e:
        health['components']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # System resources
    try:
        health['components']['system'] = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    except Exception:
        pass
    
    return jsonify(health), 200 if health['status'] == 'healthy' else 503


# Error handlers specific to admin endpoints
@admin_bp.errorhandler(403)
def admin_forbidden(e):
    """Handle admin access denied"""
    return jsonify({
        'error': 'Admin access required',
        'message': 'You do not have permission to access this resource'
    }), 403


@admin_bp.errorhandler(429)
def admin_rate_limit(e):
    """Handle rate limit exceeded for admin endpoints"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests to admin endpoint',
        'retry_after': e.description
    }), 429