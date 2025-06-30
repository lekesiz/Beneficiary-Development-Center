"""
Centralized logging configuration for BDC platform
"""

import os
import sys
import logging
import logging.config
from datetime import datetime
from pathlib import Path


def setup_logging(app=None):
    """Setup structured logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Determine log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'default',
                'stream': sys.stdout
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'logs/errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'access_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'default',
                'filename': 'logs/access.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'security_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'WARNING',
                'formatter': 'detailed',
                'filename': 'logs/security.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            'app': {
                'level': log_level,
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'app.api': {
                'level': log_level,
                'handlers': ['console', 'file', 'access_file'],
                'propagate': False
            },
            'app.security': {
                'level': 'WARNING',
                'handlers': ['console', 'security_file'],
                'propagate': False
            },
            'sqlalchemy.engine': {
                'level': 'WARNING',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'werkzeug': {
                'level': 'WARNING',
                'handlers': ['console', 'access_file'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console', 'file']
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Log startup
    logger = logging.getLogger('app')
    logger.info(
        "Logging initialized",
        extra={
            'log_level': log_level,
            'log_dir': str(log_dir.absolute()),
            'environment': os.getenv('FLASK_ENV', 'development')
        }
    )
    
    # Configure Flask app logging if provided
    if app:
        app.logger.handlers = logging.getLogger('app').handlers
        app.logger.setLevel(log_level)
        
        # Disable Flask's default logger
        logging.getLogger('flask.app').handlers = []
        
        # Log all unhandled exceptions
        def log_exception(exc_info):
            """Log unhandled exceptions"""
            app.logger.error(
                "Unhandled exception",
                exc_info=exc_info,
                extra={
                    'exception_type': exc_info[0].__name__,
                    'exception_value': str(exc_info[1]),
                    'traceback': True
                }
            )
        
        app.log_exception = log_exception


class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger('app.security')
    
    def log_login_attempt(self, email: str, success: bool, ip_address: str, 
                         tenant_id: int = None, reason: str = None):
        """Log login attempts"""
        self.logger.info(
            f"Login attempt - {'SUCCESS' if success else 'FAILED'}",
            extra={
                'event_type': 'login_attempt',
                'email': email,
                'success': success,
                'ip_address': ip_address,
                'tenant_id': tenant_id,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_permission_denied(self, user_id: int, resource: str, action: str, 
                            required_permission: str):
        """Log permission denied events"""
        self.logger.warning(
            "Permission denied",
            extra={
                'event_type': 'permission_denied',
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'required_permission': required_permission,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_suspicious_activity(self, user_id: int, activity_type: str, 
                               details: dict, ip_address: str):
        """Log suspicious activities"""
        self.logger.warning(
            f"Suspicious activity detected: {activity_type}",
            extra={
                'event_type': 'suspicious_activity',
                'user_id': user_id,
                'activity_type': activity_type,
                'details': details,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_data_access(self, user_id: int, resource_type: str, 
                       resource_id: int, action: str):
        """Log sensitive data access"""
        self.logger.info(
            "Sensitive data accessed",
            extra={
                'event_type': 'data_access',
                'user_id': user_id,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'action': action,
                'timestamp': datetime.utcnow().isoformat()
            }
        )


class PerformanceLogger:
    """Specialized logger for performance metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger('app.performance')
    
    def log_slow_query(self, query: str, duration: float, params: dict = None):
        """Log slow database queries"""
        self.logger.warning(
            f"Slow query detected ({duration:.2f}s)",
            extra={
                'event_type': 'slow_query',
                'query': query,
                'duration': duration,
                'params': params,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_slow_request(self, method: str, path: str, duration: float, 
                        status_code: int):
        """Log slow HTTP requests"""
        self.logger.warning(
            f"Slow request: {method} {path} ({duration:.2f}s)",
            extra={
                'event_type': 'slow_request',
                'method': method,
                'path': path,
                'duration': duration,
                'status_code': status_code,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_resource_usage(self, cpu_percent: float, memory_percent: float, 
                          disk_percent: float):
        """Log system resource usage"""
        self.logger.info(
            "System resource usage",
            extra={
                'event_type': 'resource_usage',
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'timestamp': datetime.utcnow().isoformat()
            }
        )


class BusinessEventLogger:
    """Logger for business events and analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger('app.business')
    
    def log_user_registration(self, user_id: int, email: str, role: str, 
                            tenant_id: int):
        """Log new user registration"""
        self.logger.info(
            "New user registered",
            extra={
                'event_type': 'user_registration',
                'user_id': user_id,
                'email': email,
                'role': role,
                'tenant_id': tenant_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_enrollment(self, user_id: int, program_id: int, course_id: int = None):
        """Log program/course enrollment"""
        self.logger.info(
            "User enrolled",
            extra={
                'event_type': 'enrollment',
                'user_id': user_id,
                'program_id': program_id,
                'course_id': course_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_evaluation_completed(self, user_id: int, evaluation_id: int, 
                                score: float, passed: bool):
        """Log evaluation completion"""
        self.logger.info(
            "Evaluation completed",
            extra={
                'event_type': 'evaluation_completed',
                'user_id': user_id,
                'evaluation_id': evaluation_id,
                'score': score,
                'passed': passed,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_milestone_completed(self, user_id: int, milestone_id: int, 
                               learning_path_id: int):
        """Log learning milestone completion"""
        self.logger.info(
            "Milestone completed",
            extra={
                'event_type': 'milestone_completed',
                'user_id': user_id,
                'milestone_id': milestone_id,
                'learning_path_id': learning_path_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        )


# Initialize specialized loggers
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()
business_logger = BusinessEventLogger()


# Export loggers
__all__ = [
    'setup_logging',
    'security_logger',
    'performance_logger',
    'business_logger',
    'SecurityLogger',
    'PerformanceLogger',
    'BusinessEventLogger'
]