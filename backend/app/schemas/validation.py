"""
Enhanced validation schemas with comprehensive error handling
"""

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError, pre_load, post_load
from datetime import datetime, date
from typing import Any, Dict
import re


class BaseSchema(Schema):
    """Base schema with common validation methods"""

    class Meta:
        ordered = True
        unknown = "exclude"  # Ignore unknown fields

    @pre_load
    def strip_strings(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Strip whitespace from string fields"""
        # Convert to a mutable dict if it's an ImmutableMultiDict
        if hasattr(data, "__setitem__"):
            try:
                # Try to modify in place first
                for key, value in data.items():
                    if isinstance(value, str):
                        data[key] = value.strip()
                return data
            except TypeError:
                # If modification fails (immutable), create a new dict
                data = dict(data)

        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()
        return data

    @pre_load
    def convert_empty_strings(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Convert empty strings to None for optional fields"""
        # Convert to a mutable dict if it's an ImmutableMultiDict
        if hasattr(data, "__setitem__"):
            try:
                # Try to modify in place first
                for key, value in data.items():
                    if value == "" and key in self.fields and self.fields[key].allow_none:
                        data[key] = None
                return data
            except TypeError:
                # If modification fails (immutable), create a new dict
                data = dict(data)

        for key, value in data.items():
            if value == "" and key in self.fields and self.fields[key].allow_none:
                data[key] = None
        return data


class PaginationSchema(BaseSchema):
    """Common pagination parameters"""

    page = fields.Integer(
        validate=validate.Range(min=1), missing=1, error_messages={"invalid": "Page must be a positive integer"}
    )
    per_page = fields.Integer(
        validate=validate.Range(min=1, max=100),
        missing=20,
        error_messages={"invalid": "Per page must be between 1 and 100"},
    )
    sort_by = fields.String(validate=validate.Length(max=50), missing="created_at")
    sort_order = fields.String(
        validate=validate.OneOf(["asc", "desc"]),
        missing="desc",
        error_messages={"invalid": "Sort order must be 'asc' or 'desc'"},
    )


class DateRangeSchema(BaseSchema):
    """Date range filtering"""

    start_date = fields.Date(format="%Y-%m-%d", error_messages={"invalid": "Invalid date format. Use YYYY-MM-DD"})
    end_date = fields.Date(format="%Y-%m-%d", error_messages={"invalid": "Invalid date format. Use YYYY-MM-DD"})

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        start = data.get("start_date")
        end = data.get("end_date")
        if start and end and start > end:
            raise ValidationError("Start date must be before or equal to end date")


class EmailSchema(BaseSchema):
    """Email validation"""

    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        error_messages={"required": "Email is required", "invalid": "Invalid email format"},
    )

    @validates("email")
    def validate_email_format(self, value):
        # Additional email validation
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, value):
            raise ValidationError("Invalid email format")


class PhoneSchema(BaseSchema):
    """Phone number validation"""

    phone = fields.String(
        validate=validate.Length(min=10, max=20),
        error_messages={"invalid": "Phone number must be between 10 and 20 characters"},
    )

    @validates("phone")
    def validate_phone_format(self, value):
        # Remove common separators
        cleaned = re.sub(r"[\s\-\(\)\+]", "", value)
        if not cleaned.isdigit():
            raise ValidationError("Phone number must contain only digits")


class URLSchema(BaseSchema):
    """URL validation"""

    url = fields.URL(validate=validate.Length(max=500), error_messages={"invalid": "Invalid URL format"})

    @validates("url")
    def validate_url_protocol(self, value):
        if value and not value.startswith(("http://", "https://")):
            raise ValidationError("URL must start with http:// or https://")


class MoneySchema(BaseSchema):
    """Money/currency validation"""

    amount = fields.Decimal(
        places=2,
        validate=validate.Range(min=0, max=999999999.99),
        error_messages={"invalid": "Amount must be a valid decimal with up to 2 decimal places"},
    )
    currency = fields.String(
        validate=[
            validate.Length(equal=3),
            validate.Regexp(r"^[A-Z]{3}$", error="Currency must be 3 uppercase letters"),
        ],
        missing="USD",
    )


class PercentageSchema(BaseSchema):
    """Percentage validation"""

    percentage = fields.Float(
        validate=validate.Range(min=0, max=100), error_messages={"invalid": "Percentage must be between 0 and 100"}
    )


class FileUploadSchema(BaseSchema):
    """File upload validation"""

    file_name = fields.String(required=True, validate=validate.Length(max=255))
    file_size = fields.Integer(
        validate=validate.Range(max=10485760), error_messages={"invalid": "File size must not exceed 10MB"}  # 10MB max
    )
    file_type = fields.String(
        validate=validate.OneOf(
            [
                "image/jpeg",
                "image/png",
                "image/gif",
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ]
        ),
        error_messages={"invalid": "Unsupported file type"},
    )


class ErrorResponseSchema(BaseSchema):
    """Standard error response schema"""

    error = fields.String(required=True)
    message = fields.String(required=True)
    details = fields.Dict(missing={})
    code = fields.String(missing=None)
    timestamp = fields.DateTime(missing=datetime.utcnow)


class SuccessResponseSchema(BaseSchema):
    """Standard success response schema"""

    success = fields.Boolean(default=True)
    message = fields.String(required=True)
    data = fields.Dict(missing={})
    timestamp = fields.DateTime(missing=datetime.utcnow)


class BatchOperationSchema(BaseSchema):
    """Batch operation request schema"""

    ids = fields.List(
        fields.Integer(validate=validate.Range(min=1)),
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            "required": "IDs list is required",
            "invalid": "IDs must be a list of positive integers",
            "validator_failed": "Batch operation limited to 100 items",
        },
    )
    operation = fields.String(
        required=True,
        validate=validate.OneOf(["delete", "archive", "activate", "deactivate"]),
        error_messages={"required": "Operation is required", "invalid": "Invalid operation type"},
    )
    confirm = fields.Boolean(missing=False, error_messages={"invalid": "Confirm must be a boolean value"})


class SearchSchema(BaseSchema):
    """Advanced search parameters"""

    query = fields.String(
        validate=validate.Length(min=2, max=100),
        error_messages={"invalid": "Search query must be between 2 and 100 characters"},
    )
    search_fields = fields.List(
        fields.String(),
        validate=validate.Length(max=10),
        error_messages={"invalid": "Cannot search more than 10 fields at once"},
    )
    exact_match = fields.Boolean(missing=False)
    case_sensitive = fields.Boolean(missing=False)


# Validation helper functions
def validate_future_date(value: date) -> None:
    """Validate that date is in the future"""
    if value <= date.today():
        raise ValidationError("Date must be in the future")


def validate_past_date(value: date) -> None:
    """Validate that date is in the past"""
    if value > date.today():
        raise ValidationError("Date must be in the past")


def validate_age(value: int, min_age: int = 0, max_age: int = 150) -> None:
    """Validate age is within reasonable bounds"""
    if not min_age <= value <= max_age:
        raise ValidationError(f"Age must be between {min_age} and {max_age}")


def validate_username(value: str) -> None:
    """Validate username format"""
    if not re.match(r"^[a-zA-Z0-9_-]{3,20}$", value):
        raise ValidationError(
            "Username must be 3-20 characters long and contain only letters, numbers, hyphens, and underscores"
        )


def validate_password_strength(value: str) -> None:
    """Validate password meets security requirements"""
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", value):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValidationError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", value):
        raise ValidationError("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError("Password must contain at least one special character")


def validate_no_sql_injection(value: str) -> None:
    """Basic SQL injection prevention"""
    # Check for actual SQL patterns, not just keywords as substrings
    sql_patterns = [
        r"\bSELECT\s+.*\s+FROM\b",
        r"\bINSERT\s+INTO\b",
        r"\bUPDATE\s+.*\s+SET\b",
        r"\bDELETE\s+FROM\b",
        r"\bDROP\s+(TABLE|DATABASE)\b",
        r"\bUNION\s+(SELECT|ALL)\b",
        r"\bEXEC(UTE)?\s*\(",
        r"<SCRIPT[\s>]",
        r";\s*(SELECT|INSERT|UPDATE|DELETE|DROP)",
        r"--\s*$",  # SQL comment at end
        r"\/\*.*\*\/",  # SQL block comment
        r"\bOR\s+1\s*=\s*1\b",  # Common injection pattern
        r"\bAND\s+1\s*=\s*1\b",  # Common injection pattern
    ]

    import re

    value_upper = value.upper()
    for pattern in sql_patterns:
        if re.search(pattern, value_upper, re.IGNORECASE):
            raise ValidationError("Invalid characters detected in input")


def validate_no_xss(value: str) -> None:
    """Basic XSS prevention"""
    dangerous_patterns = ["<script", "<iframe", "javascript:", "onerror=", "onclick="]
    value_lower = value.lower()
    for pattern in dangerous_patterns:
        if pattern in value_lower:
            raise ValidationError("Invalid HTML content detected")


def validate_percentage(value: float) -> None:
    """Validate percentage is between 0 and 100"""
    if not 0 <= value <= 100:
        raise ValidationError("Percentage must be between 0 and 100")
