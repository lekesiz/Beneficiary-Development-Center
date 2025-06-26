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


# Alias for backward compatibility
APIException = BaseError
