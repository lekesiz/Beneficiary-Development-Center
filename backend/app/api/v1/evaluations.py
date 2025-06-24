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


# AI Assessment Engine endpoints
@evaluations_bp.route('/<int:evaluation_id>/adaptive/start', methods=['POST'])
@require_auth
def start_adaptive_assessment(evaluation_id: int):
    """
    Start an adaptive assessment session
    """
    user = get_current_user()
    db = get_db()
    
    # Import AI service
    from app.services.ai import AdaptiveAssessmentEngine
    
    evaluation_service = EvaluationService(db)
    evaluation = evaluation_service.get_by_id(evaluation_id, user.tenant_id, include_questions=True)
    
    # Initialize adaptive engine
    engine = AdaptiveAssessmentEngine()
    
    # Create new attempt
    attempt_service = EvaluationAttemptService(db)
    attempt = attempt_service.create(
        evaluation_id=evaluation_id,
        user_id=user.id,
        tenant_id=user.tenant_id,
        is_adaptive=True
    )
    
    # Get first question based on average difficulty
    questions = evaluation.questions
    if not questions:
        raise ValidationError("No questions available for this evaluation")
    
    # Convert questions to parameters format
    question_params = []
    for q in questions:
        question_params.append({
            'question_id': q.id,
            'difficulty': getattr(q, 'difficulty_score', 0.0),
            'discrimination': 1.0,  # Default discrimination
            'guessing': 0.25  # Default guessing parameter
        })
    
    # Start with average ability estimate
    initial_theta = 0.0
    
    # Select first question
    from app.services.ai.assessment_engine import QuestionParameters
    available = [QuestionParameters(**params) for params in question_params]
    first_question = engine.select_next_question(initial_theta, available, [])
    
    if not first_question:
        raise ValidationError("Could not select initial question")
    
    # Find actual question object
    selected_question = next(q for q in questions if q.id == first_question.question_id)
    
    return jsonify({
        'attempt_id': attempt.id,
        'session_id': attempt.session_id,
        'question': selected_question.to_dict(),
        'question_number': 1,
        'estimated_remaining': engine.min_questions
    }), 201


@evaluations_bp.route('/adaptive/<int:attempt_id>/answer', methods=['POST'])
@require_auth
def submit_adaptive_answer(attempt_id: int):
    """
    Submit an answer and get the next adaptive question
    """
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data or 'question_id' not in data or 'answer' not in data:
        raise ValidationError("question_id and answer are required")
    
    # Import AI service
    from app.services.ai import AdaptiveAssessmentEngine
    from app.services.ai.assessment_engine import QuestionParameters, StudentAbility
    
    # Get attempt
    attempt_service = EvaluationAttemptService(db)
    attempt = attempt_service.get_by_id(attempt_id, user.tenant_id)
    
    if attempt.completed_at:
        raise ValidationError("This assessment has already been completed")
    
    # Save response
    response_service = QuestionResponseService(db)
    response = response_service.create(
        attempt_id=attempt_id,
        question_id=data['question_id'],
        answer=data['answer'],
        time_spent=data.get('time_spent', 0)
    )
    
    # Get all responses so far
    all_responses = response_service.get_by_attempt(attempt_id)
    
    # Initialize adaptive engine
    engine = AdaptiveAssessmentEngine()
    
    # Get evaluation and questions
    evaluation_service = EvaluationService(db)
    evaluation = evaluation_service.get_by_id(attempt.evaluation_id, user.tenant_id, include_questions=True)
    
    # Convert to IRT format
    question_map = {q.id: q for q in evaluation.questions}
    response_data = []
    answered_ids = []
    
    for resp in all_responses:
        question = question_map.get(resp.question_id)
        if question:
            params = QuestionParameters(
                question_id=question.id,
                difficulty=getattr(question, 'difficulty_score', 0.0),
                discrimination=1.0,
                guessing=0.25
            )
            is_correct = resp.is_correct if hasattr(resp, 'is_correct') else (resp.answer == question.correct_answer)
            response_data.append((params, is_correct))
            answered_ids.append(question.id)
    
    # Estimate current ability
    ability = engine.estimate_ability(response_data)
    
    # Check stopping criteria
    if engine.should_stop_assessment(ability):
        # Complete the assessment
        attempt_service.complete(attempt_id, user.tenant_id)
        
        # Generate performance report
        report = engine.generate_performance_report(ability, response_data)
        
        return jsonify({
            'completed': True,
            'report': report,
            'total_questions': len(response_data)
        })
    
    # Select next question
    available_params = []
    for q in evaluation.questions:
        if q.id not in answered_ids:
            available_params.append(QuestionParameters(
                question_id=q.id,
                difficulty=getattr(q, 'difficulty_score', 0.0),
                discrimination=1.0,
                guessing=0.25
            ))
    
    next_question_params = engine.select_next_question(ability.theta, available_params, answered_ids)
    
    if not next_question_params:
        # No more questions available
        attempt_service.complete(attempt_id, user.tenant_id)
        report = engine.generate_performance_report(ability, response_data)
        
        return jsonify({
            'completed': True,
            'report': report,
            'total_questions': len(response_data)
        })
    
    # Find actual question object
    next_question = question_map[next_question_params.question_id]
    
    return jsonify({
        'question': next_question.to_dict(),
        'question_number': len(response_data) + 1,
        'current_ability': round(ability.theta, 2),
        'confidence_interval': {
            'lower': round(ability.confidence_interval[0], 2),
            'upper': round(ability.confidence_interval[1], 2)
        },
        'estimated_remaining': max(engine.min_questions - len(response_data), 1)
    })


@evaluations_bp.route('/adaptive/<int:attempt_id>/report', methods=['GET'])
@require_auth
def get_adaptive_report(attempt_id: int):
    """
    Get detailed adaptive assessment report
    """
    user = get_current_user()
    db = get_db()
    
    # Import AI service
    from app.services.ai import AdaptiveAssessmentEngine
    from app.services.ai.assessment_engine import QuestionParameters
    
    # Get attempt and responses
    attempt_service = EvaluationAttemptService(db)
    attempt = attempt_service.get_by_id(attempt_id, user.tenant_id)
    
    if not attempt.completed_at:
        raise ValidationError("Assessment is not yet completed")
    
    response_service = QuestionResponseService(db)
    responses = response_service.get_by_attempt(attempt_id)
    
    # Get evaluation and questions
    evaluation_service = EvaluationService(db)
    evaluation = evaluation_service.get_by_id(attempt.evaluation_id, user.tenant_id, include_questions=True)
    
    # Convert to IRT format
    question_map = {q.id: q for q in evaluation.questions}
    response_data = []
    
    for resp in responses:
        question = question_map.get(resp.question_id)
        if question:
            params = QuestionParameters(
                question_id=question.id,
                difficulty=getattr(question, 'difficulty_score', 0.0),
                discrimination=1.0,
                guessing=0.25
            )
            is_correct = resp.is_correct if hasattr(resp, 'is_correct') else (resp.answer == question.correct_answer)
            response_data.append((params, is_correct))
    
    # Generate report
    engine = AdaptiveAssessmentEngine()
    ability = engine.estimate_ability(response_data)
    report = engine.generate_performance_report(ability, response_data)
    
    # Add question-level details
    question_details = []
    for resp in responses:
        question = question_map.get(resp.question_id)
        if question:
            question_details.append({
                'question_id': question.id,
                'question_text': question.text,
                'difficulty': getattr(question, 'difficulty_score', 0.0),
                'user_answer': resp.answer,
                'correct_answer': question.correct_answer,
                'is_correct': resp.answer == question.correct_answer,
                'time_spent': resp.time_spent
            })
    
    report['question_details'] = question_details
    report['evaluation_name'] = evaluation.name
    report['completed_at'] = attempt.completed_at.isoformat() if attempt.completed_at else None
    
    return jsonify(report)


@evaluations_bp.route('/question-bank/analyze', methods=['POST'])
@require_auth(['admin', 'trainer'])
def analyze_question_bank():
    """
    Analyze question bank quality and get recommendations
    """
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    evaluation_id = data.get('evaluation_id')
    if not evaluation_id:
        raise ValidationError("evaluation_id is required")
    
    # Import AI service
    from app.services.ai import QuestionBankOptimizer
    
    # Get evaluation questions
    evaluation_service = EvaluationService(db)
    evaluation = evaluation_service.get_by_id(evaluation_id, user.tenant_id, include_questions=True)
    
    # Get question statistics
    question_service = QuestionService(db)
    optimizer = QuestionBankOptimizer()
    
    analysis_results = []
    recommendations = []
    
    for question in evaluation.questions:
        # Get usage statistics
        stats = question_service.get_question_statistics(question.id)
        
        # Analyze quality
        quality_metrics = optimizer.analyze_question_quality(stats)
        quality_metrics['id'] = question.id
        quality_metrics['text'] = question.text
        
        analysis_results.append(quality_metrics)
    
    # Get recommendations
    recommendations = optimizer.recommend_questions_for_revision(analysis_results)
    
    return jsonify({
        'analysis': analysis_results,
        'recommendations': recommendations,
        'summary': {
            'total_questions': len(evaluation.questions),
            'high_quality': len([q for q in analysis_results if q['quality_score'] > 0.7]),
            'needs_revision': len(recommendations),
            'average_discrimination': sum(q['discrimination'] for q in analysis_results) / len(analysis_results) if analysis_results else 0
        }
    })