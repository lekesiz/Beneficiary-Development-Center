"""
Advanced Learning System Models
For Bilan de Compétence Platform - Personalized Learning
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Float, JSON, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum
from datetime import datetime

class ContentType(enum.Enum):
    ARTICLE = "article"
    VIDEO = "video"
    COURSE = "course"
    EXERCISE = "exercise"
    SIMULATION = "simulation"
    ASSESSMENT = "assessment"
    WEBINAR = "webinar"
    PODCAST = "podcast"

class LearningPathStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class MentorshipStatus(enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SimulationType(enum.Enum):
    INTERVIEW = "interview"
    PRESENTATION = "presentation"
    NEGOTIATION = "negotiation"
    PROBLEM_SOLVING = "problem_solving"
    TEAM_COLLABORATION = "team_collaboration"
    CUSTOMER_SERVICE = "customer_service"

class AdvancedLearningContent(BaseModel):
    __tablename__ = 'advanced_learning_contents'
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    
    # Content Details
    content_url = Column(String(500))
    content_data = Column(JSON)  # For embedded content
    duration_minutes = Column(Integer)
    difficulty_level = Column(Integer)  # 1-5
    
    # Categorization
    skill_categories = Column(JSON)  # ["Python", "Data Analysis", "Communication"]
    tags = Column(JSON)
    language = Column(String(2), default='fr')
    
    # Learning Objectives
    learning_objectives = Column(JSON)
    prerequisites = Column(JSON)
    target_audience = Column(String(200))
    
    # Quality Metrics
    quality_score = Column(Float)  # 0-100
    relevance_score = Column(Float)
    engagement_score = Column(Float)
    completion_rate = Column(Float)
    average_rating = Column(Float)
    
    # Provider Information
    provider_name = Column(String(200))
    provider_url = Column(String(500))
    is_free = Column(Boolean, default=True)
    price = Column(Float)
    
    # AI Metadata
    embedding_vector = Column(JSON)  # For content similarity
    auto_generated_summary = Column(Text)
    key_concepts = Column(JSON)
    
    # Relationships
    learning_paths = relationship("PathContent", back_populates="content")
    recommendations = relationship("ContentRecommendation", back_populates="content")
    progress_records = relationship("ContentProgress", back_populates="content")

class PersonalizedLearningPath(BaseModel):
    __tablename__ = 'personalized_learning_paths'
    
    # Basic Information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Path Configuration
    status = Column(Enum(LearningPathStatus), default=LearningPathStatus.DRAFT)
    start_date = Column(Date)
    target_end_date = Column(Date)
    actual_end_date = Column(Date)
    
    # Goals and Objectives
    primary_goal = Column(String(500))
    learning_objectives = Column(JSON)
    target_skills = Column(JSON)
    
    # Personalization Parameters
    learning_style = Column(String(50))  # visual, auditory, kinesthetic, reading
    time_availability = Column(Integer)  # hours per week
    preferred_content_types = Column(JSON)
    preferred_duration = Column(String(50))  # micro, short, medium, long
    
    # AI Configuration
    adaptation_enabled = Column(Boolean, default=True)
    difficulty_adjustment = Column(Boolean, default=True)
    content_diversity = Column(Float, default=0.7)  # 0-1 scale
    
    # Progress Tracking
    overall_progress = Column(Float, default=0.0)
    skills_acquired = Column(JSON)
    milestones_completed = Column(Integer, default=0)
    total_time_spent = Column(Integer, default=0)  # minutes
    
    # Performance Metrics
    average_score = Column(Float)
    completion_rate = Column(Float)
    engagement_level = Column(Float)
    
    # Relationships
    user = relationship("User", backref="personalized_learning_paths")
    contents = relationship("PathContent", back_populates="path", cascade="all, delete-orphan")
    milestones = relationship("AdvancedLearningMilestone", back_populates="path", cascade="all, delete-orphan")

class PathContent(BaseModel):
    __tablename__ = 'path_contents'
    
    # Relationships
    path_id = Column(Integer, ForeignKey('personalized_learning_paths.id'), nullable=False)
    content_id = Column(Integer, ForeignKey('advanced_learning_contents.id'), nullable=False)
    
    # Ordering and Structure
    order_index = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    unlock_condition = Column(JSON)  # Prerequisites within the path
    
    # Scheduling
    scheduled_date = Column(Date)
    deadline = Column(Date)
    reminder_sent = Column(Boolean, default=False)
    
    # Progress
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime)
    score = Column(Float)
    time_spent = Column(Integer)  # minutes
    
    # Adaptive Learning
    difficulty_override = Column(Integer)  # Override content difficulty for this user
    skip_allowed = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    path = relationship("PersonalizedLearningPath", back_populates="contents")
    content = relationship("AdvancedLearningContent", back_populates="learning_paths")

class AdvancedLearningMilestone(BaseModel):
    __tablename__ = 'advanced_learning_milestones'
    
    # Basic Information
    path_id = Column(Integer, ForeignKey('personalized_learning_paths.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Milestone Configuration
    order_index = Column(Integer, nullable=False)
    required_contents = Column(JSON)  # List of content IDs
    required_score = Column(Float)  # Minimum score to pass
    
    # Rewards
    badge_id = Column(String(100))
    certificate_template = Column(String(100))
    points_awarded = Column(Integer)
    
    # Progress
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime)
    
    # Relationships
    path = relationship("PersonalizedLearningPath", back_populates="milestones")

class MentorshipMatch(BaseModel):
    __tablename__ = 'mentorship_matches'
    
    # Participants
    mentee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    mentor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Match Details
    status = Column(Enum(MentorshipStatus), default=MentorshipStatus.PENDING)
    match_score = Column(Float)  # AI-calculated compatibility score
    match_reasons = Column(JSON)  # Why they were matched
    
    # Timeline
    requested_date = Column(DateTime, default=datetime.utcnow)
    matched_date = Column(DateTime)
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Configuration
    meeting_frequency = Column(String(50))  # weekly, biweekly, monthly
    meeting_duration = Column(Integer)  # minutes
    communication_preferences = Column(JSON)  # ["video", "chat", "email"]
    
    # Goals and Focus
    mentorship_goals = Column(JSON)
    focus_areas = Column(JSON)
    success_metrics = Column(JSON)
    
    # Progress
    sessions_completed = Column(Integer, default=0)
    goals_achieved = Column(JSON)
    
    # Feedback
    mentee_satisfaction = Column(Float)
    mentor_satisfaction = Column(Float)
    would_recommend = Column(Boolean)
    
    # Relationships
    mentee = relationship("User", foreign_keys=[mentee_id], backref="mentorships_as_mentee")
    mentor = relationship("User", foreign_keys=[mentor_id], backref="mentorships_as_mentor")
    sessions = relationship("MentorshipSession", back_populates="match", cascade="all, delete-orphan")

class MentorshipSession(BaseModel):
    __tablename__ = 'mentorship_sessions'
    
    # Basic Information
    match_id = Column(Integer, ForeignKey('mentorship_matches.id'), nullable=False)
    session_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer)
    
    # Session Details
    topics_discussed = Column(JSON)
    key_insights = Column(Text)
    action_items = Column(JSON)
    
    # Resources Shared
    resources_shared = Column(JSON)
    
    # Feedback
    mentee_notes = Column(Text)
    mentor_notes = Column(Text)
    session_rating = Column(Integer)  # 1-5
    
    # Next Steps
    next_session_date = Column(DateTime)
    homework_assigned = Column(JSON)
    
    # Relationships
    match = relationship("MentorshipMatch", back_populates="sessions")

class JobSimulation(BaseModel):
    __tablename__ = 'job_simulations'
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    simulation_type = Column(Enum(SimulationType), nullable=False)
    
    # Job Context
    job_role = Column(String(200))
    industry = Column(String(100))
    company_size = Column(String(50))  # startup, SME, enterprise
    
    # Simulation Configuration
    scenario_data = Column(JSON)  # Detailed scenario setup
    difficulty_level = Column(Integer)  # 1-5
    duration_minutes = Column(Integer)
    
    # Skills Assessed
    skills_tested = Column(JSON)
    competencies_measured = Column(JSON)
    
    # Scoring Configuration
    scoring_rubric = Column(JSON)
    passing_score = Column(Float)
    
    # AI Configuration
    ai_evaluator_enabled = Column(Boolean, default=True)
    ai_feedback_enabled = Column(Boolean, default=True)
    
    # Relationships
    attempts = relationship("SimulationAttempt", back_populates="simulation")

class SimulationAttempt(BaseModel):
    __tablename__ = 'simulation_attempts'
    
    # Basic Information
    simulation_id = Column(Integer, ForeignKey('job_simulations.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Attempt Details
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    time_spent = Column(Integer)  # minutes
    
    # User Responses
    responses = Column(JSON)  # All user actions/responses
    decisions_made = Column(JSON)
    
    # Scoring
    total_score = Column(Float)
    skill_scores = Column(JSON)  # Score per skill
    
    # AI Evaluation
    ai_feedback = Column(JSON)
    strengths_identified = Column(JSON)
    areas_for_improvement = Column(JSON)
    
    # Performance Metrics
    accuracy = Column(Float)
    response_time_avg = Column(Float)
    confidence_level = Column(Float)
    
    # Outcome
    passed = Column(Boolean)
    certificate_issued = Column(Boolean, default=False)
    
    # Relationships
    simulation = relationship("JobSimulation", back_populates="attempts")
    user = relationship("User", backref="simulation_attempts")

class ContentRecommendation(BaseModel):
    __tablename__ = 'content_recommendations'
    
    # Basic Information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_id = Column(Integer, ForeignKey('advanced_learning_contents.id'), nullable=False)
    
    # Recommendation Details
    recommendation_score = Column(Float)  # 0-100
    recommendation_reason = Column(JSON)  # Why recommended
    recommendation_type = Column(String(50))  # skill_gap, interest, trending
    
    # Context
    based_on = Column(JSON)  # What triggered this recommendation
    generated_date = Column(DateTime, default=datetime.utcnow)
    expires_date = Column(DateTime)
    
    # User Interaction
    viewed = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    feedback = Column(String(50))  # helpful, not_helpful, wrong_level
    
    # Relationships
    user = relationship("User", backref="content_recommendations")
    content = relationship("AdvancedLearningContent", back_populates="recommendations")

class ContentProgress(BaseModel):
    __tablename__ = 'content_progress'
    
    # Basic Information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_id = Column(Integer, ForeignKey('advanced_learning_contents.id'), nullable=False)
    
    # Progress Tracking
    progress_percentage = Column(Float, default=0.0)
    last_accessed = Column(DateTime)
    total_time_spent = Column(Integer, default=0)  # minutes
    
    # Completion
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime)
    
    # Performance
    score = Column(Float)
    attempts = Column(Integer, default=0)
    best_score = Column(Float)
    
    # Bookmarking
    bookmarks = Column(JSON)  # Positions/sections bookmarked
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", backref="content_progress")
    content = relationship("AdvancedLearningContent", back_populates="progress_records")