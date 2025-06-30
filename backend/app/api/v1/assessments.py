"""
360° Assessment System API endpoints
For Bilan de Compétence Platform
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.assessment import (
    Assessment, AssessmentQuestion, AssessmentInvitation,
    AssessmentResponse, AssessmentQuestionResponse, Competency,
    AssessmentType, AssessmentStatus
)
from app.models.user import User
from app.extensions import db
from app.core.decorators import tenant_required
from app.core.jwt_utils import get_current_user_id
from app.core.pagination import paginate
from datetime import datetime, timedelta
import secrets
import string

bp = Blueprint('assessments', __name__, url_prefix='/api/v1/assessments')

@bp.route('', methods=['GET'])
@jwt_required()
@tenant_required
def get_assessments():
    """Get all assessments for the current user"""
    user_id = get_current_user_id()
    
    # Get assessments where user is beneficiary or creator
    query = Assessment.query.filter(
        db.or_(
            Assessment.beneficiary_id == user_id,
            Assessment.created_by_id == user_id
        )
    )
    
    # Apply filters
    status = request.args.get('status')
    if status:
        query = query.filter(Assessment.status == status)
    
    assessment_type = request.args.get('type')
    if assessment_type:
        query = query.filter(Assessment.assessment_type == assessment_type)
    
    # Pagination
    return paginate(query, Assessment)

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_assessment(id):
    """Get a specific assessment"""
    user_id = get_current_user_id()
    
    assessment = Assessment.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if assessment.beneficiary_id != user_id and assessment.created_by_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': assessment.id,
        'title': assessment.title,
        'description': assessment.description,
        'assessment_type': assessment.assessment_type.value,
        'status': assessment.status.value,
        'beneficiary_id': assessment.beneficiary_id,
        'created_by_id': assessment.created_by_id,
        'is_anonymous': assessment.is_anonymous,
        'deadline': assessment.deadline.isoformat() if assessment.deadline else None,
        'completion_rate': assessment.completion_rate,
        'average_score': assessment.average_score,
        'questions_count': len(assessment.questions),
        'invitations_count': len(assessment.invitations),
        'responses_count': len(assessment.responses),
        'created_at': assessment.created_at.isoformat(),
        'updated_at': assessment.updated_at.isoformat()
    })

@bp.route('', methods=['POST'])
@jwt_required()
@tenant_required
def create_assessment():
    """Create a new assessment"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    if not data.get('assessment_type'):
        return jsonify({'error': 'Assessment type is required'}), 400
    
    # Create assessment
    assessment = Assessment(
        title=data['title'],
        description=data.get('description'),
        assessment_type=AssessmentType[data['assessment_type'].upper()],
        status=AssessmentStatus.DRAFT,
        beneficiary_id=data.get('beneficiary_id', user_id),
        created_by_id=user_id,
        is_anonymous=data.get('is_anonymous', False),
        deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
        reminder_frequency=data.get('reminder_frequency', 7),
        max_responses=data.get('max_responses'),
        use_weighted_scoring=data.get('use_weighted_scoring', False),
        show_results_to_beneficiary=data.get('show_results_to_beneficiary', True)
    )
    
    db.session.add(assessment)
    db.session.commit()
    
    return jsonify({
        'id': assessment.id,
        'title': assessment.title,
        'status': assessment.status.value
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_assessment(id):
    """Update an assessment"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    assessment = Assessment.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if assessment.created_by_id != user_id:
        return jsonify({'error': 'Only the creator can update the assessment'}), 403
    
    # Check if assessment can be modified
    if assessment.status == AssessmentStatus.COMPLETED:
        return jsonify({'error': 'Cannot modify completed assessment'}), 400
    
    # Update fields
    if 'title' in data:
        assessment.title = data['title']
    if 'description' in data:
        assessment.description = data['description']
    if 'deadline' in data:
        assessment.deadline = datetime.fromisoformat(data['deadline']) if data['deadline'] else None
    if 'is_anonymous' in data:
        assessment.is_anonymous = data['is_anonymous']
    if 'reminder_frequency' in data:
        assessment.reminder_frequency = data['reminder_frequency']
    if 'max_responses' in data:
        assessment.max_responses = data['max_responses']
    if 'use_weighted_scoring' in data:
        assessment.use_weighted_scoring = data['use_weighted_scoring']
    if 'show_results_to_beneficiary' in data:
        assessment.show_results_to_beneficiary = data['show_results_to_beneficiary']
    
    db.session.commit()
    
    return jsonify({'message': 'Assessment updated successfully'})

@bp.route('/<int:id>/questions', methods=['GET'])
@jwt_required()
@tenant_required
def get_assessment_questions(id):
    """Get questions for an assessment"""
    user_id = get_current_user_id()
    
    assessment = Assessment.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if assessment.beneficiary_id != user_id and assessment.created_by_id != user_id:
        # Check if user has a valid invitation
        invitation = AssessmentInvitation.query.filter_by(
            assessment_id=id,
            evaluator_email=request.args.get('email')
        ).first()
        
        if not invitation or invitation.status == 'expired':
            return jsonify({'error': 'Unauthorized'}), 403
    
    questions = assessment.questions
    
    return jsonify({
        'questions': [{
            'id': q.id,
            'question_text': q.question_text,
            'question_type': q.question_type.value,
            'skill_category': q.skill_category,
            'order_index': q.order_index,
            'is_required': q.is_required,
            'weight': q.weight,
            'min_rating': q.min_rating,
            'max_rating': q.max_rating,
            'rating_labels': q.rating_labels,
            'options': q.options,
            'allow_multiple': q.allow_multiple,
            'help_text': q.help_text,
            'example_answer': q.example_answer
        } for q in sorted(questions, key=lambda x: x.order_index)]
    })

@bp.route('/<int:id>/questions', methods=['POST'])
@jwt_required()
@tenant_required
def add_assessment_question(id):
    """Add a question to an assessment"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    assessment = Assessment.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if assessment.created_by_id != user_id:
        return jsonify({'error': 'Only the creator can add questions'}), 403
    
    # Check if assessment can be modified
    if assessment.status != AssessmentStatus.DRAFT:
        return jsonify({'error': 'Can only add questions to draft assessments'}), 400
    
    # Create question
    question = AssessmentQuestion(
        assessment_id=id,
        question_text=data['question_text'],
        question_type=data.get('question_type', 'RATING'),
        skill_category=data.get('skill_category'),
        competency_id=data.get('competency_id'),
        order_index=data.get('order_index', len(assessment.questions)),
        is_required=data.get('is_required', True),
        weight=data.get('weight', 1.0),
        min_rating=data.get('min_rating', 1),
        max_rating=data.get('max_rating', 5),
        rating_labels=data.get('rating_labels'),
        options=data.get('options'),
        allow_multiple=data.get('allow_multiple', False),
        help_text=data.get('help_text'),
        example_answer=data.get('example_answer')
    )
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify({
        'id': question.id,
        'question_text': question.question_text
    }), 201

@bp.route('/<int:id>/invitations', methods=['GET'])
@jwt_required()
@tenant_required
def get_assessment_invitations(id):
    """Get invitations for an assessment"""
    user_id = get_current_user_id()
    
    assessment = Assessment.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if assessment.created_by_id != user_id:
        return jsonify({'error': 'Only the creator can view invitations'}), 403
    
    invitations = assessment.invitations
    
    return jsonify({
        'invitations': [{
            'id': inv.id,
            'evaluator_email': inv.evaluator_email,
            'evaluator_name': inv.evaluator_name,
            'evaluator_role': inv.evaluator_role.value,
            'status': inv.status,
            'sent_at': inv.sent_at.isoformat() if inv.sent_at else None,
            'opened_at': inv.opened_at.isoformat() if inv.opened_at else None,
            'completed_at': inv.completed_at.isoformat() if inv.completed_at else None,
            'reminders_sent': inv.reminders_sent,
            'public_url': inv.generate_public_url(request.host_url)
        } for inv in invitations]
    })

@bp.route('/<int:id>/invitations', methods=['POST'])
@jwt_required()
@tenant_required
def create_assessment_invitation(id):
    """Create invitations for an assessment"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    assessment = Assessment.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if assessment.created_by_id != user_id:
        return jsonify({'error': 'Only the creator can send invitations'}), 403
    
    # Check if assessment is ready
    if assessment.status == AssessmentStatus.DRAFT:
        return jsonify({'error': 'Cannot send invitations for draft assessment'}), 400
    
    if not assessment.questions:
        return jsonify({'error': 'Assessment must have questions before sending invitations'}), 400
    
    invitations_created = []
    
    # Create invitations
    for inv_data in data.get('invitations', []):
        # Generate unique access token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        invitation = AssessmentInvitation(
            assessment_id=id,
            evaluator_email=inv_data['email'],
            evaluator_name=inv_data.get('name'),
            evaluator_role=AssessmentType[inv_data['role'].upper()],
            access_token=token,
            token_expiry=datetime.utcnow() + timedelta(days=30),
            custom_message=inv_data.get('custom_message'),
            status='sent',
            sent_at=datetime.utcnow()
        )
        
        db.session.add(invitation)
        invitations_created.append(invitation)
    
    # Update assessment status if needed
    if assessment.status == AssessmentStatus.DRAFT:
        assessment.status = AssessmentStatus.SENT
    
    db.session.commit()
    
    # TODO: Send invitation emails
    
    return jsonify({
        'message': f'{len(invitations_created)} invitations sent',
        'invitations': [{
            'id': inv.id,
            'email': inv.evaluator_email,
            'public_url': inv.generate_public_url(request.host_url)
        } for inv in invitations_created]
    }), 201

@bp.route('/<int:id>/responses', methods=['GET'])
@jwt_required()
@tenant_required
def get_assessment_responses(id):
    """Get responses for an assessment"""
    user_id = get_current_user_id()
    
    assessment = Assessment.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if assessment.beneficiary_id != user_id and assessment.created_by_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # If beneficiary, check if results are shown
    if assessment.beneficiary_id == user_id and not assessment.show_results_to_beneficiary:
        return jsonify({'error': 'Results are not available yet'}), 403
    
    responses = assessment.responses
    
    return jsonify({
        'responses': [{
            'id': resp.id,
            'respondent_name': resp.respondent.full_name if resp.respondent and not assessment.is_anonymous else 'Anonymous',
            'invitation_role': resp.invitation.evaluator_role.value if resp.invitation else None,
            'started_at': resp.started_at.isoformat(),
            'completed_at': resp.completed_at.isoformat() if resp.completed_at else None,
            'time_spent': resp.time_spent,
            'total_score': resp.total_score,
            'weighted_score': resp.weighted_score
        } for resp in responses]
    })

@bp.route('/<int:id>/submit', methods=['POST'])
@jwt_required()
@tenant_required
def submit_assessment_response(id):
    """Submit a response to an assessment"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    assessment = Assessment.query.filter_by(id=id).first_or_404()
    
    # Check if assessment is open
    if assessment.status not in [AssessmentStatus.SENT, AssessmentStatus.IN_PROGRESS]:
        return jsonify({'error': 'Assessment is not accepting responses'}), 400
    
    # Check deadline
    if assessment.deadline and datetime.utcnow() > assessment.deadline:
        return jsonify({'error': 'Assessment deadline has passed'}), 400
    
    # Get or create response
    response = AssessmentResponse.query.filter_by(
        assessment_id=id,
        respondent_id=user_id
    ).first()
    
    if not response:
        response = AssessmentResponse(
            assessment_id=id,
            respondent_id=user_id,
            started_at=datetime.utcnow()
        )
        db.session.add(response)
    
    # Process question responses
    total_score = 0
    weighted_score = 0
    total_weight = 0
    
    for q_data in data.get('responses', []):
        question = AssessmentQuestion.query.filter_by(
            id=q_data['question_id'],
            assessment_id=id
        ).first()
        
        if not question:
            continue
        
        # Get or create question response
        q_response = AssessmentQuestionResponse.query.filter_by(
            assessment_response_id=response.id,
            question_id=question.id
        ).first()
        
        if not q_response:
            q_response = AssessmentQuestionResponse(
                assessment_response_id=response.id,
                question_id=question.id
            )
            db.session.add(q_response)
        
        # Set response data
        q_response.rating_value = q_data.get('rating_value')
        q_response.text_value = q_data.get('text_value')
        q_response.selected_options = q_data.get('selected_options')
        q_response.ranking_order = q_data.get('ranking_order')
        
        # Calculate score for rating questions
        if question.question_type.value == 'RATING' and q_response.rating_value:
            score = (q_response.rating_value - question.min_rating) / (question.max_rating - question.min_rating) * 100
            q_response.score = score
            q_response.weighted_score = score * question.weight
            
            total_score += score
            weighted_score += q_response.weighted_score
            total_weight += question.weight
    
    # Update response totals
    response.completed_at = datetime.utcnow()
    response.time_spent = int((response.completed_at - response.started_at).total_seconds())
    response.total_score = total_score / len(data.get('responses', [])) if data.get('responses') else 0
    response.weighted_score = weighted_score / total_weight if total_weight > 0 else 0
    
    # Update assessment completion rate
    assessment.completion_rate = assessment.calculate_completion_rate()
    
    # Update assessment status if this is the first response
    if assessment.status == AssessmentStatus.SENT:
        assessment.status = AssessmentStatus.IN_PROGRESS
    
    db.session.commit()
    
    return jsonify({
        'message': 'Response submitted successfully',
        'total_score': response.total_score,
        'weighted_score': response.weighted_score
    })

@bp.route('/<int:id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_assessment(id):
    """Mark an assessment as completed"""
    user_id = get_current_user_id()
    
    assessment = Assessment.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if assessment.created_by_id != user_id:
        return jsonify({'error': 'Only the creator can complete the assessment'}), 403
    
    # Calculate final scores
    total_score = 0
    response_count = 0
    
    for response in assessment.responses:
        if response.completed_at:
            total_score += response.weighted_score or response.total_score or 0
            response_count += 1
    
    assessment.average_score = total_score / response_count if response_count > 0 else 0
    assessment.completion_rate = assessment.calculate_completion_rate()
    assessment.status = AssessmentStatus.COMPLETED
    
    db.session.commit()
    
    return jsonify({
        'message': 'Assessment completed',
        'average_score': assessment.average_score,
        'completion_rate': assessment.completion_rate
    })

@bp.route('/competencies', methods=['GET'])
@jwt_required()
@tenant_required
def get_competencies():
    """Get all competencies"""
    competencies = Competency.query.all()
    
    return jsonify({
        'competencies': [{
            'id': c.id,
            'name': c.name,
            'category': c.category,
            'description': c.description,
            'parent_id': c.parent_id,
            'is_technical': c.is_technical,
            'is_behavioral': c.is_behavioral,
            'industry_specific': c.industry_specific
        } for c in competencies]
    })

@bp.route('/public/<token>', methods=['GET'])
def get_public_assessment(token):
    """Get assessment for external evaluators"""
    invitation = AssessmentInvitation.query.filter_by(access_token=token).first_or_404()
    
    # Check if invitation is valid
    if invitation.status == 'expired':
        return jsonify({'error': 'Invitation has expired'}), 400
    
    if invitation.token_expiry and datetime.utcnow() > invitation.token_expiry:
        invitation.status = 'expired'
        db.session.commit()
        return jsonify({'error': 'Invitation has expired'}), 400
    
    # Mark as opened if first time
    if not invitation.opened_at:
        invitation.opened_at = datetime.utcnow()
        invitation.status = 'opened'
        db.session.commit()
    
    assessment = invitation.assessment
    
    return jsonify({
        'assessment': {
            'id': assessment.id,
            'title': assessment.title,
            'description': assessment.description,
            'beneficiary_name': assessment.beneficiary.full_name if not assessment.is_anonymous else 'Anonymous',
            'deadline': assessment.deadline.isoformat() if assessment.deadline else None,
            'custom_message': invitation.custom_message
        },
        'invitation': {
            'id': invitation.id,
            'evaluator_name': invitation.evaluator_name,
            'evaluator_role': invitation.evaluator_role.value
        }
    })

@bp.route('/public/<token>/submit', methods=['POST'])
def submit_public_assessment_response(token):
    """Submit assessment response from external evaluator"""
    data = request.get_json()
    
    invitation = AssessmentInvitation.query.filter_by(access_token=token).first_or_404()
    
    # Check if invitation is valid
    if invitation.status in ['completed', 'expired']:
        return jsonify({'error': f'Invitation is {invitation.status}'}), 400
    
    assessment = invitation.assessment
    
    # Create response
    response = AssessmentResponse(
        assessment_id=assessment.id,
        invitation_id=invitation.id,
        started_at=datetime.utcnow(),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(response)
    
    # Process responses (similar to authenticated submission)
    # ... (response processing logic)
    
    # Mark invitation as completed
    invitation.status = 'completed'
    invitation.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Thank you for your response'})