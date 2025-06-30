"""Database models package."""

from app.models.base import TenantBaseModel
from app.models.tenant import Tenant
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.course import Course, CourseStatus, CourseFormat, DifficultyLevel
from app.models.course_session import CourseSession
from app.models.course_progress import CourseProgress
from app.models.enrollment import Enrollment, EnrollmentStatus
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
from app.models.learning_path import LearningPath, LearningPathUpdate, LearningMilestone
from app.models.chat import Conversation, ChatMessage
from app.models.coach_note import CoachNote
from app.models.audit_log import AuditLog
from app.models.notification import Notification

# Bilan de Competence models
from app.models.assessment import (
    Assessment, AssessmentType, AssessmentStatus, QuestionType as AssessmentQuestionType,
    AssessmentQuestion, AssessmentInvitation, AssessmentResponse, 
    AssessmentQuestionResponse, Competency
)
from app.models.career import (
    CareerStatus, MarketDataSource, OpportunityStatus,
    JobMarketData, CareerPath, CareerMilestone as BilanCareerMilestone, SkillGapAnalysis,
    JobOpportunity, CareerDocument
)
from app.models.compliance import (
    BilanPhase, SessionStatus, ConsentType,
    BilanSession, TimeLog, CertifiedConsultant, ComplianceCheck,
    GDPRConsent, DataRetention, LegalReport
)
from app.models.learning_advanced import (
    ContentType, LearningPathStatus, MentorshipStatus, SimulationType,
    AdvancedLearningContent, PersonalizedLearningPath, PathContent, AdvancedLearningMilestone,
    MentorshipMatch, MentorshipSession, JobSimulation, SimulationAttempt,
    ContentRecommendation, ContentProgress
)

__all__ = [
    "TenantBaseModel",
    "Tenant",
    "User",
    "Beneficiary",
    "Program",
    "ProgramStatus",
    "ProgramType",
    "Course",
    "CourseStatus",
    "CourseFormat",
    "DifficultyLevel",
    "CourseSession",
    "CourseProgress",
    "Enrollment",
    "EnrollmentStatus",
    "Evaluation",
    "Question",
    "EvaluationAttempt",
    "QuestionResponse",
    "QuestionBank",
    "EvaluationStatus",
    "QuestionType",
    "AttemptStatus",
    "LearningPath",
    "LearningPathUpdate",
    "LearningMilestone",
    "Conversation",
    "ChatMessage",
    "CoachNote",
    "AuditLog",
    "Notification",
    # Bilan de Competence models
    "Assessment", "AssessmentType", "AssessmentStatus", "AssessmentQuestionType",
    "AssessmentQuestion", "AssessmentInvitation", "AssessmentResponse", 
    "AssessmentQuestionResponse", "Competency",
    "CareerStatus", "MarketDataSource", "OpportunityStatus",
    "JobMarketData", "CareerPath", "BilanCareerMilestone", "SkillGapAnalysis",
    "JobOpportunity", "CareerDocument",
    "BilanPhase", "SessionStatus", "ConsentType",
    "BilanSession", "TimeLog", "CertifiedConsultant", "ComplianceCheck",
    "GDPRConsent", "DataRetention", "LegalReport",
    "ContentType", "LearningPathStatus", "MentorshipStatus", "SimulationType",
    "AdvancedLearningContent", "PersonalizedLearningPath", "PathContent", "AdvancedLearningMilestone",
    "MentorshipMatch", "MentorshipSession", "JobSimulation", "SimulationAttempt",
    "ContentRecommendation", "ContentProgress",
]
