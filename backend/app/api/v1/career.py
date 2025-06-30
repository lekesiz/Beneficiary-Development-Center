"""
Career Intelligence System API endpoints
For Bilan de Compétence Platform
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.career import (
    JobMarketData, CareerPath, CareerMilestone, SkillGapAnalysis,
    JobOpportunity, CareerDocument, CareerStatus, OpportunityStatus
)
from app.models.user import User
from app.extensions import db
from app.core.decorators import tenant_required
from app.core.jwt_utils import get_current_user_id
from app.core.pagination import paginate
from datetime import datetime, date
from sqlalchemy import and_, or_, func
import json

bp = Blueprint('career', __name__, url_prefix='/api/v1/career')

@bp.route('/market-data', methods=['GET'])
@jwt_required()
@tenant_required
def get_job_market_data():
    """Get job market data with filters"""
    query = JobMarketData.query
    
    # Apply filters
    job_title = request.args.get('job_title')
    if job_title:
        query = query.filter(JobMarketData.job_title.ilike(f'%{job_title}%'))
    
    industry = request.args.get('industry')
    if industry:
        query = query.filter(JobMarketData.industry == industry)
    
    location = request.args.get('location')
    if location:
        query = query.filter(JobMarketData.location == location)
    
    # Filter by demand level
    demand_level = request.args.get('demand_level')
    if demand_level:
        query = query.filter(JobMarketData.demand_level == demand_level)
    
    # Sort by relevance or date
    sort_by = request.args.get('sort_by', 'collected_date')
    if sort_by == 'salary':
        query = query.order_by(JobMarketData.average_salary_max.desc())
    elif sort_by == 'growth':
        query = query.order_by(JobMarketData.growth_rate.desc())
    elif sort_by == 'demand':
        query = query.order_by(JobMarketData.job_openings_count.desc())
    else:
        query = query.order_by(JobMarketData.collected_date.desc())
    
    # Only return valid data
    query = query.filter(
        or_(
            JobMarketData.valid_until.is_(None),
            JobMarketData.valid_until >= date.today()
        )
    )
    
    return paginate(query, JobMarketData)

@bp.route('/market-data/<int:id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_job_market_detail(id):
    """Get detailed job market data"""
    data = JobMarketData.query.filter_by(id=id).first_or_404()
    
    return jsonify({
        'id': data.id,
        'job_title': data.job_title,
        'industry': data.industry,
        'location': data.location,
        'average_salary_min': data.average_salary_min,
        'average_salary_max': data.average_salary_max,
        'salary_currency': data.salary_currency,
        'job_openings_count': data.job_openings_count,
        'growth_rate': data.growth_rate,
        'demand_level': data.demand_level,
        'future_outlook': data.future_outlook,
        'automation_risk': data.automation_risk,
        'required_skills': data.required_skills,
        'preferred_skills': data.preferred_skills,
        'emerging_skills': data.emerging_skills,
        'data_source': data.data_source.value if data.data_source else None,
        'source_name': data.source_name,
        'collected_date': data.collected_date.isoformat() if data.collected_date else None,
        'is_remote_friendly': data.is_remote_friendly
    })

@bp.route('/paths', methods=['GET'])
@jwt_required()
@tenant_required
def get_career_paths():
    """Get user's career paths"""
    user_id = get_current_user_id()
    
    paths = CareerPath.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'career_paths': [{
            'id': path.id,
            'current_job_title': path.current_job_title,
            'current_industry': path.current_industry,
            'target_job_title': path.target_job_title,
            'target_industry': path.target_industry,
            'career_status': path.career_status.value if path.career_status else None,
            'progress_percentage': path.progress_percentage,
            'target_timeline_months': path.target_timeline_months,
            'estimated_completion': path.estimated_completion.isoformat() if path.estimated_completion else None,
            'feasibility_score': path.feasibility_score,
            'milestones_count': len(path.milestones),
            'created_at': path.created_at.isoformat()
        } for path in paths]
    })

@bp.route('/paths', methods=['POST'])
@jwt_required()
@tenant_required
def create_career_path():
    """Create a new career path"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    # Check if user already has an active path
    existing_path = CareerPath.query.filter_by(
        user_id=user_id,
        career_status=CareerStatus.PLANNING
    ).first()
    
    if existing_path:
        return jsonify({'error': 'You already have an active career path'}), 400
    
    # Create career path
    career_path = CareerPath(
        user_id=user_id,
        current_job_title=data.get('current_job_title'),
        current_industry=data.get('current_industry'),
        years_experience=data.get('years_experience'),
        current_salary=data.get('current_salary'),
        career_status=CareerStatus.EXPLORING,
        target_job_title=data.get('target_job_title'),
        target_industry=data.get('target_industry'),
        target_salary_min=data.get('target_salary_min'),
        target_salary_max=data.get('target_salary_max'),
        target_timeline_months=data.get('target_timeline_months', 12),
        career_motivation=data.get('career_motivation'),
        constraints=data.get('constraints', []),
        preferences=data.get('preferences', [])
    )
    
    # Link to market data if provided
    if data.get('target_market_data_id'):
        market_data = JobMarketData.query.filter_by(id=data['target_market_data_id']).first()
        if market_data:
            career_path.target_market_data_id = market_data.id
    
    db.session.add(career_path)
    db.session.commit()
    
    # TODO: Trigger AI analysis for feasibility and recommendations
    
    return jsonify({
        'id': career_path.id,
        'message': 'Career path created successfully'
    }), 201

@bp.route('/paths/<int:id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_career_path_detail(id):
    """Get detailed career path information"""
    user_id = get_current_user_id()
    
    path = CareerPath.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    return jsonify({
        'id': path.id,
        'current_job_title': path.current_job_title,
        'current_industry': path.current_industry,
        'years_experience': path.years_experience,
        'current_salary': path.current_salary,
        'career_status': path.career_status.value if path.career_status else None,
        'target_job_title': path.target_job_title,
        'target_industry': path.target_industry,
        'target_salary_min': path.target_salary_min,
        'target_salary_max': path.target_salary_max,
        'target_timeline_months': path.target_timeline_months,
        'progress_percentage': path.progress_percentage,
        'last_progress_update': path.last_progress_update.isoformat() if path.last_progress_update else None,
        'estimated_completion': path.estimated_completion.isoformat() if path.estimated_completion else None,
        'career_motivation': path.career_motivation,
        'constraints': path.constraints,
        'preferences': path.preferences,
        'feasibility_score': path.feasibility_score,
        'recommended_path': path.recommended_path,
        'alternative_paths': path.alternative_paths,
        'market_data': {
            'id': path.target_market_data.id,
            'average_salary_min': path.target_market_data.average_salary_min,
            'average_salary_max': path.target_market_data.average_salary_max,
            'demand_level': path.target_market_data.demand_level,
            'growth_rate': path.target_market_data.growth_rate
        } if path.target_market_data else None,
        'milestones': [{
            'id': m.id,
            'title': m.title,
            'status': m.status,
            'progress_percentage': m.progress_percentage,
            'target_date': m.target_date.isoformat() if m.target_date else None
        } for m in path.milestones],
        'created_at': path.created_at.isoformat(),
        'updated_at': path.updated_at.isoformat()
    })

@bp.route('/paths/<int:id>/milestones', methods=['POST'])
@jwt_required()
@tenant_required
def create_career_milestone(id):
    """Create a milestone for a career path"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    path = CareerPath.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    milestone = CareerMilestone(
        career_path_id=id,
        title=data['title'],
        description=data.get('description'),
        target_date=datetime.fromisoformat(data['target_date']) if data.get('target_date') else None,
        milestone_type=data.get('milestone_type', 'skill'),
        category=data.get('category'),
        requirements=data.get('requirements', []),
        success_criteria=data.get('success_criteria', []),
        status='pending'
    )
    
    db.session.add(milestone)
    db.session.commit()
    
    return jsonify({
        'id': milestone.id,
        'title': milestone.title,
        'status': milestone.status
    }), 201

@bp.route('/milestones/<int:id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_career_milestone(id):
    """Mark a milestone as completed"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    milestone = CareerMilestone.query.filter_by(id=id).first_or_404()
    
    # Verify ownership
    if milestone.career_path.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    milestone.status = 'completed'
    milestone.completed_date = date.today()
    milestone.progress_percentage = 100.0
    
    if data.get('evidence_documents'):
        milestone.evidence_documents = data['evidence_documents']
    
    # Update career path progress
    path = milestone.career_path
    completed_milestones = sum(1 for m in path.milestones if m.status == 'completed')
    path.progress_percentage = (completed_milestones / len(path.milestones)) * 100 if path.milestones else 0
    path.last_progress_update = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Milestone completed',
        'path_progress': path.progress_percentage
    })

@bp.route('/skill-gap-analysis', methods=['POST'])
@jwt_required()
@tenant_required
def create_skill_gap_analysis():
    """Create a skill gap analysis"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    analysis = SkillGapAnalysis(
        user_id=user_id,
        career_path_id=data.get('career_path_id'),
        current_skills=data.get('current_skills', {}),
        required_skills=data.get('required_skills', {}),
        analysis_date=datetime.utcnow()
    )
    
    # Calculate skill gaps
    skill_gaps = {}
    for skill, required_level in analysis.required_skills.items():
        current_level = analysis.current_skills.get(skill, 0)
        if current_level < required_level:
            skill_gaps[skill] = required_level - current_level
    
    analysis.skill_gaps = skill_gaps
    
    # Identify priority skills
    priority_skills = sorted(skill_gaps.items(), key=lambda x: x[1], reverse=True)[:5]
    analysis.priority_skills = [skill[0] for skill in priority_skills]
    
    # Identify critical gaps (gaps > 3 levels)
    critical_gaps = [skill for skill, gap in skill_gaps.items() if gap > 3]
    analysis.critical_gaps = critical_gaps
    
    # TODO: Get AI recommendations for courses and certifications
    
    db.session.add(analysis)
    db.session.commit()
    
    return jsonify({
        'id': analysis.id,
        'skill_gaps': analysis.skill_gaps,
        'priority_skills': analysis.priority_skills,
        'critical_gaps': analysis.critical_gaps
    }), 201

@bp.route('/skill-gap-analysis/<int:id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_skill_gap_analysis(id):
    """Get skill gap analysis details"""
    user_id = get_current_user_id()
    
    analysis = SkillGapAnalysis.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    return jsonify({
        'id': analysis.id,
        'analysis_date': analysis.analysis_date.isoformat(),
        'current_skills': analysis.current_skills,
        'required_skills': analysis.required_skills,
        'skill_gaps': analysis.skill_gaps,
        'priority_skills': analysis.priority_skills,
        'critical_gaps': analysis.critical_gaps,
        'recommended_courses': analysis.recommended_courses,
        'recommended_certifications': analysis.recommended_certifications,
        'recommended_projects': analysis.recommended_projects,
        'estimated_learning_hours': analysis.estimated_learning_hours,
        'market_demand_alignment': analysis.market_demand_alignment,
        'competitive_advantage_skills': analysis.competitive_advantage_skills,
        'skills_improved': analysis.skills_improved,
        'last_update': analysis.last_update.isoformat() if analysis.last_update else None
    })

@bp.route('/opportunities', methods=['GET'])
@jwt_required()
@tenant_required
def get_job_opportunities():
    """Get job opportunities for user"""
    user_id = get_current_user_id()
    
    query = JobOpportunity.query.filter_by(user_id=user_id)
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter(JobOpportunity.status == OpportunityStatus[status.upper()])
    
    # Sort by match score
    query = query.order_by(JobOpportunity.match_score.desc())
    
    return paginate(query, JobOpportunity)

@bp.route('/opportunities/search', methods=['POST'])
@jwt_required()
@tenant_required
def search_job_opportunities():
    """Search and save job opportunities"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    # TODO: Integrate with job search APIs
    # For now, create a mock opportunity
    
    opportunity = JobOpportunity(
        job_title=data['job_title'],
        company_name=data.get('company_name'),
        location=data.get('location'),
        job_type=data.get('job_type', 'full_time'),
        job_description=data.get('job_description'),
        requirements=data.get('requirements', []),
        nice_to_have=data.get('nice_to_have', []),
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        benefits=data.get('benefits', []),
        application_url=data.get('application_url'),
        application_deadline=datetime.fromisoformat(data['application_deadline']) if data.get('application_deadline') else None,
        source='manual',
        posted_date=date.today(),
        user_id=user_id,
        status=OpportunityStatus.SAVED,
        saved_at=datetime.utcnow()
    )
    
    # Calculate match score based on user profile
    # TODO: Implement proper matching algorithm
    opportunity.match_score = 75.0
    
    db.session.add(opportunity)
    db.session.commit()
    
    return jsonify({
        'id': opportunity.id,
        'job_title': opportunity.job_title,
        'match_score': opportunity.match_score
    }), 201

@bp.route('/opportunities/<int:id>/apply', methods=['POST'])
@jwt_required()
@tenant_required
def apply_to_opportunity(id):
    """Mark opportunity as applied"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    opportunity = JobOpportunity.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    opportunity.status = OpportunityStatus.APPLIED
    opportunity.applied_at = datetime.utcnow()
    
    if data.get('notes'):
        opportunity.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({'message': 'Application status updated'})

@bp.route('/documents', methods=['GET'])
@jwt_required()
@tenant_required
def get_career_documents():
    """Get user's career documents"""
    user_id = get_current_user_id()
    
    documents = CareerDocument.query.filter_by(
        user_id=user_id,
        is_current=True
    ).all()
    
    return jsonify({
        'documents': [{
            'id': doc.id,
            'document_type': doc.document_type,
            'file_name': doc.file_name,
            'version': doc.version,
            'language': doc.language,
            'ats_score': doc.ats_score,
            'times_used': doc.times_used,
            'last_used': doc.last_used.isoformat() if doc.last_used else None,
            'created_at': doc.created_at.isoformat()
        } for doc in documents]
    })

@bp.route('/documents', methods=['POST'])
@jwt_required()
@tenant_required
def upload_career_document():
    """Upload a career document"""
    user_id = get_current_user_id()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    document_type = request.form.get('document_type', 'resume')
    
    # TODO: Implement file upload and storage
    # TODO: Implement ATS score calculation
    
    # Create document record
    document = CareerDocument(
        user_id=user_id,
        document_type=document_type,
        file_name=file.filename,
        file_path=f'/uploads/career/{user_id}/{file.filename}',
        file_size=0,  # TODO: Get actual file size
        version=1,
        is_current=True,
        language=request.form.get('language', 'fr')
    )
    
    # Mark previous versions as not current
    CareerDocument.query.filter_by(
        user_id=user_id,
        document_type=document_type,
        is_current=True
    ).update({'is_current': False})
    
    db.session.add(document)
    db.session.commit()
    
    return jsonify({
        'id': document.id,
        'file_name': document.file_name,
        'message': 'Document uploaded successfully'
    }), 201

@bp.route('/insights', methods=['GET'])
@jwt_required()
@tenant_required
def get_career_insights():
    """Get AI-powered career insights for user"""
    user_id = get_current_user_id()
    
    # Get user's career path
    career_path = CareerPath.query.filter_by(
        user_id=user_id
    ).order_by(CareerPath.created_at.desc()).first()
    
    # Get latest skill gap analysis
    skill_analysis = SkillGapAnalysis.query.filter_by(
        user_id=user_id
    ).order_by(SkillGapAnalysis.analysis_date.desc()).first()
    
    # Get job opportunities statistics
    opportunities = JobOpportunity.query.filter_by(user_id=user_id).all()
    
    insights = {
        'career_progress': {
            'current_status': career_path.career_status.value if career_path else None,
            'progress_percentage': career_path.progress_percentage if career_path else 0,
            'milestones_completed': sum(1 for m in career_path.milestones if m.status == 'completed') if career_path else 0,
            'estimated_completion': career_path.estimated_completion.isoformat() if career_path and career_path.estimated_completion else None
        },
        'skill_status': {
            'total_skills': len(skill_analysis.current_skills) if skill_analysis else 0,
            'skills_to_develop': len(skill_analysis.skill_gaps) if skill_analysis else 0,
            'critical_gaps': skill_analysis.critical_gaps if skill_analysis else [],
            'market_alignment': skill_analysis.market_demand_alignment if skill_analysis else 0
        },
        'opportunity_metrics': {
            'total_opportunities': len(opportunities),
            'applied': sum(1 for o in opportunities if o.status == OpportunityStatus.APPLIED),
            'average_match_score': sum(o.match_score or 0 for o in opportunities) / len(opportunities) if opportunities else 0
        },
        'recommendations': {
            'next_steps': [],  # TODO: Generate AI recommendations
            'trending_skills': [],  # TODO: Get from market data
            'hot_jobs': []  # TODO: Get from market data
        }
    }
    
    return jsonify(insights)