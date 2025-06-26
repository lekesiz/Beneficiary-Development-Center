"""Unit tests for ProgramService."""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from app.services.program_service import ProgramService
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.user import User
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


class TestProgramService:
    """Test cases for ProgramService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_db, app_context):
        """Create ProgramService instance."""
        return ProgramService(mock_db)

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
    def staff_user(self):
        """Create staff user."""
        user = Mock(spec=User)
        user.id = 3
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
        program.title = "Python Programming"
        program.description = "Learn Python programming"
        program.status = ProgramStatus.PUBLISHED
        program.program_type = ProgramType.TRAINING
        program.start_date = date.today() + timedelta(days=30)
        program.end_date = date.today() + timedelta(days=90)
        program.enrollment_start = date.today()
        program.enrollment_end = date.today() + timedelta(days=20)
        program.min_participants = 5
        program.max_participants = 20
        program.deleted_at = None
        program.enrollments = []
        program.courses = []

        # Mock methods
        program.to_dict = Mock(return_value={"id": 1, "title": "Python Programming"})
        program.get_enrollment_count = Mock(return_value=0)
        program.update_status = Mock()
        program.save = Mock(return_value=program)

        return program

    def test_get_all_programs(self, service, mock_db, admin_user):
        """Test getting all programs."""
        # Setup
        programs = [Mock(spec=Program) for _ in range(3)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = programs
        mock_db.query.return_value = mock_query

        # Execute
        result = service.get_all(tenant_id=1, user=admin_user, skip=0, limit=10)

        # Assert
        assert len(result) == 3
        mock_db.query.assert_called_with(Program)

    def test_get_all_with_filters(self, service, mock_db, admin_user):
        """Test getting programs with filters."""
        # Setup
        programs = [Mock(spec=Program)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = programs
        mock_db.query.return_value = mock_query

        # Execute
        result = service.get_all(
            tenant_id=1,
            user=admin_user,
            status=ProgramStatus.ACTIVE,
            program_type=ProgramType.TRAINING,
            search="Python",
            upcoming_only=True,
        )

        # Assert
        assert len(result) == 1
        # Verify filters were applied
        assert mock_query.filter.call_count >= 3  # tenant, deleted_at, and other filters

    def test_get_by_id_success(self, service, mock_db, admin_user, sample_program):
        """Test getting program by ID successfully."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_db.query.return_value = mock_query

        # Execute
        result = service.get_by_id(1, sample_program.id, admin_user)

        # Assert
        assert result == sample_program
        mock_db.query.assert_called_with(Program)

    def test_get_by_id_not_found(self, service, mock_db, admin_user):
        """Test getting non-existent program."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query

        # Execute & Assert
        with pytest.raises(NotFoundError):
            service.get_by_id(1, 999, admin_user)

    def test_create_program_success(self, service, mock_db, admin_user):
        """Test creating program successfully."""
        # Setup
        data = {
            "title": "New Program",
            "description": "Test program",
            "start_date": date.today() + timedelta(days=30),
            "end_date": date.today() + timedelta(days=90),
            "min_participants": 5,
            "max_participants": 20,
        }

        created_program = Mock(spec=Program)
        created_program.id = 1
        created_program.code = "TRA-202401-NEW1"

        # Mock the Program class instantiation
        from unittest.mock import patch
        with patch("app.services.program_service.Program") as MockProgram:
            MockProgram.return_value = created_program

            # Execute
            result = service.create(1, data, admin_user)

            # Assert
            assert result == created_program
            mock_db.add.assert_called_once_with(created_program)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(created_program)

    def test_create_program_invalid_dates(self, service, mock_db, admin_user):
        """Test creating program with invalid dates."""
        # Setup
        data = {
            "title": "New Program",
            "start_date": date.today() + timedelta(days=90),
            "end_date": date.today() + timedelta(days=30),  # End before start
        }

        # Execute & Assert
        with pytest.raises(BadRequestError, match="Start date must be before end date"):
            service.create(1, data, admin_user)

    def test_create_program_invalid_capacity(self, service, mock_db, admin_user):
        """Test creating program with invalid capacity."""
        # Setup
        data = {
            "title": "New Program",
            "start_date": date.today() + timedelta(days=30),
            "end_date": date.today() + timedelta(days=90),
            "min_participants": 20,
            "max_participants": 10,  # Max less than min
        }

        # Execute & Assert
        with pytest.raises(BadRequestError, match="Minimum participants cannot exceed maximum"):
            service.create(1, data, admin_user)

    def test_create_program_forbidden(self, service, mock_db, staff_user):
        """Test creating program with insufficient permissions."""
        # Setup
        data = {"title": "New Program"}

        # Execute & Assert
        with pytest.raises(ForbiddenError):
            service.create(1, data, staff_user)

    def test_update_program_success(self, service, mock_db, admin_user, sample_program):
        """Test updating program successfully."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_db.query.return_value = mock_query

        update_data = {"title": "Updated Title", "max_participants": 30}

        # Execute
        result = service.update(1, sample_program.id, update_data, admin_user)

        # Assert
        assert sample_program.title == "Updated Title"
        assert sample_program.max_participants == 30
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_program)

    def test_update_program_reduce_capacity_error(self, service, mock_db, admin_user, sample_program):
        """Test updating program with capacity below current enrollment."""
        # Setup
        sample_program.get_enrollment_count.return_value = 15
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_db.query.return_value = mock_query

        update_data = {"max_participants": 10}  # Below current enrollment

        # Execute & Assert
        with pytest.raises(BadRequestError, match="Cannot reduce capacity below current enrollment"):
            service.update(1, sample_program.id, update_data, admin_user)

    def test_delete_program_success(self, service, mock_db, admin_user, sample_program):
        """Test deleting program successfully."""
        # Setup
        sample_program.enrollments = []  # No active enrollments
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_db.query.return_value = mock_query

        # Execute
        result = service.delete(1, sample_program.id, admin_user)

        # Assert
        assert result is True
        assert sample_program.deleted_at is not None
        mock_db.commit.assert_called_once()

    def test_delete_program_with_active_enrollments(self, service, mock_db, admin_user, sample_program):
        """Test deleting program with active enrollments."""
        # Setup
        active_enrollment = Mock(spec=Enrollment)
        active_enrollment.status = EnrollmentStatus.ENROLLED
        sample_program.enrollments = [active_enrollment]

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_db.query.return_value = mock_query

        # Execute & Assert
        with pytest.raises(BadRequestError, match="Cannot delete program with"):
            service.delete(1, sample_program.id, admin_user)

    def test_delete_program_forbidden(self, service, mock_db, manager_user, sample_program):
        """Test deleting program with insufficient permissions."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_db.query.return_value = mock_query

        # Execute & Assert
        with pytest.raises(ForbiddenError):
            service.delete(1, sample_program.id, manager_user)

    def test_update_status_success(self, service, mock_db, admin_user, sample_program):
        """Test updating program status successfully."""
        # Setup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_db.query.return_value = mock_query

        # Execute
        result = service.update_status(1, sample_program.id, ProgramStatus.ACTIVE, admin_user)

        # Assert
        sample_program.update_status.assert_called_once_with(ProgramStatus.ACTIVE)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_program)

    def test_update_status_invalid_transition(self, service, mock_db, admin_user, sample_program):
        """Test updating program status with invalid transition."""
        # Setup
        sample_program.update_status.side_effect = ValueError("Invalid transition")
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_program
        mock_db.query.return_value = mock_query

        # Execute & Assert
        with pytest.raises(BadRequestError, match="Invalid transition"):
            service.update_status(1, sample_program.id, ProgramStatus.COMPLETED, admin_user)

    def test_get_statistics(self, service, mock_db, admin_user):
        """Test getting program statistics."""
        # Setup
        # Status counts
        status_counts = [(ProgramStatus.DRAFT, 2), (ProgramStatus.PUBLISHED, 5), (ProgramStatus.ACTIVE, 3)]

        # Type counts
        type_counts = [(ProgramType.TRAINING, 6), (ProgramType.WORKSHOP, 4)]

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.side_effect = [status_counts, type_counts]
        mock_query.scalar.side_effect = [3, 2, 15]  # upcoming, active, enrollments

        mock_db.query.return_value = mock_query

        # Execute
        stats = service.get_statistics(1, admin_user)

        # Assert
        assert stats["total_programs"] == 10  # Sum of status counts
        assert stats["status_breakdown"]["draft"] == 2
        assert stats["status_breakdown"]["published"] == 5
        assert stats["status_breakdown"]["active"] == 3
        assert stats["type_breakdown"]["training"] == 6
        assert stats["type_breakdown"]["workshop"] == 4
        assert stats["upcoming_programs"] == 3
        assert stats["active_programs"] == 2
        assert stats["total_active_enrollments"] == 15

    def test_get_statistics_forbidden(self, service, mock_db, staff_user):
        """Test getting statistics with insufficient permissions."""
        # Execute & Assert
        with pytest.raises(ForbiddenError):
            service.get_statistics(1, staff_user)
