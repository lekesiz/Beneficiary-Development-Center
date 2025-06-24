"""Course model for managing program courses."""
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Text, Integer, Float, JSON, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.models.base import TenantBaseModel


class CourseStatus(enum.Enum):
    """Course status enumeration."""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'


class CourseFormat(enum.Enum):
    """Course format enumeration."""
    LECTURE = 'lecture'
    WORKSHOP = 'workshop'
    PRACTICAL = 'practical'
    ONLINE = 'online'
    SELF_PACED = 'self_paced'
    HYBRID = 'hybrid'


class DifficultyLevel(enum.Enum):
    """Course difficulty level."""
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    EXPERT = 'expert'


class Course(TenantBaseModel):
    """Course model."""
    __tablename__ = 'courses'
    
    # Basic information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    code = Column(String(50), nullable=False)  # Unique course code
    title = Column(String(200), nullable=False)
    subtitle = Column(String(300))
    description = Column(Text)
    
    # Course details
    program_id = Column(Integer, ForeignKey('programs.id'), nullable=False)
    status = Column(Enum(CourseStatus), default=CourseStatus.DRAFT)
    format = Column(Enum(CourseFormat), default=CourseFormat.LECTURE)
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    
    # Duration and scheduling
    duration_hours = Column(Float, default=1.0)  # Duration in hours
    duration_weeks = Column(Integer, default=1)  # For multi-week courses
    order_index = Column(Integer, default=0)  # Order within program
    
    # Content structure
    objectives = Column(JSON, default=list)  # Learning objectives
    outline = Column(JSON, default=list)  # Course outline/topics
    prerequisites = Column(JSON, default=list)  # Required knowledge/skills
    materials = Column(JSON, default=list)  # Required materials
    
    # Resources
    content_url = Column(String(500))  # Link to course content
    video_url = Column(String(500))  # Video content link
    resources = Column(JSON, default=list)  # Additional resources
    assignments = Column(JSON, default=list)  # Course assignments
    
    # Assessment
    has_assessment = Column(Boolean, default=False)
    assessment_type = Column(String(50))  # quiz, project, presentation, etc.
    passing_score = Column(Float, default=70.0)  # Percentage
    max_attempts = Column(Integer, default=3)
    
    # Capacity
    min_participants = Column(Integer, default=1)
    max_participants = Column(Integer)  # If null, use program's max
    
    # Additional information
    tags = Column(JSON, default=list)
    course_metadata = Column(JSON, default=dict)
    thumbnail_url = Column(String(500))
    
    # Relationships
    instructor_id = Column(Integer, ForeignKey('users.id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Related models
    program = relationship('Program', back_populates='courses')
    instructor = relationship('User', foreign_keys=[instructor_id])
    creator = relationship('User', foreign_keys=[created_by])
    sessions = relationship('CourseSession', back_populates='course', cascade='all, delete-orphan')
    progress_records = relationship('CourseProgress', back_populates='course')
    evaluations = relationship('Evaluation', back_populates='course', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Initialize course."""
        super().__init__(**kwargs)
        
        # Generate unique code if not provided
        if not self.code:
            self.code = self._generate_code()
        
        # Set default metadata structure
        if not self.course_metadata:
            self.course_metadata = {
                'learning_outcomes': [],
                'target_audience': '',
                'delivery_method': '',
                'tools_required': [],
                'custom_fields': {}
            }
    
    def _generate_code(self):
        """Generate unique course code."""
        prefix = 'CRS'
        timestamp = datetime.utcnow().strftime('%Y%m')
        random_suffix = str(uuid.uuid4())[:4].upper()
        return f"{prefix}-{timestamp}-{random_suffix}"
    
    @property
    def total_duration_hours(self):
        """Calculate total duration including all sessions."""
        if self.sessions:
            return sum(session.duration_hours for session in self.sessions)
        return self.duration_hours
    
    @property
    def is_available(self):
        """Check if course is available for enrollment."""
        return self.status == CourseStatus.PUBLISHED and self.program.is_enrollment_open
    
    def get_participant_count(self):
        """Get current participant count through enrollments."""
        if not self.program:
            return 0
        
        # Count active enrollments in the program
        return len([e for e in self.program.enrollments 
                   if e.status in ['enrolled', 'in_progress']])
    
    def get_available_spots(self):
        """Get number of available spots."""
        max_cap = self.max_participants or self.program.max_participants
        current_count = self.get_participant_count()
        return max(0, max_cap - current_count)
    
    def get_completion_rate(self):
        """Calculate course completion rate."""
        if not self.progress_records:
            return 0
        
        completed = len([p for p in self.progress_records if p.is_completed])
        total = len(self.progress_records)
        
        return (completed / total * 100) if total > 0 else 0
    
    def get_average_score(self):
        """Calculate average assessment score."""
        if not self.has_assessment or not self.progress_records:
            return None
        
        scores = [p.assessment_score for p in self.progress_records 
                 if p.assessment_score is not None]
        
        return sum(scores) / len(scores) if scores else None
    
    def add_session(self, session_data):
        """Add a session to the course."""
        from app.models.course_session import CourseSession
        
        session = CourseSession(
            course_id=self.id,
            tenant_id=self.tenant_id,
            **session_data
        )
        self.sessions.append(session)
        return self.save()
    
    def update_order(self, new_order):
        """Update course order within program."""
        old_order = self.order_index
        self.order_index = new_order
        
        # Reorder other courses if needed
        if old_order != new_order and self.program:
            for course in self.program.courses:
                if course.id == self.id:
                    continue
                
                if old_order < new_order:
                    # Moving down
                    if old_order < course.order_index <= new_order:
                        course.order_index -= 1
                else:
                    # Moving up
                    if new_order <= course.order_index < old_order:
                        course.order_index += 1
        
        return self.save()
    
    def duplicate(self, new_program_id=None):
        """Create a duplicate of the course."""
        new_course = Course(
            tenant_id=self.tenant_id,
            program_id=new_program_id or self.program_id,
            title=f"{self.title} (Copy)",
            subtitle=self.subtitle,
            description=self.description,
            format=self.format,
            difficulty_level=self.difficulty_level,
            duration_hours=self.duration_hours,
            duration_weeks=self.duration_weeks,
            objectives=list(self.objectives),
            outline=list(self.outline),
            prerequisites=list(self.prerequisites),
            materials=list(self.materials),
            content_url=self.content_url,
            video_url=self.video_url,
            resources=list(self.resources),
            assignments=list(self.assignments),
            has_assessment=self.has_assessment,
            assessment_type=self.assessment_type,
            passing_score=self.passing_score,
            max_attempts=self.max_attempts,
            min_participants=self.min_participants,
            max_participants=self.max_participants,
            tags=list(self.tags),
            course_metadata=dict(self.course_metadata),
            thumbnail_url=self.thumbnail_url,
            instructor_id=self.instructor_id,
            created_by=self.created_by,
            status=CourseStatus.DRAFT  # Always start as draft
        )
        
        return new_course.save()
    
    def to_dict(self, exclude=None, include_related=False):
        """Convert to dictionary."""
        exclude = exclude or []
        data = super().to_dict(exclude=exclude)
        
        # Add computed fields
        data['total_duration_hours'] = self.total_duration_hours
        data['is_available'] = self.is_available
        
        # Convert enums
        if 'status' in data and data['status']:
            data['status'] = data['status'].value
        if 'format' in data and data['format']:
            data['format'] = data['format'].value
        if 'difficulty_level' in data and data['difficulty_level']:
            data['difficulty_level'] = data['difficulty_level'].value
        
        # Add related data if requested
        if include_related:
            data['participant_count'] = self.get_participant_count()
            data['available_spots'] = self.get_available_spots()
            data['completion_rate'] = self.get_completion_rate()
            data['average_score'] = self.get_average_score()
            data['session_count'] = len(self.sessions)
            
            if self.instructor:
                data['instructor_name'] = self.instructor.full_name
            
            if self.program:
                data['program_title'] = self.program.title
                data['program_code'] = self.program.code
        
        # Convert UUID to string
        if 'uuid' in data:
            data['uuid'] = str(data['uuid'])
        
        return data
    
    def __repr__(self):
        """String representation."""
        return f"<Course {self.code}: {self.title}>"