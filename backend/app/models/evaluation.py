"""
Evaluation models for the BDC application
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import TenantBaseModel, TimestampMixin


class EvaluationStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"


class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    MATCHING = "matching"
    ORDERING = "ordering"
    FILL_IN_BLANK = "fill_in_blank"


class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class AttemptStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    TIMED_OUT = "timed_out"


class Evaluation(TenantBaseModel):
    """Evaluation model for assessments and tests"""
    __tablename__ = 'evaluations'

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    
    # Relationships
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=True)
    program_id = Column(Integer, ForeignKey('programs.id'), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Settings
    status = Column(SQLEnum(EvaluationStatus), default=EvaluationStatus.DRAFT, nullable=False)
    total_questions = Column(Integer, default=0)
    total_points = Column(Float, default=0.0)
    passing_score = Column(Float, default=70.0)
    time_limit_minutes = Column(Integer)  # NULL means no time limit
    max_attempts = Column(Integer, default=1)
    shuffle_questions = Column(Boolean, default=False)
    show_results_immediately = Column(Boolean, default=True)
    allow_review = Column(Boolean, default=True)
    is_adaptive = Column(Boolean, default=False)  # AI-powered adaptive mode
    
    # Dates
    available_from = Column(DateTime)
    available_until = Column(DateTime)
    
    # Metadata
    evaluation_metadata = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    
    # Computed properties
    @property
    def is_available(self):
        """Check if evaluation is currently available"""
        now = datetime.utcnow()
        if self.status != EvaluationStatus.ACTIVE:
            return False
        if self.available_from and now < self.available_from:
            return False
        if self.available_until and now > self.available_until:
            return False
        return True
    
    @property
    def duration_display(self):
        """Display time limit in human readable format"""
        if not self.time_limit_minutes:
            return "Unlimited"
        hours = self.time_limit_minutes // 60
        minutes = self.time_limit_minutes % 60
        if hours:
            return f"{hours}h {minutes}m" if minutes else f"{hours}h"
        return f"{minutes}m"
    
    # Relationships
    course = relationship("Course", back_populates="evaluations")
    program = relationship("Program", back_populates="evaluations")
    creator = relationship("User", foreign_keys=[created_by])
    questions = relationship("Question", back_populates="evaluation", cascade="all, delete-orphan")
    attempts = relationship("EvaluationAttempt", back_populates="evaluation", cascade="all, delete-orphan")

    def to_dict(self, exclude=None, include_related=False):
        """Convert to dictionary."""
        exclude = exclude or []
        data = {}
        
        # Add all columns
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if hasattr(value, 'value'):  # Enum
                    data[column.name] = value.value
                elif hasattr(value, 'isoformat'):  # DateTime
                    data[column.name] = value.isoformat()
                else:
                    data[column.name] = value
        
        # Add computed properties
        data['is_available'] = self.is_available
        data['duration_display'] = self.duration_display
        
        # Add related data if requested
        if include_related:
            if self.course:
                data['course_title'] = self.course.title
            if self.program:
                data['program_title'] = self.program.title
            if self.creator:
                data['creator_name'] = self.creator.full_name
        
        # Convert UUID to string
        if 'uuid' in data:
            data['uuid'] = str(data['uuid'])
        
        return data

    def __repr__(self):
        return f"<Evaluation(id={self.id}, title='{self.title}', status='{self.status}')>"


class Question(TenantBaseModel):
    """Question model for evaluation questions"""
    __tablename__ = 'questions'

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    evaluation_id = Column(Integer, ForeignKey('evaluations.id'), nullable=False)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    difficulty_level = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    difficulty_score = Column(Float, default=0.0)  # IRT difficulty parameter (-3 to 3)
    points = Column(Float, default=1.0)
    order_index = Column(Integer, default=0)
    
    # Question data (options, correct answers, etc.)
    question_data = Column(JSON, default=dict)  # Flexible data structure for different question types
    
    # Settings
    is_required = Column(Boolean, default=True)
    explanation = Column(Text)  # Explanation shown after answering
    hints = Column(JSON, default=list)
    
    # Metadata
    question_metadata = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    
    # Relationships
    evaluation = relationship("Evaluation", back_populates="questions")
    responses = relationship("QuestionResponse", back_populates="question", cascade="all, delete-orphan")

    def to_dict(self, exclude=None):
        """Convert to dictionary."""
        exclude = exclude or []
        data = {}
        
        # Add all columns
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if hasattr(value, 'value'):  # Enum
                    data[column.name] = value.value
                elif hasattr(value, 'isoformat'):  # DateTime
                    data[column.name] = value.isoformat()
                else:
                    data[column.name] = value
        
        # Convert UUID to string
        if 'uuid' in data:
            data['uuid'] = str(data['uuid'])
        
        return data

    def __repr__(self):
        return f"<Question(id={self.id}, type='{self.question_type}', points={self.points})>"


class EvaluationAttempt(TenantBaseModel):
    """User attempts at evaluations"""
    __tablename__ = 'evaluation_attempts'

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    evaluation_id = Column(Integer, ForeignKey('evaluations.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Attempt details
    attempt_number = Column(Integer, default=1)
    status = Column(SQLEnum(AttemptStatus), default=AttemptStatus.IN_PROGRESS)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    time_spent_minutes = Column(Integer)
    
    # Scoring
    total_questions = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    total_points = Column(Float, default=0.0)
    score_earned = Column(Float, default=0.0)
    percentage_score = Column(Float, default=0.0)
    passed = Column(Boolean, default=False)
    
    # Settings at time of attempt (snapshot)
    time_limit_minutes = Column(Integer)
    passing_score = Column(Float)
    
    # Additional data
    attempt_metadata = Column(JSON, default=dict)
    
    @property
    def duration_display(self):
        """Display time spent in human readable format"""
        if not self.time_spent_minutes:
            return "0m"
        hours = self.time_spent_minutes // 60
        minutes = self.time_spent_minutes % 60
        if hours:
            return f"{hours}h {minutes}m" if minutes else f"{hours}h"
        return f"{minutes}m"
    
    @property
    def is_completed(self):
        """Check if attempt is completed"""
        return self.status == AttemptStatus.COMPLETED
    
    @property
    def is_in_progress(self):
        """Check if attempt is in progress"""
        return self.status == AttemptStatus.IN_PROGRESS
    
    # Relationships
    evaluation = relationship("Evaluation", back_populates="attempts")
    user = relationship("User")
    # beneficiary = relationship("Beneficiary", back_populates="evaluation_attempts")
    responses = relationship("QuestionResponse", back_populates="attempt", cascade="all, delete-orphan")

    def to_dict(self, exclude=None, include_related=False):
        """Convert to dictionary."""
        exclude = exclude or []
        data = {}
        
        # Add all columns
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if hasattr(value, 'value'):  # Enum
                    data[column.name] = value.value
                elif hasattr(value, 'isoformat'):  # DateTime
                    data[column.name] = value.isoformat()
                else:
                    data[column.name] = value
        
        # Add computed properties
        data['duration_display'] = self.duration_display
        data['is_completed'] = self.is_completed
        data['is_in_progress'] = self.is_in_progress
        
        # Add related data if requested
        if include_related:
            if self.user:
                data['user_name'] = self.user.full_name
            if self.evaluation:
                data['evaluation_title'] = self.evaluation.title
        
        # Convert UUID to string
        if 'uuid' in data:
            data['uuid'] = str(data['uuid'])
        
        return data

    def __repr__(self):
        return f"<EvaluationAttempt(id={self.id}, user_id={self.user_id}, score={self.percentage_score}%)>"


class QuestionResponse(TenantBaseModel):
    """User responses to questions"""
    __tablename__ = 'question_responses'

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    attempt_id = Column(Integer, ForeignKey('evaluation_attempts.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    
    # Response data
    response_data = Column(JSON, default=dict)  # Flexible structure for different answer types
    is_correct = Column(Boolean)
    points_earned = Column(Float, default=0.0)
    
    # Timing
    time_spent_seconds = Column(Integer)
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # AI feedback
    ai_feedback = Column(Text)
    ai_score = Column(Float)
    
    # Metadata
    response_metadata = Column(JSON, default=dict)
    
    # Relationships
    attempt = relationship("EvaluationAttempt", back_populates="responses")
    question = relationship("Question", back_populates="responses")

    def to_dict(self, exclude=None):
        """Convert to dictionary."""
        exclude = exclude or []
        data = {}
        
        # Add all columns
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if hasattr(value, 'value'):  # Enum
                    data[column.name] = value.value
                elif hasattr(value, 'isoformat'):  # DateTime
                    data[column.name] = value.isoformat()
                else:
                    data[column.name] = value
        
        # Convert UUID to string
        if 'uuid' in data:
            data['uuid'] = str(data['uuid'])
        
        return data

    def __repr__(self):
        return f"<QuestionResponse(id={self.id}, question_id={self.question_id}, correct={self.is_correct})>"


class QuestionBank(TenantBaseModel):
    """Question bank for reusable questions"""
    __tablename__ = 'question_banks'

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Categorization
    subject = Column(String(100))
    topic = Column(String(100))
    difficulty_level = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    points = Column(Float, default=1.0)
    
    # Question data (options, correct answers, etc.)
    question_data = Column(JSON, default=dict)
    explanation = Column(Text)
    hints = Column(JSON, default=list)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_metadata = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    def to_dict(self, exclude=None):
        """Convert to dictionary."""
        exclude = exclude or []
        data = {}
        
        # Add all columns
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if hasattr(value, 'value'):  # Enum
                    data[column.name] = value.value
                elif hasattr(value, 'isoformat'):  # DateTime
                    data[column.name] = value.isoformat()
                else:
                    data[column.name] = value
        
        # Convert UUID to string
        if 'uuid' in data:
            data['uuid'] = str(data['uuid'])
        
        return data

    def __repr__(self):
        return f"<QuestionBank(id={self.id}, subject='{self.subject}', type='{self.question_type}')>"