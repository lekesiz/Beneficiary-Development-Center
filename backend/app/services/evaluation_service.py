"""
Evaluation service for managing evaluations, questions and attempts
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.evaluation import (
    Evaluation,
    Question,
    EvaluationAttempt,
    QuestionResponse,
    QuestionBank,
    EvaluationStatus,
    QuestionType,
    AttemptStatus,
)
from app.models.user import User
from app.services.base import BaseService
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError


class EvaluationService(BaseService):
    """Service for evaluation operations"""

    def __init__(self, db: Session):
        super().__init__(db, Evaluation)

    def create(self, tenant_id: int, data: Dict[str, Any], user: User) -> Evaluation:
        """Create a new evaluation"""
        # Check permissions
        if user.role not in ["admin", "manager", "instructor"]:
            raise ForbiddenError("Only admins, managers and instructors can create evaluations")

        # Validate required fields
        if not data.get("title"):
            raise BadRequestError("Title is required")

        # Set defaults
        evaluation_data = {
            "tenant_id": tenant_id,
            "created_by": user.id,
            "status": EvaluationStatus.DRAFT,
            "total_questions": 0,
            "total_points": 0.0,
            "passing_score": 70.0,
            "max_attempts": 1,
            "shuffle_questions": False,
            "show_results_immediately": True,
            "allow_review": True,
            **data,
        }

        evaluation = Evaluation(**evaluation_data)
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)

        return evaluation

    def update(self, evaluation_id: int, tenant_id: int, data: Dict[str, Any], user: User) -> Evaluation:
        """Update an evaluation"""
        evaluation = self.get_by_id(evaluation_id, tenant_id)

        # Check permissions
        if not self._can_edit_evaluation(evaluation, user):
            raise ForbiddenError("You don't have permission to edit this evaluation")

        # Don't allow editing if there are completed attempts
        if evaluation.attempts and any(a.status == AttemptStatus.COMPLETED for a in evaluation.attempts):
            if user.role != "admin":
                raise ForbiddenError("Cannot edit evaluation with completed attempts")

        # Update fields
        for key, value in data.items():
            if hasattr(evaluation, key) and key not in ["id", "uuid", "tenant_id", "created_by", "created_at"]:
                setattr(evaluation, key, value)

        evaluation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(evaluation)

        return evaluation

    def delete(self, evaluation_id: int, tenant_id: int, user: User) -> bool:
        """Delete an evaluation"""
        evaluation = self.get_by_id(evaluation_id, tenant_id)

        # Check permissions
        if not self._can_edit_evaluation(evaluation, user):
            raise ForbiddenError("You don't have permission to delete this evaluation")

        # Don't allow deletion if there are completed attempts
        if evaluation.attempts and any(a.status == AttemptStatus.COMPLETED for a in evaluation.attempts):
            if user.role != "admin":
                raise ForbiddenError("Cannot delete evaluation with completed attempts")

        self.db.delete(evaluation)
        self.db.commit()
        return True

    def get_by_id(self, evaluation_id: int, tenant_id: int, include_questions: bool = False) -> Evaluation:
        """Get evaluation by ID"""
        query = self.db.query(Evaluation).filter(
            and_(Evaluation.id == evaluation_id, Evaluation.tenant_id == tenant_id)
        )

        if include_questions:
            query = query.options(self.db.selectinload(Evaluation.questions))

        evaluation = query.first()
        if not evaluation:
            raise NotFoundError("Evaluation not found")

        return evaluation

    def get_all(self, tenant_id: int, filters: Dict[str, Any] = None, user: User = None) -> Dict[str, Any]:
        """Get all evaluations with filtering and pagination"""
        filters = filters or {}

        query = self.db.query(Evaluation).filter(Evaluation.tenant_id == tenant_id)

        # Apply role-based filtering
        if user and user.role == "instructor":
            query = query.filter(Evaluation.created_by == user.id)

        # Apply filters
        if filters.get("status"):
            query = query.filter(Evaluation.status == filters["status"])

        if filters.get("course_id"):
            query = query.filter(Evaluation.course_id == filters["course_id"])

        if filters.get("program_id"):
            query = query.filter(Evaluation.program_id == filters["program_id"])

        if filters.get("search"):
            search_term = f"%{filters['search']}%"
            query = query.filter(or_(Evaluation.title.ilike(search_term), Evaluation.description.ilike(search_term)))

        # Get total count
        total = query.count()

        # Apply sorting
        sort_by = filters.get("sort_by", "created_at")
        sort_desc = filters.get("sort_desc", True)

        if hasattr(Evaluation, sort_by):
            order_column = getattr(Evaluation, sort_by)
            if sort_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)

        # Apply pagination
        page = filters.get("page", 1)
        per_page = min(filters.get("per_page", 20), 100)
        offset = (page - 1) * per_page

        evaluations = query.offset(offset).limit(per_page).all()

        return {
            "evaluations": evaluations,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
            },
        }

    def activate(self, evaluation_id: int, tenant_id: int, user: User) -> Evaluation:
        """Activate an evaluation"""
        evaluation = self.get_by_id(evaluation_id, tenant_id)

        if not self._can_edit_evaluation(evaluation, user):
            raise ForbiddenError("You don't have permission to activate this evaluation")

        if not evaluation.questions:
            raise BadRequestError("Cannot activate evaluation without questions")

        evaluation.status = EvaluationStatus.ACTIVE
        evaluation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(evaluation)

        return evaluation

    def archive(self, evaluation_id: int, tenant_id: int, user: User) -> Evaluation:
        """Archive an evaluation"""
        evaluation = self.get_by_id(evaluation_id, tenant_id)

        if not self._can_edit_evaluation(evaluation, user):
            raise ForbiddenError("You don't have permission to archive this evaluation")

        evaluation.status = EvaluationStatus.ARCHIVED
        evaluation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(evaluation)

        return evaluation

    def _can_edit_evaluation(self, evaluation: Evaluation, user: User) -> bool:
        """Check if user can edit evaluation"""
        if user.role in ["admin", "manager"]:
            return True
        if user.role == "instructor" and evaluation.created_by == user.id:
            return True
        return False


class QuestionService(BaseService):
    """Service for question operations"""

    def __init__(self, db: Session):
        super().__init__(db, Question)

    def create(self, evaluation_id: int, tenant_id: int, data: Dict[str, Any], user: User) -> Question:
        """Create a new question"""
        # Get evaluation and check permissions
        evaluation_service = EvaluationService(self.db)
        evaluation = evaluation_service.get_by_id(evaluation_id, tenant_id)

        if not evaluation_service._can_edit_evaluation(evaluation, user):
            raise ForbiddenError("You don't have permission to add questions to this evaluation")

        # Validate required fields
        if not data.get("question_text"):
            raise BadRequestError("Question text is required")

        if not data.get("question_type"):
            raise BadRequestError("Question type is required")

        # Set defaults
        question_data = {
            "tenant_id": tenant_id,
            "evaluation_id": evaluation_id,
            "points": 1.0,
            "order_index": len(evaluation.questions) + 1,
            "is_required": True,
            **data,
        }

        question = Question(**question_data)
        self.db.add(question)

        # Update evaluation totals
        evaluation.total_questions = len(evaluation.questions) + 1
        evaluation.total_points = evaluation.total_points + question.points

        self.db.commit()
        self.db.refresh(question)

        return question

    def update(self, question_id: int, tenant_id: int, data: Dict[str, Any], user: User) -> Question:
        """Update a question"""
        question = self.get_by_id(question_id, tenant_id)

        # Check permissions through evaluation
        evaluation_service = EvaluationService(self.db)
        if not evaluation_service._can_edit_evaluation(question.evaluation, user):
            raise ForbiddenError("You don't have permission to edit this question")

        old_points = question.points

        # Update fields
        for key, value in data.items():
            if hasattr(question, key) and key not in ["id", "uuid", "tenant_id", "evaluation_id", "created_at"]:
                setattr(question, key, value)

        # Update evaluation totals if points changed
        if question.points != old_points:
            question.evaluation.total_points += question.points - old_points

        question.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(question)

        return question

    def delete(self, question_id: int, tenant_id: int, user: User) -> bool:
        """Delete a question"""
        question = self.get_by_id(question_id, tenant_id)

        # Check permissions through evaluation
        evaluation_service = EvaluationService(self.db)
        if not evaluation_service._can_edit_evaluation(question.evaluation, user):
            raise ForbiddenError("You don't have permission to delete this question")

        # Update evaluation totals
        question.evaluation.total_questions -= 1
        question.evaluation.total_points -= question.points

        self.db.delete(question)
        self.db.commit()
        return True

    def get_by_evaluation(self, evaluation_id: int, tenant_id: int) -> List[Question]:
        """Get all questions for an evaluation"""
        return (
            self.db.query(Question)
            .filter(and_(Question.evaluation_id == evaluation_id, Question.tenant_id == tenant_id))
            .order_by(Question.order_index)
            .all()
        )

    def reorder(self, question_id: int, tenant_id: int, new_order: int, user: User) -> Question:
        """Reorder a question"""
        question = self.get_by_id(question_id, tenant_id)

        # Check permissions
        evaluation_service = EvaluationService(self.db)
        if not evaluation_service._can_edit_evaluation(question.evaluation, user):
            raise ForbiddenError("You don't have permission to reorder questions")

        old_order = question.order_index
        question.order_index = new_order

        # Reorder other questions
        if old_order != new_order:
            questions = self.get_by_evaluation(question.evaluation_id, tenant_id)
            for q in questions:
                if q.id == question.id:
                    continue

                if old_order < new_order:
                    # Moving down
                    if old_order < q.order_index <= new_order:
                        q.order_index -= 1
                else:
                    # Moving up
                    if new_order <= q.order_index < old_order:
                        q.order_index += 1

        self.db.commit()
        self.db.refresh(question)
        return question


class EvaluationAttemptService(BaseService):
    """Service for evaluation attempt operations"""

    def __init__(self, db: Session):
        super().__init__(db, EvaluationAttempt)

    def start_attempt(self, evaluation_id: int, tenant_id: int, user: User) -> EvaluationAttempt:
        """Start a new evaluation attempt"""
        # Get evaluation
        evaluation_service = EvaluationService(self.db)
        evaluation = evaluation_service.get_by_id(evaluation_id, tenant_id, include_questions=True)

        # Check if evaluation is available
        if not evaluation.is_available:
            raise BadRequestError("Evaluation is not currently available")

        # Check if user has reached max attempts
        existing_attempts = (
            self.db.query(EvaluationAttempt)
            .filter(
                and_(
                    EvaluationAttempt.evaluation_id == evaluation_id,
                    EvaluationAttempt.user_id == user.id,
                    EvaluationAttempt.tenant_id == tenant_id,
                )
            )
            .count()
        )

        if existing_attempts >= evaluation.max_attempts:
            raise BadRequestError(f"Maximum attempts ({evaluation.max_attempts}) reached")

        # Check if user has an in-progress attempt
        in_progress = (
            self.db.query(EvaluationAttempt)
            .filter(
                and_(
                    EvaluationAttempt.evaluation_id == evaluation_id,
                    EvaluationAttempt.user_id == user.id,
                    EvaluationAttempt.tenant_id == tenant_id,
                    EvaluationAttempt.status == AttemptStatus.IN_PROGRESS,
                )
            )
            .first()
        )

        if in_progress:
            return in_progress

        # Create new attempt
        attempt = EvaluationAttempt(
            tenant_id=tenant_id,
            evaluation_id=evaluation_id,
            user_id=user.id,
            attempt_number=existing_attempts + 1,
            total_questions=evaluation.total_questions,
            total_points=evaluation.total_points,
            time_limit_minutes=evaluation.time_limit_minutes,
            passing_score=evaluation.passing_score,
            started_at=datetime.utcnow(),
        )

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        return attempt

    def submit_attempt(self, attempt_id: int, tenant_id: int, user: User) -> EvaluationAttempt:
        """Submit and score an evaluation attempt"""
        attempt = self.get_by_id(attempt_id, tenant_id)

        # Check permissions
        if attempt.user_id != user.id and user.role not in ["admin", "manager"]:
            raise ForbiddenError("You don't have permission to submit this attempt")

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise BadRequestError("Attempt is not in progress")

        # Calculate scores
        self._calculate_attempt_score(attempt)

        # Update attempt status
        attempt.status = AttemptStatus.COMPLETED
        attempt.completed_at = datetime.utcnow()

        if attempt.started_at:
            time_spent = attempt.completed_at - attempt.started_at
            attempt.time_spent_minutes = int(time_spent.total_seconds() / 60)

        # Check if passed
        attempt.passed = attempt.percentage_score >= attempt.passing_score

        self.db.commit()
        self.db.refresh(attempt)

        return attempt

    def _calculate_attempt_score(self, attempt: EvaluationAttempt):
        """Calculate the score for an attempt"""
        total_earned = 0.0
        questions_answered = 0

        for response in attempt.responses:
            if response.points_earned is not None:
                total_earned += response.points_earned
                questions_answered += 1

        attempt.questions_answered = questions_answered
        attempt.score_earned = total_earned
        attempt.percentage_score = (total_earned / attempt.total_points * 100) if attempt.total_points > 0 else 0

    def get_user_attempts(self, evaluation_id: int, user_id: int, tenant_id: int) -> List[EvaluationAttempt]:
        """Get all attempts by a user for an evaluation"""
        return (
            self.db.query(EvaluationAttempt)
            .filter(
                and_(
                    EvaluationAttempt.evaluation_id == evaluation_id,
                    EvaluationAttempt.user_id == user_id,
                    EvaluationAttempt.tenant_id == tenant_id,
                )
            )
            .order_by(desc(EvaluationAttempt.attempt_number))
            .all()
        )


class QuestionResponseService(BaseService):
    """Service for question response operations"""

    def __init__(self, db: Session):
        super().__init__(db, QuestionResponse)

    def save_response(
        self, attempt_id: int, question_id: int, tenant_id: int, response_data: Dict[str, Any], user: User
    ) -> QuestionResponse:
        """Save or update a question response"""
        # Get attempt and validate
        attempt_service = EvaluationAttemptService(self.db)
        attempt = attempt_service.get_by_id(attempt_id, tenant_id)

        if attempt.user_id != user.id and user.role not in ["admin", "manager"]:
            raise ForbiddenError("You don't have permission to submit responses for this attempt")

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise BadRequestError("Cannot submit responses for completed attempt")

        # Get question
        question = (
            self.db.query(Question).filter(and_(Question.id == question_id, Question.tenant_id == tenant_id)).first()
        )

        if not question:
            raise NotFoundError("Question not found")

        # Check if response already exists
        existing_response = (
            self.db.query(QuestionResponse)
            .filter(
                and_(
                    QuestionResponse.attempt_id == attempt_id,
                    QuestionResponse.question_id == question_id,
                    QuestionResponse.tenant_id == tenant_id,
                )
            )
            .first()
        )

        if existing_response:
            # Update existing response
            existing_response.response_data = response_data
            existing_response.answered_at = datetime.utcnow()
            response = existing_response
        else:
            # Create new response
            response = QuestionResponse(
                tenant_id=tenant_id,
                attempt_id=attempt_id,
                question_id=question_id,
                response_data=response_data,
                answered_at=datetime.utcnow(),
            )
            self.db.add(response)

        # Score the response
        self._score_response(response, question)

        self.db.commit()
        self.db.refresh(response)

        return response

    def _score_response(self, response: QuestionResponse, question: Question):
        """Score a question response"""
        question_data = question.question_data or {}
        response_data = response.response_data or {}

        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            correct_answer = question_data.get("correct_answer")
            user_answer = response_data.get("selected_option")

            if correct_answer == user_answer:
                response.is_correct = True
                response.points_earned = question.points
            else:
                response.is_correct = False
                response.points_earned = 0.0

        elif question.question_type == QuestionType.TRUE_FALSE:
            correct_answer = question_data.get("correct_answer")
            user_answer = response_data.get("answer")

            if correct_answer == user_answer:
                response.is_correct = True
                response.points_earned = question.points
            else:
                response.is_correct = False
                response.points_earned = 0.0

        elif question.question_type in [QuestionType.SHORT_ANSWER, QuestionType.ESSAY]:
            # For text responses, manual scoring might be needed
            # For now, give partial credit
            response.points_earned = question.points * 0.5  # Default partial credit
            response.is_correct = None  # Needs manual review

        else:
            # For other question types, implement specific scoring logic
            response.points_earned = 0.0
            response.is_correct = False
