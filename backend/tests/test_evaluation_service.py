"""
Tests for Evaluation Service
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.models.evaluation import (
    Evaluation,
    Question,
    EvaluationAttempt,
    QuestionResponse,
    EvaluationStatus,
    QuestionType,
    AttemptStatus,
)
from app.models.user import User
from app.services.evaluation_service import (
    EvaluationService,
    QuestionService,
    EvaluationAttemptService,
    QuestionResponseService,
)
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


class TestEvaluationService:
    """Test EvaluationService"""

    def setup_method(self):
        """Setup test environment"""
        self.db_mock = Mock()
        self.evaluation_service = EvaluationService(self.db_mock)

        # Mock user
        self.admin_user = Mock()
        self.admin_user.id = 1
        self.admin_user.role = "admin"
        self.admin_user.tenant_id = 1

        self.instructor_user = Mock()
        self.instructor_user.id = 2
        self.instructor_user.role = "instructor"
        self.instructor_user.tenant_id = 1

        self.student_user = Mock()
        self.student_user.id = 3
        self.student_user.role = "student"
        self.student_user.tenant_id = 1

    def test_create_evaluation_success(self):
        """Test successful evaluation creation"""
        data = {"title": "Test Evaluation", "description": "Test description", "course_id": 1}

        # Mock database operations
        self.db_mock.add = Mock()
        self.db_mock.commit = Mock()
        self.db_mock.refresh = Mock()

        result = self.evaluation_service.create(1, data, self.admin_user)

        # Assertions
        self.db_mock.add.assert_called_once()
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once()

    def test_create_evaluation_forbidden_for_student(self):
        """Test that students cannot create evaluations"""
        data = {"title": "Test Evaluation"}

        with pytest.raises(ForbiddenError):
            self.evaluation_service.create(1, data, self.student_user)

    def test_create_evaluation_missing_title(self):
        """Test evaluation creation fails without title"""
        data = {"description": "Test description"}

        with pytest.raises(BadRequestError):
            self.evaluation_service.create(1, data, self.admin_user)

    def test_update_evaluation_success(self):
        """Test successful evaluation update"""
        # Mock existing evaluation
        evaluation = Mock()
        evaluation.id = 1
        evaluation.created_by = self.admin_user.id
        evaluation.attempts = []
        evaluation.updated_at = datetime.utcnow()

        self.evaluation_service.get_by_id = Mock(return_value=evaluation)
        self.db_mock.commit = Mock()
        self.db_mock.refresh = Mock()

        data = {"title": "Updated Title"}
        result = self.evaluation_service.update(1, 1, data, self.admin_user)

        # Assertions
        assert evaluation.title == "Updated Title"
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once()

    def test_update_evaluation_with_completed_attempts_forbidden(self):
        """Test that evaluations with completed attempts cannot be updated by non-admin"""
        # Mock existing evaluation with completed attempt
        evaluation = Mock()
        evaluation.id = 1
        evaluation.created_by = self.instructor_user.id

        completed_attempt = Mock()
        completed_attempt.status = AttemptStatus.COMPLETED
        evaluation.attempts = [completed_attempt]

        self.evaluation_service.get_by_id = Mock(return_value=evaluation)

        data = {"title": "Updated Title"}

        with pytest.raises(ForbiddenError):
            self.evaluation_service.update(1, 1, data, self.instructor_user)

    def test_delete_evaluation_success(self):
        """Test successful evaluation deletion"""
        evaluation = Mock()
        evaluation.id = 1
        evaluation.created_by = self.admin_user.id
        evaluation.attempts = []

        self.evaluation_service.get_by_id = Mock(return_value=evaluation)
        self.db_mock.delete = Mock()
        self.db_mock.commit = Mock()

        result = self.evaluation_service.delete(1, 1, self.admin_user)

        assert result is True
        self.db_mock.delete.assert_called_once_with(evaluation)
        self.db_mock.commit.assert_called_once()

    def test_activate_evaluation_success(self):
        """Test successful evaluation activation"""
        evaluation = Mock()
        evaluation.id = 1
        evaluation.created_by = self.admin_user.id
        evaluation.questions = [Mock()]  # Has questions
        evaluation.status = EvaluationStatus.DRAFT

        self.evaluation_service.get_by_id = Mock(return_value=evaluation)
        self.db_mock.commit = Mock()
        self.db_mock.refresh = Mock()

        result = self.evaluation_service.activate(1, 1, self.admin_user)

        assert evaluation.status == EvaluationStatus.ACTIVE
        self.db_mock.commit.assert_called_once()

    def test_activate_evaluation_without_questions_fails(self):
        """Test that evaluation cannot be activated without questions"""
        evaluation = Mock()
        evaluation.id = 1
        evaluation.created_by = self.admin_user.id
        evaluation.questions = []  # No questions

        self.evaluation_service.get_by_id = Mock(return_value=evaluation)

        with pytest.raises(BadRequestError):
            self.evaluation_service.activate(1, 1, self.admin_user)


class TestQuestionService:
    """Test QuestionService"""

    def setup_method(self):
        """Setup test environment"""
        self.db_mock = Mock()
        self.question_service = QuestionService(self.db_mock)

        # Mock user
        self.admin_user = Mock()
        self.admin_user.id = 1
        self.admin_user.role = "admin"
        self.admin_user.tenant_id = 1

    def test_create_question_success(self):
        """Test successful question creation"""
        # Mock evaluation
        evaluation = Mock()
        evaluation.id = 1
        evaluation.questions = []
        evaluation.total_questions = 0
        evaluation.total_points = 0.0

        # Mock evaluation service
        with patch("app.services.evaluation_service.EvaluationService") as mock_eval_service:
            mock_eval_service.return_value.get_by_id.return_value = evaluation
            mock_eval_service.return_value._can_edit_evaluation.return_value = True

            self.db_mock.add = Mock()
            self.db_mock.commit = Mock()
            self.db_mock.refresh = Mock()

            data = {
                "question_text": "What is 2+2?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "question_data": {"options": ["2", "3", "4", "5"], "correct_answer": "4"},
            }

            result = self.question_service.create(1, 1, data, self.admin_user)

            # Assertions
            self.db_mock.add.assert_called_once()
            self.db_mock.commit.assert_called_once()
            self.db_mock.refresh.assert_called_once()

    def test_create_question_missing_text_fails(self):
        """Test question creation fails without question text"""
        # Mock evaluation service
        with patch("app.services.evaluation_service.EvaluationService") as mock_eval_service:
            evaluation = Mock()
            mock_eval_service.return_value.get_by_id.return_value = evaluation
            mock_eval_service.return_value._can_edit_evaluation.return_value = True

            data = {"question_type": QuestionType.MULTIPLE_CHOICE}

            with pytest.raises(BadRequestError):
                self.question_service.create(1, 1, data, self.admin_user)


class TestEvaluationAttemptService:
    """Test EvaluationAttemptService"""

    def setup_method(self):
        """Setup test environment"""
        self.db_mock = Mock()
        self.attempt_service = EvaluationAttemptService(self.db_mock)

        # Mock user
        self.student_user = Mock()
        self.student_user.id = 1
        self.student_user.tenant_id = 1

    def test_start_attempt_success(self):
        """Test successful attempt start"""
        # Mock evaluation
        evaluation = Mock()
        evaluation.id = 1
        evaluation.is_available = True
        evaluation.max_attempts = 3
        evaluation.total_questions = 5
        evaluation.total_points = 10.0
        evaluation.time_limit_minutes = 60
        evaluation.passing_score = 70.0

        # Mock evaluation service
        with patch("app.services.evaluation_service.EvaluationService") as mock_eval_service:
            mock_eval_service.return_value.get_by_id.return_value = evaluation

            # Mock existing attempts query
            self.db_mock.query.return_value.filter.return_value.count.return_value = 0
            self.db_mock.query.return_value.filter.return_value.first.return_value = None

            self.db_mock.add = Mock()
            self.db_mock.commit = Mock()
            self.db_mock.refresh = Mock()

            result = self.attempt_service.start_attempt(1, 1, self.student_user)

            # Assertions
            self.db_mock.add.assert_called_once()
            self.db_mock.commit.assert_called_once()

    def test_start_attempt_evaluation_not_available(self):
        """Test attempt fails when evaluation is not available"""
        # Mock evaluation
        evaluation = Mock()
        evaluation.id = 1
        evaluation.is_available = False

        with patch("app.services.evaluation_service.EvaluationService") as mock_eval_service:
            mock_eval_service.return_value.get_by_id.return_value = evaluation

            with pytest.raises(BadRequestError):
                self.attempt_service.start_attempt(1, 1, self.student_user)

    def test_start_attempt_max_attempts_reached(self):
        """Test attempt fails when max attempts reached"""
        # Mock evaluation
        evaluation = Mock()
        evaluation.id = 1
        evaluation.is_available = True
        evaluation.max_attempts = 1

        with patch("app.services.evaluation_service.EvaluationService") as mock_eval_service:
            mock_eval_service.return_value.get_by_id.return_value = evaluation

            # Mock existing attempts query - user has already made 1 attempt
            self.db_mock.query.return_value.filter.return_value.count.return_value = 1

            with pytest.raises(BadRequestError):
                self.attempt_service.start_attempt(1, 1, self.student_user)

    def test_submit_attempt_success(self):
        """Test successful attempt submission"""
        # Mock attempt
        attempt = Mock()
        attempt.id = 1
        attempt.user_id = self.student_user.id
        attempt.status = AttemptStatus.IN_PROGRESS
        attempt.started_at = datetime.utcnow() - timedelta(minutes=30)
        attempt.total_points = 10.0
        attempt.passing_score = 70.0
        attempt.responses = []

        self.attempt_service.get_by_id = Mock(return_value=attempt)
        self.attempt_service._calculate_attempt_score = Mock()
        self.db_mock.commit = Mock()
        self.db_mock.refresh = Mock()

        result = self.attempt_service.submit_attempt(1, 1, self.student_user)

        # Assertions
        assert attempt.status == AttemptStatus.COMPLETED
        assert attempt.completed_at is not None
        self.db_mock.commit.assert_called_once()


class TestQuestionResponseService:
    """Test QuestionResponseService"""

    def setup_method(self):
        """Setup test environment"""
        self.db_mock = Mock()
        self.response_service = QuestionResponseService(self.db_mock)

        # Mock user
        self.student_user = Mock()
        self.student_user.id = 1
        self.student_user.tenant_id = 1

    def test_save_response_success(self):
        """Test successful response saving"""
        # Mock attempt
        attempt = Mock()
        attempt.id = 1
        attempt.user_id = self.student_user.id
        attempt.status = AttemptStatus.IN_PROGRESS

        # Mock question
        question = Mock()
        question.id = 1
        question.question_type = QuestionType.MULTIPLE_CHOICE
        question.points = 2.0
        question.question_data = {"correct_answer": "B"}

        # Mock attempt service
        with patch("app.services.evaluation_service.EvaluationAttemptService") as mock_attempt_service:
            mock_attempt_service.return_value.get_by_id.return_value = attempt

            self.db_mock.query.return_value.filter.return_value.first.side_effect = [
                question,  # First call for question
                None,  # Second call for existing response (none exists)
            ]

            self.db_mock.add = Mock()
            self.db_mock.commit = Mock()
            self.db_mock.refresh = Mock()

            response_data = {"selected_option": "B"}

            result = self.response_service.save_response(1, 1, 1, response_data, self.student_user)

            # Assertions
            self.db_mock.add.assert_called_once()
            self.db_mock.commit.assert_called_once()

    def test_save_response_for_completed_attempt_fails(self):
        """Test that responses cannot be saved for completed attempts"""
        # Mock completed attempt
        attempt = Mock()
        attempt.id = 1
        attempt.user_id = self.student_user.id
        attempt.status = AttemptStatus.COMPLETED

        with patch("app.services.evaluation_service.EvaluationAttemptService") as mock_attempt_service:
            mock_attempt_service.return_value.get_by_id.return_value = attempt

            response_data = {"selected_option": "B"}

            with pytest.raises(BadRequestError):
                self.response_service.save_response(1, 1, 1, response_data, self.student_user)
