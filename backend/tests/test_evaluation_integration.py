"""
Integration tests for Evaluation module
"""

import pytest
import json
from datetime import datetime, timedelta
from flask import Flask
from app import create_app, db
from app.models.user import User
from app.models.course import Course
from app.models.program import Program
from app.models.evaluation import (
    Evaluation,
    Question,
    EvaluationAttempt,
    QuestionResponse,
    EvaluationStatus,
    QuestionType,
    AttemptStatus,
)


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def admin_user(app):
    """Create admin user."""
    with app.app_context():
        from app.models.user import Role

        # Create or get admin role
        admin_role = db.session.query(Role).filter_by(name=Role.ADMIN).first()
        if not admin_role:
            admin_role = Role(name=Role.ADMIN, permissions=Role.get_default_permissions(Role.ADMIN))
            db.session.add(admin_role)
            db.session.commit()

        user = User(
            email="admin@test.com",
            first_name="Admin",
            last_name="User",
            tenant_id=1,
            is_active=True,
            password_hash="hashed_password",
        )
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def instructor_user(app):
    """Create instructor user."""
    with app.app_context():
        from app.models.user import Role

        # Create or get trainer role
        trainer_role = db.session.query(Role).filter_by(name=Role.TRAINER).first()
        if not trainer_role:
            trainer_role = Role(name=Role.TRAINER, permissions=Role.get_default_permissions(Role.TRAINER))
            db.session.add(trainer_role)
            db.session.commit()

        user = User(
            email="instructor@test.com",
            first_name="Instructor",
            last_name="User",
            tenant_id=1,
            is_active=True,
            password_hash="hashed_password",
        )
        user.roles.append(trainer_role)
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def student_user(app):
    """Create student user."""
    with app.app_context():
        from app.models.user import Role

        # Create or get student role
        student_role = db.session.query(Role).filter_by(name=Role.STUDENT).first()
        if not student_role:
            student_role = Role(name=Role.STUDENT, permissions=Role.get_default_permissions(Role.STUDENT))
            db.session.add(student_role)
            db.session.commit()

        user = User(
            email="student@test.com",
            first_name="Student",
            last_name="User",
            tenant_id=1,
            is_active=True,
            password_hash="hashed_password",
        )
        user.roles.append(student_role)
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_program(app, admin_user):
    """Create sample program."""
    with app.app_context():
        from datetime import datetime, timedelta

        # Refresh admin_user to ensure it's attached to current session
        admin_user = db.session.merge(admin_user)
        program = Program(
            title="Test Program",
            description="Test program description",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            tenant_id=1,
            created_by=admin_user.id,
        )
        db.session.add(program)
        db.session.commit()
        return program


@pytest.fixture
def sample_course(app, admin_user, sample_program):
    """Create sample course."""
    with app.app_context():
        # Refresh objects to ensure they're attached to current session
        admin_user = db.session.merge(admin_user)
        sample_program = db.session.merge(sample_program)
        course = Course(
            title="Test Course",
            description="Test course description",
            program_id=sample_program.id,
            tenant_id=1,
            created_by=admin_user.id,
        )
        db.session.add(course)
        db.session.commit()
        return course


@pytest.fixture
def sample_evaluation(app, admin_user, sample_course):
    """Create sample evaluation."""
    with app.app_context():
        # Refresh objects to ensure they're attached to current session
        admin_user = db.session.merge(admin_user)
        sample_course = db.session.merge(sample_course)
        evaluation = Evaluation(
            title="Test Evaluation",
            description="Test evaluation description",
            course_id=sample_course.id,
            created_by=admin_user.id,
            tenant_id=1,
            status=EvaluationStatus.DRAFT,
            time_limit_minutes=60,
            max_attempts=3,
            passing_score=70.0,
        )
        db.session.add(evaluation)
        db.session.commit()
        return evaluation


@pytest.fixture
def sample_question(app, sample_evaluation):
    """Create sample question."""
    with app.app_context():
        # Refresh evaluation to ensure it's attached to current session
        sample_evaluation = db.session.merge(sample_evaluation)
        question = Question(
            evaluation_id=sample_evaluation.id,
            question_text="What is 2 + 2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=2.0,
            tenant_id=1,
            question_data={"options": ["2", "3", "4", "5"], "correct_answer": "4"},
        )
        db.session.add(question)

        # Update evaluation totals
        sample_evaluation.total_questions = 1
        sample_evaluation.total_points = 2.0

        db.session.commit()
        return question


class TestEvaluationIntegration:
    """Integration tests for Evaluation functionality"""

    def test_evaluation_lifecycle(self, app, admin_user, sample_course):
        """Test complete evaluation lifecycle"""
        with app.app_context():
            # Refresh objects to ensure they're attached to current session
            admin_user = db.session.merge(admin_user)
            sample_course = db.session.merge(sample_course)

            # Create evaluation
            evaluation = Evaluation(
                title="Integration Test Evaluation",
                description="Test evaluation lifecycle",
                course_id=sample_course.id,
                created_by=admin_user.id,
                tenant_id=1,
                status=EvaluationStatus.DRAFT,
            )
            db.session.add(evaluation)
            db.session.commit()

            # Add questions
            question1 = Question(
                evaluation_id=evaluation.id,
                question_text="Question 1",
                question_type=QuestionType.MULTIPLE_CHOICE,
                points=5.0,
                tenant_id=1,
                question_data={"options": ["A", "B", "C", "D"], "correct_answer": "B"},
            )

            question2 = Question(
                evaluation_id=evaluation.id,
                question_text="Question 2",
                question_type=QuestionType.TRUE_FALSE,
                points=3.0,
                tenant_id=1,
                question_data={"correct_answer": True},
            )

            db.session.add_all([question1, question2])

            # Update evaluation totals
            evaluation.total_questions = 2
            evaluation.total_points = 8.0

            db.session.commit()

            # Activate evaluation
            evaluation.status = EvaluationStatus.ACTIVE
            db.session.commit()

            # Verify evaluation is available
            assert evaluation.is_available is True
            assert len(evaluation.questions) == 2
            assert evaluation.total_points == 8.0

    def test_evaluation_attempt_workflow(self, app, student_user, sample_evaluation, sample_question):
        """Test evaluation attempt workflow"""
        with app.app_context():
            # Activate evaluation
            sample_evaluation.status = EvaluationStatus.ACTIVE
            db.session.commit()

            # Start attempt
            attempt = EvaluationAttempt(
                evaluation_id=sample_evaluation.id,
                user_id=student_user.id,
                tenant_id=1,
                total_questions=sample_evaluation.total_questions,
                total_points=sample_evaluation.total_points,
                passing_score=sample_evaluation.passing_score,
                time_limit_minutes=sample_evaluation.time_limit_minutes,
            )
            db.session.add(attempt)
            db.session.commit()

            # Save response
            response = QuestionResponse(
                attempt_id=attempt.id,
                question_id=sample_question.id,
                tenant_id=1,
                response_data={"selected_option": "4"},
                is_correct=True,
                points_earned=2.0,
            )
            db.session.add(response)
            db.session.commit()

            # Submit attempt
            attempt.status = AttemptStatus.COMPLETED
            attempt.completed_at = datetime.utcnow()
            attempt.questions_answered = 1
            attempt.score_earned = 2.0
            attempt.percentage_score = (2.0 / 2.0) * 100
            attempt.passed = attempt.percentage_score >= attempt.passing_score

            db.session.commit()

            # Verify attempt completion
            assert attempt.is_completed is True
            assert attempt.passed is True
            assert len(attempt.responses) == 1
            assert attempt.responses[0].is_correct is True

    def test_question_types_scoring(self, app, student_user, sample_evaluation):
        """Test different question types and their scoring"""
        with app.app_context():
            # Create different question types
            mc_question = Question(
                evaluation_id=sample_evaluation.id,
                question_text="Multiple choice question",
                question_type=QuestionType.MULTIPLE_CHOICE,
                points=5.0,
                tenant_id=1,
                question_data={"options": ["A", "B", "C", "D"], "correct_answer": "C"},
            )

            tf_question = Question(
                evaluation_id=sample_evaluation.id,
                question_text="True/False question",
                question_type=QuestionType.TRUE_FALSE,
                points=3.0,
                tenant_id=1,
                question_data={"correct_answer": False},
            )

            essay_question = Question(
                evaluation_id=sample_evaluation.id,
                question_text="Essay question",
                question_type=QuestionType.ESSAY,
                points=10.0,
                tenant_id=1,
                question_data={},
            )

            db.session.add_all([mc_question, tf_question, essay_question])

            # Update evaluation
            sample_evaluation.total_questions = 3
            sample_evaluation.total_points = 18.0
            sample_evaluation.status = EvaluationStatus.ACTIVE

            db.session.commit()

            # Create attempt
            attempt = EvaluationAttempt(
                evaluation_id=sample_evaluation.id,
                user_id=student_user.id,
                tenant_id=1,
                total_questions=3,
                total_points=18.0,
                passing_score=70.0,
            )
            db.session.add(attempt)
            db.session.commit()

            # Answer multiple choice correctly
            mc_response = QuestionResponse(
                attempt_id=attempt.id,
                question_id=mc_question.id,
                tenant_id=1,
                response_data={"selected_option": "C"},
                is_correct=True,
                points_earned=5.0,
            )

            # Answer true/false incorrectly
            tf_response = QuestionResponse(
                attempt_id=attempt.id,
                question_id=tf_question.id,
                tenant_id=1,
                response_data={"selected_option": True},
                is_correct=False,
                points_earned=0.0,
            )

            # Essay answer (requires manual grading)
            essay_response = QuestionResponse(
                attempt_id=attempt.id,
                question_id=essay_question.id,
                tenant_id=1,
                response_data={"text": "This is my essay answer..."},
                is_correct=None,  # Not auto-graded
                points_earned=0.0,  # Will be graded manually
            )

            db.session.add_all([mc_response, tf_response, essay_response])
            db.session.commit()

            # Verify scoring
            total_auto_scored = mc_response.points_earned + tf_response.points_earned
            assert total_auto_scored == 5.0
            assert mc_response.is_correct is True
            assert tf_response.is_correct is False
            assert essay_response.is_correct is None

    def test_evaluation_time_limits(self, app, student_user, sample_evaluation):
        """Test evaluation time limits"""
        with app.app_context():
            # Set evaluation with time limit
            sample_evaluation.time_limit_minutes = 30
            sample_evaluation.status = EvaluationStatus.ACTIVE
            db.session.commit()

            # Start attempt
            start_time = datetime.utcnow()
            attempt = EvaluationAttempt(
                evaluation_id=sample_evaluation.id,
                user_id=student_user.id,
                tenant_id=1,
                started_at=start_time,
                time_limit_minutes=30,
            )
            db.session.add(attempt)
            db.session.commit()

            # Simulate time passing (in real scenario, this would be checked by frontend/background job)
            elapsed_time = timedelta(minutes=35)
            current_time = start_time + elapsed_time

            # Time limit exceeded
            time_spent_minutes = int(elapsed_time.total_seconds() / 60)
            assert time_spent_minutes > sample_evaluation.time_limit_minutes

            # Attempt should be marked as timed out
            attempt.status = AttemptStatus.TIMED_OUT
            attempt.completed_at = current_time
            attempt.time_spent_minutes = time_spent_minutes

            db.session.commit()

            assert attempt.status == AttemptStatus.TIMED_OUT
            assert attempt.time_spent_minutes == 35

    def test_max_attempts_limit(self, app, student_user, sample_evaluation):
        """Test maximum attempts limit"""
        with app.app_context():
            # Set evaluation with max 2 attempts
            sample_evaluation.max_attempts = 2
            sample_evaluation.status = EvaluationStatus.ACTIVE
            db.session.commit()

            # Create first attempt
            attempt1 = EvaluationAttempt(
                evaluation_id=sample_evaluation.id,
                user_id=student_user.id,
                tenant_id=1,
                attempt_number=1,
                status=AttemptStatus.COMPLETED,
            )
            db.session.add(attempt1)

            # Create second attempt
            attempt2 = EvaluationAttempt(
                evaluation_id=sample_evaluation.id,
                user_id=student_user.id,
                tenant_id=1,
                attempt_number=2,
                status=AttemptStatus.COMPLETED,
            )
            db.session.add(attempt2)
            db.session.commit()

            # Verify user has reached max attempts
            user_attempts = EvaluationAttempt.query.filter_by(
                evaluation_id=sample_evaluation.id, user_id=student_user.id
            ).count()

            assert user_attempts == 2
            assert user_attempts >= sample_evaluation.max_attempts

    def test_evaluation_availability_dates(self, app, sample_evaluation):
        """Test evaluation availability dates"""
        with app.app_context():
            now = datetime.utcnow()

            # Set evaluation available in future
            sample_evaluation.available_from = now + timedelta(days=1)
            sample_evaluation.available_until = now + timedelta(days=7)
            sample_evaluation.status = EvaluationStatus.ACTIVE
            db.session.commit()

            # Should not be available yet
            assert sample_evaluation.is_available is False

            # Set evaluation available now
            sample_evaluation.available_from = now - timedelta(hours=1)
            db.session.commit()

            # Should be available now
            assert sample_evaluation.is_available is True

            # Set evaluation expired
            sample_evaluation.available_until = now - timedelta(hours=1)
            db.session.commit()

            # Should not be available anymore
            assert sample_evaluation.is_available is False

    def test_question_bank_integration(self, app, admin_user):
        """Test question bank functionality"""
        from app.models.evaluation import QuestionBank

        with app.app_context():
            # Create question bank entry
            bank_question = QuestionBank(
                title="Bank Question 1",
                subject="Mathematics",
                topic="Basic Arithmetic",
                question_text="What is 5 + 3?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                points=2.0,
                tenant_id=1,
                created_by=admin_user.id,
                question_data={"options": ["6", "7", "8", "9"], "correct_answer": "8"},
                explanation="5 + 3 equals 8",
            )
            db.session.add(bank_question)
            db.session.commit()

            # Verify question bank entry
            assert bank_question.title == "Bank Question 1"
            assert bank_question.subject == "Mathematics"
            assert bank_question.usage_count == 0

            # Simulate using the question (increment usage count)
            bank_question.usage_count += 1
            bank_question.last_used_at = datetime.utcnow()
            db.session.commit()

            assert bank_question.usage_count == 1
            assert bank_question.last_used_at is not None
