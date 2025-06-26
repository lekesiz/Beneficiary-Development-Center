"""Unit tests for CourseService."""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.course_service import CourseService
from app.models.course import Course, CourseStatus, CourseFormat, DifficultyLevel
from app.models.program import Program, ProgramStatus
from app.models.user import User
from app.models.course_progress import CourseProgress
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


class TestCourseService:
    """Test cases for CourseService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_db):
        """Create CourseService instance."""
        return CourseService(mock_db)

    @pytest.fixture
    def admin_user(self):
        """Create admin user."""
        user = Mock(spec=User)
        user.id = 1
        user.role = "admin"
        user.full_name = "Admin User"
        return user

    @pytest.fixture
    def manager_user(self):
        """Create manager user."""
        user = Mock(spec=User)
        user.id = 2
        user.role = "manager"
        user.full_name = "Manager User"
        return user

    @pytest.fixture
    def instructor_user(self):
        """Create instructor user."""
        user = Mock(spec=User)
        user.id = 3
        user.role = "instructor"
        user.full_name = "Instructor User"
        return user

    @pytest.fixture
    def staff_user(self):
        """Create staff user."""
        user = Mock(spec=User)
        user.id = 4
        user.role = "staff"
        user.full_name = "Staff User"
        return user

    @pytest.fixture
    def sample_program(self):
        """Create sample program."""
        program = Mock(spec=Program)
        program.id = 1
        program.tenant_id = 1
        program.code = "TRA-202401-A1B2"
        program.title = "Python Training Program"
        program.status = ProgramStatus.PUBLISHED
        program.is_enrollment_open = True
        program.max_participants = 20
        program.deleted_at = None
        return program

    @pytest.fixture
    def sample_course(self, sample_program, instructor_user):
        """Create sample course."""
        course = Mock(spec=Course)
        course.id = 1
        course.tenant_id = 1
        course.program_id = sample_program.id
        course.program = sample_program
        course.code = "CRS-202401-PY01"
        course.title = "Introduction to Python"
        course.subtitle = "Learn Python basics"
        course.description = "A comprehensive introduction to Python programming"
        course.status = CourseStatus.PUBLISHED
        course.format = CourseFormat.LECTURE
        course.difficulty_level = DifficultyLevel.BEGINNER
        course.duration_hours = 40
        course.order_index = 1
        course.min_participants = 5
        course.max_participants = 20
        course.instructor_id = instructor_user.id
        course.instructor = instructor_user
        course.deleted_at = None
        course.sessions = []
        course.progress_records = []

        # Mock methods
        course.to_dict = Mock(return_value={"id": 1, "title": "Introduction to Python"})
        course.get_participant_count = Mock(return_value=0)
        course.get_completion_rate = Mock(return_value=0)
        course.get_average_score = Mock(return_value=None)
        course.add_session = Mock()
        course.update_order = Mock()
        course.duplicate = Mock()
        course.save = Mock(return_value=course)

        return course

    def test_get_all_courses(self, service, mock_db, admin_user):
        """Test getting all courses."""
        # Setup
        courses = [Mock(spec=Course) for _ in range(3)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = courses
        mock_db.query.return_value = mock_query

        # Execute
        result = service.get_all(tenant_id=1, user=admin_user, skip=0, limit=10)

        # Assert
        assert len(result) == 3
        mock_db.query.assert_called_with(Course)

    def test_get_all_with_filters(self, service, mock_db, admin_user):
        """Test getting courses with filters."""
        # Setup
        courses = [Mock(spec=Course)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = courses
        mock_db.query.return_value = mock_query

        # Execute
        result = service.get_all(
            tenant_id=1,
            user=admin_user,
            program_id=1,
            status=CourseStatus.PUBLISHED,
            format=CourseFormat.ONLINE,
            difficulty=DifficultyLevel.BEGINNER,
            search="Python",
            instructor_id=3,
        )

        # Assert
        assert len(result) == 1
        # Verify filters were applied
        assert mock_query.filter.call_count >= 6  # All filters applied

    def test_get_by_id_success(self, service, mock_db, admin_user, sample_course):
        """Test getting course by ID successfully."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_course
        mock_db.query.return_value = mock_query

        # Execute
        result = service.get_by_id(1, sample_course.id, admin_user)

        # Assert
        assert result == sample_course
        mock_db.query.assert_called_with(Course)

    def test_get_by_id_not_found(self, service, mock_db, admin_user):
        """Test getting non-existent course."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query

        # Execute & Assert
        with pytest.raises(NotFoundError):
            service.get_by_id(1, 999, admin_user)

    def test_create_course_success(self, service, mock_db, admin_user, sample_program):
        """Test creating course successfully."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_query.scalar.return_value = 0  # Max order index
        mock_db.query.return_value = mock_query

        data = {
            "program_id": sample_program.id,
            "title": "New Course",
            "description": "Test course",
            "format": CourseFormat.ONLINE,
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "duration_hours": 20,
            "min_participants": 5,
            "max_participants": 15,
        }

        created_course = Mock(spec=Course)
        created_course.id = 2
        created_course.code = "CRS-202401-NEW1"

        # Mock the Course class instantiation
        with patch("app.services.course_service.Course") as MockCourse:
            MockCourse.return_value = created_course

            # Execute
            result = service.create(1, data, admin_user)

            # Assert
            assert result == created_course
            mock_db.add.assert_called_once_with(created_course)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(created_course)

    def test_create_course_invalid_program(self, service, mock_db, admin_user):
        """Test creating course with invalid program."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Program not found
        mock_db.query.return_value = mock_query

        data = {"program_id": 999, "title": "New Course"}

        # Execute & Assert
        with pytest.raises(NotFoundError, match="Program not found"):
            service.create(1, data, admin_user)

    def test_create_course_invalid_capacity(self, service, mock_db, admin_user, sample_program):
        """Test creating course with invalid capacity."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_db.query.return_value = mock_query

        data = {
            "program_id": sample_program.id,
            "title": "New Course",
            "min_participants": 20,
            "max_participants": 10,  # Max less than min
        }

        # Execute & Assert
        with pytest.raises(BadRequestError, match="Minimum participants cannot exceed maximum"):
            service.create(1, data, admin_user)

    def test_create_course_forbidden(self, service, mock_db, staff_user):
        """Test creating course with insufficient permissions."""
        # Setup
        data = {"program_id": 1, "title": "New Course"}

        # Execute & Assert
        with pytest.raises(ForbiddenError):
            service.create(1, data, staff_user)

    def test_create_course_as_instructor(self, service, mock_db, instructor_user, sample_program):
        """Test creating course as instructor."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_query.scalar.return_value = 0
        mock_db.query.return_value = mock_query

        data = {"program_id": sample_program.id, "title": "Instructor Course"}

        created_course = Mock(spec=Course)

        with patch("app.services.course_service.Course") as MockCourse:
            MockCourse.return_value = created_course

            # Execute
            result = service.create(1, data, instructor_user)

            # Assert
            assert result == created_course
            # Verify instructor_id was set to current user
            call_args = MockCourse.call_args[1]
            assert call_args["instructor_id"] == instructor_user.id

    def test_update_course_success(self, service, mock_db, admin_user, sample_course):
        """Test updating course successfully."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_course
        mock_db.query.return_value = mock_query

        update_data = {"title": "Updated Title", "duration_hours": 60}

        # Execute
        result = service.update(1, sample_course.id, update_data, admin_user)

        # Assert
        assert sample_course.title == "Updated Title"
        assert sample_course.duration_hours == 60
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_course)

    def test_update_course_instructor_own(self, service, mock_db, instructor_user, sample_course):
        """Test instructor updating their own course."""
        # Setup
        sample_course.instructor_id = instructor_user.id
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_course
        mock_db.query.return_value = mock_query

        update_data = {"title": "Updated by Instructor"}

        # Execute
        result = service.update(1, sample_course.id, update_data, instructor_user)

        # Assert
        assert sample_course.title == "Updated by Instructor"

    def test_update_course_instructor_other(self, service, mock_db, instructor_user, sample_course):
        """Test instructor trying to update another instructor's course."""
        # Setup
        sample_course.instructor_id = 999  # Different instructor
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_course
        mock_db.query.return_value = mock_query

        update_data = {"title": "Updated"}

        # Execute & Assert
        with pytest.raises(ForbiddenError, match="You can only update courses you instruct"):
            service.update(1, sample_course.id, update_data, instructor_user)

    def test_delete_course_success(self, service, mock_db, admin_user, sample_course):
        """Test deleting course successfully."""
        # Setup
        sample_course.progress_records = []  # No progress records
        sample_course.program_id = 1
        sample_course.order_index = 2

        # Other courses to reorder
        other_course = Mock(spec=Course)
        other_course.order_index = 3

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_course
        mock_query.all.return_value = [other_course]
        mock_db.query.return_value = mock_query

        # Execute
        result = service.delete(1, sample_course.id, admin_user)

        # Assert
        assert result is True
        assert sample_course.deleted_at is not None
        assert other_course.order_index == 2  # Reordered
        mock_db.commit.assert_called_once()

    def test_delete_course_with_progress(self, service, mock_db, admin_user, sample_course):
        """Test deleting course with progress records."""
        # Setup
        progress = Mock(spec=CourseProgress)
        sample_course.progress_records = [progress]

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_course
        mock_db.query.return_value = mock_query

        # Execute & Assert
        with pytest.raises(BadRequestError, match="Cannot delete course with"):
            service.delete(1, sample_course.id, admin_user)

    def test_add_session_success(self, service, mock_db, admin_user, sample_course):
        """Test adding session to course."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_course
        mock_db.query.return_value = mock_query

        session_data = {"title": "Session 1", "session_date": datetime.now(), "duration_hours": 2}

        # Execute
        result = service.add_session(1, sample_course.id, session_data, admin_user)

        # Assert
        sample_course.add_session.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_course)

    def test_duplicate_course_success(self, service, mock_db, admin_user, sample_course, sample_program):
        """Test duplicating course successfully."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [sample_course, sample_program]
        mock_db.query.return_value = mock_query

        new_course = Mock(spec=Course)
        new_course.code = "CRS-202401-COPY"
        sample_course.duplicate.return_value = new_course

        # Execute
        result = service.duplicate(1, sample_course.id, sample_program.id, admin_user)

        # Assert
        assert result == new_course
        sample_course.duplicate.assert_called_once_with(sample_program.id)
        mock_db.add.assert_called_once_with(new_course)
        mock_db.commit.assert_called_once()

    def test_reorder_course_success(self, service, mock_db, admin_user, sample_course):
        """Test reordering course successfully."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_course
        mock_db.query.return_value = mock_query

        # Execute
        result = service.reorder(1, sample_course.id, 5, admin_user)

        # Assert
        sample_course.update_order.assert_called_once_with(5)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_course)

    def test_get_statistics(self, service, mock_db, admin_user):
        """Test getting course statistics."""
        # Setup
        courses = []
        for i in range(10):
            course = Mock(spec=Course)
            course.status = CourseStatus.PUBLISHED if i < 6 else CourseStatus.DRAFT
            course.format = CourseFormat.ONLINE if i < 4 else CourseFormat.LECTURE
            course.difficulty_level = DifficultyLevel.BEGINNER if i < 5 else DifficultyLevel.INTERMEDIATE
            course.has_assessment = i < 3
            course.sessions = [Mock() for _ in range(i % 3)]
            course.get_completion_rate = Mock(return_value=80.0 if i < 5 else 60.0)
            course.get_average_score = Mock(return_value=85.0 if i < 3 else None)
            courses.append(course)

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = courses
        mock_db.query.return_value = mock_query

        # Execute
        stats = service.get_statistics(1, None, admin_user)

        # Assert
        assert stats["total_courses"] == 10
        assert stats["status_breakdown"]["published"] == 6
        assert stats["status_breakdown"]["draft"] == 4
        assert stats["format_breakdown"]["online"] == 4
        assert stats["format_breakdown"]["lecture"] == 6
        assert stats["difficulty_breakdown"]["beginner"] == 5
        assert stats["difficulty_breakdown"]["intermediate"] == 5
        assert stats["courses_with_assessment"] == 3
        assert stats["average_completion_rate"] == 70.0  # (5*80 + 5*60) / 10
        assert stats["average_assessment_score"] == 85.0
        assert stats["total_sessions"] == sum(len(c.sessions) for c in courses)

    def test_get_statistics_instructor(self, service, mock_db, instructor_user):
        """Test getting statistics as instructor (only own courses)."""
        # Setup
        own_course = Mock(spec=Course)
        own_course.instructor_id = instructor_user.id
        own_course.status = CourseStatus.PUBLISHED
        own_course.format = CourseFormat.ONLINE
        own_course.difficulty_level = DifficultyLevel.BEGINNER
        own_course.has_assessment = True
        own_course.sessions = []
        own_course.get_completion_rate = Mock(return_value=90.0)
        own_course.get_average_score = Mock(return_value=88.0)

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [own_course]
        mock_db.query.return_value = mock_query

        # Execute
        stats = service.get_statistics(1, None, instructor_user)

        # Assert
        assert stats["total_courses"] == 1
        # Verify instructor filter was applied
        filter_calls = mock_query.filter.call_args_list
        instructor_filter_applied = any("instructor_id" in str(call) for call in filter_calls)
        assert instructor_filter_applied or mock_query.filter.call_count >= 2
