"""
Legal Compliance System Models
For Bilan de Compétence Platform - French Labor Code Compliance
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Float, JSON, Date, CheckConstraint
from sqlalchemy.orm import relationship, validates
from app.models.base import BaseModel
import enum
from datetime import datetime, timedelta

class BilanPhase(enum.Enum):
    PRELIMINARY = "preliminary"  # Phase préliminaire
    INVESTIGATION = "investigation"  # Phase d'investigation
    CONCLUSION = "conclusion"  # Phase de conclusion

class SessionStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class ConsentType(enum.Enum):
    DATA_COLLECTION = "data_collection"
    DATA_PROCESSING = "data_processing"
    DATA_SHARING = "data_sharing"
    MARKETING = "marketing"
    COOKIES = "cookies"

class BilanSession(BaseModel):
    __tablename__ = 'bilan_sessions'
    
    # Basic Information
    beneficiary_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    consultant_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Session Details
    session_type = Column(String(50))  # individual, group, remote
    phase = Column(Enum(BilanPhase), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED)
    
    # Timing
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Legal Requirements
    contract_number = Column(String(100), unique=True)
    funding_source = Column(String(100))  # CPF, company, personal
    legal_framework = Column(String(50))  # Code du travail L6313-1
    
    # Session Content
    objectives = Column(Text)
    agenda = Column(JSON)
    outcomes = Column(Text)
    action_items = Column(JSON)
    
    # Documentation
    session_notes = Column(Text)
    documents_presented = Column(JSON)
    consent_obtained = Column(Boolean, default=False)
    
    # Validation
    validated_by_consultant = Column(Boolean, default=False)
    validated_by_beneficiary = Column(Boolean, default=False)
    validation_date = Column(DateTime)
    
    # Relationships
    beneficiary = relationship("User", foreign_keys=[beneficiary_id], backref="bilan_sessions_as_beneficiary")
    consultant = relationship("User", foreign_keys=[consultant_id], backref="bilan_sessions_as_consultant")
    time_logs = relationship("TimeLog", back_populates="session", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('scheduled_end > scheduled_start', name='check_session_time_order'),
    )
    
    @validates('duration_minutes')
    def validate_duration(self, key, value):
        """Ensure minimum duration requirements are met"""
        if value and value < 60:  # Minimum 1 hour sessions
            raise ValueError("Session duration must be at least 60 minutes")
        return value

class TimeLog(BaseModel):
    __tablename__ = 'time_logs'
    
    # Basic Information
    session_id = Column(Integer, ForeignKey('bilan_sessions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Time Tracking
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Activity Details
    activity_type = Column(String(100))  # interview, assessment, analysis, report_writing
    activity_description = Column(Text)
    phase = Column(Enum(BilanPhase), nullable=False)
    
    # Validation
    is_billable = Column(Boolean, default=True)
    is_validated = Column(Boolean, default=False)
    validated_by = Column(Integer, ForeignKey('users.id'))
    validated_at = Column(DateTime)
    
    # Location/Remote
    is_remote = Column(Boolean, default=False)
    location = Column(String(200))
    
    # Relationships
    session = relationship("BilanSession", back_populates="time_logs")
    user = relationship("User", foreign_keys=[user_id], backref="time_logs")
    validator = relationship("User", foreign_keys=[validated_by])

class CertifiedConsultant(BaseModel):
    __tablename__ = 'certified_consultants'
    
    # Basic Information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    certification_number = Column(String(100), unique=True, nullable=False)
    
    # Certification Details
    certification_body = Column(String(200))  # OPQF, Qualiopi, etc.
    certification_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    
    # Specializations
    specializations = Column(JSON)  # ["career_transition", "skills_assessment", "entrepreneurship"]
    industries = Column(JSON)  # ["IT", "Healthcare", "Finance"]
    languages = Column(JSON)  # ["fr", "en", "es"]
    
    # Experience
    years_experience = Column(Integer)
    bilans_completed = Column(Integer, default=0)
    average_rating = Column(Float)
    
    # Availability
    is_active = Column(Boolean, default=True)
    max_concurrent_bilans = Column(Integer, default=10)
    current_bilans_count = Column(Integer, default=0)
    
    # Legal Compliance
    insurance_policy_number = Column(String(100))
    insurance_expiry = Column(Date)
    
    # Relationships
    user = relationship("User", backref="consultant_certification", uselist=False)

class ComplianceCheck(BaseModel):
    __tablename__ = 'compliance_checks'
    
    # Check Information
    check_type = Column(String(100))  # duration_compliance, phase_completion, documentation
    entity_type = Column(String(50))  # bilan, session, consultant
    entity_id = Column(Integer)
    
    # Check Details
    check_date = Column(DateTime, default=datetime.utcnow)
    performed_by = Column(String(100))  # system, admin_user_id
    
    # Results
    is_compliant = Column(Boolean)
    compliance_score = Column(Float)  # 0-100
    
    # Issues Found
    issues = Column(JSON)  # List of compliance issues
    severity = Column(String(50))  # critical, high, medium, low
    
    # Remediation
    remediation_required = Column(Boolean, default=False)
    remediation_deadline = Column(Date)
    remediation_actions = Column(JSON)
    remediation_completed = Column(Boolean, default=False)
    
    # Legal References
    legal_references = Column(JSON)  # ["Code du travail L6313-1", "Décret n°2018-1330"]
    
    # Audit Trail
    evidence_documents = Column(JSON)
    notes = Column(Text)

class GDPRConsent(BaseModel):
    __tablename__ = 'gdpr_consents'
    
    # User Information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Consent Details
    consent_type = Column(Enum(ConsentType), nullable=False)
    consent_given = Column(Boolean, nullable=False)
    consent_date = Column(DateTime, default=datetime.utcnow)
    
    # Consent Context
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    consent_text = Column(Text)  # The exact text shown to user
    
    # Withdrawal
    withdrawn = Column(Boolean, default=False)
    withdrawal_date = Column(DateTime)
    withdrawal_reason = Column(Text)
    
    # Legal Basis
    legal_basis = Column(String(100))  # consent, legitimate_interest, contract
    purpose = Column(Text)
    data_categories = Column(JSON)  # Types of data being processed
    
    # Retention
    retention_period_days = Column(Integer)
    expiry_date = Column(Date)
    
    # Relationships
    user = relationship("User", backref="gdpr_consents")

class DataRetention(BaseModel):
    __tablename__ = 'data_retention_policies'
    
    # Policy Information
    data_type = Column(String(100), nullable=False)  # assessment_data, personal_info, etc.
    retention_days = Column(Integer, nullable=False)
    
    # Legal Requirements
    legal_requirement = Column(Boolean, default=False)
    legal_reference = Column(String(200))
    
    # Actions
    action_on_expiry = Column(String(50))  # delete, anonymize, archive
    
    # Exceptions
    exceptions = Column(JSON)  # Conditions where retention period changes
    
    # Status
    is_active = Column(Boolean, default=True)
    last_execution = Column(DateTime)
    next_execution = Column(DateTime)

class LegalReport(BaseModel):
    __tablename__ = 'legal_reports'
    
    # Report Information
    report_type = Column(String(100))  # synthesis_document, skills_portfolio, action_plan
    beneficiary_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Generation Details
    generated_date = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, ForeignKey('users.id'))
    
    # Content
    report_data = Column(JSON)  # Structured report data
    file_path = Column(String(500))  # Path to generated PDF
    
    # Validation
    validated_by_consultant = Column(Boolean, default=False)
    validated_by_beneficiary = Column(Boolean, default=False)
    validation_date = Column(DateTime)
    
    # Legal Requirements
    includes_mandatory_elements = Column(Boolean, default=True)
    legal_disclaimers = Column(JSON)
    
    # Signature
    consultant_signature = Column(Text)  # Digital signature
    beneficiary_signature = Column(Text)
    signature_date = Column(DateTime)
    
    # Relationships
    beneficiary = relationship("User", foreign_keys=[beneficiary_id], backref="legal_reports")
    generator = relationship("User", foreign_keys=[generated_by])