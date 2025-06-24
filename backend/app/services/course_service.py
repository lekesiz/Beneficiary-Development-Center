"""Service layer for Course operations."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.course import Course, CourseStatus, CourseFormat, DifficultyLevel
from app.models.program import Program
from app.models.user import User
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError
from app.core.logging import logger
from app.services.base import BaseService


class CourseService(BaseService[Course]):
    """Service for managing courses."""
    
    def __init__(self, db_session: Session):
        """Initialize service."""
        super().__init__(Course, db_session)
    
    def get_all(
        self,
        tenant_id: int,
        user: User,
        program_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CourseStatus] = None,
        format: Optional[CourseFormat] = None,
        difficulty: Optional[DifficultyLevel] = None,
        search: Optional[str] = None,
        instructor_id: Optional[int] = None
    ) -> List[Course]:
        """
        Get all courses for a tenant with filtering.
        
        Args:
            tenant_id: Tenant ID
            user: Current user
            program_id: Filter by program
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by course status
            format: Filter by course format
            difficulty: Filter by difficulty level
            search: Search in title, description, and code
            instructor_id: Filter by instructor
            
        Returns:
            List of courses
        """
        query = self.db.query(Course).filter(
            Course.tenant_id == tenant_id,
            Course.deleted_at.is_(None)
        )
        
        # Apply filters
        if program_id:
            query = query.filter(Course.program_id == program_id)
        
        if status:
            query = query.filter(Course.status == status)
        
        if format:
            query = query.filter(Course.format == format)
        
        if difficulty:
            query = query.filter(Course.difficulty_level == difficulty)
        
        if instructor_id:
            query = query.filter(Course.instructor_id == instructor_id)
        
        if search:
            search_filter = or_(
                Course.title.ilike(f"%{search}%"),
                Course.subtitle.ilike(f"%{search}%"),
                Course.description.ilike(f"%{search}%"),
                Course.code.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Order by program and order index
        query = query.order_by(Course.program_id, Course.order_index, Course.title)
        
        # Apply pagination
        courses = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(courses)} courses for tenant {tenant_id}")
        return courses
    
    def get_by_id(self, tenant_id: int, course_id: int, user: User) -> Course:
        """
        Get a course by ID.
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            user: Current user
            
        Returns:
            Course if found
            
        Raises:
            NotFoundError: If course not found
        """
        course = self.db.query(Course).filter(
            Course.id == course_id,
            Course.tenant_id == tenant_id,
            Course.deleted_at.is_(None)
        ).first()
        
        if not course:
            raise NotFoundError("Course not found")
        
        return course
    
    def get_by_code(self, tenant_id: int, code: str, user: User) -> Course:
        """
        Get a course by code.
        
        Args:
            tenant_id: Tenant ID
            code: Course code
            user: Current user
            
        Returns:
            Course if found
            
        Raises:
            NotFoundError: If course not found
        """
        course = self.db.query(Course).filter(
            Course.code == code,
            Course.tenant_id == tenant_id,
            Course.deleted_at.is_(None)
        ).first()
        
        if not course:
            raise NotFoundError(f"Course with code {code} not found")
        
        return course
    
    def create(self, tenant_id: int, data: Dict[str, Any], user: User) -> Course:
        """
        Create a new course.
        
        Args:
            tenant_id: Tenant ID
            data: Course data
            user: Current user
            
        Returns:
            Created course
            
        Raises:
            BadRequestError: If validation fails
            ForbiddenError: If user doesn't have permission
        """
        # Check permissions
        if user.role not in ['admin', 'manager', 'instructor']:
            raise ForbiddenError("Only admins, managers, and instructors can create courses")
        
        # Validate program exists and belongs to tenant
        program_id = data.get('program_id')
        if program_id:
            program = self.db.query(Program).filter(
                Program.id == program_id,
                Program.tenant_id == tenant_id,
                Program.deleted_at.is_(None)
            ).first()
            
            if not program:
                raise NotFoundError("Program not found")
        else:
            raise BadRequestError("Program ID is required")
        
        # Validate capacity
        min_participants = data.get('min_participants', 1)
        max_participants = data.get('max_participants')
        
        if max_participants and min_participants > max_participants:
            raise BadRequestError("Minimum participants cannot exceed maximum")
        
        # Set order index if not provided
        if 'order_index' not in data:
            max_order = self.db.query(func.max(Course.order_index)).filter(
                Course.program_id == program_id,
                Course.deleted_at.is_(None)
            ).scalar() or 0
            data['order_index'] = max_order + 1
        
        # Create course
        course_data = {
            'tenant_id': tenant_id,
            'created_by': user.id,
            **data
        }
        
        # Set instructor to current user if instructor and not specified
        if user.role == 'instructor' and 'instructor_id' not in course_data:
            course_data['instructor_id'] = user.id
        
        course = Course(**course_data)
        
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        
        logger.info(f"Created course {course.code} for program {program.code}")
        return course
    
    def update(
        self,
        tenant_id: int,
        course_id: int,
        data: Dict[str, Any],
        user: User
    ) -> Course:
        """
        Update a course.
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            data: Update data
            user: Current user
            
        Returns:
            Updated course
            
        Raises:
            NotFoundError: If course not found
            ForbiddenError: If user doesn't have permission
            BadRequestError: If validation fails
        """
        course = self.get_by_id(tenant_id, course_id, user)
        
        # Check permissions
        if user.role == 'instructor':
            # Instructors can only update their own courses
            if course.instructor_id != user.id:
                raise ForbiddenError("You can only update courses you instruct")
        elif user.role not in ['admin', 'manager']:
            raise ForbiddenError("Insufficient permissions to update courses")
        
        # Validate capacity if provided
        min_participants = data.get('min_participants', course.min_participants)
        max_participants = data.get('max_participants', course.max_participants)
        
        if max_participants and min_participants > max_participants:
            raise BadRequestError("Minimum participants cannot exceed maximum")
        
        # Check if reducing capacity below current enrollment
        if 'max_participants' in data:
            current_participants = course.get_participant_count()
            if data['max_participants'] < current_participants:
                raise BadRequestError(
                    f"Cannot reduce capacity below current participants ({current_participants})"
                )
        
        # Update fields
        for key, value in data.items():
            if hasattr(course, key) and key not in ['id', 'tenant_id', 'created_at', 'created_by', 'program_id']:
                setattr(course, key, value)
        
        course.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(course)
        
        logger.info(f"Updated course {course.code}")
        return course
    
    def delete(self, tenant_id: int, course_id: int, user: User) -> bool:
        """
        Delete a course (soft delete).
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            user: Current user
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundError: If course not found
            ForbiddenError: If user doesn't have permission
            BadRequestError: If course has progress records
        """
        course = self.get_by_id(tenant_id, course_id, user)
        
        # Check permissions
        if user.role != 'admin':
            raise ForbiddenError("Only admins can delete courses")
        
        # Check for progress records
        if course.progress_records:
            raise BadRequestError(
                f"Cannot delete course with {len(course.progress_records)} progress records"
            )
        
        # Soft delete
        course.deleted_at = datetime.utcnow()
        
        # Reorder remaining courses
        remaining_courses = self.db.query(Course).filter(
            Course.program_id == course.program_id,
            Course.order_index > course.order_index,
            Course.deleted_at.is_(None)
        ).all()
        
        for remaining_course in remaining_courses:
            remaining_course.order_index -= 1
        
        self.db.commit()
        
        logger.info(f"Deleted course {course.code}")
        return True
    
    def add_session(
        self,
        tenant_id: int,
        course_id: int,
        session_data: Dict[str, Any],
        user: User
    ) -> Course:
        """
        Add a session to a course.
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            session_data: Session data
            user: Current user
            
        Returns:
            Updated course
            
        Raises:
            NotFoundError: If course not found
            ForbiddenError: If user doesn't have permission
        """
        course = self.get_by_id(tenant_id, course_id, user)
        
        # Check permissions
        if user.role == 'instructor':
            if course.instructor_id != user.id:
                raise ForbiddenError("You can only add sessions to courses you instruct")
        elif user.role not in ['admin', 'manager']:
            raise ForbiddenError("Insufficient permissions to add sessions")
        
        # Add tenant_id to session data
        session_data['tenant_id'] = tenant_id
        
        # Set instructor if not specified
        if 'instructor_id' not in session_data:
            session_data['instructor_id'] = course.instructor_id or user.id
        
        course.add_session(session_data)
        self.db.commit()
        self.db.refresh(course)
        
        logger.info(f"Added session to course {course.code}")
        return course
    
    def duplicate(
        self,
        tenant_id: int,
        course_id: int,
        target_program_id: Optional[int],
        user: User
    ) -> Course:
        """
        Duplicate a course.
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID to duplicate
            target_program_id: Target program ID (optional)
            user: Current user
            
        Returns:
            New duplicated course
            
        Raises:
            NotFoundError: If course not found
            ForbiddenError: If user doesn't have permission
        """
        course = self.get_by_id(tenant_id, course_id, user)
        
        # Check permissions
        if user.role not in ['admin', 'manager']:
            raise ForbiddenError("Only admins and managers can duplicate courses")
        
        # Validate target program if provided
        if target_program_id:
            target_program = self.db.query(Program).filter(
                Program.id == target_program_id,
                Program.tenant_id == tenant_id,
                Program.deleted_at.is_(None)
            ).first()
            
            if not target_program:
                raise NotFoundError("Target program not found")
        
        # Duplicate the course
        new_course = course.duplicate(target_program_id)
        new_course.created_by = user.id
        
        self.db.add(new_course)
        self.db.commit()
        self.db.refresh(new_course)
        
        logger.info(f"Duplicated course {course.code} to {new_course.code}")
        return new_course
    
    def reorder(
        self,
        tenant_id: int,
        course_id: int,
        new_order: int,
        user: User
    ) -> Course:
        """
        Reorder a course within its program.
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            new_order: New order index
            user: Current user
            
        Returns:
            Updated course
            
        Raises:
            NotFoundError: If course not found
            ForbiddenError: If user doesn't have permission
        """
        course = self.get_by_id(tenant_id, course_id, user)
        
        # Check permissions
        if user.role not in ['admin', 'manager']:
            raise ForbiddenError("Only admins and managers can reorder courses")
        
        course.update_order(new_order)
        self.db.commit()
        self.db.refresh(course)
        
        logger.info(f"Reordered course {course.code} to position {new_order}")
        return course
    
    def get_statistics(
        self,
        tenant_id: int,
        program_id: Optional[int],
        user: User
    ) -> Dict[str, Any]:
        """
        Get course statistics.
        
        Args:
            tenant_id: Tenant ID
            program_id: Filter by program (optional)
            user: Current user
            
        Returns:
            Statistics dictionary
        """
        # Check permissions
        if user.role not in ['admin', 'manager', 'instructor']:
            raise ForbiddenError("Insufficient permissions to view statistics")
        
        query = self.db.query(Course).filter(
            Course.tenant_id == tenant_id,
            Course.deleted_at.is_(None)
        )
        
        if program_id:
            query = query.filter(Course.program_id == program_id)
        
        # For instructors, only show their courses
        if user.role == 'instructor':
            query = query.filter(Course.instructor_id == user.id)
        
        courses = query.all()
        
        # Calculate statistics
        total_courses = len(courses)
        
        # Status breakdown
        status_counts = {}
        for status in CourseStatus:
            count = len([c for c in courses if c.status == status])
            status_counts[status.value] = count
        
        # Format breakdown
        format_counts = {}
        for format in CourseFormat:
            count = len([c for c in courses if c.format == format])
            format_counts[format.value] = count
        
        # Difficulty breakdown
        difficulty_counts = {}
        for level in DifficultyLevel:
            count = len([c for c in courses if c.difficulty_level == level])
            difficulty_counts[level.value] = count
        
        # Assessment statistics
        with_assessment = len([c for c in courses if c.has_assessment])
        
        # Calculate average completion rate and scores
        completion_rates = [c.get_completion_rate() for c in courses]
        avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        
        scores = [c.get_average_score() for c in courses if c.get_average_score() is not None]
        avg_score = sum(scores) / len(scores) if scores else None
        
        # Total sessions
        total_sessions = sum(len(c.sessions) for c in courses)
        
        return {
            'total_courses': total_courses,
            'status_breakdown': status_counts,
            'format_breakdown': format_counts,
            'difficulty_breakdown': difficulty_counts,
            'courses_with_assessment': with_assessment,
            'average_completion_rate': round(avg_completion, 2),
            'average_assessment_score': round(avg_score, 2) if avg_score else None,
            'total_sessions': total_sessions
        }