"""Simple unit tests for ProgramService to test basic functionality."""

import pytest
from unittest.mock import Mock, patch
from datetime import date, timedelta
from app.services.program_service import ProgramService
from app.models.program import ProgramStatus, ProgramType
from app.models.user import User
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


def test_program_service_initialization():
    """Test ProgramService initialization."""
    mock_db = Mock()
    service = ProgramService(mock_db)
    assert service.db == mock_db


def test_get_all_programs_basic():
    """Test basic get_all functionality."""
    mock_db = Mock()
    service = ProgramService(mock_db)

    # Mock user
    user = Mock(spec=User)
    user.role = "admin"

    # Mock query chain
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []

    result = service.get_all(tenant_id=1, user=user)

    assert result == []
    mock_db.query.assert_called_once()


def test_create_program_validation():
    """Test program creation validation."""
    mock_db = Mock()
    service = ProgramService(mock_db)

    # Mock admin user
    admin_user = Mock(spec=User)
    admin_user.id = 1
    admin_user.role = "admin"

    # Test invalid dates
    data = {
        "title": "Test Program",
        "start_date": date.today() + timedelta(days=90),
        "end_date": date.today() + timedelta(days=30),  # End before start
    }

    with pytest.raises(BadRequestError, match="Start date must be before end date"):
        service.create(1, data, admin_user)


def test_create_program_permission_check():
    """Test program creation permission check."""
    mock_db = Mock()
    service = ProgramService(mock_db)

    # Mock staff user (insufficient permissions)
    staff_user = Mock(spec=User)
    staff_user.role = "staff"

    data = {"title": "Test Program"}

    with pytest.raises(ForbiddenError):
        service.create(1, data, staff_user)


if __name__ == "__main__":
    pytest.main([__file__])
