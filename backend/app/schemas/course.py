"""Schemas for Course validation and serialization."""

from marshmallow import Schema, fields, validate, ValidationError, pre_load, post_dump
from datetime import datetime
from app.models.course import CourseStatus, CourseFormat, DifficultyLevel


class CourseBaseSchema(Schema):
    """Base schema for course data."""

    code = fields.String(dump_only=True)
    title = fields.String(
        required=True, validate=validate.Length(min=1, max=200), error_messages={"required": "Course title is required"}
    )
    subtitle = fields.String(allow_none=True, validate=validate.Length(max=300))
    description = fields.String(allow_none=True)

    # Course details
    status = fields.String(validate=validate.OneOf([s.value for s in CourseStatus]), load_default=CourseStatus.DRAFT.value)
    format = fields.String(validate=validate.OneOf([f.value for f in CourseFormat]), load_default=CourseFormat.LECTURE.value)
    difficulty_level = fields.String(
        validate=validate.OneOf([d.value for d in DifficultyLevel]), load_default=DifficultyLevel.BEGINNER.value
    )

    # Duration
    duration_hours = fields.Float(validate=validate.Range(min=0.5, max=100), load_default=1.0)
    duration_weeks = fields.Integer(validate=validate.Range(min=1, max=52), load_default=1)
    order_index = fields.Integer(validate=validate.Range(min=0), load_default=0)

    # Content
    objectives = fields.List(fields.String(), load_default=list)
    outline = fields.List(fields.String(), load_default=list)
    prerequisites = fields.List(fields.String(), load_default=list)
    materials = fields.List(fields.String(), load_default=list)

    # Resources
    content_url = fields.URL(allow_none=True)
    video_url = fields.URL(allow_none=True)
    thumbnail_url = fields.URL(allow_none=True)
    resources = fields.List(fields.Dict(), load_default=list)
    assignments = fields.List(fields.Dict(), load_default=list)

    # Assessment
    has_assessment = fields.Boolean(load_default=False)
    assessment_type = fields.String(allow_none=True, validate=validate.Length(max=50))
    passing_score = fields.Float(validate=validate.Range(min=0, max=100), load_default=70.0)
    max_attempts = fields.Integer(validate=validate.Range(min=1, max=10), load_default=3)

    # Capacity
    min_participants = fields.Integer(validate=validate.Range(min=1), load_default=1)
    max_participants = fields.Integer(allow_none=True, validate=validate.Range(min=1))

    # Additional
    tags = fields.List(fields.String(), load_default=list)
    course_metadata = fields.Dict(load_default=dict)

    # Relations
    instructor_id = fields.Integer(allow_none=True)
    program_id = fields.Integer(required=True)

    @pre_load
    def process_input(self, data, **kwargs):
        """Process input data before validation."""
        # Ensure lists are lists
        list_fields = ["objectives", "outline", "prerequisites", "materials", "resources", "assignments", "tags"]
        for field in list_fields:
            if field in data and not isinstance(data[field], list):
                data[field] = [data[field]]

        # Validate assessment fields consistency
        if data.get("has_assessment"):
            if not data.get("assessment_type"):
                raise ValidationError("Assessment type is required when has_assessment is true")

        return data

    @post_dump
    def process_output(self, data, **kwargs):
        """Process output data after serialization."""
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


class CourseCreateSchema(CourseBaseSchema):
    """Schema for creating a new course."""

    pass


class CourseUpdateSchema(CourseBaseSchema):
    """Schema for updating an existing course."""

    title = fields.String(validate=validate.Length(min=1, max=200))
    program_id = fields.Integer()  # Not required for updates

    class Meta:
        """Schema meta configuration."""

        partial = True  # Allow partial updates


class CourseResponseSchema(CourseBaseSchema):
    """Schema for course response data."""

    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Computed fields
    total_duration_hours = fields.Float(dump_only=True)
    is_available = fields.Boolean(dump_only=True)
    participant_count = fields.Integer(dump_only=True)
    available_spots = fields.Integer(dump_only=True)
    completion_rate = fields.Float(dump_only=True)
    average_score = fields.Float(dump_only=True, allow_none=True)
    session_count = fields.Integer(dump_only=True)

    # Related data
    instructor_name = fields.String(dump_only=True)
    program_title = fields.String(dump_only=True)
    program_code = fields.String(dump_only=True)
    
    # Optional related data
    sessions = fields.List(fields.Dict(), dump_only=True, load_default=None)


class CourseListSchema(Schema):
    """Schema for course list response."""

    courses = fields.List(fields.Nested(CourseResponseSchema))
    pagination = fields.Dict()


class CourseOrderUpdateSchema(Schema):
    """Schema for updating course order."""

    order_index = fields.Integer(required=True, validate=validate.Range(min=0))


class CourseDuplicateSchema(Schema):
    """Schema for duplicating a course."""

    program_id = fields.Integer(allow_none=True)
    title = fields.String(allow_none=True, validate=validate.Length(min=1, max=200))


class CourseSessionAddSchema(Schema):
    """Schema for adding a session to a course."""

    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    scheduled_date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    duration_hours = fields.Float(required=True, validate=validate.Range(min=0.5, max=8))
    location = fields.String(allow_none=True, validate=validate.Length(max=200))
    online_link = fields.URL(allow_none=True)
    instructor_id = fields.Integer(allow_none=True)
    max_participants = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    description = fields.String(allow_none=True)
    materials = fields.List(fields.Dict(), load_default=list)
