"""
Enhanced Course schemas with comprehensive validation
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError, post_dump
from datetime import datetime, date, time
from typing import Optional

from .validation import (
    BaseSchema, PaginationSchema,
    validate_no_sql_injection, validate_no_xss
)


class CourseBaseSchema(BaseSchema):
    """Base schema for course data"""
    
    title = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=200),
            validate_no_sql_injection,
            validate_no_xss
        ],
        error_messages={
            "required": "Course title is required",
            "invalid": "Course title must be between 3 and 200 characters"
        }
    )
    
    subtitle = fields.String(
        validate=[
            validate.Length(max=300),
            validate_no_xss
        ],
        allow_none=True
    )
    
    code = fields.String(
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(r'^[A-Z0-9\-]+$', error="Code must contain only uppercase letters, numbers, and hyphens")
        ]
    )
    
    description = fields.String(
        validate=[
            validate.Length(max=5000),
            validate_no_xss
        ],
        allow_none=True
    )
    
    objectives = fields.List(
        fields.String(validate=[validate.Length(max=500), validate_no_xss]),
        validate=validate.Length(max=20),
        missing=[]
    )
    
    outline = fields.List(
        fields.Dict(keys=fields.String(), values=fields.Raw()),
        validate=validate.Length(max=50),
        missing=[]
    )
    
    prerequisites = fields.List(
        fields.String(validate=[validate.Length(max=200), validate_no_xss]),
        validate=validate.Length(max=10),
        missing=[]
    )
    
    materials = fields.List(
        fields.String(validate=[validate.Length(max=200), validate_no_xss]),
        validate=validate.Length(max=20),
        missing=[]
    )
    
    format = fields.String(
        validate=validate.OneOf([
            'lecture', 'workshop', 'practical', 'online', 
            'self_paced', 'hybrid', 'seminar', 'lab'
        ]),
        missing='lecture',
        error_messages={
            "invalid": "Invalid course format"
        }
    )
    
    difficulty_level = fields.String(
        validate=validate.OneOf(['beginner', 'intermediate', 'advanced', 'expert']),
        missing='beginner',
        error_messages={
            "invalid": "Invalid difficulty level"
        }
    )
    
    status = fields.String(
        validate=validate.OneOf(['draft', 'published', 'archived']),
        missing='draft'
    )
    
    duration_hours = fields.Float(
        validate=validate.Range(min=0.5, max=200),
        missing=1.0,
        error_messages={
            "invalid": "Duration must be between 0.5 and 200 hours"
        }
    )
    
    duration_weeks = fields.Integer(
        validate=validate.Range(min=1, max=52),
        missing=1,
        error_messages={
            "invalid": "Duration must be between 1 and 52 weeks"
        }
    )
    
    order_index = fields.Integer(
        validate=validate.Range(min=0),
        missing=0
    )
    
    # Content and resources
    content_url = fields.URL(
        validate=validate.Length(max=500),
        allow_none=True
    )
    
    video_url = fields.URL(
        validate=validate.Length(max=500),
        allow_none=True
    )
    
    resources = fields.List(
        fields.Dict(
            title=fields.String(required=True, validate=validate.Length(max=200)),
            type=fields.String(required=True, validate=validate.OneOf(['document', 'video', 'link', 'file'])),
            url=fields.URL(required=True),
            description=fields.String(validate=validate.Length(max=500))
        ),
        validate=validate.Length(max=50),
        missing=[]
    )
    
    assignments = fields.List(
        fields.Dict(
            title=fields.String(required=True, validate=validate.Length(max=200)),
            description=fields.String(validate=validate.Length(max=1000)),
            due_days=fields.Integer(validate=validate.Range(min=1)),
            points=fields.Integer(validate=validate.Range(min=0, max=1000))
        ),
        validate=validate.Length(max=20),
        missing=[]
    )
    
    # Assessment settings
    has_assessment = fields.Boolean(missing=False)
    
    assessment_type = fields.String(
        validate=validate.OneOf(['quiz', 'project', 'presentation', 'exam', 'assignment']),
        allow_none=True
    )
    
    passing_score = fields.Float(
        validate=validate.Range(min=0, max=100),
        missing=70.0,
        error_messages={
            "invalid": "Passing score must be between 0 and 100"
        }
    )
    
    max_attempts = fields.Integer(
        validate=validate.Range(min=1, max=10),
        missing=3
    )
    
    # Capacity
    min_participants = fields.Integer(
        validate=validate.Range(min=1, max=1000),
        missing=1
    )
    
    max_participants = fields.Integer(
        validate=validate.Range(min=1, max=1000),
        allow_none=True
    )
    
    # Additional information
    instructor_id = fields.Integer(
        validate=validate.Range(min=1),
        allow_none=True
    )
    
    tags = fields.List(
        fields.String(validate=validate.Length(max=50)),
        validate=validate.Length(max=20),
        missing=[]
    )
    
    thumbnail_url = fields.URL(
        validate=validate.Length(max=500),
        allow_none=True
    )
    
    course_metadata = fields.Dict(
        missing={},
        error_messages={
            "invalid": "Metadata must be a valid JSON object"
        }
    )
    
    @validates_schema
    def validate_assessment_settings(self, data, **kwargs):
        has_assessment = data.get('has_assessment', False)
        assessment_type = data.get('assessment_type')
        
        if has_assessment and not assessment_type:
            raise ValidationError("Assessment type is required when assessment is enabled")
        
        if not has_assessment and assessment_type:
            raise ValidationError("Assessment type should not be provided when assessment is disabled")
    
    @validates_schema
    def validate_capacity(self, data, **kwargs):
        min_participants = data.get('min_participants', 1)
        max_participants = data.get('max_participants')
        
        if max_participants and min_participants > max_participants:
            raise ValidationError("Minimum participants cannot exceed maximum participants")


class CourseCreateSchema(CourseBaseSchema):
    """Schema for creating a course"""
    
    program_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            "required": "Program ID is required",
            "invalid": "Invalid program ID"
        }
    )


class CourseUpdateSchema(BaseSchema):
    """Schema for updating a course - all fields optional"""
    
    title = fields.String(
        validate=[
            validate.Length(min=3, max=200),
            validate_no_sql_injection,
            validate_no_xss
        ],
        missing=fields.missing_
    )
    
    subtitle = fields.String(
        validate=[
            validate.Length(max=300),
            validate_no_xss
        ],
        allow_none=True,
        missing=fields.missing_
    )
    
    description = fields.String(
        validate=[
            validate.Length(max=5000),
            validate_no_xss
        ],
        allow_none=True,
        missing=fields.missing_
    )
    
    objectives = fields.List(
        fields.String(validate=[validate.Length(max=500), validate_no_xss]),
        validate=validate.Length(max=20),
        missing=fields.missing_
    )
    
    prerequisites = fields.List(
        fields.String(validate=[validate.Length(max=200), validate_no_xss]),
        validate=validate.Length(max=10),
        missing=fields.missing_
    )
    
    format = fields.String(
        validate=validate.OneOf([
            'lecture', 'workshop', 'practical', 'online', 
            'self_paced', 'hybrid', 'seminar', 'lab'
        ]),
        missing=fields.missing_
    )
    
    difficulty_level = fields.String(
        validate=validate.OneOf(['beginner', 'intermediate', 'advanced', 'expert']),
        missing=fields.missing_
    )
    
    status = fields.String(
        validate=validate.OneOf(['draft', 'published', 'archived']),
        missing=fields.missing_
    )
    
    duration_hours = fields.Float(
        validate=validate.Range(min=0.5, max=200),
        missing=fields.missing_
    )
    
    duration_weeks = fields.Integer(
        validate=validate.Range(min=1, max=52),
        missing=fields.missing_
    )
    
    tags = fields.List(
        fields.String(validate=validate.Length(max=50)),
        validate=validate.Length(max=20),
        missing=fields.missing_
    )
    
    # Assessment settings
    has_assessment = fields.Boolean(missing=fields.missing_)
    assessment_type = fields.String(
        validate=validate.OneOf(['quiz', 'project', 'presentation', 'exam', 'assignment']),
        allow_none=True,
        missing=fields.missing_
    )
    passing_score = fields.Float(
        validate=validate.Range(min=0, max=100),
        missing=fields.missing_
    )
    
    # Capacity
    min_participants = fields.Integer(
        validate=validate.Range(min=1, max=1000),
        missing=fields.missing_
    )
    max_participants = fields.Integer(
        validate=validate.Range(min=1, max=1000),
        allow_none=True,
        missing=fields.missing_
    )
    
    # Additional fields
    instructor_id = fields.Integer(
        validate=validate.Range(min=1),
        allow_none=True,
        missing=fields.missing_
    )


class CourseQuerySchema(PaginationSchema):
    """Schema for course search/filter parameters"""
    
    status = fields.String(
        validate=validate.OneOf(['draft', 'published', 'archived']),
        missing=fields.missing_
    )
    
    format = fields.String(
        validate=validate.OneOf([
            'lecture', 'workshop', 'practical', 'online', 
            'self_paced', 'hybrid', 'seminar', 'lab'
        ]),
        missing=fields.missing_
    )
    
    difficulty_level = fields.String(
        validate=validate.OneOf(['beginner', 'intermediate', 'advanced', 'expert']),
        missing=fields.missing_
    )
    
    instructor_id = fields.Integer(
        validate=validate.Range(min=1),
        missing=fields.missing_
    )
    
    search = fields.String(
        validate=[validate.Length(min=2, max=100), validate_no_sql_injection],
        missing=fields.missing_
    )
    
    has_assessment = fields.Boolean(missing=fields.missing_)
    has_sessions = fields.Boolean(missing=fields.missing_)
    
    min_duration_hours = fields.Float(
        validate=validate.Range(min=0),
        missing=fields.missing_
    )
    
    max_duration_hours = fields.Float(
        validate=validate.Range(min=0),
        missing=fields.missing_
    )
    
    tags = fields.List(
        fields.String(),
        missing=fields.missing_
    )
    
    @validates_schema
    def validate_duration_range(self, data, **kwargs):
        min_duration = data.get('min_duration_hours')
        max_duration = data.get('max_duration_hours')
        if min_duration is not None and max_duration is not None and min_duration > max_duration:
            raise ValidationError("Minimum duration cannot exceed maximum duration")


class CourseSessionSchema(BaseSchema):
    """Schema for course sessions"""
    
    title = fields.String(
        required=True,
        validate=[validate.Length(min=3, max=200), validate_no_xss],
        error_messages={
            "required": "Session title is required"
        }
    )
    
    description = fields.String(
        validate=[validate.Length(max=1000), validate_no_xss],
        allow_none=True
    )
    
    session_date = fields.Date(
        required=True,
        format="%Y-%m-%d",
        error_messages={
            "required": "Session date is required",
            "invalid": "Invalid date format. Use YYYY-MM-DD"
        }
    )
    
    start_time = fields.Time(
        required=True,
        format="%H:%M",
        error_messages={
            "required": "Start time is required",
            "invalid": "Invalid time format. Use HH:MM"
        }
    )
    
    end_time = fields.Time(
        required=True,
        format="%H:%M",
        error_messages={
            "required": "End time is required",
            "invalid": "Invalid time format. Use HH:MM"
        }
    )
    
    duration_hours = fields.Float(
        validate=validate.Range(min=0.25, max=12),
        error_messages={
            "invalid": "Session duration must be between 0.25 and 12 hours"
        }
    )
    
    location = fields.String(
        validate=[validate.Length(max=200), validate_no_xss],
        allow_none=True
    )
    
    online_link = fields.URL(
        validate=validate.Length(max=500),
        allow_none=True
    )
    
    is_online = fields.Boolean(missing=False)
    
    instructor_id = fields.Integer(
        validate=validate.Range(min=1),
        allow_none=True
    )
    
    max_participants = fields.Integer(
        validate=validate.Range(min=1, max=1000),
        allow_none=True
    )
    
    is_mandatory = fields.Boolean(missing=True)
    is_recorded = fields.Boolean(missing=False)
    
    materials = fields.List(
        fields.Dict(),
        validate=validate.Length(max=20),
        missing=[]
    )
    
    @validates_schema
    def validate_times(self, data, **kwargs):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError("End time must be after start time")
        
        # Calculate duration if not provided
        if start_time and end_time and 'duration_hours' not in data:
            # Convert times to minutes for calculation
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            duration_minutes = end_minutes - start_minutes
            data['duration_hours'] = duration_minutes / 60
    
    @validates_schema
    def validate_online_settings(self, data, **kwargs):
        is_online = data.get('is_online', False)
        online_link = data.get('online_link')
        location = data.get('location')
        
        if is_online and not online_link:
            raise ValidationError("Online link is required for online sessions")
        
        if not is_online and not location:
            raise ValidationError("Location is required for in-person sessions")


class CourseReorderSchema(BaseSchema):
    """Schema for reordering courses"""
    
    course_orders = fields.Dict(
        keys=fields.Integer(validate=validate.Range(min=1)),
        values=fields.Integer(validate=validate.Range(min=0)),
        required=True,
        error_messages={
            "required": "Course orders mapping is required"
        }
    )


class CourseDuplicateSchema(BaseSchema):
    """Schema for duplicating a course"""
    
    title = fields.String(
        validate=[validate.Length(min=3, max=200), validate_no_xss],
        missing=None
    )
    
    program_id = fields.Integer(
        validate=validate.Range(min=1),
        missing=None
    )
    
    include_sessions = fields.Boolean(missing=False)
    include_materials = fields.Boolean(missing=True)
    include_assignments = fields.Boolean(missing=True)


class CourseResponseSchema(BaseSchema):
    """Schema for course response serialization"""
    
    id = fields.Integer()
    uuid = fields.UUID()
    code = fields.String()
    title = fields.String()
    subtitle = fields.String()
    description = fields.String()
    
    program_id = fields.Integer()
    program_title = fields.String()
    program_code = fields.String()
    
    status = fields.String()
    format = fields.String()
    difficulty_level = fields.String()
    
    objectives = fields.List(fields.String())
    outline = fields.List(fields.Dict())
    prerequisites = fields.List(fields.String())
    materials = fields.List(fields.String())
    
    duration_hours = fields.Float()
    duration_weeks = fields.Integer()
    total_duration_hours = fields.Float()
    order_index = fields.Integer()
    
    content_url = fields.URL()
    video_url = fields.URL()
    resources = fields.List(fields.Dict())
    assignments = fields.List(fields.Dict())
    
    has_assessment = fields.Boolean()
    assessment_type = fields.String()
    passing_score = fields.Float()
    max_attempts = fields.Integer()
    
    min_participants = fields.Integer()
    max_participants = fields.Integer()
    participant_count = fields.Integer()
    available_spots = fields.Integer()
    
    instructor_id = fields.Integer()
    instructor_name = fields.String()
    instructor = fields.Dict()
    
    program = fields.Dict()
    
    tags = fields.List(fields.String())
    thumbnail_url = fields.URL()
    course_metadata = fields.Dict()
    
    # Computed fields
    is_available = fields.Boolean()
    completion_rate = fields.Float()
    average_score = fields.Float()
    session_count = fields.Integer()
    
    # Optional nested data
    sessions = fields.List(fields.Dict())
    
    # Timestamps
    created_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    updated_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    created_by = fields.Integer()
    
    @post_dump
    def format_response(self, data, **kwargs):
        """Format response data"""
        # Convert None to empty string for optional string fields
        string_fields = ['subtitle', 'description', 'content_url', 'video_url', 
                        'thumbnail_url', 'instructor_name']
        for field in string_fields:
            if field in data and data[field] is None:
                data[field] = ""
        
        # Ensure lists are not None
        list_fields = ['objectives', 'outline', 'prerequisites', 'materials', 
                      'resources', 'assignments', 'tags']
        for field in list_fields:
            if field in data and data[field] is None:
                data[field] = []
        
        return data


class CourseStatisticsResponseSchema(BaseSchema):
    """Schema for course statistics response"""
    
    course_id = fields.Integer()
    course_title = fields.String()
    
    total_sessions = fields.Integer()
    completed_sessions = fields.Integer()
    upcoming_sessions = fields.Integer()
    
    total_participants = fields.Integer()
    active_participants = fields.Integer()
    completed_participants = fields.Integer()
    
    completion_rate = fields.Float()
    average_score = fields.Float()
    pass_rate = fields.Float()
    
    total_assignments = fields.Integer()
    average_assignment_score = fields.Float()
    
    attendance_rate = fields.Float()
    satisfaction_rating = fields.Float()
    
    popular_resources = fields.List(fields.Dict())
    session_attendance = fields.List(fields.Dict())
    score_distribution = fields.Dict()
    
    generated_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")