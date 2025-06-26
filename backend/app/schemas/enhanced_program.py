"""
Enhanced Program schemas with comprehensive validation
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError, post_dump
from datetime import datetime, date
from typing import Optional

from .validation import (
    BaseSchema, PaginationSchema, DateRangeSchema,
    validate_future_date, validate_no_sql_injection, validate_no_xss
)


class ProgramBaseSchema(BaseSchema):
    """Base schema for program data"""
    
    title = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=200),
            validate_no_sql_injection,
            validate_no_xss
        ],
        error_messages={
            "required": "Program title is required",
            "invalid": "Program title must be between 3 and 200 characters"
        }
    )
    
    code = fields.String(
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(r'^[A-Z0-9\-]+$', error="Code must contain only uppercase letters, numbers, and hyphens")
        ],
        error_messages={
            "invalid": "Program code must be 3-50 characters long"
        }
    )
    
    description = fields.String(
        validate=[
            validate.Length(max=5000),
            validate_no_xss
        ],
        allow_none=True,
        error_messages={
            "invalid": "Description must not exceed 5000 characters"
        }
    )
    
    objectives = fields.List(
        fields.String(validate=[validate.Length(max=500), validate_no_xss]),
        validate=validate.Length(max=20),
        missing=[],
        error_messages={
            "invalid": "Maximum 20 objectives allowed, each up to 500 characters"
        }
    )
    
    program_type = fields.String(
        validate=validate.OneOf([
            'education', 'training', 'workshop', 'bootcamp', 
            'certification', 'mentorship', 'internship'
        ]),
        error_messages={
            "invalid": "Invalid program type"
        }
    )
    
    status = fields.String(
        validate=validate.OneOf(['draft', 'published', 'active', 'completed', 'archived']),
        missing='draft',
        error_messages={
            "invalid": "Invalid program status"
        }
    )
    
    location = fields.String(
        validate=[validate.Length(max=200), validate_no_xss],
        allow_none=True
    )
    
    is_online = fields.Boolean(missing=False)
    is_hybrid = fields.Boolean(missing=False)
    
    online_link = fields.URL(
        validate=validate.Length(max=500),
        allow_none=True,
        error_messages={
            "invalid": "Invalid URL format for online link"
        }
    )
    
    min_participants = fields.Integer(
        validate=validate.Range(min=1, max=1000),
        missing=1,
        error_messages={
            "invalid": "Minimum participants must be between 1 and 1000"
        }
    )
    
    max_participants = fields.Integer(
        validate=validate.Range(min=1, max=10000),
        missing=50,
        error_messages={
            "invalid": "Maximum participants must be between 1 and 10000"
        }
    )
    
    price = fields.Decimal(
        places=2,
        validate=validate.Range(min=0, max=999999.99),
        missing=0,
        error_messages={
            "invalid": "Price must be a valid amount up to 999,999.99"
        }
    )
    
    currency = fields.String(
        validate=[
            validate.Length(equal=3),
            validate.Regexp(r'^[A-Z]{3}$')
        ],
        missing="USD",
        error_messages={
            "invalid": "Currency must be a 3-letter ISO code (e.g., USD, EUR)"
        }
    )
    
    tags = fields.List(
        fields.String(validate=validate.Length(max=50)),
        validate=validate.Length(max=20),
        missing=[],
        error_messages={
            "invalid": "Maximum 20 tags allowed, each up to 50 characters"
        }
    )
    
    cover_image_url = fields.URL(
        validate=validate.Length(max=500),
        allow_none=True
    )
    
    coordinator_id = fields.Integer(
        validate=validate.Range(min=1),
        allow_none=True
    )
    
    metadata = fields.Dict(
        missing={},
        error_messages={
            "invalid": "Metadata must be a valid JSON object"
        }
    )
    
    @validates_schema
    def validate_capacity(self, data, **kwargs):
        min_participants = data.get('min_participants', 1)
        max_participants = data.get('max_participants', 50)
        if min_participants > max_participants:
            raise ValidationError("Minimum participants cannot exceed maximum participants")
    
    @validates_schema
    def validate_online_settings(self, data, **kwargs):
        is_online = data.get('is_online', False)
        is_hybrid = data.get('is_hybrid', False)
        online_link = data.get('online_link')
        
        if (is_online or is_hybrid) and not online_link:
            raise ValidationError("Online link is required for online or hybrid programs")
        
        if not (is_online or is_hybrid) and online_link:
            raise ValidationError("Online link should only be provided for online or hybrid programs")


class ProgramCreateSchema(ProgramBaseSchema):
    """Schema for creating a program"""
    
    start_date = fields.Date(
        required=True,
        format="%Y-%m-%d",
        error_messages={
            "required": "Start date is required",
            "invalid": "Invalid date format. Use YYYY-MM-DD"
        }
    )
    
    end_date = fields.Date(
        required=True,
        format="%Y-%m-%d",
        error_messages={
            "required": "End date is required",
            "invalid": "Invalid date format. Use YYYY-MM-DD"
        }
    )
    
    enrollment_start = fields.Date(
        format="%Y-%m-%d",
        allow_none=True,
        error_messages={
            "invalid": "Invalid date format. Use YYYY-MM-DD"
        }
    )
    
    enrollment_end = fields.Date(
        format="%Y-%m-%d",
        allow_none=True,
        error_messages={
            "invalid": "Invalid date format. Use YYYY-MM-DD"
        }
    )
    
    requirements = fields.Dict(
        missing={
            "age_min": None,
            "age_max": None,
            "education_level": None,
            "skills": [],
            "other": []
        }
    )
    
    resources = fields.List(
        fields.Dict(keys=fields.String(), values=fields.Raw()),
        validate=validate.Length(max=50),
        missing=[]
    )
    
    @validates_schema
    def validate_dates(self, data, **kwargs):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        enrollment_start = data.get('enrollment_start')
        enrollment_end = data.get('enrollment_end')
        
        # Validate date sequence
        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError("End date must be after start date")
            
            # Validate program duration
            duration = (end_date - start_date).days
            if duration > 365 * 2:  # 2 years max
                raise ValidationError("Program duration cannot exceed 2 years")
        
        # Validate enrollment dates
        if enrollment_start and enrollment_end:
            if enrollment_start >= enrollment_end:
                raise ValidationError("Enrollment end date must be after enrollment start date")
        
        # Enrollment must end before program starts
        if enrollment_end and start_date:
            if enrollment_end > start_date:
                raise ValidationError("Enrollment must end before or on program start date")
        
        # If no enrollment dates provided, set defaults
        if not enrollment_start and start_date:
            data['enrollment_start'] = date.today()
        
        if not enrollment_end and start_date:
            data['enrollment_end'] = start_date


class ProgramUpdateSchema(ProgramBaseSchema):
    """Schema for updating a program"""
    
    # All fields are optional for updates
    title = fields.String(
        validate=[
            validate.Length(min=3, max=200),
            validate_no_sql_injection,
            validate_no_xss
        ],
        missing=fields.missing_
    )
    
    start_date = fields.Date(
        format="%Y-%m-%d",
        missing=fields.missing_
    )
    
    end_date = fields.Date(
        format="%Y-%m-%d",
        missing=fields.missing_
    )
    
    enrollment_start = fields.Date(
        format="%Y-%m-%d",
        allow_none=True,
        missing=fields.missing_
    )
    
    enrollment_end = fields.Date(
        format="%Y-%m-%d",
        allow_none=True,
        missing=fields.missing_
    )
    
    @validates_schema
    def validate_update_dates(self, data, **kwargs):
        # Only validate if dates are provided in update
        if 'start_date' in data and 'end_date' in data:
            self.validate_dates(data, **kwargs)


class ProgramQuerySchema(PaginationSchema):
    """Schema for program search/filter parameters"""
    
    status = fields.String(
        validate=validate.OneOf(['draft', 'published', 'active', 'completed', 'archived']),
        missing=fields.missing_
    )
    
    program_type = fields.String(
        validate=validate.OneOf([
            'education', 'training', 'workshop', 'bootcamp', 
            'certification', 'mentorship', 'internship'
        ]),
        missing=fields.missing_
    )
    
    search = fields.String(
        validate=[validate.Length(min=2, max=100), validate_no_sql_injection],
        missing=fields.missing_
    )
    
    upcoming_only = fields.Boolean(missing=False)
    active_only = fields.Boolean(missing=False)
    has_seats = fields.Boolean(missing=False)
    
    min_price = fields.Decimal(
        places=2,
        validate=validate.Range(min=0),
        missing=fields.missing_
    )
    
    max_price = fields.Decimal(
        places=2,
        validate=validate.Range(min=0),
        missing=fields.missing_
    )
    
    coordinator_id = fields.Integer(
        validate=validate.Range(min=1),
        missing=fields.missing_
    )
    
    tags = fields.List(
        fields.String(),
        missing=fields.missing_
    )
    
    start_date_from = fields.Date(
        format="%Y-%m-%d",
        missing=fields.missing_
    )
    
    start_date_to = fields.Date(
        format="%Y-%m-%d",
        missing=fields.missing_
    )
    
    @validates_schema
    def validate_price_range(self, data, **kwargs):
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationError("Minimum price cannot exceed maximum price")
    
    @validates_schema
    def validate_date_range(self, data, **kwargs):
        start_from = data.get('start_date_from')
        start_to = data.get('start_date_to')
        if start_from and start_to and start_from > start_to:
            raise ValidationError("Start date from must be before start date to")


class ProgramResponseSchema(BaseSchema):
    """Schema for program response serialization"""
    
    id = fields.Integer()
    uuid = fields.UUID()
    code = fields.String()
    title = fields.String()
    description = fields.String()
    objectives = fields.List(fields.String())
    program_type = fields.String()
    status = fields.String()
    
    start_date = fields.Date(format="%Y-%m-%d")
    end_date = fields.Date(format="%Y-%m-%d")
    enrollment_start = fields.Date(format="%Y-%m-%d")
    enrollment_end = fields.Date(format="%Y-%m-%d")
    
    location = fields.String()
    is_online = fields.Boolean()
    is_hybrid = fields.Boolean()
    online_link = fields.URL()
    
    min_participants = fields.Integer()
    max_participants = fields.Integer()
    current_participants = fields.Integer()
    available_seats = fields.Integer()
    
    price = fields.Decimal(places=2, as_string=True)
    currency = fields.String()
    
    coordinator_id = fields.Integer()
    coordinator_name = fields.String()
    
    tags = fields.List(fields.String())
    metadata = fields.Dict()
    cover_image_url = fields.URL()
    
    # Computed fields
    is_enrollment_open = fields.Boolean()
    is_active = fields.Boolean()
    is_upcoming = fields.Boolean()
    is_past = fields.Boolean()
    duration_days = fields.Integer()
    progress_percentage = fields.Float()
    
    # Statistics
    total_courses = fields.Integer()
    total_enrollments = fields.Integer()
    completion_rate = fields.Float()
    average_rating = fields.Float()
    
    # Timestamps
    created_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    updated_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    created_by = fields.Integer()
    updated_by = fields.Integer()
    
    @post_dump
    def format_response(self, data, **kwargs):
        """Format response data"""
        # Convert None to empty string for optional string fields
        string_fields = ['description', 'location', 'online_link', 'coordinator_name']
        for field in string_fields:
            if field in data and data[field] is None:
                data[field] = ""
        
        # Ensure lists are not None
        list_fields = ['objectives', 'tags']
        for field in list_fields:
            if field in data and data[field] is None:
                data[field] = []
        
        return data


class ProgramBatchOperationSchema(BaseSchema):
    """Schema for batch operations on programs"""
    
    program_ids = fields.List(
        fields.Integer(validate=validate.Range(min=1)),
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            "required": "Program IDs are required",
            "invalid": "Must provide between 1 and 100 valid program IDs"
        }
    )
    
    operation = fields.String(
        required=True,
        validate=validate.OneOf(['archive', 'delete', 'publish', 'activate']),
        error_messages={
            "required": "Operation is required",
            "invalid": "Invalid operation. Choose from: archive, delete, publish, activate"
        }
    )
    
    confirm = fields.Boolean(
        required=True,
        error_messages={
            "required": "Confirmation is required for batch operations"
        }
    )
    
    reason = fields.String(
        validate=[validate.Length(max=500), validate_no_xss],
        missing=None
    )


class ProgramStatisticsResponseSchema(BaseSchema):
    """Schema for program statistics response"""
    
    total_programs = fields.Integer()
    status_breakdown = fields.Dict(keys=fields.String(), values=fields.Integer())
    type_breakdown = fields.Dict(keys=fields.String(), values=fields.Integer())
    
    upcoming_programs = fields.Integer()
    active_programs = fields.Integer()
    completed_programs = fields.Integer()
    
    total_participants = fields.Integer()
    total_enrollments = fields.Integer()
    active_enrollments = fields.Integer()
    
    total_courses = fields.Integer()
    total_sessions = fields.Integer()
    
    average_completion_rate = fields.Float()
    average_satisfaction_rating = fields.Float()
    
    revenue_total = fields.Decimal(places=2, as_string=True)
    revenue_by_program_type = fields.Dict(keys=fields.String(), values=fields.Decimal(places=2, as_string=True))
    
    popular_tags = fields.List(fields.Dict())
    trending_programs = fields.List(fields.Dict())
    
    date_range = fields.Dict()
    generated_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")