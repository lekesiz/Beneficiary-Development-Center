"""Custom exception classes for the application."""


class BaseError(Exception):
    """Base error class for all custom exceptions."""

    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(BaseError):
    """Raised when validation fails."""

    def __init__(self, message, code="VALIDATION_ERROR"):
        super().__init__(message, code)


class NotFoundError(BaseError):
    """Raised when a resource is not found."""

    def __init__(self, message, code="NOT_FOUND"):
        super().__init__(message, code)


class PermissionError(BaseError):
    """Raised when user doesn't have permission."""

    def __init__(self, message, code="PERMISSION_DENIED"):
        super().__init__(message, code)


class BadRequestError(BaseError):
    """Raised when request is invalid."""

    def __init__(self, message, code="BAD_REQUEST"):
        super().__init__(message, code)


class ForbiddenError(BaseError):
    """Raised when user doesn't have permission."""

    def __init__(self, message, code="FORBIDDEN"):
        super().__init__(message, code)


class AuthenticationError(BaseError):
    """Raised when authentication fails."""

    def __init__(self, message, code="AUTHENTICATION_ERROR"):
        super().__init__(message, code)


class UnauthorizedError(BaseError):
    """Raised when user is not authorized."""

    def __init__(self, message, code="UNAUTHORIZED"):
        super().__init__(message, code)


class TokenError(BaseError):
    """Raised when token is invalid or expired."""

    def __init__(self, message, code="TOKEN_ERROR"):
        super().__init__(message, code)


class DuplicateError(BaseError):
    """Raised when trying to create a duplicate resource."""

    def __init__(self, message, code="DUPLICATE_ERROR"):
        super().__init__(message, code)


class ConfigurationError(BaseError):
    """Raised when configuration is invalid."""

    def __init__(self, message, code="CONFIGURATION_ERROR"):
        super().__init__(message, code)


class ExternalServiceError(BaseError):
    """Raised when external service fails."""

    def __init__(self, message, code="EXTERNAL_SERVICE_ERROR"):
        super().__init__(message, code)


class RateLimitError(BaseError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message, code="RATE_LIMIT_ERROR"):
        super().__init__(message, code)


class ConflictError(BaseError):
    """Raised when there's a resource conflict."""

    def __init__(self, message, code="CONFLICT"):
        super().__init__(message, code)


class ServiceUnavailableError(BaseError):
    """Raised when service is temporarily unavailable."""

    def __init__(self, message, code="SERVICE_UNAVAILABLE"):
        super().__init__(message, code)


class PayloadTooLargeError(BaseError):
    """Raised when request payload is too large."""

    def __init__(self, message, code="PAYLOAD_TOO_LARGE"):
        super().__init__(message, code)


class MethodNotAllowedError(BaseError):
    """Raised when HTTP method is not allowed."""

    def __init__(self, message, code="METHOD_NOT_ALLOWED"):
        super().__init__(message, code)


class TimeoutError(BaseError):
    """Raised when operation times out."""

    def __init__(self, message, code="TIMEOUT"):
        super().__init__(message, code)


class BusinessLogicError(BaseError):
    """Raised when business logic validation fails."""

    def __init__(self, message, code="BUSINESS_LOGIC_ERROR"):
        super().__init__(message, code)


class InvalidStateError(BaseError):
    """Raised when resource is in invalid state for operation."""

    def __init__(self, message, code="INVALID_STATE"):
        super().__init__(message, code)


class ResourceLockedError(BaseError):
    """Raised when resource is locked and cannot be modified."""

    def __init__(self, message, code="RESOURCE_LOCKED"):
        super().__init__(message, code)


class QuotaExceededError(BaseError):
    """Raised when user exceeds their quota."""

    def __init__(self, message, code="QUOTA_EXCEEDED"):
        super().__init__(message, code)


class MaintenanceModeError(BaseError):
    """Raised when system is in maintenance mode."""

    def __init__(self, message, code="MAINTENANCE_MODE"):
        super().__init__(message, code)


# Alias for backward compatibility
APIException = BaseError
