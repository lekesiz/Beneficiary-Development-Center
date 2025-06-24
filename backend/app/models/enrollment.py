"""Enrollment model for managing beneficiary enrollments in programs."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.models.base import TenantBaseModel


class EnrollmentStatus(enum.Enum):
    """Enrollment status enumeration."""
    PENDING = 'pending'
    ENROLLED = 'enrolled'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    SUSPENDED = 'suspended'


class Enrollment(TenantBaseModel):
    """Enrollment model."""
    __tablename__ = 'enrollments'
    
    # Basic information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    enrollment_number = Column(String(50), unique=True, nullable=False)
    
    # Relationships
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=False)
    program_id = Column(Integer, ForeignKey('programs.id'), nullable=False)
    
    # Status and dates
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.PENDING)
    enrolled_date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime)
    completion_date = Column(DateTime)
    cancellation_date = Column(DateTime)
    
    # Progress
    overall_progress = Column(Float, default=0.0)
    attendance_percentage = Column(Float, default=0.0)
    
    # Notes and reasons
    enrollment_notes = Column(Text)
    cancellation_reason = Column(Text)
    suspension_reason = Column(Text)
    
    # Additional data
    enrollment_metadata = Column(JSON, default=dict)
    
    # Relationships
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Related models
    beneficiary = relationship('Beneficiary', back_populates='enrollments')
    program = relationship('Program', back_populates='enrollments')
    creator = relationship('User')
    course_progress = relationship('CourseProgress', back_populates='enrollment')
    attendance_records = relationship('SessionAttendance', back_populates='enrollment')
    
    def __init__(self, **kwargs):
        """Initialize enrollment."""
        super().__init__(**kwargs)
        
        # Generate enrollment number if not provided
        if not self.enrollment_number:
            self.enrollment_number = self._generate_enrollment_number()
        
        # Set default metadata structure
        if not self.enrollment_metadata:
            self.enrollment_metadata = {
                'referral_source': '',
                'motivation': '',
                'goals': [],
                'special_requirements': {},
                'custom_fields': {}
            }
    
    def _generate_enrollment_number(self):
        """Generate unique enrollment number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_suffix = str(uuid.uuid4())[:6].upper()
        return f"ENR-{timestamp}-{random_suffix}"
    
    def calculate_progress(self):
        """Calculate overall progress based on course completions."""
        if not self.program or not self.program.courses:
            return 0.0
        
        total_courses = len(self.program.courses)
        completed_courses = sum(
            1 for progress in self.course_progress 
            if progress.is_completed
        )
        
        self.overall_progress = (completed_courses / total_courses * 100) if total_courses > 0 else 0.0
        return self.overall_progress
    
    def calculate_attendance(self):
        """Calculate attendance percentage."""
        if not self.attendance_records:
            return 0.0
        
        total_sessions = len(self.attendance_records)
        attended_sessions = sum(
            1 for record in self.attendance_records 
            if record.is_present
        )
        
        self.attendance_percentage = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
        return self.attendance_percentage
    
    def update_status(self, new_status, reason=None):
        """Update enrollment status with validation."""
        old_status = self.status
        
        # Status transition rules
        transitions = {
            EnrollmentStatus.PENDING: [EnrollmentStatus.ENROLLED, EnrollmentStatus.CANCELLED],
            EnrollmentStatus.ENROLLED: [EnrollmentStatus.IN_PROGRESS, EnrollmentStatus.CANCELLED, EnrollmentStatus.SUSPENDED],
            EnrollmentStatus.IN_PROGRESS: [EnrollmentStatus.COMPLETED, EnrollmentStatus.CANCELLED, EnrollmentStatus.SUSPENDED],
            EnrollmentStatus.SUSPENDED: [EnrollmentStatus.IN_PROGRESS, EnrollmentStatus.CANCELLED],
            EnrollmentStatus.COMPLETED: [],  # Cannot change from completed
            EnrollmentStatus.CANCELLED: []   # Cannot change from cancelled
        }
        
        allowed_transitions = transitions.get(old_status, [])
        
        if new_status not in allowed_transitions:
            raise ValueError(f"Cannot transition from {old_status.value} to {new_status.value}")
        
        self.status = new_status
        
        # Update relevant dates
        if new_status == EnrollmentStatus.IN_PROGRESS and not self.start_date:
            self.start_date = datetime.utcnow()
        elif new_status == EnrollmentStatus.COMPLETED:
            self.completion_date = datetime.utcnow()
            self.overall_progress = 100.0
        elif new_status == EnrollmentStatus.CANCELLED:
            self.cancellation_date = datetime.utcnow()
            self.cancellation_reason = reason
        elif new_status == EnrollmentStatus.SUSPENDED:
            self.suspension_reason = reason
        
        return self.save()
    
    def can_access_course(self, course):
        """Check if enrolled beneficiary can access a course."""
        if self.status not in [EnrollmentStatus.ENROLLED, EnrollmentStatus.IN_PROGRESS]:
            return False
        
        if course.program_id != self.program_id:
            return False
        
        return True
    
    def get_certificate_eligibility(self):
        """Check if eligible for certificate."""
        if self.status != EnrollmentStatus.COMPLETED:
            return False, "Enrollment not completed"
        
        if self.overall_progress < 100:
            return False, "Course progress incomplete"
        
        # Check minimum attendance if required
        min_attendance = self.program.requirements.get('min_attendance', 0) if self.program else 0
        if min_attendance > 0 and self.attendance_percentage < min_attendance:
            return False, f"Attendance below minimum requirement ({min_attendance}%)"
        
        # Check if all assessments passed
        failed_assessments = [
            progress for progress in self.course_progress
            if progress.course.has_assessment and not progress.assessment_passed
        ]
        if failed_assessments:
            return False, "Not all assessments passed"
        
        return True, None
    
    def to_dict(self, exclude=None, include_related=False):
        """Convert to dictionary."""
        exclude = exclude or []
        data = super().to_dict(exclude=exclude)
        
        # Convert enum
        if 'status' in data and data['status']:
            data['status'] = data['status'].value
        
        # Convert datetime to ISO format
        for field in ['enrolled_date', 'start_date', 'completion_date', 'cancellation_date']:
            if field in data and data[field]:
                data[field] = data[field].isoformat()
        
        # Add related data if requested
        if include_related:
            if self.beneficiary:
                data['beneficiary_name'] = self.beneficiary.full_name
                data['beneficiary_email'] = self.beneficiary.email
            
            if self.program:
                data['program_title'] = self.program.title
                data['program_code'] = self.program.code
            
            data['certificate_eligible'] = self.get_certificate_eligibility()[0]
        
        # Convert UUID to string
        if 'uuid' in data:
            data['uuid'] = str(data['uuid'])
        
        return data
    
    def __repr__(self):
        """String representation."""
        return f"<Enrollment {self.enrollment_number}>"