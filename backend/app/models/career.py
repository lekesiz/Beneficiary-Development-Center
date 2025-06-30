"""
Career Intelligence System Models
For Bilan de Compétence Platform
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Float, JSON, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum
from datetime import datetime

class CareerStatus(enum.Enum):
    EXPLORING = "exploring"
    PLANNING = "planning"
    TRANSITIONING = "transitioning"
    ESTABLISHED = "established"
    ADVANCING = "advancing"

class MarketDataSource(enum.Enum):
    GOVERNMENT = "government"
    INDUSTRY = "industry"
    SURVEY = "survey"
    AI_PREDICTION = "ai_prediction"

class OpportunityStatus(enum.Enum):
    ACTIVE = "active"
    SAVED = "saved"
    APPLIED = "applied"
    REJECTED = "rejected"
    EXPIRED = "expired"

class JobMarketData(BaseModel):
    __tablename__ = 'job_market_data'
    
    # Job Information
    job_title = Column(String(200), nullable=False)
    industry = Column(String(100), nullable=False)
    location = Column(String(100))
    
    # Market Metrics
    average_salary_min = Column(Float)
    average_salary_max = Column(Float)
    salary_currency = Column(String(3), default='EUR')
    job_openings_count = Column(Integer)
    growth_rate = Column(Float)  # Percentage
    
    # Demand Indicators
    demand_level = Column(String(50))  # high, medium, low
    future_outlook = Column(String(50))  # growing, stable, declining
    automation_risk = Column(Float)  # 0-100 percentage
    
    # Skills Data
    required_skills = Column(JSON)  # ["Python", "SQL", "Machine Learning"]
    preferred_skills = Column(JSON)
    emerging_skills = Column(JSON)
    
    # Source and Validity
    data_source = Column(Enum(MarketDataSource))
    source_name = Column(String(200))
    collected_date = Column(Date)
    valid_until = Column(Date)
    
    # Geographic Scope
    country_code = Column(String(2), default='FR')
    region = Column(String(100))
    is_remote_friendly = Column(Boolean, default=False)
    
    # Relationships
    career_paths = relationship("CareerPath", back_populates="target_market_data")

class CareerPath(BaseModel):
    __tablename__ = 'career_paths'
    
    # User Information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Current State
    current_job_title = Column(String(200))
    current_industry = Column(String(100))
    years_experience = Column(Integer)
    current_salary = Column(Float)
    career_status = Column(Enum(CareerStatus), default=CareerStatus.EXPLORING)
    
    # Target State
    target_job_title = Column(String(200))
    target_industry = Column(String(100))
    target_salary_min = Column(Float)
    target_salary_max = Column(Float)
    target_timeline_months = Column(Integer)
    
    # Market Data Link
    target_market_data_id = Column(Integer, ForeignKey('job_market_data.id'))
    
    # Progress Tracking
    progress_percentage = Column(Float, default=0.0)
    last_progress_update = Column(DateTime)
    estimated_completion = Column(Date)
    
    # Motivation and Context
    career_motivation = Column(Text)
    constraints = Column(JSON)  # ["location_bound", "no_travel", "part_time_only"]
    preferences = Column(JSON)  # ["remote_work", "startup_culture", "work_life_balance"]
    
    # AI Insights
    feasibility_score = Column(Float)  # 0-100
    recommended_path = Column(JSON)  # Step by step recommendations
    alternative_paths = Column(JSON)  # Alternative career options
    
    # Relationships
    user = relationship("User", backref="career_paths")
    target_market_data = relationship("JobMarketData", back_populates="career_paths")
    milestones = relationship("CareerMilestone", back_populates="career_path", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGapAnalysis", back_populates="career_path", cascade="all, delete-orphan")

class CareerMilestone(BaseModel):
    __tablename__ = 'career_milestones'
    
    # Basic Information
    career_path_id = Column(Integer, ForeignKey('career_paths.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Timeline
    target_date = Column(Date)
    completed_date = Column(Date)
    
    # Type and Category
    milestone_type = Column(String(50))  # skill, certification, experience, network
    category = Column(String(100))
    
    # Requirements
    requirements = Column(JSON)  # What needs to be done
    success_criteria = Column(JSON)  # How to measure completion
    
    # Status
    status = Column(String(50), default='pending')  # pending, in_progress, completed, skipped
    progress_percentage = Column(Float, default=0.0)
    
    # Evidence
    evidence_documents = Column(JSON)  # Links or references to proof
    verified_by = Column(Integer, ForeignKey('users.id'))
    verified_at = Column(DateTime)
    
    # Relationships
    career_path = relationship("CareerPath", back_populates="milestones")
    verifier = relationship("User", foreign_keys=[verified_by])

class SkillGapAnalysis(BaseModel):
    __tablename__ = 'skill_gap_analyses'
    
    # Basic Information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    career_path_id = Column(Integer, ForeignKey('career_paths.id'))
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Current vs Required Analysis
    current_skills = Column(JSON)  # {"Python": 7, "SQL": 5, "Leadership": 6}
    required_skills = Column(JSON)  # {"Python": 9, "SQL": 7, "Leadership": 8}
    skill_gaps = Column(JSON)  # {"Python": 2, "SQL": 2, "Leadership": 2}
    
    # Priority and Impact
    priority_skills = Column(JSON)  # Ordered list of skills to develop
    critical_gaps = Column(JSON)  # Skills that are blocking progress
    
    # Learning Recommendations
    recommended_courses = Column(JSON)
    recommended_certifications = Column(JSON)
    recommended_projects = Column(JSON)
    estimated_learning_hours = Column(Integer)
    
    # Market Alignment
    market_demand_alignment = Column(Float)  # 0-100 score
    competitive_advantage_skills = Column(JSON)  # Skills that set apart
    
    # Progress Tracking
    skills_improved = Column(JSON)  # Skills that have been developed
    last_update = Column(DateTime)
    
    # Relationships
    user = relationship("User", backref="skill_gap_analyses")
    career_path = relationship("CareerPath", back_populates="skill_gaps")

class JobOpportunity(BaseModel):
    __tablename__ = 'job_opportunities'
    
    # Job Details
    job_title = Column(String(200), nullable=False)
    company_name = Column(String(200))
    location = Column(String(200))
    job_type = Column(String(50))  # full_time, part_time, contract, freelance
    
    # Description
    job_description = Column(Text)
    requirements = Column(JSON)
    nice_to_have = Column(JSON)
    
    # Compensation
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(3), default='EUR')
    benefits = Column(JSON)
    
    # Application Details
    application_url = Column(String(500))
    application_deadline = Column(Date)
    contact_person = Column(String(200))
    contact_email = Column(String(255))
    
    # Source
    source = Column(String(100))  # linkedin, indeed, company_website, referral
    source_url = Column(String(500))
    posted_date = Column(Date)
    
    # Matching
    match_score = Column(Float)  # 0-100 based on user profile
    matching_skills = Column(JSON)
    missing_skills = Column(JSON)
    
    # User Interaction
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum(OpportunityStatus), default=OpportunityStatus.ACTIVE)
    saved_at = Column(DateTime)
    applied_at = Column(DateTime)
    notes = Column(Text)
    
    # AI Insights
    success_probability = Column(Float)  # 0-100
    salary_negotiation_range = Column(JSON)
    interview_tips = Column(JSON)
    
    # Relationships
    user = relationship("User", backref="job_opportunities")

class CareerDocument(BaseModel):
    """Documents related to career development"""
    __tablename__ = 'career_documents'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    document_type = Column(String(50))  # resume, cover_letter, portfolio, certification
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    
    # Version Control
    version = Column(Integer, default=1)
    is_current = Column(Boolean, default=True)
    
    # Metadata
    language = Column(String(2), default='fr')
    keywords = Column(JSON)
    ats_score = Column(Float)  # ATS compatibility score
    
    # Usage Tracking
    times_used = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship("User", backref="career_documents")