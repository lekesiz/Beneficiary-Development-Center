"""
Enhanced Evaluation API endpoints with comprehensive CRUD operations, validation, and error handling
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
import csv
import io

from app.services.evaluation_service import EvaluationService
from app.models.evaluation import (
    Evaluation,
    EvaluationStatus,
    Question,
    QuestionType,
    EvaluationAttempt as Attempt,
    AttemptStatus,
)
from app.models.user import User
from app.core.decorators import require_tenant, check_role, rate_limit, audit_log
from app.extensions import db, cache
from app.core.logging import logger
from app.core.exceptions import (
    NotFoundError,
    BadRequestError,
    ForbiddenError,
    ConflictError,
    BusinessLogicError,
    InvalidStateError,
)
from app.core.error_handlers import ErrorResponse
from app.schemas.enhanced_evaluation import (
    EvaluationCreateSchema,
    EvaluationUpdateSchema,
    EvaluationQuerySchema,
    EvaluationResponseSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    QuestionResponseSchema,
    AttemptStartSchema,
    ResponseSubmitSchema,
    AttemptSubmitSchema,
    AttemptResponseSchema,
    EvaluationStatisticsSchema,
)

bp = Blueprint("enhanced_evaluations", __name__)

# Initialize schemas
evaluation_create_schema = EvaluationCreateSchema()
evaluation_update_schema = EvaluationUpdateSchema()
evaluation_query_schema = EvaluationQuerySchema()
evaluation_response_schema = EvaluationResponseSchema()
question_create_schema = QuestionCreateSchema()
question_update_schema = QuestionUpdateSchema()
question_response_schema = QuestionResponseSchema()
attempt_start_schema = AttemptStartSchema()
response_submit_schema = ResponseSubmitSchema()
attempt_submit_schema = AttemptSubmitSchema()
attempt_response_schema = AttemptResponseSchema()
evaluation_stats_schema = EvaluationStatisticsSchema()


# Helper functions
def get_current_user() -> User:
    """Get the current authenticated user"""
    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        raise NotFoundError("User not found")
    return user


def serialize_evaluation(evaluation: Evaluation, include_stats: bool = False) -> Dict[str, Any]:
    """Serialize an evaluation with optional statistics"""
    data = evaluation_response_schema.dump(evaluation.to_dict(include_related=True))

    if include_stats:
        # Add real-time statistics
        data["total_questions"] = len(evaluation.questions)
        data["total_points"] = sum(q.points for q in evaluation.questions)
        data["attempt_count"] = len(evaluation.attempts)

        # Calculate pass rate and average score
        completed_attempts = [a for a in evaluation.attempts if a.status == AttemptStatus.COMPLETED]
        if completed_attempts:
            data["average_score"] = sum(a.percentage_score for a in completed_attempts) / len(completed_attempts)
            data["pass_rate"] = len([a for a in completed_attempts if a.passed]) / len(completed_attempts) * 100
        else:
            data["average_score"] = 0
            data["pass_rate"] = 0

    return data


def serialize_question(question: Question) -> Dict[str, Any]:
    """Serialize a question"""
    data = question_response_schema.dump(question.to_dict())

    # Add statistics if available
    if hasattr(question, "responses"):
        total_responses = len(question.responses)
        if total_responses > 0:
            correct_responses = len([r for r in question.responses if r.is_correct])
            data["attempt_count"] = total_responses
            data["correct_count"] = correct_responses
            data["success_rate"] = (correct_responses / total_responses) * 100

            # Calculate average time
            response_times = [r.time_spent_seconds for r in question.responses if r.time_spent_seconds]
            if response_times:
                data["average_time_seconds"] = sum(response_times) / len(response_times)

    return data


# Main CRUD endpoints
@bp.route("", methods=["GET"])
@jwt_required()
@require_tenant()
@rate_limit(calls=100, period=60)
def list_evaluations():
    """
    List all evaluations with filtering and pagination

    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - status: Filter by status
    - evaluation_type: Filter by type
    - course_id: Filter by course
    - program_id: Filter by program
    - search: Search in title, description
    - is_adaptive: Filter adaptive evaluations
    - has_time_limit: Filter evaluations with time limit
    - available_now: Show only currently available
    - tags: Filter by tags
    - sort_by: Sort field
    - sort_order: Sort order
    - include_stats: Include statistics
    """
    try:
        # Validate query parameters
        try:
            filters = evaluation_query_schema.load(request.args)
        except ValidationError as e:
            return jsonify({"error": "Invalid query parameters", "details": e.messages}), 400

        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Extract pagination
        page = filters.get("page", 1)
        per_page = filters.get("per_page", 20)
        include_stats = request.args.get("include_stats", "false").lower() == "true"

        # Get evaluations
        service = EvaluationService(db.session)
        evaluations = service.get_all(
            tenant_id=tenant_id,
            user=user,
            skip=(page - 1) * per_page,
            limit=per_page,
            **{k: v for k, v in filters.items() if k not in ["page", "per_page"]},
        )

        # Get total count
        total = service.count(tenant_id, filters)

        # Serialize evaluations
        evaluations_data = [serialize_evaluation(e, include_stats) for e in evaluations]

        # Build response
        response = {
            "evaluations": evaluations_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1,
            },
        }

        logger.info(f"Retrieved {len(evaluations)} evaluations for user {user.id}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error listing evaluations: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to retrieve evaluations", status_code=500)


@bp.route("/<int:evaluation_id>", methods=["GET"])
@jwt_required()
@require_tenant()
@rate_limit(calls=200, period=60)
def get_evaluation(evaluation_id: int):
    """
    Get a specific evaluation by ID

    Query Parameters:
    - include_questions: Include question list
    - include_stats: Include statistics
    - include_attempts: Include user's attempts
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Parse query parameters
        include_questions = request.args.get("include_questions", "false").lower() == "true"
        include_stats = request.args.get("include_stats", "false").lower() == "true"
        include_attempts = request.args.get("include_attempts", "false").lower() == "true"

        # Get evaluation
        service = EvaluationService(db.session)
        evaluation = service.get_by_id(tenant_id, evaluation_id, user)

        # Serialize evaluation
        data = serialize_evaluation(evaluation, include_stats)

        # Add questions if requested
        if include_questions:
            # Check if user can view questions
            if user.role in ["admin", "manager", "instructor"] or evaluation.show_questions_before_attempt:
                data["questions"] = [serialize_question(q) for q in evaluation.questions if not q.deleted_at]
            else:
                data["questions"] = []
                data["message"] = "Questions are not available before attempting the evaluation"

        # Add user's attempts if requested
        if include_attempts:
            user_attempts = [a for a in evaluation.attempts if a.user_id == user.id]
            data["user_attempts"] = [
                {
                    "id": a.id,
                    "attempt_number": a.attempt_number,
                    "status": a.status.value,
                    "started_at": a.started_at.isoformat(),
                    "completed_at": a.completed_at.isoformat() if a.completed_at else None,
                    "score_earned": a.score_earned,
                    "percentage_score": a.percentage_score,
                    "passed": a.passed,
                }
                for a in user_attempts
            ]

            # Check if user can attempt
            data["can_attempt"] = service.can_user_attempt(evaluation_id, user.id)
            if not data["can_attempt"]:
                data["next_attempt_available"] = service.get_next_attempt_time(evaluation_id, user.id)

        logger.info(f"Retrieved evaluation {evaluation_id} for user {user.id}")
        return jsonify(data), 200

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except Exception as e:
        logger.error(f"Error retrieving evaluation {evaluation_id}: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to retrieve evaluation", status_code=500)


@bp.route("", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=20, period=60)
@audit_log(action="create_evaluation")
def create_evaluation():
    """
    Create a new evaluation

    Request Body: EvaluationCreateSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Validate request data
        try:
            data = evaluation_create_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Create evaluation
        service = EvaluationService(db.session)
        evaluation = service.create(tenant_id, data, user)

        # Return created evaluation
        response_data = serialize_evaluation(evaluation, include_stats=True)

        logger.info(f"Created evaluation {evaluation.title} by user {user.id}")
        return jsonify(response_data), 201

    except BusinessLogicError as e:
        return ErrorResponse.create(
            error="BusinessLogicError", message=str(e), status_code=400, error_code="BUSINESS_RULE_VIOLATION"
        )
    except Exception as e:
        logger.error(f"Error creating evaluation: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to create evaluation", status_code=500)


@bp.route("/<int:evaluation_id>", methods=["PUT", "PATCH"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=50, period=60)
@audit_log(action="update_evaluation")
def update_evaluation(evaluation_id: int):
    """
    Update an evaluation

    Request Body: EvaluationUpdateSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Check instructor permissions
        if user.role == "instructor":
            evaluation = db.session.query(Evaluation).filter_by(id=evaluation_id, tenant_id=tenant_id).first()

            if not evaluation or evaluation.created_by != user.id:
                raise ForbiddenError("You can only update evaluations you created")

        # Validate request data
        partial = request.method == "PATCH"
        try:
            data = evaluation_update_schema.load(request.json, partial=partial)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Update evaluation
        service = EvaluationService(db.session)
        evaluation = service.update(tenant_id, evaluation_id, data, user)

        # Return updated evaluation
        response_data = serialize_evaluation(evaluation, include_stats=True)

        logger.info(f"Updated evaluation {evaluation_id} by user {user.id}")
        return jsonify(response_data), 200

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except ForbiddenError as e:
        return ErrorResponse.create(
            error="Forbidden", message=str(e), status_code=403, error_code="INSUFFICIENT_PERMISSIONS"
        )
    except InvalidStateError as e:
        return ErrorResponse.create(
            error="InvalidState", message=str(e), status_code=400, error_code="INVALID_EVALUATION_STATE"
        )
    except Exception as e:
        logger.error(f"Error updating evaluation {evaluation_id}: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to update evaluation", status_code=500)


@bp.route("/<int:evaluation_id>", methods=["DELETE"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
@rate_limit(calls=10, period=60)
@audit_log(action="delete_evaluation")
def delete_evaluation(evaluation_id: int):
    """
    Delete an evaluation (soft delete)

    Query Parameters:
    - force: Force delete even with attempts
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        force_delete = request.args.get("force", "false").lower() == "true"

        # Delete evaluation
        service = EvaluationService(db.session)

        # Check if evaluation has attempts
        evaluation = service.get_by_id(tenant_id, evaluation_id, user)
        if evaluation.attempts and not force_delete:
            return ErrorResponse.create(
                error="Conflict",
                message=f"Cannot delete evaluation with {len(evaluation.attempts)} attempts",
                status_code=409,
                error_code="ATTEMPTS_EXIST",
                details={"attempt_count": len(evaluation.attempts)},
            )

        service.delete(tenant_id, evaluation_id, user)

        logger.info(f"Deleted evaluation {evaluation_id} by user {user.id}")
        return "", 204

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except Exception as e:
        logger.error(f"Error deleting evaluation {evaluation_id}: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to delete evaluation", status_code=500)


# Question management endpoints
@bp.route("/<int:evaluation_id>/questions", methods=["GET"])
@jwt_required()
@require_tenant()
@rate_limit(calls=100, period=60)
def list_questions(evaluation_id: int):
    """
    List all questions for an evaluation

    Query Parameters:
    - include_stats: Include question statistics
    - question_type: Filter by type
    - difficulty_level: Filter by difficulty
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Parse query parameters
        include_stats = request.args.get("include_stats", "false").lower() == "true"
        question_type = request.args.get("question_type")
        difficulty_level = request.args.get("difficulty_level")

        # Get evaluation and questions
        service = EvaluationService(db.session)
        evaluation = service.get_by_id(tenant_id, evaluation_id, user)

        # Filter questions
        questions = evaluation.questions
        if question_type:
            questions = [q for q in questions if q.question_type.value == question_type]
        if difficulty_level:
            questions = [q for q in questions if q.difficulty_level == difficulty_level]

        # Sort by order_index
        questions = sorted(questions, key=lambda q: q.order_index)

        # Serialize questions
        questions_data = [serialize_question(q) for q in questions if not q.deleted_at]

        return (
            jsonify(
                {
                    "questions": questions_data,
                    "evaluation": {
                        "id": evaluation.id,
                        "title": evaluation.title,
                        "total_questions": len(questions_data),
                        "total_points": sum(q["points"] for q in questions_data),
                    },
                }
            ),
            200,
        )

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except Exception as e:
        logger.error(f"Error fetching questions: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to fetch questions", status_code=500)


@bp.route("/<int:evaluation_id>/questions", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=50, period=60)
@audit_log(action="add_question")
def add_question(evaluation_id: int):
    """
    Add a question to an evaluation

    Request Body: QuestionCreateSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Validate request data
        try:
            data = question_create_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Get evaluation
        service = EvaluationService(db.session)
        evaluation = service.get_by_id(tenant_id, evaluation_id, user)

        # Check permissions
        if user.role == "instructor" and evaluation.created_by != user.id:
            raise ForbiddenError("You can only add questions to evaluations you created")

        # Check if evaluation is editable
        if evaluation.status != EvaluationStatus.DRAFT:
            raise InvalidStateError("Cannot add questions to non-draft evaluations")

        # Add question
        question = service.add_question(tenant_id, evaluation_id, data, user)

        logger.info(f"Added question to evaluation {evaluation_id} by user {user.id}")
        return jsonify(serialize_question(question)), 201

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except ForbiddenError as e:
        return ErrorResponse.create(
            error="Forbidden", message=str(e), status_code=403, error_code="INSUFFICIENT_PERMISSIONS"
        )
    except InvalidStateError as e:
        return ErrorResponse.create(
            error="InvalidState", message=str(e), status_code=400, error_code="INVALID_EVALUATION_STATE"
        )
    except Exception as e:
        logger.error(f"Error adding question: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to add question", status_code=500)


@bp.route("/<int:evaluation_id>/questions/<int:question_id>", methods=["PUT", "PATCH"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=50, period=60)
@audit_log(action="update_question")
def update_question(evaluation_id: int, question_id: int):
    """
    Update a question

    Request Body: QuestionUpdateSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Validate request data
        partial = request.method == "PATCH"
        try:
            data = question_update_schema.load(request.json, partial=partial)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Update question
        service = EvaluationService(db.session)
        question = service.update_question(tenant_id, evaluation_id, question_id, data, user)

        logger.info(f"Updated question {question_id} by user {user.id}")
        return jsonify(serialize_question(question)), 200

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="QUESTION_NOT_FOUND")
    except ForbiddenError as e:
        return ErrorResponse.create(
            error="Forbidden", message=str(e), status_code=403, error_code="INSUFFICIENT_PERMISSIONS"
        )
    except InvalidStateError as e:
        return ErrorResponse.create(
            error="InvalidState", message=str(e), status_code=400, error_code="INVALID_EVALUATION_STATE"
        )
    except Exception as e:
        logger.error(f"Error updating question {question_id}: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to update question", status_code=500)


@bp.route("/<int:evaluation_id>/questions/<int:question_id>", methods=["DELETE"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=30, period=60)
@audit_log(action="delete_question")
def delete_question(evaluation_id: int, question_id: int):
    """
    Delete a question from an evaluation
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Delete question
        service = EvaluationService(db.session)
        service.delete_question(tenant_id, evaluation_id, question_id, user)

        logger.info(f"Deleted question {question_id} by user {user.id}")
        return "", 204

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="QUESTION_NOT_FOUND")
    except InvalidStateError as e:
        return ErrorResponse.create(
            error="InvalidState", message=str(e), status_code=400, error_code="INVALID_EVALUATION_STATE"
        )
    except Exception as e:
        logger.error(f"Error deleting question {question_id}: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to delete question", status_code=500)


# Attempt management endpoints
@bp.route("/<int:evaluation_id>/attempts/start", methods=["POST"])
@jwt_required()
@require_tenant()
@rate_limit(calls=10, period=60)
@audit_log(action="start_attempt")
def start_attempt(evaluation_id: int):
    """
    Start an evaluation attempt

    Request Body: AttemptStartSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Validate request data
        try:
            data = attempt_start_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Start attempt
        service = EvaluationService(db.session)
        attempt = service.start_attempt(tenant_id, evaluation_id, user.id, data)

        # Get questions for the attempt
        questions = service.get_attempt_questions(attempt.id, user.id)

        # Prepare response
        response_data = {
            "attempt_id": attempt.id,
            "attempt_number": attempt.attempt_number,
            "started_at": attempt.started_at.isoformat(),
            "time_limit_minutes": attempt.evaluation.time_limit_minutes,
            "total_questions": len(questions),
            "total_points": sum(q["points"] for q in questions),
        }

        # Add questions based on display settings
        if attempt.evaluation.show_one_question_at_time:
            # Only show first question
            response_data["current_question"] = questions[0] if questions else None
            response_data["question_index"] = 0
        else:
            # Show all questions
            response_data["questions"] = questions

        logger.info(f"Started attempt for evaluation {evaluation_id} by user {user.id}")
        return jsonify(response_data), 201

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except BusinessLogicError as e:
        return ErrorResponse.create(
            error="BusinessLogicError", message=str(e), status_code=400, error_code="CANNOT_START_ATTEMPT"
        )
    except Exception as e:
        logger.error(f"Error starting attempt: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to start attempt", status_code=500)


@bp.route("/<int:evaluation_id>/attempts/<int:attempt_id>/submit", methods=["POST"])
@jwt_required()
@require_tenant()
@rate_limit(calls=50, period=60)
@audit_log(action="submit_attempt")
def submit_attempt(evaluation_id: int, attempt_id: int):
    """
    Submit an evaluation attempt

    Request Body: AttemptSubmitSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Validate request data
        try:
            data = attempt_submit_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Submit attempt
        service = EvaluationService(db.session)
        result = service.submit_attempt(
            tenant_id=tenant_id,
            evaluation_id=evaluation_id,
            attempt_id=attempt_id,
            user_id=user.id,
            responses=data["responses"],
        )

        # Prepare response based on evaluation settings
        response_data = {
            "attempt_id": attempt_id,
            "status": "completed",
            "completed_at": result["completed_at"].isoformat(),
            "time_spent_minutes": result["time_spent_minutes"],
        }

        if result["show_results"]:
            response_data.update(
                {
                    "score_earned": result["score_earned"],
                    "percentage_score": result["percentage_score"],
                    "passed": result["passed"],
                    "passing_score": result["passing_score"],
                }
            )

            if result["show_correct_answers"]:
                response_data["detailed_results"] = result["detailed_results"]
        else:
            response_data["message"] = "Results will be available after review"

        logger.info(f"Submitted attempt {attempt_id} for evaluation {evaluation_id} by user {user.id}")
        return jsonify(response_data), 200

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="ATTEMPT_NOT_FOUND")
    except InvalidStateError as e:
        return ErrorResponse.create(
            error="InvalidState", message=str(e), status_code=400, error_code="INVALID_ATTEMPT_STATE"
        )
    except Exception as e:
        logger.error(f"Error submitting attempt: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to submit attempt", status_code=500)


@bp.route("/<int:evaluation_id>/attempts/<int:attempt_id>/response", methods=["POST"])
@jwt_required()
@require_tenant()
@rate_limit(calls=200, period=60)
def submit_response(evaluation_id: int, attempt_id: int):
    """
    Submit a response for a single question (for one-at-a-time mode)

    Request Body: ResponseSubmitSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Validate request data
        try:
            data = response_submit_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Submit response
        service = EvaluationService(db.session)
        result = service.submit_response(
            tenant_id=tenant_id,
            attempt_id=attempt_id,
            user_id=user.id,
            question_id=data["question_id"],
            response_data=data["response_data"],
            time_spent_seconds=data.get("time_spent_seconds", 0),
        )

        # Prepare response
        response_data = {
            "response_saved": True,
            "question_index": result["question_index"],
            "questions_answered": result["questions_answered"],
            "total_questions": result["total_questions"],
        }

        # Add next question if applicable
        if result.get("next_question"):
            response_data["next_question"] = result["next_question"]
        else:
            response_data["all_questions_answered"] = True

        return jsonify(response_data), 200

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="ATTEMPT_NOT_FOUND")
    except InvalidStateError as e:
        return ErrorResponse.create(
            error="InvalidState", message=str(e), status_code=400, error_code="INVALID_ATTEMPT_STATE"
        )
    except Exception as e:
        logger.error(f"Error submitting response: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to submit response", status_code=500)


# Results and statistics endpoints
@bp.route("/<int:evaluation_id>/attempts", methods=["GET"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=50, period=60)
def list_attempts(evaluation_id: int):
    """
    List all attempts for an evaluation

    Query Parameters:
    - user_id: Filter by user
    - status: Filter by status
    - passed: Filter by pass/fail
    - page: Page number
    - per_page: Items per page
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Parse query parameters
        user_id = request.args.get("user_id", type=int)
        status = request.args.get("status")
        passed = request.args.get("passed")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        # Get attempts
        service = EvaluationService(db.session)
        attempts = service.get_attempts(
            tenant_id=tenant_id,
            evaluation_id=evaluation_id,
            user_id=user_id,
            status=status,
            passed=passed,
            skip=(page - 1) * per_page,
            limit=per_page,
        )

        # Serialize attempts
        attempts_data = []
        for attempt in attempts:
            attempt_dict = attempt_response_schema.dump(attempt.to_dict())
            attempt_dict["user_name"] = attempt.user.full_name
            attempts_data.append(attempt_dict)

        return (
            jsonify(
                {
                    "attempts": attempts_data,
                    "pagination": {"page": page, "per_page": per_page, "total": len(attempts_data)},
                }
            ),
            200,
        )

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except Exception as e:
        logger.error(f"Error fetching attempts: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to fetch attempts", status_code=500)


@bp.route("/<int:evaluation_id>/statistics", methods=["GET"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=50, period=60)
def get_evaluation_statistics(evaluation_id: int):
    """
    Get detailed statistics for an evaluation

    Query Parameters:
    - include_questions: Include per-question statistics
    - include_timeline: Include attempt timeline
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Parse query parameters
        include_questions = request.args.get("include_questions", "true").lower() == "true"
        include_timeline = request.args.get("include_timeline", "false").lower() == "true"

        # Get statistics
        service = EvaluationService(db.session)
        stats = service.get_statistics(
            tenant_id=tenant_id,
            evaluation_id=evaluation_id,
            user=user,
            include_questions=include_questions,
            include_timeline=include_timeline,
        )

        # Add metadata
        stats["generated_at"] = datetime.utcnow()

        return jsonify(evaluation_stats_schema.dump(stats)), 200

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except ForbiddenError as e:
        return ErrorResponse.create(
            error="Forbidden", message=str(e), status_code=403, error_code="INSUFFICIENT_PERMISSIONS"
        )
    except Exception as e:
        logger.error(f"Error fetching evaluation statistics: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to fetch statistics", status_code=500)


# Additional operations
@bp.route("/<int:evaluation_id>/duplicate", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=10, period=60)
@audit_log(action="duplicate_evaluation")
def duplicate_evaluation(evaluation_id: int):
    """
    Duplicate an evaluation with all questions

    Request Body:
    {
        "title": "New title (optional)",
        "course_id": "New course ID (optional)",
        "program_id": "New program ID (optional)"
    }
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        data = request.json or {}

        # Duplicate evaluation
        service = EvaluationService(db.session)
        duplicate = service.duplicate_evaluation(
            tenant_id=tenant_id,
            evaluation_id=evaluation_id,
            new_title=data.get("title"),
            new_course_id=data.get("course_id"),
            new_program_id=data.get("program_id"),
            user=user,
        )

        logger.info(f"Duplicated evaluation {evaluation_id} to {duplicate.id} by user {user.id}")
        return jsonify(serialize_evaluation(duplicate, include_stats=True)), 201

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except Exception as e:
        logger.error(f"Error duplicating evaluation: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to duplicate evaluation", status_code=500)


@bp.route("/<int:evaluation_id>/export", methods=["GET"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=20, period=60)
def export_evaluation(evaluation_id: int):
    """
    Export evaluation questions and results

    Query Parameters:
    - format: Export format (json|csv|pdf)
    - include_results: Include attempt results
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        export_format = request.args.get("format", "json")
        include_results = request.args.get("include_results", "false").lower() == "true"

        # Get evaluation data
        service = EvaluationService(db.session)
        evaluation = service.get_by_id(tenant_id, evaluation_id, user)

        if export_format == "json":
            # Export as JSON
            data = {
                "evaluation": serialize_evaluation(evaluation, include_stats=True),
                "questions": [serialize_question(q) for q in evaluation.questions if not q.deleted_at],
            }

            if include_results and user.role in ["admin", "manager"]:
                attempts = service.get_attempts(tenant_id, evaluation_id)
                data["attempts"] = [attempt_response_schema.dump(a.to_dict()) for a in attempts]

            return jsonify(data), 200

        elif export_format == "csv":
            # Export as CSV
            output = io.StringIO()
            writer = csv.writer(output)

            # Write headers
            writer.writerow(["Question #", "Question Text", "Type", "Difficulty", "Points", "Correct Answer"])

            # Write questions
            for idx, question in enumerate(evaluation.questions):
                if not question.deleted_at:
                    writer.writerow(
                        [
                            idx + 1,
                            question.question_text,
                            question.question_type.value,
                            question.difficulty_level,
                            question.points,
                            question.correct_answer or "Multiple Choice",
                        ]
                    )

            # Return CSV
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment; filename=evaluation_{evaluation.id}_questions.csv"},
            )

        else:
            return ErrorResponse.create(
                error="BadRequest", message="Unsupported export format", status_code=400, error_code="INVALID_FORMAT"
            )

    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound", message=str(e), status_code=404, error_code="EVALUATION_NOT_FOUND"
        )
    except Exception as e:
        logger.error(f"Error exporting evaluation: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to export evaluation", status_code=500)


@bp.route("/batch/grade", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=10, period=60)
@audit_log(action="batch_grade_attempts")
def batch_grade_attempts():
    """
    Batch grade multiple attempts

    Request Body:
    {
        "attempt_ids": [1, 2, 3],
        "grading_data": {...}
    }
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        data = request.json
        attempt_ids = data.get("attempt_ids", [])
        grading_data = data.get("grading_data", {})

        if not attempt_ids:
            raise BadRequestError("No attempt IDs provided")

        # Batch grade attempts
        service = EvaluationService(db.session)
        results = service.batch_grade_attempts(
            tenant_id=tenant_id, attempt_ids=attempt_ids, grading_data=grading_data, grader=user
        )

        logger.info(f"Batch graded {len(results['success'])} attempts by user {user.id}")

        return (
            jsonify(
                {
                    "total": len(attempt_ids),
                    "success": len(results["success"]),
                    "failed": len(results["failed"]),
                    "results": results,
                }
            ),
            200,
        )

    except BadRequestError as e:
        return ErrorResponse.create(error="BadRequest", message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error in batch grading: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to batch grade attempts", status_code=500)
