"""
Evaluation API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from marshmallow import ValidationError

from app.models.user import User
from app.models.evaluation import AttemptStatus
from app.services.evaluation_service import (
    EvaluationService,
    QuestionService,
    EvaluationAttemptService,
    QuestionResponseService,
)
from app.schemas.evaluation import (
    EvaluationCreateSchema,
    EvaluationUpdateSchema,
    EvaluationResponseSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    QuestionResponseSchema,
    EvaluationAttemptResponseSchema,
    QuestionResponseSaveSchema,
    EvaluationListQuerySchema,
)
from app.core.decorators import require_tenant, check_role
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError
from app.core.database import get_db

evaluations_bp = Blueprint("evaluations", __name__, url_prefix="/api/v1/evaluations")


@evaluations_bp.route("", methods=["GET"])
@jwt_required()
@require_tenant()
def get_evaluations():
    """Get all evaluations with filtering and pagination"""
    # Parse and validate query parameters
    query_schema = EvaluationListQuerySchema()
    try:
        filters = query_schema.load(request.args)
    except ValidationError as e:
        return jsonify({"error": "Invalid query parameters", "details": e.messages}), 400

    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get evaluations
        service = EvaluationService(db)
        result = service.get_all(tenant_id, filters, user)

        # Serialize response
        schema = EvaluationResponseSchema(many=True)
        evaluations_data = schema.dump(result["evaluations"])

        return jsonify({"evaluations": evaluations_data, "pagination": result["pagination"]}), 200

    finally:
        db.close()


@evaluations_bp.route("/<int:evaluation_id>", methods=["GET"])
@jwt_required()
@require_tenant()
def get_evaluation(evaluation_id):
    """Get evaluation by ID"""
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")
    include_questions = request.args.get("include_questions", "false").lower() == "true"

    db = next(get_db())
    try:
        service = EvaluationService(db)
        evaluation = service.get_by_id(evaluation_id, tenant_id, include_questions)

        schema = EvaluationResponseSchema()
        return jsonify(schema.dump(evaluation)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        db.close()


@evaluations_bp.route("", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def create_evaluation():
    """Create a new evaluation"""
    # Validate request data
    schema = EvaluationCreateSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": "Invalid data", "details": e.messages}), 400

    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Create evaluation
        service = EvaluationService(db)
        evaluation = service.create(tenant_id, data, user)

        # Serialize response
        response_schema = EvaluationResponseSchema()
        return jsonify(response_schema.dump(evaluation)), 201

    except (BadRequestError, ForbiddenError) as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@evaluations_bp.route("/<int:evaluation_id>", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def update_evaluation(evaluation_id):
    """Update an evaluation"""
    # Validate request data
    schema = EvaluationUpdateSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": "Invalid data", "details": e.messages}), 400

    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update evaluation
        service = EvaluationService(db)
        evaluation = service.update(evaluation_id, tenant_id, data, user)

        # Serialize response
        response_schema = EvaluationResponseSchema()
        return jsonify(response_schema.dump(evaluation)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (BadRequestError, ForbiddenError) as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@evaluations_bp.route("/<int:evaluation_id>", methods=["DELETE"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def delete_evaluation(evaluation_id):
    """Delete an evaluation"""
    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Delete evaluation
        service = EvaluationService(db)
        service.delete(evaluation_id, tenant_id, user)

        return jsonify({"message": "Evaluation deleted successfully"}), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    finally:
        db.close()


@evaluations_bp.route("/<int:evaluation_id>/activate", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def activate_evaluation(evaluation_id):
    """Activate an evaluation"""
    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Activate evaluation
        service = EvaluationService(db)
        evaluation = service.activate(evaluation_id, tenant_id, user)

        # Serialize response
        response_schema = EvaluationResponseSchema()
        return jsonify(response_schema.dump(evaluation)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (BadRequestError, ForbiddenError) as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@evaluations_bp.route("/<int:evaluation_id>/archive", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def archive_evaluation(evaluation_id):
    """Archive an evaluation"""
    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Archive evaluation
        service = EvaluationService(db)
        evaluation = service.archive(evaluation_id, tenant_id, user)

        # Serialize response
        response_schema = EvaluationResponseSchema()
        return jsonify(response_schema.dump(evaluation)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    finally:
        db.close()


# Question endpoints
@evaluations_bp.route("/<int:evaluation_id>/questions", methods=["GET"])
@jwt_required()
@require_tenant()
def get_questions(evaluation_id):
    """Get all questions for an evaluation"""
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        # Verify evaluation exists
        eval_service = EvaluationService(db)
        eval_service.get_by_id(evaluation_id, tenant_id)

        # Get questions
        service = QuestionService(db)
        questions = service.get_by_evaluation(evaluation_id, tenant_id)

        # Serialize response
        schema = QuestionResponseSchema(many=True)
        return jsonify(schema.dump(questions)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        db.close()


@evaluations_bp.route("/<int:evaluation_id>/questions", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def add_question(evaluation_id):
    """Add a question to an evaluation"""
    # Validate request data
    schema = QuestionCreateSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": "Invalid data", "details": e.messages}), 400

    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Create question
        service = QuestionService(db)
        question = service.create(evaluation_id, tenant_id, data, user)

        # Serialize response
        response_schema = QuestionResponseSchema()
        return jsonify(response_schema.dump(question)), 201

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (BadRequestError, ForbiddenError) as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@evaluations_bp.route("/questions/<int:question_id>", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def update_question(question_id):
    """Update a question"""
    # Validate request data
    schema = QuestionUpdateSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": "Invalid data", "details": e.messages}), 400

    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update question
        service = QuestionService(db)
        question = service.update(question_id, tenant_id, data, user)

        # Serialize response
        response_schema = QuestionResponseSchema()
        return jsonify(response_schema.dump(question)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    finally:
        db.close()


@evaluations_bp.route("/questions/<int:question_id>", methods=["DELETE"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def delete_question(question_id):
    """Delete a question"""
    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Delete question
        service = QuestionService(db)
        service.delete(question_id, tenant_id, user)

        return jsonify({"message": "Question deleted successfully"}), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    finally:
        db.close()


# Evaluation attempt endpoints
@evaluations_bp.route("/<int:evaluation_id>/start", methods=["POST"])
@jwt_required()
@require_tenant()
def start_attempt(evaluation_id):
    """Start a new evaluation attempt"""
    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Start attempt
        service = EvaluationAttemptService(db)
        attempt = service.start_attempt(evaluation_id, tenant_id, user)

        # Serialize response
        response_schema = EvaluationAttemptResponseSchema()
        return jsonify(response_schema.dump(attempt)), 201

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@evaluations_bp.route("/attempts/<int:attempt_id>", methods=["GET"])
@jwt_required()
@require_tenant()
def get_attempt(attempt_id):
    """Get evaluation attempt details"""
    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get attempt
        service = EvaluationAttemptService(db)
        attempt = service.get_by_id(attempt_id, tenant_id)

        # Check permissions
        if attempt.user_id != user.id and user.role not in ["admin", "manager", "instructor"]:
            return jsonify({"error": "You do not have permission to view this attempt"}), 403

        # Serialize response
        response_schema = EvaluationAttemptResponseSchema()
        return jsonify(response_schema.dump(attempt)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        db.close()


@evaluations_bp.route("/attempts/<int:attempt_id>/submit", methods=["POST"])
@jwt_required()
@require_tenant()
def submit_attempt(attempt_id):
    """Submit and score an evaluation attempt"""
    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Submit attempt
        service = EvaluationAttemptService(db)
        attempt = service.submit_attempt(attempt_id, tenant_id, user)

        # Serialize response
        response_schema = EvaluationAttemptResponseSchema()
        return jsonify(response_schema.dump(attempt)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (BadRequestError, ForbiddenError) as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@evaluations_bp.route("/attempts/<int:attempt_id>/responses", methods=["POST"])
@jwt_required()
@require_tenant()
def save_response(attempt_id):
    """Save a question response"""
    # Validate request data
    schema = QuestionResponseSaveSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": "Invalid data", "details": e.messages}), 400

    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Save response
        service = QuestionResponseService(db)
        response = service.save_response(attempt_id, data["question_id"], tenant_id, data["response_data"], user)

        return (
            jsonify(
                {
                    "message": "Response saved successfully",
                    "is_correct": response.is_correct,
                    "points_earned": response.points_earned,
                }
            ),
            200,
        )

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except (BadRequestError, ForbiddenError) as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@evaluations_bp.route("/attempts/<int:attempt_id>/results", methods=["GET"])
@jwt_required()
@require_tenant()
def get_attempt_results(attempt_id):
    """Get detailed results for an evaluation attempt"""
    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get attempt with responses
        service = EvaluationAttemptService(db)
        attempt = service.get_by_id(attempt_id, tenant_id)

        # Check permissions
        if attempt.user_id != user.id and user.role not in ["admin", "manager", "instructor"]:
            return jsonify({"error": "You do not have permission to view these results"}), 403

        # Check if results can be shown
        if attempt.status != AttemptStatus.COMPLETED:
            return jsonify({"error": "Attempt not yet completed"}), 400

        if not attempt.evaluation.show_results_immediately and user.role not in ["admin", "manager", "instructor"]:
            return jsonify({"error": "Results are not available yet"}), 403

        # Build detailed results
        results = {
            "attempt_id": attempt.id,
            "evaluation_title": attempt.evaluation.title,
            "status": attempt.status.value,
            "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
            "time_spent_minutes": attempt.time_spent_minutes,
            "duration_display": attempt.duration_display,
            "total_questions": attempt.total_questions,
            "questions_answered": attempt.questions_answered,
            "total_points": attempt.total_points,
            "score_earned": attempt.score_earned,
            "percentage_score": attempt.percentage_score,
            "passing_score": attempt.passing_score,
            "passed": attempt.passed,
            "responses": [],
        }

        # Add question responses if review is allowed
        if attempt.evaluation.allow_review or user.role in ["admin", "manager", "instructor"]:
            for response in attempt.responses:
                question_data = {
                    "question_id": response.question_id,
                    "question_text": response.question.question_text,
                    "question_type": response.question.question_type.value,
                    "points": response.question.points,
                    "response_data": response.response_data,
                    "is_correct": response.is_correct,
                    "points_earned": response.points_earned,
                }

                # Include correct answer and explanation if review is allowed
                if response.question.explanation:
                    question_data["explanation"] = response.question.explanation

                if response.ai_feedback:
                    question_data["ai_feedback"] = response.ai_feedback

                results["responses"].append(question_data)

        return jsonify(results), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        db.close()


@evaluations_bp.route("/<int:evaluation_id>/attempts", methods=["GET"])
@jwt_required()
@require_tenant()
def get_user_attempts(evaluation_id):
    """Get all attempts by the current user for an evaluation"""
    # Get current user
    user_id = get_jwt_identity()
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        # Get attempts
        service = EvaluationAttemptService(db)
        attempts = service.get_user_attempts(evaluation_id, user_id, tenant_id)

        # Serialize response
        response_schema = EvaluationAttemptResponseSchema(many=True)
        return jsonify(response_schema.dump(attempts)), 200

    finally:
        db.close()


@evaluations_bp.route("/<int:evaluation_id>/statistics", methods=["GET"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def get_evaluation_statistics(evaluation_id):
    """Get statistics for an evaluation"""
    claims = get_jwt()
    tenant_id = claims.get("tenant_id")

    db = next(get_db())
    try:
        # Get evaluation
        service = EvaluationService(db)
        evaluation = service.get_by_id(evaluation_id, tenant_id, include_questions=True)

        # Calculate statistics
        total_attempts = len(evaluation.attempts)
        completed_attempts = [a for a in evaluation.attempts if a.status == AttemptStatus.COMPLETED]
        passed_attempts = [a for a in completed_attempts if a.passed]

        stats = {
            "evaluation_id": evaluation.id,
            "evaluation_title": evaluation.title,
            "total_questions": evaluation.total_questions,
            "total_points": evaluation.total_points,
            "passing_score": evaluation.passing_score,
            "total_attempts": total_attempts,
            "completed_attempts": len(completed_attempts),
            "passed_attempts": len(passed_attempts),
            "pass_rate": (len(passed_attempts) / len(completed_attempts) * 100) if completed_attempts else 0,
            "average_score": (
                sum(a.percentage_score for a in completed_attempts) / len(completed_attempts)
                if completed_attempts
                else 0
            ),
            "average_time_minutes": (
                sum(a.time_spent_minutes or 0 for a in completed_attempts) / len(completed_attempts)
                if completed_attempts
                else 0
            ),
            "question_statistics": [],
        }

        # Calculate per-question statistics
        for question in evaluation.questions:
            correct_responses = [r for r in question.responses if r.is_correct is True]
            total_responses = [r for r in question.responses if r.attempt.status == AttemptStatus.COMPLETED]

            question_stats = {
                "question_id": question.id,
                "question_type": question.question_type.value,
                "difficulty_level": question.difficulty_level.value,
                "points": question.points,
                "total_responses": len(total_responses),
                "correct_responses": len(correct_responses),
                "success_rate": (len(correct_responses) / len(total_responses) * 100) if total_responses else 0,
            }
            stats["question_statistics"].append(question_stats)

        return jsonify(stats), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        db.close()


# Register the blueprint in __init__.py
