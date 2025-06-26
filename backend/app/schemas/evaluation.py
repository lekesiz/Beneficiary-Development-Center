"""Schemas for Evaluation validation and serialization."""

from marshmallow import Schema, fields, validate, ValidationError, pre_load, post_dump
from datetime import datetime
from app.models.evaluation import EvaluationStatus, QuestionType, DifficultyLevel, AttemptStatus


class EvaluationSettingsSchema(Schema):
    """Schema for evaluation settings."""

    time_limit_minutes = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1, max=600),
        metadata={"description": "Time limit in minutes, NULL means no time limit"},
    )
    max_attempts = fields.Integer(validate=validate.Range(min=1, max=10), missing=1)
    passing_score = fields.Float(validate=validate.Range(min=0, max=100), missing=70.0)
    shuffle_questions = fields.Boolean(missing=False)
    show_results_immediately = fields.Boolean(missing=True)
    allow_review = fields.Boolean(missing=True)
    is_adaptive = fields.Boolean(missing=False)


class EvaluationCreateSchema(Schema):
    """Schema for creating evaluations."""

    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={"required": "Evaluation title is required"},
    )
    description = fields.String(allow_none=True)
    instructions = fields.String(allow_none=True)

    # Relationships
    course_id = fields.Integer(allow_none=True)
    program_id = fields.Integer(allow_none=True)

    # Settings (nested)
    settings = fields.Nested(EvaluationSettingsSchema, missing={})

    # Status
    status = fields.String(
        validate=validate.OneOf([s.value for s in EvaluationStatus]), missing=EvaluationStatus.DRAFT.value
    )

    # Dates
    available_from = fields.DateTime(allow_none=True, format="iso")
    available_until = fields.DateTime(allow_none=True, format="iso")

    # Metadata
    evaluation_metadata = fields.Dict(missing={})
    tags = fields.List(fields.String(), missing=[])

    @pre_load
    def extract_settings(self, data, **kwargs):
        """Extract settings fields into nested object."""
        settings_fields = [
            "time_limit_minutes",
            "max_attempts",
            "passing_score",
            "shuffle_questions",
            "show_results_immediately",
            "allow_review",
            "is_adaptive",
        ]

        if "settings" not in data:
            data["settings"] = {}

        for field in settings_fields:
            if field in data:
                data["settings"][field] = data.pop(field)

        return data

    @post_dump
    def flatten_settings(self, data, **kwargs):
        """Flatten settings for response."""
        if "settings" in data:
            settings = data.pop("settings")
            data.update(settings)
        return data


class EvaluationUpdateSchema(Schema):
    """Schema for updating evaluations (partial updates)."""

    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    instructions = fields.String(allow_none=True)

    # Relationships
    course_id = fields.Integer(allow_none=True)
    program_id = fields.Integer(allow_none=True)

    # Settings
    time_limit_minutes = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=600))
    max_attempts = fields.Integer(validate=validate.Range(min=1, max=10))
    passing_score = fields.Float(validate=validate.Range(min=0, max=100))
    shuffle_questions = fields.Boolean()
    show_results_immediately = fields.Boolean()
    allow_review = fields.Boolean()
    is_adaptive = fields.Boolean()

    # Status
    status = fields.String(validate=validate.OneOf([s.value for s in EvaluationStatus]))

    # Dates
    available_from = fields.DateTime(allow_none=True, format="iso")
    available_until = fields.DateTime(allow_none=True, format="iso")

    # Metadata
    evaluation_metadata = fields.Dict()
    tags = fields.List(fields.String())


class EvaluationResponseSchema(Schema):
    """Schema for evaluation API responses."""

    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    title = fields.String()
    description = fields.String()
    instructions = fields.String()

    # Relationships
    course_id = fields.Integer()
    program_id = fields.Integer()
    created_by = fields.Integer()

    # Settings
    status = fields.String()
    total_questions = fields.Integer()
    total_points = fields.Float()
    passing_score = fields.Float()
    time_limit_minutes = fields.Integer(allow_none=True)
    max_attempts = fields.Integer()
    shuffle_questions = fields.Boolean()
    show_results_immediately = fields.Boolean()
    allow_review = fields.Boolean()
    is_adaptive = fields.Boolean()

    # Dates
    available_from = fields.DateTime(format="iso")
    available_until = fields.DateTime(format="iso")
    created_at = fields.DateTime(format="iso", dump_only=True)
    updated_at = fields.DateTime(format="iso", dump_only=True)

    # Metadata
    evaluation_metadata = fields.Dict()
    tags = fields.List(fields.String())

    # Computed properties
    is_available = fields.Boolean(dump_only=True)
    duration_display = fields.String(dump_only=True)

    # Related data (optional)
    course_title = fields.String(dump_only=True)
    program_title = fields.String(dump_only=True)
    creator_name = fields.String(dump_only=True)

    # Nested data (optional)
    questions = fields.List(fields.Nested("QuestionResponseSchema"), dump_only=True)
    attempts = fields.List(fields.Nested("EvaluationAttemptResponseSchema"), dump_only=True)


class QuestionCreateSchema(Schema):
    """Schema for creating questions."""

    question_text = fields.String(
        required=True, validate=validate.Length(min=1), error_messages={"required": "Question text is required"}
    )
    question_type = fields.String(
        required=True,
        validate=validate.OneOf([q.value for q in QuestionType]),
        error_messages={"required": "Question type is required"},
    )
    difficulty_level = fields.String(
        validate=validate.OneOf([d.value for d in DifficultyLevel]), missing=DifficultyLevel.MEDIUM.value
    )
    points = fields.Float(validate=validate.Range(min=0, max=100), missing=1.0)
    order_index = fields.Integer(validate=validate.Range(min=0), missing=0)

    # Question data (flexible structure for different question types)
    question_data = fields.Dict(required=True, error_messages={"required": "Question data is required"})

    # Settings
    is_required = fields.Boolean(missing=True)
    explanation = fields.String(allow_none=True)
    hints = fields.List(fields.String(), missing=[])

    # Metadata
    question_metadata = fields.Dict(missing={})
    tags = fields.List(fields.String(), missing=[])

    @pre_load
    def validate_question_data(self, data, **kwargs):
        """Validate question_data based on question_type."""
        question_type = data.get("question_type")
        question_data = data.get("question_data", {})

        if question_type == QuestionType.MULTIPLE_CHOICE.value:
            if "options" not in question_data:
                raise ValidationError("Options are required for multiple choice questions")
            if "correct_answer" not in question_data:
                raise ValidationError("Correct answer is required for multiple choice questions")

        elif question_type == QuestionType.TRUE_FALSE.value:
            if "correct_answer" not in question_data:
                raise ValidationError("Correct answer is required for true/false questions")

        elif question_type == QuestionType.MATCHING.value:
            if "pairs" not in question_data:
                raise ValidationError("Pairs are required for matching questions")

        elif question_type == QuestionType.ORDERING.value:
            if "items" not in question_data:
                raise ValidationError("Items are required for ordering questions")

        elif question_type == QuestionType.FILL_IN_BLANK.value:
            if "blanks" not in question_data:
                raise ValidationError("Blanks are required for fill-in-the-blank questions")

        return data


class QuestionUpdateSchema(Schema):
    """Schema for updating questions."""

    question_text = fields.String(validate=validate.Length(min=1))
    question_type = fields.String(validate=validate.OneOf([q.value for q in QuestionType]))
    difficulty_level = fields.String(validate=validate.OneOf([d.value for d in DifficultyLevel]))
    points = fields.Float(validate=validate.Range(min=0, max=100))
    order_index = fields.Integer(validate=validate.Range(min=0))

    # Question data
    question_data = fields.Dict()

    # Settings
    is_required = fields.Boolean()
    explanation = fields.String(allow_none=True)
    hints = fields.List(fields.String())

    # Metadata
    question_metadata = fields.Dict()
    tags = fields.List(fields.String())


class QuestionResponseSchema(Schema):
    """Schema for question API responses."""

    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    evaluation_id = fields.Integer()

    # Question content
    question_text = fields.String()
    question_type = fields.String()
    difficulty_level = fields.String()
    difficulty_score = fields.Float()
    points = fields.Float()
    order_index = fields.Integer()

    # Question data
    question_data = fields.Dict()

    # Settings
    is_required = fields.Boolean()
    explanation = fields.String()
    hints = fields.List(fields.String())

    # Metadata
    question_metadata = fields.Dict()
    tags = fields.List(fields.String())

    # Timestamps
    created_at = fields.DateTime(format="iso", dump_only=True)
    updated_at = fields.DateTime(format="iso", dump_only=True)


class EvaluationAttemptResponseSchema(Schema):
    """Schema for evaluation attempt API responses."""

    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    evaluation_id = fields.Integer()
    user_id = fields.Integer()

    # Attempt details
    attempt_number = fields.Integer()
    status = fields.String()

    # Timing
    started_at = fields.DateTime(format="iso")
    completed_at = fields.DateTime(format="iso")
    time_spent_minutes = fields.Integer()

    # Scoring
    total_questions = fields.Integer()
    questions_answered = fields.Integer()
    total_points = fields.Float()
    score_earned = fields.Float()
    percentage_score = fields.Float()
    passed = fields.Boolean()

    # Settings snapshot
    time_limit_minutes = fields.Integer()
    passing_score = fields.Float()

    # Additional data
    attempt_metadata = fields.Dict()

    # Computed properties
    duration_display = fields.String(dump_only=True)
    is_completed = fields.Boolean(dump_only=True)
    is_in_progress = fields.Boolean(dump_only=True)

    # Related data (optional)
    user_name = fields.String(dump_only=True)
    evaluation_title = fields.String(dump_only=True)

    # Timestamps
    created_at = fields.DateTime(format="iso", dump_only=True)
    updated_at = fields.DateTime(format="iso", dump_only=True)


class QuestionResponseSaveSchema(Schema):
    """Schema for saving question responses."""

    question_id = fields.Integer(required=True, error_messages={"required": "Question ID is required"})
    response_data = fields.Dict(required=True, error_messages={"required": "Response data is required"})
    time_spent_seconds = fields.Integer(validate=validate.Range(min=0), missing=0)

    @pre_load
    def validate_response_data(self, data, **kwargs):
        """Basic validation of response_data structure."""
        response_data = data.get("response_data", {})

        if not response_data:
            raise ValidationError("Response data cannot be empty")

        return data


class EvaluationListQuerySchema(Schema):
    """Schema for filtering evaluations."""

    status = fields.String(validate=validate.OneOf([s.value for s in EvaluationStatus]))
    course_id = fields.Integer()
    program_id = fields.Integer()
    search = fields.String(validate=validate.Length(max=100))

    # Pagination
    page = fields.Integer(validate=validate.Range(min=1), missing=1)
    per_page = fields.Integer(validate=validate.Range(min=1, max=100), missing=20)

    # Sorting
    sort_by = fields.String(
        validate=validate.OneOf(["title", "created_at", "updated_at", "status"]), missing="created_at"
    )
    sort_order = fields.String(validate=validate.OneOf(["asc", "desc"]), missing="desc")

    # Filters
    is_available = fields.Boolean()
    created_by = fields.Integer()
    has_attempts = fields.Boolean()

    # Date filters
    created_after = fields.DateTime(format="iso")
    created_before = fields.DateTime(format="iso")
    available_after = fields.DateTime(format="iso")
    available_before = fields.DateTime(format="iso")


class EvaluationStatisticsSchema(Schema):
    """Schema for evaluation statistics responses."""

    evaluation_id = fields.Integer()
    evaluation_title = fields.String()

    # Attempt statistics
    total_attempts = fields.Integer()
    unique_users = fields.Integer()
    completion_rate = fields.Float()
    average_score = fields.Float()
    pass_rate = fields.Float()

    # Time statistics
    average_time_minutes = fields.Float()
    min_time_minutes = fields.Integer()
    max_time_minutes = fields.Integer()

    # Question statistics
    total_questions = fields.Integer()
    average_questions_answered = fields.Float()

    # Score distribution
    score_distribution = fields.Dict()

    # Question performance
    question_performance = fields.List(fields.Dict())

    # Recent attempts
    recent_attempts = fields.List(fields.Nested(EvaluationAttemptResponseSchema))

    # Metadata
    last_updated = fields.DateTime(format="iso")

    @post_dump
    def format_statistics(self, data, **kwargs):
        """Format statistics for better readability."""
        # Format percentages
        if "completion_rate" in data:
            data["completion_rate"] = round(data["completion_rate"], 2)
        if "pass_rate" in data:
            data["pass_rate"] = round(data["pass_rate"], 2)
        if "average_score" in data:
            data["average_score"] = round(data["average_score"], 2)
        if "average_time_minutes" in data:
            data["average_time_minutes"] = round(data["average_time_minutes"], 1)

        return data


# Additional utility schemas


class BulkQuestionCreateSchema(Schema):
    """Schema for creating multiple questions at once."""

    questions = fields.List(
        fields.Nested(QuestionCreateSchema), required=True, validate=validate.Length(min=1, max=100)
    )


class QuestionBankImportSchema(Schema):
    """Schema for importing questions from question bank."""

    question_bank_ids = fields.List(fields.Integer(), required=True, validate=validate.Length(min=1, max=50))
    randomize_order = fields.Boolean(missing=False)


class EvaluationDuplicateSchema(Schema):
    """Schema for duplicating an evaluation."""

    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    course_id = fields.Integer(allow_none=True)
    program_id = fields.Integer(allow_none=True)
    include_questions = fields.Boolean(missing=True)
    status = fields.String(
        validate=validate.OneOf([s.value for s in EvaluationStatus]), missing=EvaluationStatus.DRAFT.value
    )
