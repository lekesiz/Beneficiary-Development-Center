"""Simple unit tests for CourseService to test basic functionality."""
import pytest
from unittest.mock import Mock, patch
from datetime import date, timedelta
from app.services.course_service import CourseService
from app.models.course import CourseStatus, CourseFormat, DifficultyLevel
from app.models.user import User
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


def test_course_service_initialization():
    """Test CourseService initialization."""
    mock_db = Mock()
    service = CourseService(mock_db)
    assert service.db == mock_db


def test_get_all_courses_basic():
    """Test basic get_all functionality."""
    mock_db = Mock()
    service = CourseService(mock_db)
    
    # Mock user
    user = Mock(spec=User)
    user.role = 'admin'
    
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


def test_create_course_validation():
    """Test course creation validation."""
    mock_db = Mock()
    service = CourseService(mock_db)
    
    # Mock admin user
    admin_user = Mock(spec=User)
    admin_user.id = 1
    admin_user.role = 'admin'
    
    # Test missing program_id
    data = {
        'title': 'Test Course'
        # Missing program_id
    }
    
    with pytest.raises(BadRequestError, match="Program ID is required"):
        service.create(1, data, admin_user)


def test_create_course_permission_check():
    """Test course creation permission check."""
    mock_db = Mock()
    service = CourseService(mock_db)
    
    # Mock staff user (insufficient permissions)
    staff_user = Mock(spec=User)
    staff_user.role = 'staff'
    
    data = {'program_id': 1, 'title': 'Test Course'}
    
    with pytest.raises(ForbiddenError):
        service.create(1, data, staff_user)


def test_instructor_can_create_course():
    """Test that instructors can create courses."""
    mock_db = Mock()
    service = CourseService(mock_db)
    
    # Mock instructor user
    instructor_user = Mock(spec=User)
    instructor_user.id = 3
    instructor_user.role = 'instructor'
    
    # Mock program exists
    mock_program = Mock()
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_program
    mock_query.scalar.return_value = 0  # Max order index
    mock_db.query.return_value = mock_query
    
    data = {
        'program_id': 1,
        'title': 'Instructor Course'
    }
    
    created_course = Mock()
    
    with patch('app.services.course_service.Course') as MockCourse:
        MockCourse.return_value = created_course
        
        result = service.create(1, data, instructor_user)
        
        # Should succeed - instructors can create courses
        assert result == created_course
        
        # Verify instructor_id was set to current user
        call_args = MockCourse.call_args[1]
        assert call_args['instructor_id'] == instructor_user.id


if __name__ == '__main__':
    pytest.main([__file__])