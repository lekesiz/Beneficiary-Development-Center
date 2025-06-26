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
        skip: int = 0,
        limit: int = 100,
        program_id: Optional[int] = None,
        status: Optional[CourseStatus] = None,
        format: Optional[CourseFormat] = None,
        difficulty: Optional[DifficultyLevel] = None,
        instructor_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Course]:
        """
        Get all courses with filtering (backward compatibility method).
        
        Args:
            tenant_id: Tenant ID
            user: Current user
            skip: Number of records to skip
            limit: Maximum number of records to return
            program_id: Filter by program ID
            status: Filter by course status
            format: Filter by course format
            difficulty: Filter by difficulty level
            instructor_id: Filter by instructor
            search: Search in title, subtitle, and description
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            
        Returns:
            List of courses
        """
        # Build query
        query = self.db.query(Course).filter(
            Course.tenant_id == tenant_id, 
            Course.deleted_at.is_(None)
        )
        
        # Apply program filter if provided
        if program_id:
            query = query.filter(Course.program_id == program_id)
            
        # Apply role-based access control
        if user.role == "instructor":
            # Instructors only see courses they teach
            query = query.filter(Course.instructor_id == user.id)
        elif user.role == "student":
            # Students only see published courses
            query = query.filter(Course.status == CourseStatus.PUBLISHED)
        # Admin, manager, staff see all courses
        
        # Apply filters
        if status:
            if isinstance(status, str):
                try:
                    status = CourseStatus(status)
                except ValueError:
                    pass  # Invalid status, ignore filter
            query = query.filter(Course.status == status)

        if format:
            if isinstance(format, str):
                try:
                    format = CourseFormat(format)
                except ValueError:
                    pass  # Invalid format, ignore filter
            query = query.filter(Course.format == format)

        if difficulty:
            if isinstance(difficulty, str):
                try:
                    difficulty = DifficultyLevel(difficulty)
                except ValueError:
                    pass  # Invalid difficulty, ignore filter
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

        logger.info(f"Retrieved {len(courses)} courses for tenant {tenant_id}")
        return courses

    def get_by_id_compat(self, tenant_id: int, course_id: int, user: User) -> Course:
        """
        Get a course by ID (backward compatibility method).
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            user: Current user
            
        Returns:
            Course if found
            
        Raises:
            NotFoundError: If course not found
        """
        from sqlalchemy.orm import joinedload
        
        course = (
            self.db.query(Course)
            .options(
                joinedload(Course.sessions),
                joinedload(Course.instructor),
                joinedload(Course.program)
            )
            .filter(
                Course.id == course_id,
                Course.tenant_id == tenant_id,
                Course.deleted_at.is_(None),
            )
            .first()
        )

        if not course:
            raise NotFoundError("Course not found")

        # Apply role-based access control
        if user.role == "instructor" and course.instructor_id != user.id:
            raise ForbiddenError("You can only access courses you teach")
        elif user.role == "student" and course.status != CourseStatus.PUBLISHED:
            raise ForbiddenError("You can only access published courses")

        return course

    def create(self, tenant_id: int, data: Dict[str, Any], user: User) -> Course:
        """
        Create a new course (backward compatibility method).
        
        Args:
            tenant_id: Tenant ID
            data: Course data (must include program_id)
            user: Current user
            
        Returns:
            Created course
            
        Raises:
            BadRequestError: If validation fails
            ForbiddenError: If user doesn't have permission
            NotFoundError: If program not found
        """
        # Extract program_id from data
        program_id = data.get("program_id")
        if not program_id:
            raise BadRequestError("program_id is required")
            
        # Call the enhanced create method
        return self.create_for_program(tenant_id, program_id, data, user)

    def create_for_program(self, tenant_id: int, program_id: int, data: Dict[str, Any], user: User) -> Course:
        """Alias for the original create method."""
        # This will be the original create logic, rename the current create method
        return self._create_original(tenant_id, program_id, data, user)

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
            if isinstance(status, str):
                try:
                    status = CourseStatus(status)
                except ValueError:
                    pass  # Invalid status, ignore filter
            query = query.filter(Course.status == status)

        if format:
            if isinstance(format, str):
                try:
                    format = CourseFormat(format)
                except ValueError:
                    pass  # Invalid format, ignore filter
            query = query.filter(Course.format == format)

        if difficulty:
            if isinstance(difficulty, str):
                try:
                    difficulty = DifficultyLevel(difficulty)
                except ValueError:
                    pass  # Invalid difficulty, ignore filter
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

    def count_by_program(
        self,
        tenant_id: int,
        program_id: int,
        filters: dict = None
    ) -> int:
        """
        Count courses for a program with filtering.

        Args:
            tenant_id: Tenant ID
            program_id: Program ID  
            filters: Dictionary of filters to apply

        Returns:
            Total count of courses matching filters
        """
        from app.models.program import Program
        
        # First verify program exists and user has access
        program = (
            self.db.query(Program)
            .filter_by(id=program_id, tenant_id=tenant_id, deleted_at=None)
            .first()
        )
        
        if not program:
            raise NotFoundError(f"Program {program_id} not found")

        # Build base query
        query = self.db.query(Course).filter_by(
            tenant_id=tenant_id,
            program_id=program_id,
            deleted_at=None
        )

        # Apply filters if provided
        if filters:
            # Apply status filter
            if 'status' in filters and filters['status']:
                if isinstance(filters['status'], str):
                    try:
                        from app.models.course import CourseStatus
                        status_enum = CourseStatus(filters['status'])
                        query = query.filter(Course.status == status_enum)
                    except ValueError:
                        pass
                else:
                    query = query.filter(Course.status == filters['status'])
            
            # Apply format filter
            if 'format' in filters and filters['format']:
                if isinstance(filters['format'], str):
                    try:
                        from app.models.course import CourseFormat
                        format_enum = CourseFormat(filters['format'])
                        query = query.filter(Course.format == format_enum)
                    except ValueError:
                        pass
                else:
                    query = query.filter(Course.format == filters['format'])
            
            # Apply difficulty filter
            if 'difficulty_level' in filters and filters['difficulty_level']:
                if isinstance(filters['difficulty_level'], str):
                    try:
                        from app.models.course import DifficultyLevel
                        difficulty_enum = DifficultyLevel(filters['difficulty_level'])
                        query = query.filter(Course.difficulty_level == difficulty_enum)
                    except ValueError:
                        pass
                else:
                    query = query.filter(Course.difficulty_level == filters['difficulty_level'])
            
            # Apply instructor filter
            if 'instructor_id' in filters and filters['instructor_id']:
                query = query.filter(Course.instructor_id == filters['instructor_id'])
            
            # Apply search filter
            if 'search' in filters and filters['search']:
                from sqlalchemy import or_
                search_pattern = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Course.title.ilike(search_pattern),
                        Course.subtitle.ilike(search_pattern),
                        Course.description.ilike(search_pattern),
                        Course.code.ilike(search_pattern)
                    )
                )

        return query.count()

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
        from sqlalchemy.orm import joinedload
        
        course = (
            self.db.query(Course)
            .options(
                joinedload(Course.sessions),
                joinedload(Course.instructor),
                joinedload(Course.program)
            )
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

    def _create_original(self, tenant_id: int, program_id: int, data: Dict[str, Any], user: User) -> Course:
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

        # Create course
        course_data = {"tenant_id": tenant_id, "program_id": program_id, "created_by": user.id, **data}

        # Set order index to be at the end if not provided or set to default
        if "order_index" not in course_data or course_data.get("order_index") == 0:
            max_order = (
                self.db.query(func.max(Course.order_index))
                .filter(Course.program_id == program_id, Course.deleted_at.is_(None))
                .scalar()
                or -1
            )
            course_data["order_index"] = max_order + 1

        # Set instructor to creator if not specified and user is instructor
        if user.role == "instructor" and "instructor_id" not in course_data:
            course_data["instructor_id"] = user.id

        # Convert string enum values to proper enum instances
        if "status" in course_data and isinstance(course_data["status"], str):
            try:
                course_data["status"] = CourseStatus(course_data["status"])
            except ValueError:
                raise BadRequestError(f"Invalid status: {course_data['status']}")
                
        if "format" in course_data and isinstance(course_data["format"], str):
            try:
                course_data["format"] = CourseFormat(course_data["format"])
            except ValueError:
                raise BadRequestError(f"Invalid format: {course_data['format']}")
                
        if "difficulty_level" in course_data and isinstance(course_data["difficulty_level"], str):
            try:
                course_data["difficulty_level"] = DifficultyLevel(course_data["difficulty_level"])
            except ValueError:
                raise BadRequestError(f"Invalid difficulty_level: {course_data['difficulty_level']}")

        course = Course(**course_data)

        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)

        logger.info(f"Created course {course.code} for program {program_id}")
        return course

    def update(self, tenant_id: int, course_id: int, data: Dict[str, Any], user: User) -> Course:
        """
        Update a course (backward compatibility method).
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            data: Update data
            user: Current user
            
        Returns:
            Updated course
        """
        # Get the course first to determine program_id
        course = self.get_by_id_compat(tenant_id, course_id, user)
        return self._update_original(tenant_id, course.program_id, course_id, data, user)

    def _update_original(self, tenant_id: int, program_id: int, course_id: int, data: Dict[str, Any], user: User) -> Course:
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

    def delete(self, tenant_id: int, course_id: int, user: User) -> bool:
        """
        Delete a course (backward compatibility method).
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            user: Current user
            
        Returns:
            True if deleted
        """
        # Get the course first to determine program_id
        course = self.get_by_id_compat(tenant_id, course_id, user)
        return self._delete_original(tenant_id, course.program_id, course_id, user)

    def _delete_original(self, tenant_id: int, program_id: int, course_id: int, user: User) -> bool:
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

    def add_session(self, tenant_id: int, course_id: int, session_data: Dict[str, Any], user: User) -> Course:
        """
        Add a session to a course (backward compatibility method).
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            session_data: Session data
            user: Current user
            
        Returns:
            Updated course
        """
        # Get the course first
        course = self.get_by_id_compat(tenant_id, course_id, user)
        
        # Check permissions
        if user.role == "instructor" and course.instructor_id != user.id:
            raise ForbiddenError("You can only add sessions to courses you teach")
        elif user.role not in ["admin", "manager", "instructor"]:
            raise ForbiddenError("Insufficient permissions to add sessions")
        
        # Add session using course model method
        course.add_session(session_data)
        
        self.db.commit()
        self.db.refresh(course)
        
        logger.info(f"Added session to course {course.code}")
        return course

    def duplicate(self, tenant_id: int, course_id: int, target_program_id: int, user: User) -> Course:
        """
        Duplicate a course (backward compatibility method).
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            target_program_id: Target program ID
            user: Current user
            
        Returns:
            Duplicated course
        """
        # Get the original course
        course = self.get_by_id_compat(tenant_id, course_id, user)
        
        # Check permissions
        if user.role not in ["admin", "manager"]:
            raise ForbiddenError("Only admins and managers can duplicate courses")
        
        # Verify target program exists
        target_program = (
            self.db.query(Program)
            .filter(Program.id == target_program_id, Program.tenant_id == tenant_id, Program.deleted_at.is_(None))
            .first()
        )
        
        if not target_program:
            raise NotFoundError("Target program not found")
        
        # Create duplicate using course model method
        duplicate = course.duplicate(new_program_id=target_program_id)
        duplicate.created_by = user.id
        
        self.db.add(duplicate)
        self.db.commit()
        self.db.refresh(duplicate)
        
        logger.info(f"Duplicated course {course.code} as {duplicate.code}")
        return duplicate

    def reorder(self, tenant_id: int, course_id: int, new_order: int, user: User) -> Course:
        """
        Reorder a course (backward compatibility method).
        
        Args:
            tenant_id: Tenant ID
            course_id: Course ID
            new_order: New order index
            user: Current user
            
        Returns:
            Updated course
        """
        # Get the course
        course = self.get_by_id_compat(tenant_id, course_id, user)
        
        # Check permissions
        if user.role not in ["admin", "manager"]:
            raise ForbiddenError("Only admins and managers can reorder courses")
        
        # Update order using course model method
        course.update_order(new_order)
        
        self.db.commit()
        self.db.refresh(course)
        
        logger.info(f"Reordered course {course.code} to position {new_order}")
        return course

    def get_statistics(self, tenant_id: int, program_id: Optional[int], user: User) -> Dict[str, Any]:
        """
        Get course statistics (backward compatibility method).
        
        Args:
            tenant_id: Tenant ID
            program_id: Program ID (optional)
            user: Current user
            
        Returns:
            Statistics dictionary
        """
        # Build query
        query = self.db.query(Course).filter(
            Course.tenant_id == tenant_id,
            Course.deleted_at.is_(None)
        )
        
        # Filter by program if provided
        if program_id:
            query = query.filter(Course.program_id == program_id)
        
        # Apply role-based filtering
        if user.role == "instructor":
            query = query.filter(Course.instructor_id == user.id)
        elif user.role == "student":
            query = query.filter(Course.status == CourseStatus.PUBLISHED)
        
        courses = query.all()
        
        # Calculate statistics
        total_courses = len(courses)
        
        status_breakdown = {}
        format_breakdown = {}
        difficulty_breakdown = {}
        courses_with_assessment = 0
        total_sessions = 0
        completion_rates = []
        assessment_scores = []
        
        for course in courses:
            # Status breakdown
            status_key = course.status.value if course.status else "unknown"
            status_breakdown[status_key] = status_breakdown.get(status_key, 0) + 1
            
            # Format breakdown
            format_key = course.format.value if course.format else "unknown"
            format_breakdown[format_key] = format_breakdown.get(format_key, 0) + 1
            
            # Difficulty breakdown
            difficulty_key = course.difficulty_level.value if course.difficulty_level else "unknown"
            difficulty_breakdown[difficulty_key] = difficulty_breakdown.get(difficulty_key, 0) + 1
            
            # Assessment count
            if course.has_assessment:
                courses_with_assessment += 1
            
            # Session count
            total_sessions += len(course.sessions)
            
            # Completion rates
            try:
                completion_rate = course.get_completion_rate()
                if completion_rate is not None:
                    completion_rates.append(completion_rate)
            except:
                pass
            
            # Assessment scores
            try:
                avg_score = course.get_average_score()
                if avg_score is not None:
                    assessment_scores.append(avg_score)
            except:
                pass
        
        # Calculate averages
        average_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        average_assessment_score = sum(assessment_scores) / len(assessment_scores) if assessment_scores else 0
        
        return {
            "total_courses": total_courses,
            "status_breakdown": status_breakdown,
            "format_breakdown": format_breakdown,
            "difficulty_breakdown": difficulty_breakdown,
            "courses_with_assessment": courses_with_assessment,
            "total_sessions": total_sessions,
            "average_completion_rate": average_completion_rate,
            "average_assessment_score": average_assessment_score,
        }
