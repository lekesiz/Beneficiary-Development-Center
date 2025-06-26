"""Program model for managing training programs."""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Date, JSON, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.models.base import TenantBaseModel


class ProgramStatus(enum.Enum):
    """Program status enumeration."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProgramType(enum.Enum):
    """Program type enumeration."""

    TRAINING = "training"
    WORKSHOP = "workshop"
    CERTIFICATION = "certification"
    BOOTCAMP = "bootcamp"
    MENTORSHIP = "mentorship"
    OTHER = "other"


class Program(TenantBaseModel):
    """Program model."""

    __tablename__ = "programs"

    # Basic information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    code = Column(String(50), nullable=False)  # Unique program code
    title = Column(String(200), nullable=False)
    description = Column(Text)
    objectives = Column(JSON, default=list)  # Learning objectives

    # Program details
    program_type = Column(Enum(ProgramType), default=ProgramType.TRAINING)
    status = Column(Enum(ProgramStatus), default=ProgramStatus.DRAFT)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    enrollment_start = Column(Date)
    enrollment_end = Column(Date)

    # Capacity and requirements
    min_participants = Column(Integer, default=1)
    max_participants = Column(Integer, default=50)
    requirements = Column(JSON, default=dict)  # Prerequisites and requirements

    # Location and delivery
    location = Column(String(200))
    is_online = Column(Boolean, default=False)
    is_hybrid = Column(Boolean, default=False)
    online_link = Column(String(500))

    # Pricing
    price = Column(Integer, default=0)  # Price in cents
    currency = Column(String(3), default="EUR")

    # Additional information
    tags = Column(JSON, default=list)
    program_metadata = Column(JSON, default=dict)  # Additional flexible data
    cover_image_url = Column(String(500))
    resources = Column(JSON, default=list)  # External resources/links

    # Relationships
    created_by = Column(Integer, ForeignKey("users.id"))
    coordinator_id = Column(Integer, ForeignKey("users.id"))

    # Related models
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_programs")
    coordinator = relationship("User", foreign_keys=[coordinator_id], back_populates="coordinated_programs")
    courses = relationship("Course", back_populates="program", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="program")
    evaluations = relationship("Evaluation", back_populates="program")

    def __init__(self, **kwargs):
        """Initialize program."""
        super().__init__(**kwargs)

        # Generate unique code if not provided
        if not self.code:
            self.code = self._generate_code()

        # Set default metadata structure
        if not self.program_metadata:
            self.program_metadata = {
                "target_audience": "",
                "certification_info": {},
                "partners": [],
                "custom_fields": {},
            }

    def _generate_code(self):
        """Generate unique program code."""
        prefix = self.program_type.value[:3].upper() if self.program_type else "PRG"
        timestamp = datetime.utcnow().strftime("%Y%m")
        random_suffix = str(uuid.uuid4())[:4].upper()
        return f"{prefix}-{timestamp}-{random_suffix}"

    @property
    def duration_days(self):
        """Calculate program duration in days."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def is_enrollment_open(self):
        """Check if enrollment is currently open."""
        today = datetime.today().date()

        if self.status != ProgramStatus.PUBLISHED:
            return False

        if self.enrollment_start and self.enrollment_end:
            return self.enrollment_start <= today <= self.enrollment_end

        # If no enrollment dates, check if before program start
        return today < self.start_date

    @property
    def is_active(self):
        """Check if program is currently active."""
        today = datetime.today().date()
        return self.status == ProgramStatus.ACTIVE and self.start_date <= today <= self.end_date

    @property
    def is_upcoming(self):
        """Check if program is upcoming."""
        today = datetime.today().date()
        return self.status in [ProgramStatus.PUBLISHED, ProgramStatus.ACTIVE] and today < self.start_date

    @property
    def is_past(self):
        """Check if program has ended."""
        today = datetime.today().date()
        return today > self.end_date

    def get_enrollment_count(self):
        """Get current enrollment count."""
        return len([e for e in self.enrollments if e.status in ["enrolled", "in_progress"]])

    def get_available_spots(self):
        """Get number of available spots."""
        current_count = self.get_enrollment_count()
        return max(0, self.max_participants - current_count)

    def can_enroll(self):
        """Check if new enrollments are allowed."""
        if not self.is_enrollment_open:
            return False, "Enrollment is closed"

        if self.get_available_spots() <= 0:
            return False, "Program is full"

        return True, None

    def get_completion_rate(self):
        """Calculate program completion rate."""
        if not self.enrollments:
            return 0

        completed = len([e for e in self.enrollments if e.status == "completed"])
        total = len([e for e in self.enrollments if e.status != "cancelled"])

        return (completed / total * 100) if total > 0 else 0

    def add_course(self, course):
        """Add a course to the program."""
        course.program = self
        self.courses.append(course)
        return self.save()

    def update_status(self, new_status):
        """Update program status with validation."""
        # Status transition rules
        transitions = {
            ProgramStatus.DRAFT: [ProgramStatus.PUBLISHED, ProgramStatus.ARCHIVED],
            ProgramStatus.PUBLISHED: [ProgramStatus.ACTIVE, ProgramStatus.ARCHIVED],
            ProgramStatus.ACTIVE: [ProgramStatus.COMPLETED, ProgramStatus.ARCHIVED],
            ProgramStatus.COMPLETED: [ProgramStatus.ARCHIVED],
            ProgramStatus.ARCHIVED: [ProgramStatus.DRAFT],
        }

        current_status = self.status
        allowed_transitions = transitions.get(current_status, [])

        if new_status not in allowed_transitions:
            raise ValueError(f"Cannot transition from {current_status.value} to {new_status.value}")

        self.status = new_status

        # Auto-update based on dates
        if new_status == ProgramStatus.ACTIVE:
            today = datetime.today().date()
            if today < self.start_date:
                raise ValueError("Cannot activate program before start date")

        return self.save()

    def to_dict(self, exclude=None, include_related=False):
        """Convert to dictionary."""
        exclude = exclude or []
        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data["duration_days"] = self.duration_days
        data["is_enrollment_open"] = self.is_enrollment_open
        data["is_active"] = self.is_active
        data["is_upcoming"] = self.is_upcoming
        data["is_past"] = self.is_past

        # Convert enums
        if "status" in data and data["status"]:
            data["status"] = data["status"].value
        if "program_type" in data and data["program_type"]:
            data["program_type"] = data["program_type"].value

        # Convert dates to ISO format
        for date_field in ["start_date", "end_date", "enrollment_start", "enrollment_end"]:
            if date_field in data and data[date_field]:
                data[date_field] = data[date_field].isoformat()

        # Add related data if requested
        if include_related:
            data["enrollment_count"] = self.get_enrollment_count()
            data["available_spots"] = self.get_available_spots()
            data["completion_rate"] = self.get_completion_rate()
            data["course_count"] = len(self.courses)

            if self.coordinator:
                data["coordinator_name"] = self.coordinator.full_name

        # Convert UUID to string
        if "uuid" in data:
            data["uuid"] = str(data["uuid"])

        return data

    def __repr__(self):
        """String representation."""
        return f"<Program {self.code}: {self.title}>"
