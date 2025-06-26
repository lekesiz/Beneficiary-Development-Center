"""
Enhanced error handling system with comprehensive error responses
"""

from flask import jsonify, request, current_app
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DataError, OperationalError
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import logging

from app.core.exceptions import (
    NotFoundError, BadRequestError, ForbiddenError, 
    UnauthorizedError, ConflictError, ServiceUnavailableError
)

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standardized error response builder"""
    
    @staticmethod
    def create(
        error: str,
        message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """Create a standardized error response"""
        
        response = {
            "error": error,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.path if request else None,
            "method": request.method if request else None
        }
        
        if details:
            response["details"] = details
        
        if error_code:
            response["error_code"] = error_code
        
        if request_id or (request and hasattr(request, 'request_id')):
            response["request_id"] = request_id or request.request_id
        
        return response, status_code
    
    @staticmethod
    def json_response(
        error: str,
        message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Create a standardized error response as a Flask JSON response"""
        from flask import jsonify
        response, code = ErrorResponse.create(error, message, status_code, details, error_code, request_id)
        return jsonify(response), code


def handle_validation_error(e: ValidationError) -> Tuple[Dict[str, Any], int]:
    """Handle Marshmallow validation errors"""
    
    # Format validation errors
    formatted_errors = {}
    for field, errors in e.messages.items():
        if isinstance(errors, list):
            formatted_errors[field] = errors[0] if len(errors) == 1 else errors
        else:
            formatted_errors[field] = errors
    
    return ErrorResponse.create(
        error="ValidationError",
        message="Invalid input data",
        status_code=400,
        details={"validation_errors": formatted_errors},
        error_code="VALIDATION_FAILED"
    )


def handle_not_found_error(e: NotFoundError) -> Tuple[Dict[str, Any], int]:
    """Handle resource not found errors"""
    
    return ErrorResponse.create(
        error="NotFoundError",
        message=str(e) or "Resource not found",
        status_code=404,
        error_code="RESOURCE_NOT_FOUND"
    )


def handle_bad_request_error(e: BadRequestError) -> Tuple[Dict[str, Any], int]:
    """Handle bad request errors"""
    
    return ErrorResponse.create(
        error="BadRequestError",
        message=str(e) or "Bad request",
        status_code=400,
        error_code="BAD_REQUEST"
    )


def handle_forbidden_error(e: ForbiddenError) -> Tuple[Dict[str, Any], int]:
    """Handle forbidden access errors"""
    
    return ErrorResponse.create(
        error="ForbiddenError",
        message=str(e) or "Access forbidden",
        status_code=403,
        error_code="ACCESS_FORBIDDEN"
    )


def handle_unauthorized_error(e: UnauthorizedError) -> Tuple[Dict[str, Any], int]:
    """Handle unauthorized access errors"""
    
    return ErrorResponse.create(
        error="UnauthorizedError",
        message=str(e) or "Unauthorized access",
        status_code=401,
        error_code="UNAUTHORIZED"
    )


def handle_conflict_error(e: ConflictError) -> Tuple[Dict[str, Any], int]:
    """Handle resource conflict errors"""
    
    return ErrorResponse.create(
        error="ConflictError",
        message=str(e) or "Resource conflict",
        status_code=409,
        error_code="RESOURCE_CONFLICT"
    )


def handle_service_unavailable_error(e: ServiceUnavailableError) -> Tuple[Dict[str, Any], int]:
    """Handle service unavailable errors"""
    
    return ErrorResponse.create(
        error="ServiceUnavailableError",
        message=str(e) or "Service temporarily unavailable",
        status_code=503,
        error_code="SERVICE_UNAVAILABLE"
    )


def handle_jwt_expired_error(e: ExpiredSignatureError) -> Tuple[Dict[str, Any], int]:
    """Handle JWT token expiration"""
    
    return ErrorResponse.create(
        error="TokenExpiredError",
        message="Authentication token has expired",
        status_code=401,
        error_code="TOKEN_EXPIRED"
    )


def handle_jwt_invalid_error(e: InvalidTokenError) -> Tuple[Dict[str, Any], int]:
    """Handle invalid JWT token"""
    
    return ErrorResponse.create(
        error="InvalidTokenError",
        message="Invalid authentication token",
        status_code=401,
        error_code="INVALID_TOKEN"
    )


def handle_integrity_error(e: IntegrityError) -> Tuple[Dict[str, Any], int]:
    """Handle database integrity errors"""
    
    # Extract useful information from the error
    error_info = str(e.orig) if hasattr(e, 'orig') else str(e)
    
    # Common integrity error patterns
    if 'duplicate key' in error_info.lower():
        message = "A resource with the same unique identifier already exists"
        error_code = "DUPLICATE_RESOURCE"
    elif 'foreign key constraint' in error_info.lower():
        message = "Cannot perform operation due to related resource constraints"
        error_code = "FOREIGN_KEY_VIOLATION"
    elif 'not null constraint' in error_info.lower():
        message = "Required field is missing"
        error_code = "REQUIRED_FIELD_MISSING"
    else:
        message = "Database constraint violation"
        error_code = "INTEGRITY_ERROR"
    
    # Log the full error for debugging
    logger.error(f"Database integrity error: {error_info}")
    
    return ErrorResponse.create(
        error="IntegrityError",
        message=message,
        status_code=409,
        error_code=error_code,
        details={"database_error": error_info} if current_app.debug else None
    )


def handle_data_error(e: DataError) -> Tuple[Dict[str, Any], int]:
    """Handle database data errors"""
    
    error_info = str(e.orig) if hasattr(e, 'orig') else str(e)
    
    return ErrorResponse.create(
        error="DataError",
        message="Invalid data format or type",
        status_code=400,
        error_code="INVALID_DATA",
        details={"database_error": error_info} if current_app.debug else None
    )


def handle_operational_error(e: OperationalError) -> Tuple[Dict[str, Any], int]:
    """Handle database operational errors"""
    
    logger.error(f"Database operational error: {str(e)}")
    
    return ErrorResponse.create(
        error="DatabaseError",
        message="Database connection or operation failed",
        status_code=503,
        error_code="DATABASE_ERROR"
    )


def handle_http_exception(e: HTTPException) -> Tuple[Dict[str, Any], int]:
    """Handle Werkzeug HTTP exceptions"""
    
    return ErrorResponse.create(
        error=e.__class__.__name__,
        message=e.description or str(e),
        status_code=e.code,
        error_code=e.name.upper().replace(' ', '_')
    )


def handle_generic_exception(e: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle any unhandled exceptions"""
    
    # Log the full traceback
    logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
    
    # In production, don't expose internal errors
    if current_app.debug:
        details = {
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "traceback": traceback.format_exc().split('\n')
        }
    else:
        details = None
    
    return ErrorResponse.create(
        error="InternalServerError",
        message="An unexpected error occurred",
        status_code=500,
        error_code="INTERNAL_ERROR",
        details=details
    )


def register_error_handlers(app):
    """Register all error handlers with the Flask app"""
    
    # Application exceptions
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(NotFoundError, handle_not_found_error)
    app.register_error_handler(BadRequestError, handle_bad_request_error)
    app.register_error_handler(ForbiddenError, handle_forbidden_error)
    app.register_error_handler(UnauthorizedError, handle_unauthorized_error)
    app.register_error_handler(ConflictError, handle_conflict_error)
    app.register_error_handler(ServiceUnavailableError, handle_service_unavailable_error)
    
    # JWT exceptions
    app.register_error_handler(ExpiredSignatureError, handle_jwt_expired_error)
    app.register_error_handler(InvalidTokenError, handle_jwt_invalid_error)
    
    # Database exceptions
    app.register_error_handler(IntegrityError, handle_integrity_error)
    app.register_error_handler(DataError, handle_data_error)
    app.register_error_handler(OperationalError, handle_operational_error)
    
    # HTTP exceptions
    app.register_error_handler(HTTPException, handle_http_exception)
    
    # Generic exception handler (catches everything else)
    app.register_error_handler(Exception, handle_generic_exception)
    
    # Special handlers for common HTTP status codes
    @app.errorhandler(404)
    def not_found(e):
        return ErrorResponse.create(
            error="NotFound",
            message="The requested resource was not found",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return ErrorResponse.create(
            error="MethodNotAllowed",
            message=f"Method {request.method} is not allowed for this endpoint",
            status_code=405,
            error_code="METHOD_NOT_ALLOWED",
            details={"allowed_methods": e.valid_methods} if hasattr(e, 'valid_methods') else None
        )
    
    @app.errorhandler(413)
    def request_entity_too_large(e):
        return ErrorResponse.create(
            error="RequestEntityTooLarge",
            message="The request payload is too large",
            status_code=413,
            error_code="PAYLOAD_TOO_LARGE"
        )
    
    @app.errorhandler(429)
    def too_many_requests(e):
        return ErrorResponse.create(
            error="TooManyRequests",
            message="Rate limit exceeded. Please try again later",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return ErrorResponse.create(
            error="InternalServerError",
            message="An internal server error occurred",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )


# Error code constants for consistency
class ErrorCodes:
    """Centralized error codes"""
    
    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    ACCESS_FORBIDDEN = "ACCESS_FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation
    VALIDATION_FAILED = "VALIDATION_FAILED"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Resources
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    RESOURCE_LOCKED = "RESOURCE_LOCKED"
    
    # Business Logic
    INVALID_OPERATION = "INVALID_OPERATION"
    PRECONDITION_FAILED = "PRECONDITION_FAILED"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    
    # System
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"