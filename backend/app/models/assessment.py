"""
360° Assessment System Models
For Bilan de Compétence Platform
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Float, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum
from datetime import datetime

class AssessmentType(enum.Enum):
    SELF = "self"
    PEER = "peer"
    MANAGER = "manager"
    CUSTOMER = "customer"
    SUBORDINATE = "subordinate"
    EXTERNAL = "external"

class AssessmentStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class QuestionType(enum.Enum):
    RATING = "rating"
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    RANKING = "ranking"
    MATRIX = "matrix"

class Assessment(BaseModel):
    __tablename__ = 'assessments'
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    assessment_type = Column(Enum(AssessmentType), nullable=False)
    status = Column(Enum(AssessmentStatus), default=AssessmentStatus.DRAFT)
    
    # Relationships
    beneficiary_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Assessment Configuration
    is_anonymous = Column(Boolean, default=False)
    deadline = Column(DateTime)
    reminder_frequency = Column(Integer, default=7)  # days
    max_responses = Column(Integer)  # null means unlimited
    
    # Scoring Configuration
    use_weighted_scoring = Column(Boolean, default=False)
    show_results_to_beneficiary = Column(Boolean, default=True)
    
    # Metadata
    completion_rate = Column(Float, default=0.0)
    average_score = Column(Float)
    
    # Relationships
    beneficiary = relationship("User", foreign_keys=[beneficiary_id], backref="assessments_received")
    created_by = relationship("User", foreign_keys=[created_by_id], backref="assessments_created")
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    invitations = relationship("AssessmentInvitation", back_populates="assessment", cascade="all, delete-orphan")
    responses = relationship("AssessmentResponse", back_populates="assessment", cascade="all, delete-orphan")
    
    def calculate_completion_rate(self):
        """Calculate the completion rate of the assessment"""
        if not self.invitations:
            return 0.0
        completed = sum(1 for inv in self.invitations if inv.status == 'completed')
        return (completed / len(self.invitations)) * 100

class AssessmentQuestion(BaseModel):
    __tablename__ = 'assessment_questions'
    
    # Basic Information
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), default=QuestionType.RATING)
    skill_category = Column(String(100))
    competency_id = Column(Integer, ForeignKey('competencies.id'))
    
    # Question Configuration
    order_index = Column(Integer, default=0)
    is_required = Column(Boolean, default=True)
    weight = Column(Float, default=1.0)  # For weighted scoring
    
    # Rating Configuration
    min_rating = Column(Integer, default=1)
    max_rating = Column(Integer, default=5)
    rating_labels = Column(JSON)  # {"1": "Poor", "5": "Excellent"}
    
    # Multiple Choice Configuration
    options = Column(JSON)  # [{"value": "a", "label": "Option A", "is_correct": true}]
    allow_multiple = Column(Boolean, default=False)
    
    # Help Text
    help_text = Column(Text)
    example_answer = Column(Text)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    responses = relationship("AssessmentQuestionResponse", back_populates="question", cascade="all, delete-orphan")
    competency = relationship("Competency", backref="assessment_questions")

class AssessmentInvitation(BaseModel):
    __tablename__ = 'assessment_invitations'
    
    # Basic Information
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    evaluator_email = Column(String(255), nullable=False)
    evaluator_name = Column(String(255))
    evaluator_role = Column(Enum(AssessmentType), nullable=False)
    
    # Access Control
    access_token = Column(String(100), unique=True, nullable=False)
    token_expiry = Column(DateTime)
    
    # Status Tracking
    status = Column(String(50), default='pending')  # pending, sent, opened, completed, expired
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Reminder Tracking
    reminders_sent = Column(Integer, default=0)
    last_reminder_at = Column(DateTime)
    
    # Custom Message
    custom_message = Column(Text)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="invitations")
    response = relationship("AssessmentResponse", back_populates="invitation", uselist=False)
    
    def generate_public_url(self, base_url):
        """Generate the public URL for this invitation"""
        return f"{base_url}/public/assessment/{self.access_token}"

class AssessmentResponse(BaseModel):
    __tablename__ = 'assessment_responses'
    
    # Basic Information
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    invitation_id = Column(Integer, ForeignKey('assessment_invitations.id'))
    respondent_id = Column(Integer, ForeignKey('users.id'))  # null for anonymous
    
    # Response Metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    time_spent = Column(Integer)  # seconds
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    
    # Scoring
    total_score = Column(Float)
    weighted_score = Column(Float)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="responses")
    invitation = relationship("AssessmentInvitation", back_populates="response")
    respondent = relationship("User", backref="assessment_responses_given")
    question_responses = relationship("AssessmentQuestionResponse", back_populates="assessment_response", cascade="all, delete-orphan")

class AssessmentQuestionResponse(BaseModel):
    __tablename__ = 'assessment_question_responses'
    
    # Basic Information
    assessment_response_id = Column(Integer, ForeignKey('assessment_responses.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('assessment_questions.id'), nullable=False)
    
    # Response Data
    rating_value = Column(Integer)  # For rating questions
    text_value = Column(Text)  # For text questions
    selected_options = Column(JSON)  # For multiple choice ["a", "b"]
    ranking_order = Column(JSON)  # For ranking questions [1, 3, 2, 4]
    
    # Scoring
    score = Column(Float)
    weighted_score = Column(Float)
    
    # Metadata
    time_spent = Column(Integer)  # seconds on this question
    
    # Relationships
    assessment_response = relationship("AssessmentResponse", back_populates="question_responses")
    question = relationship("AssessmentQuestion", back_populates="responses")

class Competency(BaseModel):
    """Competency model for skill categorization"""
    __tablename__ = 'competencies'
    
    name = Column(String(100), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('competencies.id'))
    
    # Hierarchy (self-referential)
    # Parent competency will have children, children will have parent
    
    # Metadata
    is_technical = Column(Boolean, default=False)
    is_behavioral = Column(Boolean, default=False)
    industry_specific = Column(Boolean, default=False)