"""Course progress model for tracking beneficiary progress in courses."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import TenantBaseModel


class CourseProgress(TenantBaseModel):
    """Course progress model."""

    __tablename__ = "course_progress"

    # Basic information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)

    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    completed_topics = Column(JSON, default=list)  # List of completed topic IDs
    last_accessed = Column(DateTime, default=datetime.utcnow)
    time_spent_minutes = Column(Integer, default=0)

    # Completion
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)

    # Assessment
    assessment_attempts = Column(Integer, default=0)
    assessment_score = Column(Float)
    assessment_passed = Column(Boolean, default=False)
    assessment_date = Column(DateTime)
    assessment_feedback = Column(Text)

    # Additional data
    notes = Column(Text)
    progress_metadata = Column(JSON, default=dict)

    # Relationships
    course = relationship("Course", back_populates="progress_records")
    beneficiary = relationship("Beneficiary", back_populates="course_progress")
    enrollment = relationship("Enrollment", back_populates="course_progress")

    def update_progress(self, completed_topic_id=None, time_spent=0):
        """Update course progress."""
        # Update time spent
        self.time_spent_minutes += time_spent
        self.last_accessed = datetime.utcnow()

        # Add completed topic
        if completed_topic_id and completed_topic_id not in self.completed_topics:
            self.completed_topics.append(completed_topic_id)

        # Calculate progress percentage
        if self.course and self.course.outline:
            total_topics = len(self.course.outline)
            completed_count = len(self.completed_topics)
            self.progress_percentage = (completed_count / total_topics * 100) if total_topics > 0 else 0

        # Check if completed
        if self.progress_percentage >= 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = datetime.utcnow()

        return self.save()

    def record_assessment(self, score, feedback=None):
        """Record assessment attempt."""
        self.assessment_attempts += 1
        self.assessment_score = score
        self.assessment_date = datetime.utcnow()
        self.assessment_feedback = feedback

        # Check if passed
        if self.course and self.course.passing_score:
            self.assessment_passed = score >= self.course.passing_score

        return self.save()

    def to_dict(self, exclude=None, include_related=False):
        """Convert to dictionary."""
        exclude = exclude or []
        data = super().to_dict(exclude=exclude)

        # Convert datetime to ISO format
        for field in ["last_accessed", "completed_at", "assessment_date"]:
            if field in data and data[field]:
                data[field] = data[field].isoformat()

        # Add related data if requested
        if include_related:
            if self.course:
                data["course_title"] = self.course.title
                data["course_code"] = self.course.code

            if self.beneficiary:
                data["beneficiary_name"] = self.beneficiary.full_name

        # Convert UUID to string
        if "uuid" in data:
            data["uuid"] = str(data["uuid"])

        return data
