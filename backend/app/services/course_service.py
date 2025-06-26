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

    def get_all_by_program(
        self,
        tenant_id: int,
        program_id: int,
        user: User,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CourseStatus] = None,
        format: Optional[CourseFormat] = None,
        difficulty: Optional[DifficultyLevel] = None,
        instructor_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Course]:
        """
        Get all courses for a program with filtering.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            user: Current user
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by course status
            format: Filter by course format
            difficulty: Filter by difficulty level
            instructor_id: Filter by instructor
            search: Search in title, subtitle, and description
            sort_by: Field to sort by (title, created_at, order_index, status, format)
            sort_order: Sort order (asc or desc)

        Returns:
            List of courses
        """
        # First verify program exists and user has access
        program = (
            self.db.query(Program)
            .filter(Program.id == program_id, Program.tenant_id == tenant_id, Program.deleted_at.is_(None))
            .first()
        )

        if not program:
            raise NotFoundError("Program not found")

        # Build query
        query = self.db.query(Course).filter(
            Course.program_id == program_id, Course.tenant_id == tenant_id, Course.deleted_at.is_(None)
        )

        # Apply filters
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
                Course.code.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Apply sorting
        sort_mapping = {
            "title": Course.title,
            "created_at": Course.created_at,
            "order_index": Course.order_index,
            "status": Course.status,
            "format": Course.format,
            "difficulty_level": Course.difficulty_level,
            "duration_hours": Course.duration_hours,
        }
        
        # Default to created_at if invalid sort field
        sort_field = sort_mapping.get(sort_by, Course.created_at)
        
        # Apply sort order
        if sort_order.lower() == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())

        # Apply pagination
        courses = query.offset(skip).limit(limit).all()

        logger.info(f"Retrieved {len(courses)} courses for program {program_id}")
        return courses

    def get_by_id(self, tenant_id: int, program_id: int, course_id: int, user: User) -> Course:
        """
        Get a course by ID.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            course_id: Course ID
            user: Current user

        Returns:
            Course if found

        Raises:
            NotFoundError: If course not found
        """
        course = (
            self.db.query(Course)
            .filter(
                Course.id == course_id,
                Course.program_id == program_id,
                Course.tenant_id == tenant_id,
                Course.deleted_at.is_(None),
            )
            .first()
        )

        if not course:
            raise NotFoundError("Course not found")

        return course

    def get_by_code(self, tenant_id: int, program_id: int, code: str, user: User) -> Course:
        """
        Get a course by code.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            code: Course code
            user: Current user

        Returns:
            Course if found

        Raises:
            NotFoundError: If course not found
        """
        course = (
            self.db.query(Course)
            .filter(
                Course.code == code,
                Course.program_id == program_id,
                Course.tenant_id == tenant_id,
                Course.deleted_at.is_(None),
            )
            .first()
        )

        if not course:
            raise NotFoundError(f"Course with code {code} not found")

        return course

    def create(self, tenant_id: int, program_id: int, data: Dict[str, Any], user: User) -> Course:
        """
        Create a new course.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            data: Course data
            user: Current user

        Returns:
            Created course

        Raises:
            BadRequestError: If validation fails
            ForbiddenError: If user doesn't have permission
            NotFoundError: If program not found
        """
        # Check permissions
        if user.role not in ["admin", "manager", "instructor"]:
            raise ForbiddenError("Only admins, managers, and instructors can create courses")

        # Verify program exists
        program = (
            self.db.query(Program)
            .filter(Program.id == program_id, Program.tenant_id == tenant_id, Program.deleted_at.is_(None))
            .first()
        )

        if not program:
            raise NotFoundError("Program not found")

        # Check if user has permission to add courses to this program
        if user.role == "instructor":
            # Instructors can only add courses to programs where they are coordinators
            if program.coordinator_id != user.id:
                raise ForbiddenError("You can only add courses to programs you coordinate")

        # Validate capacity
        min_participants = data.get("min_participants", 1)
        max_participants = data.get("max_participants")

        if max_participants and min_participants > max_participants:
            raise BadRequestError("Minimum participants cannot exceed maximum")

        # Set order index to be at the end
        if "order_index" not in data:
            max_order = (
                self.db.query(func.max(Course.order_index))
                .filter(Course.program_id == program_id, Course.deleted_at.is_(None))
                .scalar()
                or -1
            )
            data["order_index"] = max_order + 1

        # Create course
        course_data = {"tenant_id": tenant_id, "program_id": program_id, "created_by": user.id, **data}

        # Set instructor to creator if not specified and user is instructor
        if user.role == "instructor" and "instructor_id" not in course_data:
            course_data["instructor_id"] = user.id

        course = Course(**course_data)

        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)

        logger.info(f"Created course {course.code} for program {program_id}")
        return course

    def update(self, tenant_id: int, program_id: int, course_id: int, data: Dict[str, Any], user: User) -> Course:
        """
        Update a course.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
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
        course = self.get_by_id(tenant_id, program_id, course_id, user)

        # Check permissions
        if user.role == "instructor":
            # Instructors can only update courses they teach or in programs they coordinate
            if course.instructor_id != user.id and course.program.coordinator_id != user.id:
                raise ForbiddenError("You can only update courses you teach or coordinate")
        elif user.role not in ["admin", "manager"]:
            raise ForbiddenError("Insufficient permissions to update course")

        # Validate capacity if provided
        min_participants = data.get("min_participants", course.min_participants)
        max_participants = data.get("max_participants", course.max_participants)

        if max_participants and min_participants > max_participants:
            raise BadRequestError("Minimum participants cannot exceed maximum")

        # Check if reducing capacity below current enrollment
        if "max_participants" in data and max_participants:
            current_enrollment = course.get_participant_count()
            if max_participants < current_enrollment:
                raise BadRequestError(f"Cannot reduce capacity below current enrollment ({current_enrollment})")

        # Prevent changing program_id
        if "program_id" in data:
            del data["program_id"]

        # Update fields
        for key, value in data.items():
            if hasattr(course, key) and key not in ["id", "tenant_id", "created_at", "created_by"]:
                setattr(course, key, value)

        course.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(course)

        logger.info(f"Updated course {course.code}")
        return course

    def delete(self, tenant_id: int, program_id: int, course_id: int, user: User) -> bool:
        """
        Delete a course (soft delete).

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            course_id: Course ID
            user: Current user

        Returns:
            True if deleted

        Raises:
            NotFoundError: If course not found
            ForbiddenError: If user doesn't have permission
            BadRequestError: If course has active sessions or progress
        """
        course = self.get_by_id(tenant_id, program_id, course_id, user)

        # Check permissions
        if user.role not in ["admin", "manager"]:
            raise ForbiddenError("Only admins and managers can delete courses")

        # Check for active sessions
        active_sessions = [s for s in course.sessions if not s.is_completed]
        if active_sessions:
            raise BadRequestError(f"Cannot delete course with {len(active_sessions)} active sessions")

        # Check for progress records
        if course.progress_records:
            raise BadRequestError("Cannot delete course with existing progress records. Archive it instead.")

        # Soft delete
        course.deleted_at = datetime.utcnow()

        # Reorder remaining courses
        remaining_courses = (
            self.db.query(Course)
            .filter(
                Course.program_id == program_id, Course.deleted_at.is_(None), Course.order_index > course.order_index
            )
            .all()
        )

        for c in remaining_courses:
            c.order_index -= 1

        self.db.commit()

        logger.info(f"Deleted course {course.code}")
        return True

    def update_status(
        self, tenant_id: int, program_id: int, course_id: int, new_status: CourseStatus, user: User
    ) -> Course:
        """
        Update course status.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            course_id: Course ID
            new_status: New status
            user: Current user

        Returns:
            Updated course

        Raises:
            NotFoundError: If course not found
            ForbiddenError: If user doesn't have permission
            BadRequestError: If status transition invalid
        """
        course = self.get_by_id(tenant_id, program_id, course_id, user)

        # Check permissions
        if user.role not in ["admin", "manager"]:
            if user.role == "instructor" and course.instructor_id != user.id:
                raise ForbiddenError("You can only update status of courses you teach")

        # Status transition validation
        current_status = course.status

        # Draft can go to Published or Archived
        if current_status == CourseStatus.DRAFT:
            if new_status not in [CourseStatus.PUBLISHED, CourseStatus.ARCHIVED]:
                raise BadRequestError(f"Cannot transition from {current_status.value} to {new_status.value}")

        # Published can go to Archived
        elif current_status == CourseStatus.PUBLISHED:
            if new_status != CourseStatus.ARCHIVED:
                raise BadRequestError(f"Cannot transition from {current_status.value} to {new_status.value}")

        # Archived can go back to Draft
        elif current_status == CourseStatus.ARCHIVED:
            if new_status != CourseStatus.DRAFT:
                raise BadRequestError(f"Cannot transition from {current_status.value} to {new_status.value}")

        course.status = new_status
        course.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(course)

        logger.info(f"Updated course {course.code} status to {new_status.value}")
        return course

    def reorder_courses(
        self, tenant_id: int, program_id: int, course_orders: Dict[int, int], user: User
    ) -> List[Course]:
        """
        Reorder courses within a program.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            course_orders: Dictionary of course_id: new_order_index
            user: Current user

        Returns:
            Reordered courses

        Raises:
            NotFoundError: If any course not found
            ForbiddenError: If user doesn't have permission
            BadRequestError: If order indices invalid
        """
        # Check permissions
        if user.role not in ["admin", "manager"]:
            raise ForbiddenError("Only admins and managers can reorder courses")

        # Get all courses for the program
        courses = (
            self.db.query(Course)
            .filter(Course.program_id == program_id, Course.tenant_id == tenant_id, Course.deleted_at.is_(None))
            .all()
        )

        # Validate all course IDs exist
        course_ids = {c.id for c in courses}
        requested_ids = set(course_orders.keys())

        if not requested_ids.issubset(course_ids):
            raise BadRequestError("Invalid course IDs provided")

        # Validate order indices
        order_indices = list(course_orders.values())
        if len(order_indices) != len(set(order_indices)):
            raise BadRequestError("Duplicate order indices provided")

        if min(order_indices) < 0:
            raise BadRequestError("Order indices must be non-negative")

        # Update order indices
        for course_id, new_order in course_orders.items():
            course = next(c for c in courses if c.id == course_id)
            course.order_index = new_order
            course.updated_at = datetime.utcnow()

        self.db.commit()

        # Return courses in new order
        courses.sort(key=lambda c: c.order_index)

        logger.info(f"Reordered {len(course_orders)} courses in program {program_id}")
        return courses

    def duplicate_course(
        self,
        tenant_id: int,
        program_id: int,
        course_id: int,
        new_program_id: Optional[int],
        new_title: Optional[str],
        user: User,
    ) -> Course:
        """
        Duplicate a course.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            course_id: Course ID
            new_program_id: Target program ID (if different)
            new_title: New title for the duplicate
            user: Current user

        Returns:
            Duplicated course

        Raises:
            NotFoundError: If course or target program not found
            ForbiddenError: If user doesn't have permission
        """
        # Check permissions
        if user.role not in ["admin", "manager"]:
            raise ForbiddenError("Only admins and managers can duplicate courses")

        # Get original course
        course = self.get_by_id(tenant_id, program_id, course_id, user)

        # Verify target program if different
        target_program_id = new_program_id or program_id
        if target_program_id != program_id:
            target_program = (
                self.db.query(Program)
                .filter(Program.id == target_program_id, Program.tenant_id == tenant_id, Program.deleted_at.is_(None))
                .first()
            )

            if not target_program:
                raise NotFoundError("Target program not found")

        # Create duplicate
        duplicate = course.duplicate(new_program_id=target_program_id)

        if new_title:
            duplicate.title = new_title

        duplicate.created_by = user.id

        self.db.add(duplicate)
        self.db.commit()
        self.db.refresh(duplicate)

        logger.info(f"Duplicated course {course.code} as {duplicate.code}")
        return duplicate

    def get_statistics(self, tenant_id: int, program_id: int, user: User) -> Dict[str, Any]:
        """
        Get course statistics for a program.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID
            user: Current user

        Returns:
            Statistics dictionary
        """
        # Verify program exists
        program = (
            self.db.query(Program)
            .filter(Program.id == program_id, Program.tenant_id == tenant_id, Program.deleted_at.is_(None))
            .first()
        )

        if not program:
            raise NotFoundError("Program not found")

        # Total courses by status
        status_counts = (
            self.db.query(Course.status, func.count(Course.id))
            .filter(Course.program_id == program_id, Course.tenant_id == tenant_id, Course.deleted_at.is_(None))
            .group_by(Course.status)
            .all()
        )

        # Total courses by format
        format_counts = (
            self.db.query(Course.format, func.count(Course.id))
            .filter(Course.program_id == program_id, Course.tenant_id == tenant_id, Course.deleted_at.is_(None))
            .group_by(Course.format)
            .all()
        )

        # Total courses by difficulty
        difficulty_counts = (
            self.db.query(Course.difficulty_level, func.count(Course.id))
            .filter(Course.program_id == program_id, Course.tenant_id == tenant_id, Course.deleted_at.is_(None))
            .group_by(Course.difficulty_level)
            .all()
        )

        # Calculate total duration
        total_duration = (
            self.db.query(func.sum(Course.duration_hours))
            .filter(Course.program_id == program_id, Course.tenant_id == tenant_id, Course.deleted_at.is_(None))
            .scalar()
            or 0
        )

        # Count courses with assessments
        assessment_count = (
            self.db.query(func.count(Course.id))
            .filter(
                Course.program_id == program_id,
                Course.tenant_id == tenant_id,
                Course.deleted_at.is_(None),
                Course.has_assessment.is_(True),
            )
            .scalar()
        )

        return {
            "total_courses": sum(count for _, count in status_counts),
            "status_breakdown": {status.value: count for status, count in status_counts},
            "format_breakdown": {format.value: count for format, count in format_counts},
            "difficulty_breakdown": {level.value: count for level, count in difficulty_counts},
            "total_duration_hours": float(total_duration),
            "courses_with_assessment": assessment_count,
            "program_title": program.title,
            "program_code": program.code,
        }
