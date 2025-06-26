"""Structured JSON logging configuration."""

import logging
import sys
from datetime import datetime
from flask import request, g, has_request_context
from pythonjsonlogger import jsonlogger
from flask_jwt_extended import get_jwt_identity, get_jwt


class RequestContextFilter(logging.Filter):
    """Add request context to log records"""

    def filter(self, record):
        if has_request_context():
            # Add request information
            record.method = request.method
            record.url = request.url
            record.path = request.path
            record.remote_addr = request.remote_addr
            record.user_agent = request.headers.get("User-Agent", "")

            # Add request ID if available
            record.request_id = g.get("request_id", "")

            # Add user context if available
            try:
                user_id = get_jwt_identity()
                if user_id:
                    record.user_id = user_id

                    # Add tenant info from JWT claims
                    claims = get_jwt()
                    if claims:
                        record.tenant_id = claims.get("tenant_id", "")
                        record.user_role = claims.get("role", "")
            except Exception:
                # JWT not available or invalid
                record.user_id = ""
                record.tenant_id = ""
                record.user_role = ""
        else:
            # No request context
            record.method = ""
            record.url = ""
            record.path = ""
            record.remote_addr = ""
            record.user_agent = ""
            record.request_id = ""
            record.user_id = ""
            record.tenant_id = ""
            record.user_role = ""

        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Add service information
        log_record["service"] = "bdc-backend"
        log_record["version"] = "1.0.0"

        # Ensure level is included
        if not log_record.get("level"):
            log_record["level"] = record.levelname

        # Add source location
        log_record["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
            "module": record.module,
        }

        # Handle exception information
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
            }


def setup_logging(app):
    """Setup structured JSON logging"""

    # Remove default handlers
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)

    # Create JSON formatter
    json_formatter = CustomJsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        static_fields={"service": "bdc-backend", "environment": app.config.get("ENVIRONMENT", "development")},
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)

    # Add request context filter
    request_filter = RequestContextFilter()
    console_handler.addFilter(request_filter)

    # Set logging level based on environment
    if app.config.get("DEBUG"):
        logging_level = logging.DEBUG
    elif app.config.get("ENVIRONMENT") == "production":
        logging_level = logging.WARNING
    else:
        logging_level = logging.INFO

    console_handler.setLevel(logging_level)

    # Add handler to app logger
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging_level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging_level)

    # Configure specific loggers
    loggers = ["werkzeug", "sqlalchemy.engine", "flask_socketio", "socketio", "engineio"]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(console_handler)
        logger.setLevel(logging.WARNING)  # Reduce noise from these loggers
        logger.propagate = False

    app.logger.info(
        "Structured JSON logging configured",
        extra={"level": logging_level, "environment": app.config.get("ENVIRONMENT", "development")},
    )

    return app.logger


# Create logger instance
logger = logging.getLogger(__name__)


# Helper functions for structured logging
def log_user_action(action, user_id=None, **kwargs):
    """Log user action with structured data"""
    extra_data = {"action": action, "user_id": user_id or get_jwt_identity(), **kwargs}
    logger.info(f"User action: {action}", extra=extra_data)


def log_api_request(endpoint, method, duration_ms=None, status_code=None, **kwargs):
    """Log API request with performance metrics"""
    extra_data = {
        "endpoint": endpoint,
        "method": method,
        "duration_ms": duration_ms,
        "status_code": status_code,
        **kwargs,
    }
    logger.info(f"API request: {method} {endpoint}", extra=extra_data)


def log_database_operation(operation, table, duration_ms=None, **kwargs):
    """Log database operation with performance metrics"""
    extra_data = {"operation": operation, "table": table, "duration_ms": duration_ms, **kwargs}
    logger.info(f"DB operation: {operation} on {table}", extra=extra_data)


def log_security_event(event_type, severity="info", **kwargs):
    """Log security-related events"""
    extra_data = {"event_type": event_type, "severity": severity, "category": "security", **kwargs}

    if severity == "critical":
        logger.critical(f"Security event: {event_type}", extra=extra_data)
    elif severity == "warning":
        logger.warning(f"Security event: {event_type}", extra=extra_data)
    else:
        logger.info(f"Security event: {event_type}", extra=extra_data)
