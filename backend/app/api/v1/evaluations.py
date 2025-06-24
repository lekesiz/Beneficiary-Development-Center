"""
Evaluation API endpoints
"""
from typing import Dict, Any, List
from flask import Blueprint, request, jsonify
from app.services.evaluation_service import (
    EvaluationService, QuestionService, EvaluationAttemptService, QuestionResponseService
)
from app.services.adaptive_evaluation_service import adaptive_evaluation_service
from app.core.auth import require_auth, get_current_user
from app.core.database import get_db
from app.core.exceptions import ValidationError

evaluations_bp = Blueprint('evaluations', __name__, url_prefix='/api/evaluations')


@evaluations_bp.route('', methods=['GET'])
@require_auth
def get_evaluations():
    """Get all evaluations"""
    user = get_current_user()
    db = get_db()
    
    # Get query parameters
    filters = {
        'page': request.args.get('page', 1, type=int),
        'per_page': request.args.get('per_page', 20, type=int),
        'status': request.args.get('status'),
        'course_id': request.args.get('course_id', type=int),
        'program_id': request.args.get('program_id', type=int),
        'search': request.args.get('search'),
        'sort_by': request.args.get('sort_by', 'created_at'),
        'sort_desc': request.args.get('sort_desc', 'true').lower() == 'true'
    }
    
    evaluation_service = EvaluationService(db)
    result = evaluation_service.get_all(user.tenant_id, filters, user)
    
    # Convert to dict
    evaluations = []
    for evaluation in result['evaluations']:
        evaluation_dict = evaluation.to_dict()
        evaluations.append(evaluation_dict)
    
    return jsonify({
        'evaluations': evaluations,
        'pagination': result['pagination']
    })


@evaluations_bp.route('/<int:evaluation_id>', methods=['GET'])
@require_auth
def get_evaluation(evaluation_id: int):
    """Get evaluation by ID"""
    user = get_current_user()
    db = get_db()
    
    include_questions = request.args.get('include_questions', 'false').lower() == 'true'
    
    evaluation_service = EvaluationService(db)
    evaluation = evaluation_service.get_by_id(evaluation_id, user.tenant_id, include_questions)
    
    evaluation_dict = evaluation.to_dict()
    
    if include_questions and evaluation.questions:
        evaluation_dict['questions'] = [q.to_dict() for q in evaluation.questions]
    
    return jsonify(evaluation_dict)


@evaluations_bp.route('', methods=['POST'])
@require_auth
def create_evaluation():
    """Create a new evaluation"""
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data:
        raise ValidationError("Request body is required")
    
    evaluation_service = EvaluationService(db)
    evaluation = evaluation_service.create(user.tenant_id, data, user)
    
    return jsonify(evaluation.to_dict()), 201


@evaluations_bp.route('/<int:evaluation_id>', methods=['PUT'])
@require_auth
def update_evaluation(evaluation_id: int):
    """Update an evaluation"""
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data:
        raise ValidationError("Request body is required")
    
    evaluation_service = EvaluationService(db)
    evaluation = evaluation_service.update(evaluation_id, user.tenant_id, data, user)
    
    return jsonify(evaluation.to_dict())


@evaluations_bp.route('/<int:evaluation_id>', methods=['DELETE'])
@require_auth
def delete_evaluation(evaluation_id: int):
    """Delete an evaluation"""
    user = get_current_user()
    db = get_db()
    
    evaluation_service = EvaluationService(db)
    evaluation_service.delete(evaluation_id, user.tenant_id, user)
    
    return jsonify({'message': 'Evaluation deleted successfully'})


@evaluations_bp.route('/<int:evaluation_id>/activate', methods=['POST'])
@require_auth
def activate_evaluation(evaluation_id: int):
    """Activate an evaluation"""
    user = get_current_user()
    db = get_db()
    
    evaluation_service = EvaluationService(db)
    evaluation = evaluation_service.activate(evaluation_id, user.tenant_id, user)
    
    return jsonify(evaluation.to_dict())


@evaluations_bp.route('/<int:evaluation_id>/archive', methods=['POST'])
@require_auth
def archive_evaluation(evaluation_id: int):
    """Archive an evaluation"""
    user = get_current_user()
    db = get_db()
    
    evaluation_service = EvaluationService(db)
    evaluation = evaluation_service.archive(evaluation_id, user.tenant_id, user)
    
    return jsonify(evaluation.to_dict())


# Question endpoints
@evaluations_bp.route('/<int:evaluation_id>/questions', methods=['GET'])
@require_auth
def get_questions(evaluation_id: int):
    """Get all questions for an evaluation"""
    user = get_current_user()
    db = get_db()
    
    question_service = QuestionService(db)
    questions = question_service.get_by_evaluation(evaluation_id, user.tenant_id)
    
    return jsonify([q.to_dict() for q in questions])


@evaluations_bp.route('/<int:evaluation_id>/questions', methods=['POST'])
@require_auth
def create_question(evaluation_id: int):
    """Create a new question"""
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data:
        raise ValidationError("Request body is required")
    
    question_service = QuestionService(db)
    question = question_service.create(evaluation_id, user.tenant_id, data, user)
    
    return jsonify(question.to_dict()), 201


@evaluations_bp.route('/<int:evaluation_id>/questions/<int:question_id>', methods=['PUT'])
@require_auth
def update_question(evaluation_id: int, question_id: int):
    """Update a question"""
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data:
        raise ValidationError("Request body is required")
    
    question_service = QuestionService(db)
    question = question_service.update(question_id, user.tenant_id, data, user)
    
    return jsonify(question.to_dict())


@evaluations_bp.route('/<int:evaluation_id>/questions/<int:question_id>', methods=['DELETE'])
@require_auth
def delete_question(evaluation_id: int, question_id: int):
    """Delete a question"""
    user = get_current_user()
    db = get_db()
    
    question_service = QuestionService(db)
    question_service.delete(question_id, user.tenant_id, user)
    
    return jsonify({'message': 'Question deleted successfully'})


@evaluations_bp.route('/<int:evaluation_id>/questions/<int:question_id>/reorder', methods=['POST'])
@require_auth
def reorder_question(evaluation_id: int, question_id: int):
    """Reorder a question"""
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data or 'order_index' not in data:
        raise ValidationError("order_index is required")
    
    question_service = QuestionService(db)
    question = question_service.reorder(question_id, user.tenant_id, data['order_index'], user)
    
    return jsonify(question.to_dict())


# Attempt endpoints
@evaluations_bp.route('/<int:evaluation_id>/attempts', methods=['POST'])
@require_auth
def start_attempt(evaluation_id: int):
    """Start a new evaluation attempt"""
    user = get_current_user()
    db = get_db()
    
    attempt_service = EvaluationAttemptService(db)
    attempt = attempt_service.start_attempt(evaluation_id, user.tenant_id, user)
    
    return jsonify(attempt.to_dict()), 201


@evaluations_bp.route('/<int:evaluation_id>/attempts/<int:attempt_id>', methods=['GET'])
@require_auth
def get_attempt(evaluation_id: int, attempt_id: int):
    """Get an evaluation attempt"""
    user = get_current_user()
    db = get_db()
    
    attempt_service = EvaluationAttemptService(db)
    attempt = attempt_service.get_by_id(attempt_id, user.tenant_id)
    
    # Check permissions
    if attempt.user_id != user.id and user.role not in ['admin', 'manager', 'instructor']:
        return jsonify({'error': 'Forbidden'}), 403
    
    attempt_dict = attempt.to_dict()
    
    # Include responses if user owns the attempt or has admin rights
    if attempt.user_id == user.id or user.role in ['admin', 'manager']:
        attempt_dict['responses'] = [r.to_dict() for r in attempt.responses]
    
    return jsonify(attempt_dict)


@evaluations_bp.route('/<int:evaluation_id>/attempts/<int:attempt_id>/submit', methods=['POST'])
@require_auth
def submit_attempt(evaluation_id: int, attempt_id: int):
    """Submit an evaluation attempt"""
    user = get_current_user()
    db = get_db()
    
    attempt_service = EvaluationAttemptService(db)
    attempt = attempt_service.submit_attempt(attempt_id, user.tenant_id, user)
    
    return jsonify(attempt.to_dict())


@evaluations_bp.route('/<int:evaluation_id>/attempts/<int:attempt_id>/responses', methods=['POST'])
@require_auth
def save_response(evaluation_id: int, attempt_id: int):
    """Save a question response"""
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data or 'question_id' not in data or 'response_data' not in data:
        raise ValidationError("question_id and response_data are required")
    
    response_service = QuestionResponseService(db)
    response = response_service.save_response(
        attempt_id, 
        data['question_id'], 
        user.tenant_id, 
        data['response_data'], 
        user
    )
    
    return jsonify(response.to_dict())


@evaluations_bp.route('/<int:evaluation_id>/my-attempts', methods=['GET'])
@require_auth
def get_my_attempts(evaluation_id: int):
    """Get current user's attempts for an evaluation"""
    user = get_current_user()
    db = get_db()
    
    attempt_service = EvaluationAttemptService(db)
    attempts = attempt_service.get_user_attempts(evaluation_id, user.id, user.tenant_id)
    
    return jsonify([attempt.to_dict() for attempt in attempts])


@evaluations_bp.route('/statistics', methods=['GET'])
@require_auth
def get_evaluation_statistics():
    """Get evaluation statistics"""
    user = get_current_user()
    db = get_db()
    
    # Get basic statistics
    evaluation_service = EvaluationService(db)
    
    # This would be implemented based on specific requirements
    # For now, return a placeholder
    stats = {
        'total_evaluations': 0,
        'active_evaluations': 0,
        'total_attempts': 0,
        'average_score': 0,
        'pass_rate': 0
    }
    
    return jsonify(stats)


@evaluations_bp.route('/<int:evaluation_id>/next-question', methods=['GET'])
@require_auth
def get_next_adaptive_question(evaluation_id: int):
    """
    Get the next question using AI-powered adaptive logic.
    The question difficulty adapts based on user's recent performance.
    """
    user = get_current_user()
    
    # Get attempt_id from query params
    attempt_id = request.args.get('attempt_id', type=int)
    if not attempt_id:
        raise ValidationError("attempt_id query parameter is required")
    
    # Get next question using adaptive service
    next_question = adaptive_evaluation_service.get_next_question(
        tenant_id=user.tenant_id,
        evaluation_id=evaluation_id,
        attempt_id=attempt_id,
        user_id=user.id
    )
    
    if not next_question:
        # No more questions - evaluation complete
        return jsonify({
            'complete': True,
            'message': 'All questions have been answered',
            'next_action': 'submit'
        })
    
    # Return question data with adaptive metadata
    question_data = next_question.to_dict()
    
    # Add adaptive metadata
    question_data['adaptive_metadata'] = {
        'difficulty_adjusted': True,
        'current_difficulty': next_question.difficulty_level,
        'question_number': request.args.get('current_index', 0, type=int) + 1
    }
    
    return jsonify({
        'complete': False,
        'question': question_data
    })


@evaluations_bp.route('/<int:evaluation_id>/attempts/<int:attempt_id>/insights', methods=['GET'])
@require_auth
def get_learning_insights(evaluation_id: int, attempt_id: int):
    """
    Get AI-powered learning insights for the evaluation attempt.
    Provides personalized recommendations and performance analysis.
    """
    user = get_current_user()
    
    # Get insights from adaptive service
    insights = adaptive_evaluation_service.get_learning_insights(
        tenant_id=user.tenant_id,
        evaluation_id=evaluation_id,
        attempt_id=attempt_id
    )
    
    return jsonify(insights)


@evaluations_bp.route('/<int:evaluation_id>/attempts/<int:attempt_id>/learning-path', methods=['POST'])
@require_auth
def create_learning_path(evaluation_id: int, attempt_id: int):
    """
    Create a personalized learning path based on evaluation results.
    Uses AI to generate a 4-week customized study plan.
    """
    user = get_current_user()
    db = get_db()
    
    # Import service here to avoid circular imports
    from app.services.learning_path_service import learning_path_service
    
    # Create learning path
    learning_path = learning_path_service.create_learning_path(
        tenant_id=user.tenant_id,
        evaluation_id=evaluation_id,
        attempt_id=attempt_id,
        user=user
    )
    
    return jsonify(learning_path.to_dict()), 201