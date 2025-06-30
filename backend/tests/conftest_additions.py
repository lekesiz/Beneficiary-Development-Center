"""
Additional fixtures to be added to conftest.py for comprehensive testing
"""

import pytest
from datetime import datetime, timedelta
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.report import Report, ReportType, ReportStatus
from app.models.evaluation import Evaluation, Question, EvaluationAttempt, QuestionResponse
from app.models.learning_path import LearningPath, LearningMilestone
from app.models.coach_note import CoachNote, NoteCategory, NotePriority
from app.models.program import Program
from app.models.course import Course


@pytest.fixture
def sample_notification(db_session, test_tenant, admin_user):
    """Create a sample notification"""
    notification = Notification(
        tenant_id=test_tenant.id,
        user_id=admin_user.id,
        type=NotificationType.INFO,
        priority=NotificationPriority.MEDIUM,
        title="Test Notification",
        message="This is a test notification",
        data={"test": True}
    )
    db_session.add(notification)
    db_session.commit()
    return notification


@pytest.fixture
def sample_report(db_session, test_tenant, admin_user):
    """Create a sample report"""
    report = Report(
        tenant_id=test_tenant.id,
        created_by=admin_user.id,
        type=ReportType.PROGRESS,
        name="Test Progress Report",
        description="Test report description",
        status=ReportStatus.COMPLETED,
        parameters={"period": "month"},
        result_data={"total": 100}
    )
    db_session.add(report)
    db_session.commit()
    return report


@pytest.fixture
def sample_program(db_session, test_tenant):
    """Create a sample program"""
    program = Program(
        tenant_id=test_tenant.id,
        name="Test Program",
        description="Test program description",
        code="TST101",
        category="technical",
        status="active",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=90)
    )
    db_session.add(program)
    db_session.commit()
    return program


@pytest.fixture
def sample_course(db_session, test_tenant, sample_program, trainer_user):
    """Create a sample course"""
    course = Course(
        tenant_id=test_tenant.id,
        program_id=sample_program.id,
        title="Test Course",
        description="Test course description",
        code="CRS101",
        instructor_id=trainer_user.id,
        status="active",
        format="online",
        difficulty_level="beginner",
        duration_hours=40
    )
    db_session.add(course)
    db_session.commit()
    return course


@pytest.fixture
def sample_evaluation(db_session, test_tenant, admin_user, sample_course):
    """Create a sample evaluation"""
    evaluation = Evaluation(
        tenant_id=test_tenant.id,
        created_by=admin_user.id,
        course_id=sample_course.id,
        title="Test Evaluation",
        description="Test evaluation description",
        status="active",
        total_questions=5,
        total_points=100.0,
        passing_score=70.0,
        max_attempts=3,
        time_limit_minutes=60
    )
    db_session.add(evaluation)
    db_session.commit()
    
    # Add sample questions
    questions = [
        Question(
            tenant_id=test_tenant.id,
            evaluation_id=evaluation.id,
            question_text="What is Python?",
            question_type="multiple_choice",
            points=20.0,
            order_index=1,
            question_data={
                "options": ["A language", "A snake", "Both", "Neither"],
                "correct_answer": 2
            }
        ),
        Question(
            tenant_id=test_tenant.id,
            evaluation_id=evaluation.id,
            question_text="Python is interpreted",
            question_type="true_false",
            points=20.0,
            order_index=2,
            question_data={"correct_answer": True}
        )
    ]
    
    for question in questions:
        db_session.add(question)
    
    db_session.commit()
    return evaluation


@pytest.fixture
def sample_learning_path(db_session, test_tenant, student_user):
    """Create a sample learning path with milestones"""
    path = LearningPath(
        tenant_id=test_tenant.id,
        user_id=student_user.id,
        title="Sample Learning Path",
        description="A test learning path",
        status="accepted",
        goals=["Goal 1", "Goal 2"]
    )
    db_session.add(path)
    db_session.commit()
    
    # Add milestones
    milestones = [
        LearningMilestone(
            tenant_id=test_tenant.id,
            learning_path_id=path.id,
            title="Milestone 1",
            description="First milestone",
            week_number=1,
            estimated_hours=10
        ),
        LearningMilestone(
            tenant_id=test_tenant.id,
            learning_path_id=path.id,
            title="Milestone 2",
            description="Second milestone",
            week_number=2,
            estimated_hours=15
        )
    ]
    
    for milestone in milestones:
        db_session.add(milestone)
    
    db_session.commit()
    return path


@pytest.fixture
def auth_headers_factory(api_client):
    """Factory for creating auth headers for any user"""
    def _get_headers(user):
        response = api_client.post(
            '/api/v1/auth/login',
            json={
                'email': user.email,
                'password': 'testpass123'  # Assumes all test users have this password
            }
        )
        token = response.json['access_token']
        return {
            'Authorization': f'Bearer {token}',
            'X-Tenant-ID': str(user.tenant_id)
        }
    return _get_headers


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis client for testing"""
    mock = mocker.Mock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    mock.exists.return_value = False
    mock.expire.return_value = True
    return mock


@pytest.fixture
def mock_socketio(mocker):
    """Mock SocketIO for testing"""
    mock = mocker.Mock()
    mock.emit.return_value = None
    mock.send.return_value = None
    return mock


# Parametrized fixtures for testing different scenarios
@pytest.fixture(params=['admin', 'trainer', 'student'])
def user_with_role(request, admin_user, trainer_user, student_user):
    """Parametrized fixture that provides users with different roles"""
    users = {
        'admin': admin_user,
        'trainer': trainer_user,
        'student': student_user
    }
    return users[request.param]


@pytest.fixture(params=['active', 'inactive', 'suspended'])
def user_with_status(request, db_session, test_tenant):
    """Create users with different statuses"""
    user = User(
        email=f"{request.param}@example.com",
        username=f"{request.param}_user",
        full_name=f"{request.param.title()} User",
        tenant_id=test_tenant.id,
        is_active=request.param == 'active',
        status=request.param
    )
    user.set_password("testpass123")
    db_session.add(user)
    db_session.commit()
    return user