"""
Google App Engine specific handlers and middleware
Handles GAE health checks, warmup requests, and headers
"""

from flask import Flask, jsonify, request, current_app
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


def init_gae_handlers(app: Flask):
    """Initialize Google App Engine specific handlers"""
    
    @app.route('/_ah/health')
    def health_check():
        """
        App Engine health check endpoint
        Used by GAE to determine if instance is healthy
        """
        # Perform basic health checks
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'bdc-platform',
            'version': os.environ.get('GAE_VERSION', 'unknown')
        }
        
        # Check database connectivity
        try:
            from app.extensions import db
            db.engine.execute('SELECT 1')
            health_status['database'] = 'connected'
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            health_status['database'] = 'error'
            health_status['status'] = 'unhealthy'
            return jsonify(health_status), 503
        
        # Check cache connectivity
        try:
            from app.extensions import cache
            cache.set('health_check', 'ok', timeout=10)
            if cache.get('health_check') == 'ok':
                health_status['cache'] = 'connected'
            else:
                health_status['cache'] = 'error'
        except Exception as e:
            logger.warning(f"Cache health check failed: {str(e)}")
            health_status['cache'] = 'unavailable'
        
        return jsonify(health_status), 200
    
    @app.route('/_ah/warmup')
    def warmup():
        """
        App Engine warmup endpoint
        Called to initialize new instances before they receive traffic
        """
        logger.info("Warming up App Engine instance")
        
        warmup_tasks = []
        
        # Warm up database connection pool
        try:
            from app.extensions import db
            db.engine.execute('SELECT 1')
            warmup_tasks.append('database')
        except Exception as e:
            logger.error(f"Database warmup failed: {str(e)}")
        
        # Warm up cache connection
        try:
            from app.extensions import cache
            cache.set('warmup', True, timeout=60)
            warmup_tasks.append('cache')
        except Exception as e:
            logger.warning(f"Cache warmup failed: {str(e)}")
        
        # Pre-load frequently used data
        try:
            from app.models import User, Tenant
            # Load system tenant
            Tenant.query.filter_by(id=1).first()
            warmup_tasks.append('models')
        except Exception as e:
            logger.warning(f"Model warmup failed: {str(e)}")
        
        # Initialize any ML models or heavy resources
        try:
            # Add any ML model loading here
            warmup_tasks.append('resources')
        except Exception as e:
            logger.warning(f"Resource warmup failed: {str(e)}")
        
        response = {
            'status': 'warmed up',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks_completed': warmup_tasks,
            'instance_id': os.environ.get('GAE_INSTANCE', 'unknown')
        }
        
        logger.info(f"Warmup completed: {warmup_tasks}")
        return jsonify(response), 200
    
    @app.route('/_ah/start')
    def start():
        """
        App Engine start endpoint
        Called when instance starts
        """
        logger.info("App Engine instance starting")
        
        return jsonify({
            'status': 'started',
            'timestamp': datetime.utcnow().isoformat(),
            'version': os.environ.get('GAE_VERSION', 'unknown')
        }), 200
    
    @app.route('/_ah/stop')
    def stop():
        """
        App Engine stop endpoint
        Called when instance is about to be shut down
        """
        logger.info("App Engine instance stopping")
        
        # Perform any cleanup tasks
        cleanup_tasks = []
        
        # Close database connections gracefully
        try:
            from app.extensions import db
            db.session.remove()
            cleanup_tasks.append('database')
        except Exception as e:
            logger.error(f"Database cleanup failed: {str(e)}")
        
        # Clear cache if needed
        try:
            from app.extensions import cache
            cache.clear()
            cleanup_tasks.append('cache')
        except Exception as e:
            logger.warning(f"Cache cleanup failed: {str(e)}")
        
        response = {
            'status': 'stopping',
            'timestamp': datetime.utcnow().isoformat(),
            'cleanup_completed': cleanup_tasks
        }
        
        logger.info(f"Cleanup completed: {cleanup_tasks}")
        return jsonify(response), 200
    
    @app.before_request
    def log_gae_headers():
        """Log Google App Engine specific headers for debugging"""
        if current_app.config.get('DEBUG') or current_app.config.get('LOG_GAE_HEADERS'):
            gae_headers = {
                'GAE_ENV': os.environ.get('GAE_ENV'),
                'GAE_APPLICATION': os.environ.get('GAE_APPLICATION'),
                'GAE_SERVICE': os.environ.get('GAE_SERVICE'),
                'GAE_VERSION': os.environ.get('GAE_VERSION'),
                'GAE_INSTANCE': os.environ.get('GAE_INSTANCE'),
                'X-Appengine-Country': request.headers.get('X-Appengine-Country'),
                'X-Appengine-Region': request.headers.get('X-Appengine-Region'),
                'X-Appengine-City': request.headers.get('X-Appengine-City'),
                'X-Appengine-CityLatLong': request.headers.get('X-Appengine-CityLatLong'),
                'X-Appengine-User-IP': request.headers.get('X-Appengine-User-IP'),
                'X-Cloud-Trace-Context': request.headers.get('X-Cloud-Trace-Context')
            }
            
            # Filter out None values
            gae_headers = {k: v for k, v in gae_headers.items() if v is not None}
            
            if gae_headers:
                logger.debug(f"GAE Headers: {gae_headers}")
    
    @app.errorhandler(413)
    def handle_large_request(e):
        """Handle requests that exceed App Engine's 32MB limit"""
        return jsonify({
            'error': 'Request too large',
            'message': 'Request size exceeds the maximum allowed limit',
            'max_size_mb': 32
        }), 413
    
    @app.errorhandler(408)
    def handle_timeout(e):
        """Handle App Engine timeout errors"""
        return jsonify({
            'error': 'Request timeout',
            'message': 'The request took too long to process',
            'timeout_seconds': 60
        }), 408
    
    # Add App Engine specific headers to all responses
    @app.after_request
    def add_gae_headers(response):
        """Add App Engine specific headers to responses"""
        # Add trace header for distributed tracing
        trace_header = request.headers.get('X-Cloud-Trace-Context')
        if trace_header:
            response.headers['X-Cloud-Trace-Context'] = trace_header
        
        # Add instance information for debugging
        if current_app.config.get('DEBUG'):
            response.headers['X-GAE-Instance'] = os.environ.get('GAE_INSTANCE', 'local')
            response.headers['X-GAE-Version'] = os.environ.get('GAE_VERSION', 'local')
        
        return response


def is_app_engine() -> bool:
    """Check if running on App Engine"""
    return os.environ.get('GAE_ENV', '').startswith('standard')


def get_project_id() -> str:
    """Get the Google Cloud project ID"""
    return os.environ.get('GOOGLE_CLOUD_PROJECT', '')


def get_service_name() -> str:
    """Get the App Engine service name"""
    return os.environ.get('GAE_SERVICE', 'default')


def get_version_id() -> str:
    """Get the App Engine version ID"""
    return os.environ.get('GAE_VERSION', 'unknown')


def get_instance_id() -> str:
    """Get the App Engine instance ID"""
    return os.environ.get('GAE_INSTANCE', 'unknown')


def get_trace_id() -> str:
    """Extract trace ID from Cloud Trace header"""
    trace_header = request.headers.get('X-Cloud-Trace-Context', '')
    if trace_header:
        # Format: TRACE_ID/SPAN_ID;o=TRACE_TRUE
        return trace_header.split('/')[0]
    return ''