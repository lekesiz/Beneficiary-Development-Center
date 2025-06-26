"""
Learning Path model for personalized learning plans
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import TenantBaseModel, TimestampMixin


class LearningPathStatus(Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MilestoneStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class LearningPath(TenantBaseModel, TimestampMixin):
    """AI-generated personalized learning path based on evaluation performance"""

    __tablename__ = "learning_paths"

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    evaluation_attempt_id = Column(Integer, ForeignKey("evaluation_attempts.id"), nullable=False)

    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    objective = Column(Text)  # Main learning objective

    # Status and Acceptance
    status = Column(String(20), default=LearningPathStatus.PROPOSED.value, nullable=False)
    accepted_by_user = Column(Boolean, default=False, nullable=False)
    accepted_at = Column(DateTime)

    # Duration and Schedule
    duration_weeks = Column(Integer, default=4, nullable=False)
    estimated_hours_per_week = Column(Float, default=5.0, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    # AI-Generated Content
    ai_insights_summary = Column(JSON)  # Summary of insights used to generate the path
    learning_style = Column(String(50))  # visual, auditory, kinesthetic, reading
    difficulty_adjustment = Column(String(20))  # easy, balanced, challenging

    # Progress Tracking
    overall_progress = Column(Float, default=0.0)  # 0-100 percentage
    completed_milestones = Column(Integer, default=0)
    total_milestones = Column(Integer, default=0)

    # Metadata
    customization_notes = Column(Text)  # User's customization notes
    feedback = Column(Text)  # User feedback on the learning path
    rating = Column(Float)  # User rating 1-5

    # JSON Fields for Complex Data
    weekly_schedule = Column(JSON, default=dict)  # Detailed weekly schedule
    resources = Column(JSON, default=list)  # Recommended resources
    prerequisites = Column(JSON, default=list)  # Required knowledge/skills

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="learning_paths")
    evaluation = relationship("Evaluation", back_populates="learning_paths")
    evaluation_attempt = relationship("EvaluationAttempt", back_populates="learning_paths")
    milestones = relationship("LearningMilestone", back_populates="learning_path", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "user_id": self.user_id,
            "evaluation_id": self.evaluation_id,
            "evaluation_attempt_id": self.evaluation_attempt_id,
            "title": self.title,
            "description": self.description,
            "objective": self.objective,
            "status": self.status,
            "accepted_by_user": self.accepted_by_user,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "duration_weeks": self.duration_weeks,
            "estimated_hours_per_week": self.estimated_hours_per_week,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "ai_insights_summary": self.ai_insights_summary,
            "learning_style": self.learning_style,
            "difficulty_adjustment": self.difficulty_adjustment,
            "overall_progress": self.overall_progress,
            "completed_milestones": self.completed_milestones,
            "total_milestones": self.total_milestones,
            "weekly_schedule": self.weekly_schedule,
            "resources": self.resources,
            "prerequisites": self.prerequisites,
            "customization_notes": self.customization_notes,
            "feedback": self.feedback,
            "rating": self.rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "milestones": [m.to_dict() for m in self.milestones] if hasattr(self, "milestones") else [],
        }


class LearningMilestone(TenantBaseModel, TimestampMixin):
    """Individual milestone within a learning path"""

    __tablename__ = "learning_milestones"

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    # Relationships
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)

    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    objective = Column(Text)

    # Order and Timing
    order_index = Column(Integer, default=0, nullable=False)
    week_number = Column(Integer, nullable=False)
    estimated_hours = Column(Float, default=2.0, nullable=False)

    # Status and Progress
    status = Column(String(20), default=MilestoneStatus.PENDING.value, nullable=False)
    progress = Column(Float, default=0.0)  # 0-100 percentage
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Resources and Activities
    resources = Column(JSON, default=list)  # List of recommended resources
    activities = Column(JSON, default=list)  # Specific activities to complete
    assessment_criteria = Column(JSON, default=list)  # How to measure completion

    # Related Content
    related_courses = Column(JSON, default=list)  # Related course IDs
    related_topics = Column(JSON, default=list)  # Topic tags
    skill_focus = Column(String(100))  # Primary skill being developed

    # User Interaction
    user_notes = Column(Text)
    feedback = Column(Text)
    difficulty_rating = Column(Integer)  # 1-5 scale

    # Relationships
    learning_path = relationship("LearningPath", back_populates="milestones")
    progress_records = relationship("MilestoneProgress", back_populates="milestone")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "learning_path_id": self.learning_path_id,
            "title": self.title,
            "description": self.description,
            "objective": self.objective,
            "order_index": self.order_index,
            "week_number": self.week_number,
            "estimated_hours": self.estimated_hours,
            "status": self.status,
            "progress": self.progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "resources": self.resources,
            "activities": self.activities,
            "assessment_criteria": self.assessment_criteria,
            "related_courses": self.related_courses,
            "related_topics": self.related_topics,
            "skill_focus": self.skill_focus,
            "user_notes": self.user_notes,
            "feedback": self.feedback,
            "difficulty_rating": self.difficulty_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LearningPathUpdate(TenantBaseModel, TimestampMixin):
    """Suggested updates to learning paths based on student progress"""

    __tablename__ = "learning_path_updates"

    # Relationships
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    suggested_by_user_id = Column(Integer, ForeignKey("users.id"))  # Who suggested (if manual)

    # Update Type
    update_type = Column(
        String(50), nullable=False
    )  # 'add_milestone', 'reorder', 'obsolete_milestone', 'modify_milestone'
    source = Column(String(50), nullable=False)  # 'ai', 'system', 'manual'

    # Suggested Changes
    suggested_milestones = Column(JSON, default=list)  # New milestones to add
    milestone_updates = Column(JSON, default=dict)  # Updates to existing milestones
    obsolete_milestone_ids = Column(JSON, default=list)  # Milestones to mark as obsolete
    reorder_map = Column(JSON, default=dict)  # New order for milestones

    # Reasoning and Impact
    reason = Column(Text)  # Why this update is suggested
    expected_impact = Column(String(200))  # Expected impact on learning
    priority = Column(String(20), default="medium")  # 'critical', 'high', 'medium', 'low'

    # Status
    status = Column(String(20), default="pending")  # 'pending', 'approved', 'rejected', 'applied'
    approved_by_user_id = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    applied_at = Column(DateTime)
    rejection_reason = Column(Text)

    # AI Analysis Context
    ai_analysis_data = Column(JSON)  # AI analysis that led to this suggestion
    student_metrics = Column(JSON)  # Student metrics at time of suggestion

    # Relationships
    learning_path = relationship("LearningPath")
    suggested_by = relationship(
        "User", foreign_keys=[suggested_by_user_id], back_populates="suggested_learning_path_updates"
    )
    approved_by = relationship(
        "User", foreign_keys=[approved_by_user_id], back_populates="approved_learning_path_updates"
    )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "learning_path_id": self.learning_path_id,
            "update_type": self.update_type,
            "source": self.source,
            "suggested_milestones": self.suggested_milestones,
            "milestone_updates": self.milestone_updates,
            "obsolete_milestone_ids": self.obsolete_milestone_ids,
            "reorder_map": self.reorder_map,
            "reason": self.reason,
            "expected_impact": self.expected_impact,
            "priority": self.priority,
            "status": self.status,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MilestoneProgress(TenantBaseModel, TimestampMixin):
    """
    Tracks student progress on individual milestones.
    """

    __tablename__ = "milestone_progress"

    # Basic Info
    milestone_id = Column(Integer, ForeignKey("learning_milestones.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Progress
    status = Column(String(20), default="pending")  # 'pending', 'in_progress', 'completed'
    progress_percentage = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Activity Tracking
    completed_activities = Column(JSON, default=list)  # List of completed activity indices
    time_spent_minutes = Column(Integer, default=0)

    # Help and Support
    help_requested = Column(Boolean, default=False)
    help_message = Column(Text)
    help_requested_at = Column(DateTime)

    # Notes
    student_notes = Column(Text)
    coach_notes = Column(Text)

    # Relationships
    milestone = relationship("LearningMilestone", back_populates="progress_records")
    user = relationship("User", back_populates="milestone_progress")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "milestone_id": self.milestone_id,
            "user_id": self.user_id,
            "status": self.status,
            "progress_percentage": self.progress_percentage,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "completed_activities": self.completed_activities,
            "time_spent_minutes": self.time_spent_minutes,
            "help_requested": self.help_requested,
            "help_message": self.help_message,
            "help_requested_at": self.help_requested_at.isoformat() if self.help_requested_at else None,
            "student_notes": self.student_notes,
            "coach_notes": self.coach_notes,
        }
