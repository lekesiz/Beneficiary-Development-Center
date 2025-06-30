"""Performance monitoring and health checks for Flask application."""

from flask import Flask, jsonify, request, g
from datetime import datetime, timedelta
import psutil
import time
import logging
import json
import os
from functools import wraps
from typing import Dict, Any, Optional, Callable

# Try to import monitoring libraries
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


def init_monitoring(app: Flask):
    """Initialize monitoring endpoints and middleware."""
    
    # Initialize monitoring state
    app._start_time = time.time()
    app._request_count = 0
    app._error_count = 0
    app._active_connections = 0
    
    @app.route('/health')
    def health_check():
        """Basic health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config.get('VERSION', '1.0.0'),
            'environment': app.config.get('FLASK_ENV', 'development')
        }), 200
    
    @app.route('/health/detailed')
    def detailed_health_check():
        """Detailed health check with system metrics."""
        status = 'healthy'
        services = {}
        
        # Database check
        try:
            from app.extensions import db
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            services['database'] = 'healthy'
        except Exception as e:
            services['database'] = f'unhealthy: {str(e)}'
            status = 'degraded'
        
        # Redis check
        try:
            from app.extensions import cache
            cache.set('health_check', 'ok', timeout=10)
            result = cache.get('health_check')
            if result == 'ok':
                services['redis'] = 'healthy'
            else:
                services['redis'] = 'unhealthy: cache test failed'
                status = 'degraded'
        except Exception as e:
            services['redis'] = f'unhealthy: {str(e)}'
            status = 'degraded'
        
        # System metrics
        try:
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else 'N/A'
            }
        except Exception as e:
            system_metrics = {'error': f'Failed to get system metrics: {str(e)}'}
        
        # Application metrics
        uptime_seconds = time.time() - app._start_time
        app_metrics = {
            'uptime_seconds': uptime_seconds,
            'uptime_human': str(timedelta(seconds=int(uptime_seconds))),
            'total_requests': getattr(app, '_request_count', 0),
            'error_count': getattr(app, '_error_count', 0),
            'active_connections': getattr(app, '_active_connections', 0),
            'requests_per_minute': (getattr(app, '_request_count', 0) / max(uptime_seconds / 60, 1))
        }
        
        return jsonify({
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'services': services,
            'system': system_metrics,
            'application': app_metrics
        }), 200 if status == 'healthy' else 503
    
    if PROMETHEUS_AVAILABLE:
        # Initialize Prometheus metrics
        http_requests_total = Counter(
            'bdc_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        http_request_duration = Histogram(
            'bdc_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        
        active_users_gauge = Gauge(
            'bdc_active_users',
            'Currently active users'
        )
        
        database_connections_gauge = Gauge(
            'bdc_database_connections',
            'Active database connections'
        )
    
    @app.route('/metrics')
    def metrics_endpoint():
        """Prometheus-style metrics endpoint."""
        if PROMETHEUS_AVAILABLE:
            # Update system metrics
            try:
                from app.extensions import db
                if hasattr(db.engine.pool, 'size'):
                    database_connections_gauge.set(db.engine.pool.size())
            except:
                pass
                
            return generate_latest()
        else:
            # Fallback to simple metrics
            uptime_seconds = time.time() - app._start_time
            
            metrics = []
            metrics.append(f'# HELP bdc_uptime_seconds Total uptime in seconds')
            metrics.append(f'# TYPE bdc_uptime_seconds counter')
            metrics.append(f'bdc_uptime_seconds {uptime_seconds}')
            
            metrics.append(f'# HELP bdc_requests_total Total number of requests')
            metrics.append(f'# TYPE bdc_requests_total counter')
            metrics.append(f'bdc_requests_total {getattr(app, "_request_count", 0)}')
            
            metrics.append(f'# HELP bdc_errors_total Total number of errors')
            metrics.append(f'# TYPE bdc_errors_total counter')
            metrics.append(f'bdc_errors_total {getattr(app, "_error_count", 0)}')
            
            metrics.append(f'# HELP bdc_active_connections Current active connections')
            metrics.append(f'# TYPE bdc_active_connections gauge')
            metrics.append(f'bdc_active_connections {getattr(app, "_active_connections", 0)}')
            
            try:
                cpu_percent = psutil.cpu_percent()
                metrics.append(f'# HELP bdc_cpu_percent CPU usage percentage')
                metrics.append(f'# TYPE bdc_cpu_percent gauge')
                metrics.append(f'bdc_cpu_percent {cpu_percent}')
                
                memory_percent = psutil.virtual_memory().percent
                metrics.append(f'# HELP bdc_memory_percent Memory usage percentage')
                metrics.append(f'# TYPE bdc_memory_percent gauge')
                metrics.append(f'bdc_memory_percent {memory_percent}')
            except Exception as e:
                logger.warning(f'Failed to get system metrics: {e}')
            
            return '\n'.join(metrics), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    @app.route('/health/readiness')
    def readiness_check():
        """Kubernetes readiness probe endpoint."""
        try:
            # Check if application is ready to serve requests
            from app.extensions import db
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            
            return jsonify({
                'status': 'ready',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'not_ready',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 503
    
    @app.route('/health/liveness')
    def liveness_check():
        """Kubernetes liveness probe endpoint."""
        # Simple check to ensure the application is alive
        return jsonify({
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat(),
            'pid': psutil.Process().pid
        }), 200
    
    # Request counter middleware
    @app.before_request
    def count_requests():
        """Count incoming requests."""
        app._request_count += 1
        app._active_connections += 1
        g.request_start_time = time.time()
        
        # Generate request ID if not present
        import uuid
        if 'X-Request-ID' not in request.headers:
            g.request_id = str(uuid.uuid4())
        else:
            g.request_id = request.headers.get('X-Request-ID')
    
    @app.after_request
    def after_request_monitoring(response):
        """Monitor request completion."""
        app._active_connections -= 1
        
        # Calculate request duration
        request_duration = 0
        if hasattr(g, 'request_start_time'):
            request_duration = time.time() - g.request_start_time
            
            # Log slow requests
            if request_duration > 1.0:  # Log requests taking more than 1 second
                logger.warning(
                    'Slow request detected',
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'duration': request_duration,
                        'status_code': response.status_code,
                        'request_id': getattr(g, 'request_id', 'unknown')
                    }
                )
        
        # Track metrics with Prometheus if available
        if PROMETHEUS_AVAILABLE and request.endpoint:
            http_requests_total.labels(
                method=request.method,
                endpoint=request.endpoint,
                status=str(response.status_code)
            ).inc()
            
            if request_duration > 0:
                http_request_duration.labels(
                    method=request.method,
                    endpoint=request.endpoint
                ).observe(request_duration)
        
        # Count errors
        if response.status_code >= 400:
            app._error_count += 1
        
        # Add performance headers
        if hasattr(g, 'request_start_time'):
            response.headers['X-Response-Time'] = f'{(time.time() - g.request_start_time) * 1000:.2f}ms'
        
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        
        return response
    
    # Error handling middleware
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors with monitoring."""
        app._error_count += 1
        logger.error(f'Internal server error: {error}')
        return jsonify({
            'error': 'Internal server error',
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': request.headers.get('X-Request-ID', 'unknown')
        }), 500


def monitor_performance(threshold_ms=1000):
    """Decorator to monitor function performance."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                if duration_ms > threshold_ms:
                    logger.warning(
                        f'Performance warning: {f.__name__} took {duration_ms:.2f}ms '
                        f'(threshold: {threshold_ms}ms)'
                    )
        return wrapper
    return decorator


class PerformanceMonitor:
    """Context manager for monitoring performance of code blocks."""
    
    def __init__(self, name: str, threshold_ms: float = 1000):
        self.name = name
        self.threshold_ms = threshold_ms
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            if duration_ms > self.threshold_ms:
                logger.warning(
                    f'Performance warning: {self.name} took {duration_ms:.2f}ms '
                    f'(threshold: {self.threshold_ms}ms)'
                )


def log_database_queries():
    """Enable database query logging for performance monitoring."""
    import logging
    db_logger = logging.getLogger('sqlalchemy.engine')
    db_logger.setLevel(logging.INFO)
    
    # Create handler for database logs
    db_handler = logging.StreamHandler()
    db_formatter = logging.Formatter(
        '%(asctime)s [DB] %(message)s'
    )
    db_handler.setFormatter(db_formatter)
    db_logger.addHandler(db_handler)


class StructuredLogger:
    """Structured logging with JSON output for better observability"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove default handlers
        self.logger.handlers = []
        
        # Add JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self.JSONFormatter())
        self.logger.addHandler(handler)
    
    class JSONFormatter(logging.Formatter):
        """Custom JSON formatter for structured logs"""
        
        def format(self, record):
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add request context if available
            if hasattr(g, 'request_id'):
                log_data['request_id'] = g.request_id
            
            # Add exception info if present
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            # Add extra fields
            if hasattr(record, 'extra'):
                log_data.update(record.extra)
            
            return json.dumps(log_data)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)


def track_business_event(event_type: str, **kwargs):
    """Track business events for analytics"""
    structured_logger = StructuredLogger('business_events')
    structured_logger.info(
        f'Business event: {event_type}',
        event_type=event_type,
        **kwargs
    )