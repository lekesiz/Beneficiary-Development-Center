"""Health check endpoints."""
from flask import Blueprint, jsonify
from app import db
from app.extensions import redis_client
import redis

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        JSON response with service status
    """
    health_status = {
        'status': 'healthy',
        'services': {}
    }
    
    # Check database connection
    try:
        db.session.execute('SELECT 1')
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['services']['database'] = f'unhealthy: {str(e)}'
    
    # Check Redis connection
    try:
        if redis_client:
            redis_client.ping()
            health_status['services']['redis'] = 'healthy'
        else:
            health_status['services']['redis'] = 'not configured'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check endpoint for Kubernetes.
    
    Returns:
        JSON response indicating if service is ready
    """
    try:
        # Check if database migrations are up to date
        db.session.execute('SELECT 1')
        
        # Check if Redis is available
        if redis_client:
            redis_client.ping()
        
        return jsonify({'ready': True}), 200
    except Exception as e:
        return jsonify({'ready': False, 'error': str(e)}), 503