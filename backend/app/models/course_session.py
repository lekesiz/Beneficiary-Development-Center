"""Course session model for managing individual course sessions."""

from datetime import datetime, timedelta
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import TenantBaseModel


class CourseSession(TenantBaseModel):
    """Course session model."""

    __tablename__ = "course_sessions"

    # Basic information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Schedule
    session_date = Column(DateTime, nullable=False)
    duration_hours = Column(Float, default=1.0)

    # Location
    location = Column(String(200))
    room_number = Column(String(50))
    is_online = Column(Boolean, default=False)
    online_link = Column(String(500))

    # Instructor
    instructor_id = Column(Integer, ForeignKey("users.id"))

    # Status
    is_mandatory = Column(Boolean, default=True)
    is_cancelled = Column(Boolean, default=False)
    cancellation_reason = Column(Text)

    # Materials
    materials_url = Column(String(500))
    recording_url = Column(String(500))

    # Relationships
    course = relationship("Course", back_populates="sessions")
    instructor = relationship("User", foreign_keys=[instructor_id], back_populates="instructed_sessions")
    # attendance_records = relationship('SessionAttendance', back_populates='session')

    @property
    def end_time(self):
        """Calculate session end time."""
        if self.session_date and self.duration_hours:
            return self.session_date + timedelta(hours=self.duration_hours)
        return None

    def to_dict(self, exclude=None, include_related=False):
        """Convert to dictionary."""
        exclude = exclude or []
        data = super().to_dict(exclude=exclude)

        # Convert datetime to ISO format
        if "session_date" in data and data["session_date"]:
            data["session_date"] = data["session_date"].isoformat()

        # Add computed fields
        data["end_time"] = self.end_time.isoformat() if self.end_time else None

        # Add related data if requested
        if include_related:
            if self.instructor:
                data["instructor_name"] = self.instructor.full_name
            data["attendance_count"] = len(self.attendance_records)

        # Convert UUID to string
        if "uuid" in data:
            data["uuid"] = str(data["uuid"])

        return data
