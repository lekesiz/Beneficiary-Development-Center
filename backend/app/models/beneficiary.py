"""Beneficiary model for managing program participants."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Date, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.models.base import TenantBaseModel


class BeneficiaryStatus(enum.Enum):
    """Beneficiary status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    SUSPENDED = "suspended"


class EmploymentStatus(enum.Enum):
    """Employment status enumeration."""

    EMPLOYED = "employed"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"
    SELF_EMPLOYED = "self_employed"
    RETIRED = "retired"
    OTHER = "other"


class EducationLevel(enum.Enum):
    """Education level enumeration."""

    NO_DIPLOMA = "no_diploma"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HIGH_SCHOOL = "high_school"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    OTHER = "other"


class Beneficiary(TenantBaseModel):
    """Beneficiary model."""

    __tablename__ = "beneficiaries"

    # Basic information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    external_id = Column(String(100))  # ID from external system
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    mobile_phone = Column(String(20))

    # Personal information
    date_of_birth = Column(Date)
    gender = Column(String(10))
    nationality = Column(String(50))
    birthplace = Column(String(100))

    # Address
    address = Column(JSON, default=dict)  # Structured address data

    # Professional information
    employment_status = Column(Enum(EmploymentStatus))
    job_title = Column(String(100))
    company = Column(String(100))
    industry = Column(String(100))
    years_of_experience = Column(Integer)

    # Education
    education_level = Column(Enum(EducationLevel))
    field_of_study = Column(String(100))
    certifications = Column(JSON, default=list)

    # Profile data
    profile_data = Column(JSON, default=dict)  # Flexible profile information
    skills = Column(JSON, default=list)
    interests = Column(JSON, default=list)
    goals = Column(JSON, default=list)

    # Status and management
    status = Column(Enum(BeneficiaryStatus), default=BeneficiaryStatus.ACTIVE)
    notes = Column(JSON, default=list)  # Internal notes
    tags = Column(JSON, default=list)  # Tags for categorization

    # Relationships
    created_by = Column(Integer, ForeignKey("users.id"))
    assigned_trainer_id = Column(Integer, ForeignKey("users.id"))

    # Related models
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_beneficiaries")
    assigned_trainer = relationship("User", foreign_keys=[assigned_trainer_id], back_populates="assigned_beneficiaries")
    enrollments = relationship("Enrollment", back_populates="beneficiary")
    course_progress = relationship("CourseProgress", back_populates="beneficiary")
    # documents = relationship('Document', back_populates='beneficiary')
    # appointments = relationship('Appointment', back_populates='beneficiary')
    # evaluation_attempts = relationship('EvaluationAttempt', back_populates='beneficiary')
    # notifications = relationship('Notification', back_populates='beneficiary')

    def __init__(self, **kwargs):
        """Initialize beneficiary."""
        super().__init__(**kwargs)

        # Set default address structure
        if not self.address:
            self.address = {"street": "", "city": "", "state": "", "postal_code": "", "country": "France"}

        # Set default profile data
        if not self.profile_data:
            self.profile_data = {
                "emergency_contact": {},
                "languages": [],
                "availability": {},
                "preferences": {},
                "custom_fields": {},
            }

    @property
    def full_name(self):
        """Get beneficiary's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """Calculate age from date of birth."""
        if self.date_of_birth:
            today = datetime.today().date()
            age = today.year - self.date_of_birth.year
            if today.month < self.date_of_birth.month or (
                today.month == self.date_of_birth.month and today.day < self.date_of_birth.day
            ):
                age -= 1
            return age
        return None

    def get_active_enrollments(self):
        """Get active enrollments."""
        return [e for e in self.enrollments if e.status in ["enrolled", "in_progress"]]

    def get_completed_programs(self):
        """Get completed programs."""
        return [e.program for e in self.enrollments if e.status == "completed"]

    def get_progress_summary(self):
        """Get overall progress summary."""
        active_enrollments = self.get_active_enrollments()
        if not active_enrollments:
            return {"overall_progress": 0, "enrollments": []}

        enrollment_progress = []
        total_progress = 0

        for enrollment in active_enrollments:
            progress = enrollment.calculate_progress()
            enrollment_progress.append(
                {
                    "program_id": enrollment.program_id,
                    "program_name": enrollment.program.name,
                    "progress": progress,
                    "status": enrollment.status,
                }
            )
            total_progress += progress

        return {
            "overall_progress": total_progress / len(active_enrollments) if active_enrollments else 0,
            "enrollments": enrollment_progress,
        }

    def add_note(self, note_text, user_id):
        """Add a note to the beneficiary."""
        if self.notes is None:
            self.notes = []

        note = {
            "id": str(uuid.uuid4()),
            "text": note_text,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.notes.append(note)
        return self.save()

    def add_tag(self, tag):
        """Add a tag to the beneficiary."""
        if self.tags is None:
            self.tags = []

        if tag not in self.tags:
            self.tags.append(tag)
            return self.save()

    def remove_tag(self, tag):
        """Remove a tag from the beneficiary."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            return self.save()

    def update_profile_data(self, data):
        """Update profile data."""
        if self.profile_data is None:
            self.profile_data = {}
        self.profile_data.update(data)
        return self.save()

    def can_enroll_in_program(self, program):
        """Check if beneficiary can enroll in a program."""
        # Check if already enrolled
        existing = [e for e in self.enrollments if e.program_id == program.id]
        if existing:
            return False, "Already enrolled in this program"

        # Check status
        if self.status != BeneficiaryStatus.ACTIVE:
            return False, "Beneficiary is not active"

        # Check program requirements
        if program.requirements:
            # Add logic to check requirements
            pass

        return True, None

    def get_evaluation_history(self):
        """Get evaluation attempt history."""
        attempts = []
        for attempt in self.evaluation_attempts:
            attempts.append(
                {
                    "id": attempt.id,
                    "evaluation_name": attempt.evaluation.name,
                    "attempt_number": attempt.attempt_number,
                    "score": attempt.score,
                    "passed": attempt.passed,
                    "completed_at": attempt.completed_at,
                }
            )
        return sorted(attempts, key=lambda x: x["completed_at"], reverse=True)

    def to_dict(self, exclude=None, include_related=False):
        """Convert to dictionary."""
        exclude = exclude or []
        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data["full_name"] = self.full_name
        data["age"] = self.age

        # Convert enums
        if "status" in data and data["status"]:
            data["status"] = data["status"].value
        if "employment_status" in data and data["employment_status"]:
            data["employment_status"] = data["employment_status"].value
        if "education_level" in data and data["education_level"]:
            data["education_level"] = data["education_level"].value

        # Add related data if requested
        if include_related:
            data["progress_summary"] = self.get_progress_summary()
            data["active_enrollments"] = len(self.get_active_enrollments())
            data["completed_programs"] = len(self.get_completed_programs())

            if self.assigned_trainer:
                data["assigned_trainer_name"] = self.assigned_trainer.full_name

        # Convert UUID to string
        if "uuid" in data:
            data["uuid"] = str(data["uuid"])

        return data

    def __repr__(self):
        """String representation."""
        return f"<Beneficiary {self.full_name}>"
