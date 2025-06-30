"""
Enhanced Evaluation schemas with comprehensive validation
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError, post_dump
from datetime import datetime, date, timedelta
from typing import Optional

from .validation import BaseSchema, PaginationSchema, validate_no_sql_injection, validate_no_xss, validate_percentage


class EvaluationBaseSchema(BaseSchema):
    """Base schema for evaluation data"""

    title = fields.String(
        required=True,
        validate=[validate.Length(min=3, max=200), validate_no_sql_injection, validate_no_xss],
        error_messages={
            "required": "Evaluation title is required",
            "invalid": "Evaluation title must be between 3 and 200 characters",
        },
    )

    description = fields.String(validate=[validate.Length(max=2000), validate_no_xss], allow_none=True)

    evaluation_type = fields.String(
        validate=validate.OneOf(["quiz", "exam", "assessment", "survey", "diagnostic", "placement", "certification"]),
        missing="quiz",
        error_messages={"invalid": "Invalid evaluation type"},
    )

    status = fields.String(validate=validate.OneOf(["draft", "active", "archived"]), missing="draft")

    # Timing settings
    time_limit_minutes = fields.Integer(
        validate=validate.Range(min=0, max=480),  # Max 8 hours
        allow_none=True,
        error_messages={"invalid": "Time limit must be between 0 and 480 minutes"},
    )

    available_from = fields.DateTime(format="%Y-%m-%dT%H:%M:%S", allow_none=True)

    available_until = fields.DateTime(format="%Y-%m-%dT%H:%M:%S", allow_none=True)

    # Attempt settings
    max_attempts = fields.Integer(
        validate=validate.Range(min=1, max=10),
        missing=3,
        error_messages={"invalid": "Maximum attempts must be between 1 and 10"},
    )

    attempt_cooldown_hours = fields.Integer(
        validate=validate.Range(min=0, max=168),  # Max 1 week
        missing=0,
        error_messages={"invalid": "Cooldown period must be between 0 and 168 hours"},
    )

    # Scoring settings
    passing_score = fields.Float(
        validate=validate.Range(min=0, max=100),
        missing=70.0,
        error_messages={"invalid": "Passing score must be between 0 and 100"},
    )

    scoring_method = fields.String(validate=validate.OneOf(["highest", "latest", "average"]), missing="highest")

    # Display settings
    randomize_questions = fields.Boolean(missing=False)
    randomize_options = fields.Boolean(missing=False)
    show_one_question_at_time = fields.Boolean(missing=False)
    allow_navigation = fields.Boolean(missing=True)

    # Feedback settings
    show_results_immediately = fields.Boolean(missing=True)
    show_correct_answers = fields.Boolean(missing=False)
    allow_review = fields.Boolean(missing=True)
    provide_feedback = fields.Boolean(missing=True)

    # AI settings
    enable_ai_proctoring = fields.Boolean(missing=False)
    enable_plagiarism_check = fields.Boolean(missing=False)

    # Adaptive settings
    is_adaptive = fields.Boolean(missing=False)
    difficulty_adjustment_factor = fields.Float(validate=validate.Range(min=0.1, max=2.0), missing=1.0)

    # Additional settings
    instructions = fields.String(validate=[validate.Length(max=5000), validate_no_xss], allow_none=True)

    tags = fields.List(fields.String(validate=validate.Length(max=50)), validate=validate.Length(max=20), missing=[])

    metadata = fields.Dict(missing={})

    @validates_schema
    def validate_availability(self, data, **kwargs):
        available_from = data.get("available_from")
        available_until = data.get("available_until")

        if available_from and available_until:
            if available_from >= available_until:
                raise ValidationError("Available until must be after available from")

            # Check reasonable duration
            duration = available_until - available_from
            if duration > timedelta(days=365):
                raise ValidationError("Availability period cannot exceed 1 year")

    @validates_schema
    def validate_adaptive_settings(self, data, **kwargs):
        is_adaptive = data.get("is_adaptive", False)
        show_one_question = data.get("show_one_question_at_time", False)
        allow_navigation = data.get("allow_navigation", True)

        if is_adaptive:
            if not show_one_question:
                raise ValidationError("Adaptive evaluations must show one question at a time")
            if allow_navigation:
                raise ValidationError("Adaptive evaluations cannot allow navigation between questions")


class QuestionBaseSchema(BaseSchema):
    """Base schema for question data"""

    question_text = fields.String(
        required=True,
        validate=[validate.Length(min=5, max=2000), validate_no_xss],
        error_messages={
            "required": "Question text is required",
            "invalid": "Question text must be between 5 and 2000 characters",
        },
    )

    question_type = fields.String(
        required=True,
        validate=validate.OneOf(
            ["multiple_choice", "true_false", "short_answer", "essay", "matching", "ordering", "fill_blank"]
        ),
        error_messages={"required": "Question type is required", "invalid": "Invalid question type"},
    )

    difficulty_level = fields.String(validate=validate.OneOf(["easy", "medium", "hard", "expert"]), missing="medium")

    points = fields.Integer(
        validate=validate.Range(min=1, max=100),
        missing=1,
        error_messages={"invalid": "Points must be between 1 and 100"},
    )

    order_index = fields.Integer(validate=validate.Range(min=0), missing=0)

    # Options for multiple choice questions
    options = fields.List(
        fields.Dict(
            text=fields.String(required=True, validate=[validate.Length(max=500), validate_no_xss]),
            is_correct=fields.Boolean(required=True),
            feedback=fields.String(validate=[validate.Length(max=500), validate_no_xss]),
        ),
        validate=validate.Length(min=2, max=10),
    )

    # Correct answer for other question types
    correct_answer = fields.String(validate=[validate.Length(max=1000), validate_no_xss], allow_none=True)

    # Additional content
    explanation = fields.String(validate=[validate.Length(max=2000), validate_no_xss], allow_none=True)

    hint = fields.String(validate=[validate.Length(max=500), validate_no_xss], allow_none=True)

    media_url = fields.URL(validate=validate.Length(max=500), allow_none=True)

    # Scoring options
    partial_credit_enabled = fields.Boolean(missing=False)
    negative_marking = fields.Boolean(missing=False)
    negative_marks = fields.Float(validate=validate.Range(min=0, max=1), missing=0)

    # Time limit for individual question
    time_limit_seconds = fields.Integer(
        validate=validate.Range(min=0, max=3600), allow_none=True  # Max 1 hour per question
    )

    # Categories and tags
    category = fields.String(validate=[validate.Length(max=100), validate_no_xss], allow_none=True)

    tags = fields.List(fields.String(validate=validate.Length(max=50)), validate=validate.Length(max=10), missing=[])

    @validates_schema
    def validate_question_type_requirements(self, data, **kwargs):
        question_type = data.get("question_type")
        options = data.get("options", [])
        correct_answer = data.get("correct_answer")

        if question_type == "multiple_choice":
            if len(options) < 2:
                raise ValidationError("Multiple choice questions must have at least 2 options")

            # Validate at least one correct option
            correct_options = [opt for opt in options if opt.get("is_correct")]
            if not correct_options:
                raise ValidationError("Multiple choice questions must have at least one correct option")

        elif question_type == "true_false":
            if correct_answer not in ["true", "false", "True", "False"]:
                raise ValidationError("True/False questions must have correct_answer as 'true' or 'false'")

        elif question_type in ["short_answer", "fill_blank"]:
            if not correct_answer:
                raise ValidationError(f"{question_type} questions must have a correct_answer")

    @validates_schema
    def validate_negative_marking(self, data, **kwargs):
        negative_marking = data.get("negative_marking", False)
        negative_marks = data.get("negative_marks", 0)

        if negative_marking and negative_marks <= 0:
            raise ValidationError("Negative marks must be greater than 0 when negative marking is enabled")


class EvaluationCreateSchema(EvaluationBaseSchema):
    """Schema for creating an evaluation"""

    course_id = fields.Integer(validate=validate.Range(min=1), allow_none=True)

    program_id = fields.Integer(validate=validate.Range(min=1), allow_none=True)

    @validates_schema
    def validate_association(self, data, **kwargs):
        course_id = data.get("course_id")
        program_id = data.get("program_id")

        if not course_id and not program_id:
            raise ValidationError("Evaluation must be associated with either a course or program")


class EvaluationUpdateSchema(EvaluationBaseSchema):
    """Schema for updating an evaluation"""

    # All fields are optional for updates
    title = fields.String(
        validate=[validate.Length(min=3, max=200), validate_no_sql_injection, validate_no_xss], missing=fields.missing_
    )


class QuestionCreateSchema(QuestionBaseSchema):
    """Schema for creating a question"""

    pass


class QuestionUpdateSchema(QuestionBaseSchema):
    """Schema for updating a question"""

    # All fields are optional for updates
    question_text = fields.String(validate=[validate.Length(min=5, max=2000), validate_no_xss], missing=fields.missing_)

    question_type = fields.String(
        validate=validate.OneOf(
            ["multiple_choice", "true_false", "short_answer", "essay", "matching", "ordering", "fill_blank"]
        ),
        missing=fields.missing_,
    )


class EvaluationQuerySchema(PaginationSchema):
    """Schema for evaluation search/filter parameters"""

    status = fields.String(validate=validate.OneOf(["draft", "active", "archived"]), missing=fields.missing_)

    evaluation_type = fields.String(
        validate=validate.OneOf(["quiz", "exam", "assessment", "survey", "diagnostic", "placement", "certification"]),
        missing=fields.missing_,
    )

    course_id = fields.Integer(validate=validate.Range(min=1), missing=fields.missing_)

    program_id = fields.Integer(validate=validate.Range(min=1), missing=fields.missing_)

    search = fields.String(
        validate=[validate.Length(min=2, max=100), validate_no_sql_injection], missing=fields.missing_
    )

    is_adaptive = fields.Boolean(missing=fields.missing_)
    has_time_limit = fields.Boolean(missing=fields.missing_)

    available_now = fields.Boolean(missing=False)

    tags = fields.List(fields.String(), missing=fields.missing_)


class AttemptStartSchema(BaseSchema):
    """Schema for starting an evaluation attempt"""

    acknowledgment = fields.Boolean(
        required=True, error_messages={"required": "You must acknowledge the evaluation rules"}
    )

    device_info = fields.Dict(missing={})


class ResponseSubmitSchema(BaseSchema):
    """Schema for submitting a question response"""

    question_id = fields.Integer(
        required=True, validate=validate.Range(min=1), error_messages={"required": "Question ID is required"}
    )

    response_data = fields.Dict(required=True, error_messages={"required": "Response data is required"})

    time_spent_seconds = fields.Integer(validate=validate.Range(min=0), missing=0)


class AttemptSubmitSchema(BaseSchema):
    """Schema for submitting an evaluation attempt"""

    responses = fields.List(
        fields.Nested(ResponseSubmitSchema),
        validate=validate.Length(min=1),
        error_messages={"validator_failed": "At least one response is required"},
    )

    submit_confirmation = fields.Boolean(
        required=True, error_messages={"required": "Submission confirmation is required"}
    )


class EvaluationResponseSchema(BaseSchema):
    """Schema for evaluation response serialization"""

    id = fields.Integer()
    uuid = fields.UUID()
    title = fields.String()
    description = fields.String()

    evaluation_type = fields.String()
    status = fields.String()

    course_id = fields.Integer()
    course_title = fields.String()
    program_id = fields.Integer()
    program_title = fields.String()

    # Timing
    time_limit_minutes = fields.Integer()
    available_from = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    available_until = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")

    # Attempts
    max_attempts = fields.Integer()
    attempt_cooldown_hours = fields.Integer()
    attempts_used = fields.Integer()
    can_attempt = fields.Boolean()
    next_attempt_available = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")

    # Scoring
    total_questions = fields.Integer()
    total_points = fields.Integer()
    passing_score = fields.Float()
    scoring_method = fields.String()

    # Settings
    randomize_questions = fields.Boolean()
    randomize_options = fields.Boolean()
    show_one_question_at_time = fields.Boolean()
    allow_navigation = fields.Boolean()
    show_results_immediately = fields.Boolean()
    show_correct_answers = fields.Boolean()
    allow_review = fields.Boolean()

    # Adaptive
    is_adaptive = fields.Boolean()

    # Additional
    instructions = fields.String()
    tags = fields.List(fields.String())

    # Statistics
    attempt_count = fields.Integer()
    average_score = fields.Float()
    pass_rate = fields.Float()

    # Timestamps
    created_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    updated_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    created_by = fields.Integer()

    @post_dump
    def format_response(self, data, **kwargs):
        """Format response data"""
        # Convert None to empty string for optional string fields
        string_fields = ["description", "instructions", "course_title", "program_title"]
        for field in string_fields:
            if field in data and data[field] is None:
                data[field] = ""

        # Ensure lists are not None
        if "tags" in data and data["tags"] is None:
            data["tags"] = []

        return data


class QuestionResponseSchema(BaseSchema):
    """Schema for question response serialization"""

    id = fields.Integer()
    question_text = fields.String()
    question_type = fields.String()
    difficulty_level = fields.String()
    points = fields.Integer()
    order_index = fields.Integer()

    options = fields.List(fields.Dict())
    correct_answer = fields.String()

    explanation = fields.String()
    hint = fields.String()
    media_url = fields.URL()

    partial_credit_enabled = fields.Boolean()
    negative_marking = fields.Boolean()
    negative_marks = fields.Float()

    time_limit_seconds = fields.Integer()

    category = fields.String()
    tags = fields.List(fields.String())

    # Statistics
    attempt_count = fields.Integer()
    correct_count = fields.Integer()
    success_rate = fields.Float()
    average_time_seconds = fields.Float()


class AttemptResponseSchema(BaseSchema):
    """Schema for attempt response serialization"""

    id = fields.Integer()
    evaluation_id = fields.Integer()
    evaluation_title = fields.String()

    user_id = fields.Integer()
    user_name = fields.String()

    attempt_number = fields.Integer()
    status = fields.String()

    started_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    completed_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    time_spent_minutes = fields.Integer()

    total_questions = fields.Integer()
    questions_answered = fields.Integer()

    total_points = fields.Integer()
    score_earned = fields.Float()
    percentage_score = fields.Float()

    passed = fields.Boolean()

    ai_proctoring_flags = fields.List(fields.Dict())
    device_info = fields.Dict()


class EvaluationStatisticsSchema(BaseSchema):
    """Schema for evaluation statistics response"""

    evaluation_id = fields.Integer()
    evaluation_title = fields.String()

    total_questions = fields.Integer()
    total_points = fields.Integer()
    passing_score = fields.Float()

    total_attempts = fields.Integer()
    completed_attempts = fields.Integer()
    passed_attempts = fields.Integer()

    pass_rate = fields.Float()
    average_score = fields.Float()
    highest_score = fields.Float()
    lowest_score = fields.Float()

    average_time_minutes = fields.Float()

    question_statistics = fields.List(fields.Dict())
    score_distribution = fields.Dict()
    attempt_timeline = fields.List(fields.Dict())

    generated_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
