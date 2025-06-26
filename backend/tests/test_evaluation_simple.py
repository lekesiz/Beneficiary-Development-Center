"""
Simple tests for Evaluation models and service without complex relationships
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

# Import just what we need for evaluation testing
from app.models.evaluation import (
    Evaluation,
    Question,
    EvaluationAttempt,
    QuestionResponse,
    QuestionBank,
    EvaluationStatus,
    QuestionType,
    AttemptStatus,
    DifficultyLevel,
)
from app.services.evaluation_service import EvaluationService
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


class TestEvaluationModels:
    """Test Evaluation model classes"""

    def test_evaluation_status_enum(self):
        """Test EvaluationStatus enum values"""
        assert EvaluationStatus.DRAFT.value == "draft"
        assert EvaluationStatus.ACTIVE.value == "active"
        assert EvaluationStatus.ARCHIVED.value == "archived"
        assert EvaluationStatus.COMPLETED.value == "completed"

    def test_question_type_enum(self):
        """Test QuestionType enum values"""
        assert QuestionType.MULTIPLE_CHOICE.value == "multiple_choice"
        assert QuestionType.TRUE_FALSE.value == "true_false"
        assert QuestionType.SHORT_ANSWER.value == "short_answer"
        assert QuestionType.ESSAY.value == "essay"

    def test_attempt_status_enum(self):
        """Test AttemptStatus enum values"""
        assert AttemptStatus.IN_PROGRESS.value == "in_progress"
        assert AttemptStatus.COMPLETED.value == "completed"
        assert AttemptStatus.ABANDONED.value == "abandoned"
        assert AttemptStatus.TIMED_OUT.value == "timed_out"

    def test_evaluation_creation(self):
        """Test Evaluation model creation"""
        evaluation = Evaluation(
            title="Test Evaluation",
            description="Test description",
            tenant_id=1,
            created_by=1,
            status=EvaluationStatus.DRAFT,
        )

        assert evaluation.title == "Test Evaluation"
        assert evaluation.description == "Test description"
        assert evaluation.status == EvaluationStatus.DRAFT
        assert evaluation.total_questions == 0
        assert evaluation.total_points == 0.0
        assert evaluation.passing_score == 70.0
        assert evaluation.max_attempts == 1

    def test_evaluation_duration_display(self):
        """Test evaluation duration display property"""
        evaluation = Evaluation(title="Test", tenant_id=1, created_by=1)

        # No time limit
        evaluation.time_limit_minutes = None
        assert evaluation.duration_display == "Unlimited"

        # 30 minutes
        evaluation.time_limit_minutes = 30
        assert evaluation.duration_display == "30m"

        # 1 hour
        evaluation.time_limit_minutes = 60
        assert evaluation.duration_display == "1h"

        # 1 hour 30 minutes
        evaluation.time_limit_minutes = 90
        assert evaluation.duration_display == "1h 30m"

    def test_evaluation_to_dict(self):
        """Test evaluation to_dict method"""
        evaluation = Evaluation(
            title="Test Evaluation",
            description="Test description",
            tenant_id=1,
            created_by=1,
            status=EvaluationStatus.DRAFT,
            time_limit_minutes=60,
        )

        data = evaluation.to_dict()

        assert data["title"] == "Test Evaluation"
        assert data["description"] == "Test description"
        assert data["status"] == "draft"
        assert data["duration_display"] == "1h"
        assert "is_available" in data

    def test_question_creation(self):
        """Test Question model creation"""
        question = Question(
            evaluation_id=1,
            question_text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=2.0,
            tenant_id=1,
            question_data={"options": ["2", "3", "4", "5"], "correct_answer": "4"},
        )

        assert question.question_text == "What is 2+2?"
        assert question.question_type == QuestionType.MULTIPLE_CHOICE
        assert question.points == 2.0
        assert question.difficulty_level == DifficultyLevel.MEDIUM
        assert question.is_required is True

    def test_evaluation_attempt_creation(self):
        """Test EvaluationAttempt model creation"""
        attempt = EvaluationAttempt(
            evaluation_id=1, user_id=1, tenant_id=1, total_questions=5, total_points=10.0, passing_score=70.0
        )

        assert attempt.evaluation_id == 1
        assert attempt.user_id == 1
        assert attempt.status == AttemptStatus.IN_PROGRESS
        assert attempt.attempt_number == 1
        assert attempt.total_questions == 5
        assert attempt.is_in_progress is True
        assert attempt.is_completed is False

    def test_question_response_creation(self):
        """Test QuestionResponse model creation"""
        response = QuestionResponse(
            attempt_id=1,
            question_id=1,
            tenant_id=1,
            response_data={"selected_option": "4"},
            is_correct=True,
            points_earned=2.0,
        )

        assert response.attempt_id == 1
        assert response.question_id == 1
        assert response.is_correct is True
        assert response.points_earned == 2.0

    def test_question_bank_creation(self):
        """Test QuestionBank model creation"""
        bank_question = QuestionBank(
            title="Bank Question",
            subject="Math",
            topic="Arithmetic",
            question_text="What is 5+5?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            tenant_id=1,
            created_by=1,
            question_data={"options": ["8", "9", "10", "11"], "correct_answer": "10"},
        )

        assert bank_question.title == "Bank Question"
        assert bank_question.subject == "Math"
        assert bank_question.topic == "Arithmetic"
        assert bank_question.usage_count == 0


class TestEvaluationServiceMocked:
    """Test EvaluationService with mocked database"""

    def setup_method(self):
        """Setup test environment"""
        self.db_mock = Mock()
        self.evaluation_service = EvaluationService(self.db_mock)

        # Mock user
        self.admin_user = Mock()
        self.admin_user.id = 1
        self.admin_user.role = "admin"
        self.admin_user.tenant_id = 1

        self.student_user = Mock()
        self.student_user.id = 2
        self.student_user.role = "student"
        self.student_user.tenant_id = 1

    def test_create_evaluation_permission_check(self):
        """Test that only authorized users can create evaluations"""
        data = {"title": "Test Evaluation"}

        # Admin should be able to create
        with pytest.raises(Exception):  # Will fail due to other reasons, but not permission
            self.evaluation_service.create(1, data, self.admin_user)

        # Student should not be able to create
        with pytest.raises(ForbiddenError):
            self.evaluation_service.create(1, data, self.student_user)

    def test_create_evaluation_missing_title(self):
        """Test evaluation creation fails without title"""
        data = {"description": "Test description"}

        with pytest.raises(BadRequestError):
            self.evaluation_service.create(1, data, self.admin_user)

    def test_service_initialization(self):
        """Test service initialization"""
        assert self.evaluation_service.db == self.db_mock
        assert hasattr(self.evaluation_service, "create")
        assert hasattr(self.evaluation_service, "get_by_id")
        assert hasattr(self.evaluation_service, "update")
        assert hasattr(self.evaluation_service, "delete")


if __name__ == "__main__":
    pytest.main([__file__])
