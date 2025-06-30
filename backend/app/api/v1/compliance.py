"""
Legal Compliance System API endpoints
For Bilan de Compétence Platform - French Labor Code Compliance
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from app.models.compliance import (
    BilanSession, TimeLog, CertifiedConsultant, ComplianceCheck,
    GDPRConsent, DataRetention, LegalReport,
    BilanPhase, SessionStatus, ConsentType
)
from app.models.user import User
from app.extensions import db
from app.core.decorators import tenant_required
from app.core.jwt_utils import get_current_user_id
from app.core.pagination import paginate
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, func
import io
import json

bp = Blueprint('compliance', __name__, url_prefix='/api/v1/compliance')

@bp.route('/sessions', methods=['GET'])
@jwt_required()
@tenant_required
def get_bilan_sessions():
    """Get Bilan sessions for user"""
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    
    # Check if user is consultant or beneficiary
    if user.role == 'consultant':
        query = BilanSession.query.filter_by(consultant_id=user_id)
    else:
        query = BilanSession.query.filter_by(beneficiary_id=user_id)
    
    # Apply filters
    phase = request.args.get('phase')
    if phase:
        query = query.filter(BilanSession.phase == BilanPhase[phase.upper()])
    
    status = request.args.get('status')
    if status:
        query = query.filter(BilanSession.status == SessionStatus[status.upper()])
    
    # Sort by date
    query = query.order_by(BilanSession.scheduled_start.desc())
    
    return paginate(query, BilanSession)

@bp.route('/sessions', methods=['POST'])
@jwt_required()
@tenant_required
def create_bilan_session():
    """Create a new Bilan session"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    # Verify user is a certified consultant
    consultant = CertifiedConsultant.query.filter_by(user_id=user_id).first()
    if not consultant or not consultant.is_active:
        return jsonify({'error': 'Only certified consultants can create sessions'}), 403
    
    # Validate minimum duration (1 hour)
    scheduled_start = datetime.fromisoformat(data['scheduled_start'])
    scheduled_end = datetime.fromisoformat(data['scheduled_end'])
    duration = (scheduled_end - scheduled_start).total_seconds() / 60
    
    if duration < 60:
        return jsonify({'error': 'Session must be at least 60 minutes'}), 400
    
    # Generate contract number
    contract_number = f"BILAN-{datetime.now().year}-{BilanSession.query.count() + 1:04d}"
    
    # Create session
    session = BilanSession(
        beneficiary_id=data['beneficiary_id'],
        consultant_id=user_id,
        session_type=data.get('session_type', 'individual'),
        phase=BilanPhase[data['phase'].upper()],
        status=SessionStatus.SCHEDULED,
        scheduled_start=scheduled_start,
        scheduled_end=scheduled_end,
        contract_number=contract_number,
        funding_source=data.get('funding_source', 'CPF'),
        legal_framework='Code du travail L6313-1',
        objectives=data.get('objectives'),
        agenda=data.get('agenda', [])
    )
    
    # Validate against consultant's capacity
    if consultant.current_bilans_count >= consultant.max_concurrent_bilans:
        return jsonify({'error': 'Consultant has reached maximum concurrent bilans'}), 400
    
    db.session.add(session)
    
    # Update consultant's current count
    consultant.current_bilans_count += 1
    
    db.session.commit()
    
    return jsonify({
        'id': session.id,
        'contract_number': session.contract_number,
        'scheduled_start': session.scheduled_start.isoformat()
    }), 201

@bp.route('/sessions/<int:id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_bilan_session_detail(id):
    """Get detailed session information"""
    user_id = get_current_user_id()
    
    session = BilanSession.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if session.beneficiary_id != user_id and session.consultant_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': session.id,
        'beneficiary': {
            'id': session.beneficiary.id,
            'name': session.beneficiary.full_name
        },
        'consultant': {
            'id': session.consultant.id,
            'name': session.consultant.full_name
        },
        'session_type': session.session_type,
        'phase': session.phase.value,
        'status': session.status.value,
        'scheduled_start': session.scheduled_start.isoformat(),
        'scheduled_end': session.scheduled_end.isoformat(),
        'actual_start': session.actual_start.isoformat() if session.actual_start else None,
        'actual_end': session.actual_end.isoformat() if session.actual_end else None,
        'duration_minutes': session.duration_minutes,
        'contract_number': session.contract_number,
        'funding_source': session.funding_source,
        'legal_framework': session.legal_framework,
        'objectives': session.objectives,
        'agenda': session.agenda,
        'outcomes': session.outcomes,
        'action_items': session.action_items,
        'consent_obtained': session.consent_obtained,
        'validated_by_consultant': session.validated_by_consultant,
        'validated_by_beneficiary': session.validated_by_beneficiary,
        'time_logs': [{
            'id': log.id,
            'activity_type': log.activity_type,
            'duration_minutes': log.duration_minutes,
            'is_billable': log.is_billable
        } for log in session.time_logs],
        'total_time_logged': sum(log.duration_minutes or 0 for log in session.time_logs)
    })

@bp.route('/sessions/<int:id>/start', methods=['POST'])
@jwt_required()
@tenant_required
def start_bilan_session(id):
    """Start a Bilan session"""
    user_id = get_current_user_id()
    
    session = BilanSession.query.filter_by(id=id).first_or_404()
    
    # Verify consultant
    if session.consultant_id != user_id:
        return jsonify({'error': 'Only the assigned consultant can start the session'}), 403
    
    if session.status != SessionStatus.SCHEDULED:
        return jsonify({'error': 'Session is not in scheduled status'}), 400
    
    session.status = SessionStatus.IN_PROGRESS
    session.actual_start = datetime.utcnow()
    
    # Create time log entry
    time_log = TimeLog(
        session_id=id,
        user_id=user_id,
        start_time=datetime.utcnow(),
        activity_type='session',
        phase=session.phase,
        is_billable=True
    )
    
    db.session.add(time_log)
    db.session.commit()
    
    return jsonify({
        'message': 'Session started',
        'time_log_id': time_log.id
    })

@bp.route('/sessions/<int:id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_bilan_session(id):
    """Complete a Bilan session"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    session = BilanSession.query.filter_by(id=id).first_or_404()
    
    # Verify consultant
    if session.consultant_id != user_id:
        return jsonify({'error': 'Only the assigned consultant can complete the session'}), 403
    
    if session.status != SessionStatus.IN_PROGRESS:
        return jsonify({'error': 'Session is not in progress'}), 400
    
    session.status = SessionStatus.COMPLETED
    session.actual_end = datetime.utcnow()
    session.duration_minutes = int((session.actual_end - session.actual_start).total_seconds() / 60)
    
    # Update session data
    if data.get('outcomes'):
        session.outcomes = data['outcomes']
    if data.get('action_items'):
        session.action_items = data['action_items']
    if data.get('session_notes'):
        session.session_notes = data['session_notes']
    
    session.consent_obtained = data.get('consent_obtained', True)
    
    # Complete active time log
    active_log = TimeLog.query.filter_by(
        session_id=id,
        user_id=user_id,
        end_time=None
    ).first()
    
    if active_log:
        active_log.end_time = datetime.utcnow()
        active_log.duration_minutes = int((active_log.end_time - active_log.start_time).total_seconds() / 60)
    
    db.session.commit()
    
    # Check compliance
    check_session_compliance(session)
    
    return jsonify({
        'message': 'Session completed',
        'duration_minutes': session.duration_minutes
    })

@bp.route('/time-logs', methods=['POST'])
@jwt_required()
@tenant_required
def create_time_log():
    """Create a time log entry"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    time_log = TimeLog(
        session_id=data['session_id'],
        user_id=user_id,
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
        activity_type=data['activity_type'],
        activity_description=data.get('activity_description'),
        phase=BilanPhase[data['phase'].upper()],
        is_billable=data.get('is_billable', True),
        is_remote=data.get('is_remote', False),
        location=data.get('location')
    )
    
    if time_log.end_time:
        time_log.duration_minutes = int((time_log.end_time - time_log.start_time).total_seconds() / 60)
    
    db.session.add(time_log)
    db.session.commit()
    
    return jsonify({
        'id': time_log.id,
        'duration_minutes': time_log.duration_minutes
    }), 201

@bp.route('/consultants', methods=['GET'])
@jwt_required()
@tenant_required
def get_certified_consultants():
    """Get list of certified consultants"""
    query = CertifiedConsultant.query.filter_by(is_active=True)
    
    # Filter by specialization
    specialization = request.args.get('specialization')
    if specialization:
        query = query.filter(CertifiedConsultant.specializations.contains([specialization]))
    
    # Filter by language
    language = request.args.get('language')
    if language:
        query = query.filter(CertifiedConsultant.languages.contains([language]))
    
    # Sort by rating
    query = query.order_by(CertifiedConsultant.average_rating.desc())
    
    return paginate(query, CertifiedConsultant)

@bp.route('/consultants/register', methods=['POST'])
@jwt_required()
@tenant_required
def register_consultant():
    """Register as a certified consultant"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    # Check if already registered
    existing = CertifiedConsultant.query.filter_by(user_id=user_id).first()
    if existing:
        return jsonify({'error': 'Already registered as consultant'}), 400
    
    consultant = CertifiedConsultant(
        user_id=user_id,
        certification_number=data['certification_number'],
        certification_body=data['certification_body'],
        certification_date=date.fromisoformat(data['certification_date']),
        expiry_date=date.fromisoformat(data['expiry_date']),
        specializations=data.get('specializations', []),
        industries=data.get('industries', []),
        languages=data.get('languages', ['fr']),
        years_experience=data.get('years_experience'),
        insurance_policy_number=data.get('insurance_policy_number'),
        insurance_expiry=date.fromisoformat(data['insurance_expiry']) if data.get('insurance_expiry') else None
    )
    
    db.session.add(consultant)
    db.session.commit()
    
    return jsonify({
        'message': 'Consultant registration successful',
        'id': consultant.id
    }), 201

@bp.route('/compliance/check/<int:session_id>', methods=['POST'])
@jwt_required()
@tenant_required
def check_compliance(session_id):
    """Check compliance for a Bilan session"""
    session = BilanSession.query.filter_by(id=session_id).first_or_404()
    
    return jsonify(check_session_compliance(session))

def check_session_compliance(session):
    """Internal function to check session compliance"""
    issues = []
    
    # Check minimum duration (24 hours total)
    total_time = sum(log.duration_minutes or 0 for log in session.time_logs)
    if total_time < 1440:  # 24 hours = 1440 minutes
        issues.append({
            'type': 'duration',
            'severity': 'critical',
            'message': f'Total duration ({total_time/60:.1f} hours) is less than required 24 hours'
        })
    
    # Check three phases
    phases_logged = set(log.phase for log in session.time_logs)
    if len(phases_logged) < 3:
        issues.append({
            'type': 'phases',
            'severity': 'critical',
            'message': 'All three phases must be completed'
        })
    
    # Check consultant certification
    consultant = CertifiedConsultant.query.filter_by(user_id=session.consultant_id).first()
    if not consultant or consultant.expiry_date < date.today():
        issues.append({
            'type': 'certification',
            'severity': 'critical',
            'message': 'Consultant certification is invalid or expired'
        })
    
    # Check consent
    if not session.consent_obtained:
        issues.append({
            'type': 'consent',
            'severity': 'high',
            'message': 'Beneficiary consent not obtained'
        })
    
    # Create compliance check record
    compliance_check = ComplianceCheck(
        check_type='session_compliance',
        entity_type='bilan_session',
        entity_id=session.id,
        performed_by='system',
        is_compliant=len(issues) == 0,
        compliance_score=100 - (len(issues) * 25),
        issues=issues,
        severity='critical' if any(i['severity'] == 'critical' for i in issues) else 'high' if issues else 'low',
        legal_references=['Code du travail L6313-1', 'Décret n°2018-1330']
    )
    
    db.session.add(compliance_check)
    db.session.commit()
    
    return {
        'is_compliant': compliance_check.is_compliant,
        'compliance_score': compliance_check.compliance_score,
        'issues': issues
    }

@bp.route('/gdpr/consent', methods=['POST'])
@jwt_required()
@tenant_required
def record_gdpr_consent():
    """Record GDPR consent"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    consent = GDPRConsent(
        user_id=user_id,
        consent_type=ConsentType[data['consent_type'].upper()],
        consent_given=data['consent_given'],
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        consent_text=data.get('consent_text'),
        legal_basis=data.get('legal_basis', 'consent'),
        purpose=data['purpose'],
        data_categories=data.get('data_categories', []),
        retention_period_days=data.get('retention_period_days', 730)  # 2 years default
    )
    
    # Calculate expiry date
    consent.expiry_date = date.today() + timedelta(days=consent.retention_period_days)
    
    db.session.add(consent)
    db.session.commit()
    
    return jsonify({
        'id': consent.id,
        'expiry_date': consent.expiry_date.isoformat()
    }), 201

@bp.route('/gdpr/consent', methods=['GET'])
@jwt_required()
@tenant_required
def get_gdpr_consents():
    """Get user's GDPR consents"""
    user_id = get_current_user_id()
    
    consents = GDPRConsent.query.filter_by(
        user_id=user_id,
        withdrawn=False
    ).all()
    
    return jsonify({
        'consents': [{
            'id': c.id,
            'consent_type': c.consent_type.value,
            'consent_given': c.consent_given,
            'consent_date': c.consent_date.isoformat(),
            'purpose': c.purpose,
            'expiry_date': c.expiry_date.isoformat() if c.expiry_date else None
        } for c in consents]
    })

@bp.route('/gdpr/consent/<int:id>/withdraw', methods=['POST'])
@jwt_required()
@tenant_required
def withdraw_consent(id):
    """Withdraw GDPR consent"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    consent = GDPRConsent.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    consent.withdrawn = True
    consent.withdrawal_date = datetime.utcnow()
    consent.withdrawal_reason = data.get('reason')
    
    db.session.commit()
    
    # TODO: Trigger data deletion/anonymization processes
    
    return jsonify({'message': 'Consent withdrawn successfully'})

@bp.route('/reports/synthesis/<int:beneficiary_id>', methods=['POST'])
@jwt_required()
@tenant_required
def generate_synthesis_report(beneficiary_id):
    """Generate synthesis document for Bilan"""
    user_id = get_current_user_id()
    
    # Verify consultant permissions
    consultant = CertifiedConsultant.query.filter_by(user_id=user_id).first()
    if not consultant:
        return jsonify({'error': 'Only certified consultants can generate reports'}), 403
    
    # Get all sessions for beneficiary
    sessions = BilanSession.query.filter_by(
        beneficiary_id=beneficiary_id,
        consultant_id=user_id
    ).all()
    
    if not sessions:
        return jsonify({'error': 'No sessions found for beneficiary'}), 404
    
    # Create legal report
    report = LegalReport(
        report_type='synthesis_document',
        beneficiary_id=beneficiary_id,
        generated_by=user_id,
        report_data={
            'sessions': len(sessions),
            'total_hours': sum(s.duration_minutes or 0 for s in sessions) / 60,
            'phases_completed': list(set(s.phase.value for s in sessions)),
            'contract_numbers': [s.contract_number for s in sessions]
        },
        includes_mandatory_elements=True,
        legal_disclaimers=[
            'Document établi conformément au Code du travail',
            'Données personnelles protégées selon RGPD'
        ]
    )
    
    db.session.add(report)
    db.session.commit()
    
    # TODO: Generate actual PDF document
    
    return jsonify({
        'id': report.id,
        'message': 'Report generated successfully'
    }), 201

@bp.route('/reports/<int:id>/validate', methods=['POST'])
@jwt_required()
@tenant_required
def validate_report(id):
    """Validate a legal report"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    report = LegalReport.query.filter_by(id=id).first_or_404()
    
    # Check permissions
    if report.beneficiary_id == user_id:
        report.validated_by_beneficiary = True
    elif report.generated_by == user_id:
        report.validated_by_consultant = True
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if report.validated_by_beneficiary and report.validated_by_consultant:
        report.validation_date = datetime.utcnow()
    
    # Add signature if provided
    if data.get('signature'):
        if report.beneficiary_id == user_id:
            report.beneficiary_signature = data['signature']
        else:
            report.consultant_signature = data['signature']
        
        if report.beneficiary_signature and report.consultant_signature:
            report.signature_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Report validated',
        'fully_validated': report.validated_by_beneficiary and report.validated_by_consultant
    })

@bp.route('/data-retention', methods=['GET'])
@jwt_required()
@tenant_required
def get_data_retention_policies():
    """Get data retention policies"""
    policies = DataRetention.query.filter_by(is_active=True).all()
    
    return jsonify({
        'policies': [{
            'id': p.id,
            'data_type': p.data_type,
            'retention_days': p.retention_days,
            'legal_requirement': p.legal_requirement,
            'legal_reference': p.legal_reference,
            'action_on_expiry': p.action_on_expiry
        } for p in policies]
    })

@bp.route('/statistics', methods=['GET'])
@jwt_required()
@tenant_required
def get_compliance_statistics():
    """Get compliance statistics for dashboard"""
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    
    stats = {}
    
    if user.role == 'consultant':
        consultant = CertifiedConsultant.query.filter_by(user_id=user_id).first()
        if consultant:
            # Get consultant statistics
            sessions = BilanSession.query.filter_by(consultant_id=user_id).all()
            
            stats = {
                'total_bilans': consultant.bilans_completed,
                'active_bilans': consultant.current_bilans_count,
                'average_rating': consultant.average_rating,
                'certification_valid_until': consultant.expiry_date.isoformat(),
                'total_hours_logged': sum(
                    log.duration_minutes or 0 
                    for session in sessions 
                    for log in session.time_logs
                ) / 60,
                'compliance_rate': calculate_compliance_rate(sessions)
            }
    else:
        # Get beneficiary statistics
        sessions = BilanSession.query.filter_by(beneficiary_id=user_id).all()
        
        stats = {
            'total_sessions': len(sessions),
            'completed_phases': list(set(s.phase.value for s in sessions if s.status == SessionStatus.COMPLETED)),
            'total_hours': sum(s.duration_minutes or 0 for s in sessions) / 60,
            'next_session': next(
                (s.scheduled_start.isoformat() for s in sessions if s.status == SessionStatus.SCHEDULED),
                None
            )
        }
    
    return jsonify(stats)

def calculate_compliance_rate(sessions):
    """Calculate compliance rate for sessions"""
    if not sessions:
        return 100.0
    
    compliant_sessions = 0
    for session in sessions:
        if session.status == SessionStatus.COMPLETED:
            check = ComplianceCheck.query.filter_by(
                entity_type='bilan_session',
                entity_id=session.id
            ).order_by(ComplianceCheck.check_date.desc()).first()
            
            if check and check.is_compliant:
                compliant_sessions += 1
    
    return (compliant_sessions / len(sessions)) * 100 if sessions else 100.0